# Serializer Factory

> **Design Pattern:** Factory Method | **Categoria:** Creational
> **Framework:** Streamlit | **Serviços:** Nenhum (aplicação autocontida)

## Objetivo Pedagógico

Demonstrar o **Factory Method** em um cenário realista: uma aplicação que
precisa exportar/importar dados em múltiplos formatos (JSON, XML, CSV, YAML)
sem que o código de negócio conheça as classes concretas de cada formato. O
aluno deve identificar claramente: **Creator** (`SerializerFactory`),
**ConcreteCreators** (`JSONSerializerFactory`, `XMLSerializerFactory`,
`CSVSerializerFactory`, `YAMLSerializerFactory`), **Product**
(`DataSerializer`, um `Protocol`) e **ConcreteProducts**
(`JSONSerializer`, `XMLSerializer`, `CSVSerializer`, `YAMLSerializer`).

## O Pattern Aplicado

A interface Streamlit deixa o usuário colar/enviar dados e escolher um
formato de saída em um `selectbox`. Internamente, o app nunca instancia
`JSONSerializer` ou `XMLSerializer` diretamente: ele pega a
`SerializerFactory` correspondente em um registro (`SERIALIZER_FACTORY_REGISTRY`)
e chama `factory.create_serializer()` — o **factory method**. Cada
`ConcreteCreator` sabe construir exatamente o `ConcreteProduct` certo; o
restante do sistema (`SerializeDataUseCase`, `DeserializeDataUseCase`) só
depende da abstração `SerializerFactory`/`DataSerializer`. Adicionar um novo
formato (ex.: MessagePack) significa criar um novo par
Creator/Product em `infrastructure/serializers.py` e registrá-lo — nenhuma
linha em `domain/` ou `application/` muda.

## Diagrama UML (ASCII)

```
                 <<Protocol>>
                 DataSerializer
            +---------------------+
            | serialize(data)     |
            | deserialize(raw)    |
            | get_mime_type()     |
            | get_extension()     |
            +---------------------+
                      ^
        +-------------+-------------+-------------+
        |             |             |              |
  JSONSerializer XMLSerializer CSVSerializer  YAMLSerializer
        |             |             |              |
        | creates      | creates     | creates       | creates
        |             |             |              |
  +-----------------------------------------------------------+
  |                  <<abstract>> SerializerFactory            |
  |  + create_serializer(): DataSerializer   (factory method) |
  |  + get_format_name(): str                                 |
  |  + round_trip(data): list[dict]          (template method)|
  +-----------------------------------------------------------+
        ^             ^             ^              ^
        |             |             |              |
JSONSerializerFactory  XMLSerializerFactory  CSVSerializerFactory  YAMLSerializerFactory
  (ConcreteCreator)    (ConcreteCreator)     (ConcreteCreator)     (ConcreteCreator)
```

## Princípios SOLID Demonstrados

- **O (Open/Closed):** `SerializerFactory` é uma ABC fechada para
  modificação. Suportar um novo formato exige apenas uma nova subclasse em
  `infrastructure/serializers.py` registrada em
  `SERIALIZER_FACTORY_REGISTRY` — nenhuma classe existente é alterada.
- **D (Dependency Inversion):** `SerializeDataUseCase` e
  `DeserializeDataUseCase` (em `application/use_cases.py`) recebem uma
  `SerializerFactory` via construtor e nunca importam
  `JSONSerializer`/`XMLSerializer`/etc. diretamente. A escolha concreta só
  acontece no *composition root* (`main.py`, via `SERIALIZER_FACTORY_REGISTRY`).
- **I (Interface Segregation):** `DataSerializer` é um `Protocol` com apenas
  4 métodos focados (`serialize`, `deserialize`, `get_mime_type`,
  `get_extension`) — clientes que só serializam não são forçados a depender
  de nada além do que usam.
- **S (Single Responsibility):** cada `ConcreteProduct` só sabe converter
  registros de/para seu formato; os casos de uso só orquestram a chamada; a
  UI Streamlit só lida com apresentação/entrada do usuário.

## Como Rodar

```bash
cp .env.example .env
docker-compose up --build
```

Acesse a interface Streamlit em **http://localhost:8501**.

## Rodar os Testes

```bash
docker-compose run --rm app pytest
```

## Rodar Localmente (sem Docker)

```bash
pip install -e ".[dev]"
streamlit run src/serializer/main.py
```
