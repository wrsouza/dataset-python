# Multi-step Form Wizard (State) — P5

App Streamlit que implementa um formulário em três etapas
(`PersonalInfo` → `Address` → `Review` → `Submitted`) como uma máquina
de estados explícita, sem nenhum serviço externo — tudo vive em
`st.session_state`.

## Objetivo pedagógico

Demonstrar o pattern **State** num cenário de UI: `WizardSession`
(Context) delega `next_step`/`previous_step`/`submit` ao objeto de
etapa atual, sem nenhum `if/elif` checando em qual etapa o usuário
está. Cada etapa decide por si só quais transições permite — `Review`
não pode `next_step` (não existe próxima etapa), só `previous_step` e
`submit`.

Elementos do pattern:
- **Context:** `WizardSession` (`domain/entities.py`)
- **State (abstrato):** `WizardStep` (`domain/interfaces.py`)
- **Concrete States:** `PersonalInfoStep`, `AddressStep`, `ReviewStep`, `SubmittedStep` (`infrastructure/states/`)

## Diagrama (ASCII)

```
PersonalInfo ──next_step──► Address ──next_step──► Review ──submit──► Submitted
                  ▲              │                     │
                  └──previous_step┘◄────previous_step───┘
```

## Como rodar

```bash
docker-compose up --build
```

App disponível em `http://localhost:8501`.

## Testes

```bash
pip install -e ".[dev]"
pytest --cov=src --cov-report=term-missing
```

`app.py` é excluído do cálculo de cobertura (mesmo padrão dos demais
projetos Streamlit do dataset); a FSM e os use cases são testados sem
nenhuma dependência de `streamlit`.

## SOLID

- **SRP:** cada etapa concreta só sabe lidar com suas próprias transições; `WizardSession` só acumula os dados coletados, sem saber qual etapa vem a seguir.
- **OCP:** uma nova etapa (ex.: `PaymentStep`) é uma nova classe `WizardStep` — sem tocar nas etapas existentes.
- **LSP:** qualquer `WizardStep` concreto pode ocupar `WizardSession._state` — todos respeitam o mesmo contrato (transições não suportadas levantam `InvalidTransitionError` por padrão).
- **ISP:** `WizardStep` expõe só as três transições que o domínio precisa; cada etapa concreta sobrescreve apenas as que permite.
- **DIP:** `app.py` depende só de `WizardSession` e dos use cases (abstrações de alto nível), nunca de uma etapa concreta diretamente.
