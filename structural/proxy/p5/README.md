# Rate Limiting Proxy — Protection Proxy Pattern (gRPC)

> **Design Pattern:** Proxy (Protection Proxy) | **Categoria:** Structural
> **Framework:** gRPC (`grpcio` + `grpcio-tools`) | **Serviços:** Redis

## Objetivo Pedagógico

Demonstrar o padrão Proxy interceptando chamadas a um serviço **gRPC** real
para aplicar **rate limiting** (token bucket) antes de delegar a chamada. O
cliente conecta-se normalmente ao endereço do proxy — usando o stub gerado
do `.proto` — e não tem nenhuma forma de saber que existe um Proxy entre ele
e o serviço real, nem de contorná-lo.

## O Pattern Aplicado

| Papel do Pattern | Classe | Arquivo |
|-------------------|--------|---------|
| Subject (interface gRPC) | `DataServiceServicer` / `DataServiceStub` (gerados) | `src/rate_limiting/infrastructure/generated/service_pb2_grpc.py` |
| RealSubject | `RealDataServiceServicer` | `src/rate_limiting/infrastructure/real_data_service.py` |
| Proxy | `RateLimitingProxyServicer` | `src/rate_limiting/infrastructure/rate_limiting_proxy.py` |
| RateLimiter (estratégia) | `RateLimiter` (Protocol) / `TokenBucketRateLimiter` | `domain/interfaces.py`, `infrastructure/token_bucket_rate_limiter.py` |
| Client | `client_example.py` | `src/client_example.py` |

## Diagrama UML (ASCII)

```
<<gRPC service, gerado de service.proto>>
DataServiceServicer (Subject)
  + GetData(DataRequest) -> DataResponse
        ▲                              ▲
        │ implements                  │ implements
        │                              │
RealDataServiceServicer        RateLimitingProxyServicer
  (RealSubject — lógica de       (Proxy — verifica RateLimiter,
   negócio pura, sem rate         delega ao RealSubject ou
   limiting)                      retorna RESOURCE_EXHAUSTED)
                                        │
                                        │ depende de (DIP)
                                        ▼
                              <<Protocol>> RateLimiter
                                        ▲
                                        │ implements
                                        │
                          TokenBucketRateLimiter (Redis, Lua script)
                          [SlidingWindowRateLimiter — extensão futura, OCP]
```

## Fluxo de uma chamada

```
Cliente (DataServiceStub) ──gRPC──▶ servidor escuta na porta 50051
                                         │
                              RateLimitingProxyServicer.GetData()
                                         │
                         EnforceRateLimitUseCase.execute(client_id)
                                         │
                         RateLimiter.check_and_consume() [Redis EVAL]
                              │ permitido               │ excedido
                              ▼                          ▼
                  RealDataServiceServicer.GetData()   RESOURCE_EXHAUSTED
                              │
                          DataResponse
```

## Princípios SOLID Demonstrados

- **S — Single Responsibility:** a lógica do algoritmo de rate limit
  (`TokenBucketRateLimiter`) está isolada da lógica de negócio do serviço
  real (`RealDataServiceServicer`) e da lógica de decisão allow/deny
  (`EnforceRateLimitUseCase`). Cada classe tem um único motivo para mudar.
- **O — Open/Closed:** o algoritmo de rate limit é uma interface
  (`RateLimiter` Protocol). Adicionar um `SlidingWindowRateLimiter` não exige
  alterar `RateLimitingProxyServicer` nem `EnforceRateLimitUseCase` — basta
  injetar a nova implementação.
- **D — Dependency Inversion:** `RateLimitingProxyServicer.__init__` recebe
  `RateLimiter` (abstração) e `DataServiceServicer` (a interface gerada do
  `.proto`, não uma classe concreta fixa) — pode envolver qualquer serviço
  real e qualquer estratégia de rate limit.
- **L — Liskov Substitution:** tanto `RealDataServiceServicer` quanto
  `RateLimitingProxyServicer` implementam `DataServiceServicer`; um cliente
  gRPC que conversa com qualquer um dos dois não percebe diferença de
  contrato (apenas o comportamento de proteção extra do Proxy).

## Stubs gRPC — como foram gerados

Os arquivos gerados (`service_pb2.py`, `service_pb2.pyi`,
`service_pb2_grpc.py`) estão **commitados** em
`src/rate_limiting/infrastructure/generated/` para que o projeto rode sem
exigir `grpcio-tools` em produção. Eles foram gerados a partir de
`proto/service.proto` com:

```bash
pip install -e ".[dev]"   # inclui grpcio-tools

python -m grpc_tools.protoc \
    -I proto \
    --python_out=src/rate_limiting/infrastructure/generated \
    --grpc_python_out=src/rate_limiting/infrastructure/generated \
    --pyi_out=src/rate_limiting/infrastructure/generated \
    proto/service.proto
```

protoc gera um import plano (`import service_pb2 as service__pb2`) em
`service_pb2_grpc.py`, que só funciona se o diretório `generated/` estiver
diretamente no `sys.path`. Para que o pacote funcione como parte normal de
`rate_limiting.infrastructure`, esse import foi reescrito manualmente (e o
script `scripts/generate_stubs.sh` automatiza essa correção via `sed` para
quem regenerar os stubs no futuro):

```bash
bash scripts/generate_stubs.sh
```

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
```

O servidor gRPC escuta em `localhost:50051`.

## Testando com um cliente Python de exemplo

```bash
docker-compose run --rm app python src/client_example.py
```

Com `RATE_LIMIT_MAX_REQUESTS=5` (padrão), as 5 primeiras chamadas retornam
`OK`; a partir da 6ª, o cliente recebe `StatusCode.RESOURCE_EXHAUSTED`.

## Testando com grpcurl

```bash
grpcurl -plaintext -d '{"client_id": "alice", "key": "greeting"}' \
    localhost:50051 rate_limiting.DataService/GetData
```

Repita a chamada mais vezes que `RATE_LIMIT_MAX_REQUESTS` dentro de
`RATE_LIMIT_WINDOW_SECONDS` para observar o erro `RESOURCE_EXHAUSTED`.

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```

Localmente:

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

- **tests/unit/** usam `fakeredis` (cliente assíncrono) para exercitar o
  Lua script do token bucket sem Redis real, e mocks do `RealDataServiceServicer`
  para verificar que o Proxy delega corretamente dentro do limite e bloqueia
  com `RESOURCE_EXHAUSTED` fora dele.
- **tests/integration/** sobem um `grpc.server` real em uma thread de
  background (porta efêmera escolhida pelo SO) com `RateLimitingProxyServicer`
  registrado, e um `grpc.insecure_channel` real conversa com ele via gRPC de
  ponta a ponta — apenas o Redis é substituído por `fakeredis`.

## Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `REDIS_URL` | URL de conexão com o Redis | `redis://redis:6379/0` |
| `GRPC_PORT` | Porta em que o servidor gRPC escuta | `50051` |
| `RATE_LIMIT_MAX_REQUESTS` | Capacidade do token bucket | `5` |
| `RATE_LIMIT_WINDOW_SECONDS` | Janela de tempo para reabastecer o bucket | `10` |
| `GRPC_TARGET` | Endereço usado pelo `client_example.py` | `localhost:50051` |
| `CLIENT_ID` | client_id usado pelo `client_example.py` | `demo-client` |
