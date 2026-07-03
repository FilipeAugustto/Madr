# 📜 MADR

> API RESTful responsável por gerir um acervo digital com cadastro de usuários, livros e autores.
> Desenvolvida com **Python 3.13 + FastAPI** e banco de dados **PostgreSQL**.

---

## 📝 Índice

- [🚀 Visão Geral](#-visão-geral)
- [🔧 Stack de Tecnologias](#-stack-de-tecnologias)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [🌐 Rotas da API](#-rotas-da-api)
  - [👤 Usuários (/users)](#-usuários-users)
  - [🔐 Autenticação (/auth)](#-autenticação-auth)
  - [📚 Livros (/books)](#-livros-books)
  - [✍️ Autores (/authors)](#️-autores-authors)
- [🖥️ Como Rodar a Aplicação](#️-como-rodar-a-aplicação)
  - [Pré-requisitos](#pré-requisitos)
  - [Subir todos os containers com Docker Compose](#subir-todos-os-containers-com-docker-compose)
  - [Verificar se subiu corretamente](#verificar-se-subiu-corretamente)
  - [Derruba os containers](#derruba-os-containers)
- [🔧 Variáveis de Ambiente](#-variáveis-de-ambiente)
- [👨‍💻 Documentação com Swagger](#-documentação-com-swagger)
- [🧪 Testes com Pytest](#-testes-com-pytest)
  - [Pré-requisitos (Testes)](#pré-requisitos-testes)
  - [Instala as dependências](#instala-as-dependências)
  - [Roda os testes automatizados](#roda-os-testes-automatizados)
  - [Visualiza o coverage do projeto](#visualiza-o-coverage-do-projeto)

---

## 🚀 Visão Geral

O **MADR** é uma API RESTful desenvolvida para criar e gerenciar um acervo digital de livros, responsável por:

- **Realizar o gerenciamento CRUD** de usuários (criação, leitura, atualização e exclusão)
- **Autenticar e autorizar** usuários de forma segura com a utilização de tokens JWT
- **Realizar o cadastro** de autores e livros, tendo relação direta dos autores com suas obras
- **Gerenciar o acervo digital dos usuários**, permitindo consultas detalhadas ao catálogo

---

## 🔧 Stack de Tecnologias

### 🐍 Python 3.13 + ⚡FastAPI

Linguagem e framework principal do projeto.

A escolha de uma versão recente do Python garante melhor performance, segurança e recursos modernos.
O FastAPI é um framework moderno utilizado na criação de APIs fornecendo todo o leque de ferramentas para a construção eficiente.

### 📋 Pydantic

Biblioteca utilizada para validação de dados por meio de schemas, garantindo maior robustez da aplicação.

### 🔒 PyJWT + pwdlib

Conjunto de bibliotecas para autenticação e autorização por meio de tokens JWT, além do hashing de senhas para garantir a segurança dos dados no banco.

### 🔬 Pytest + Testcontainers

Conjunto de ferramentas utilizadas para garantir a qualidade e resiliência do código através de testes automatizados.

- O **Pytest** atua como o framework principal para a escrita e execução de testes de unidade e integração, operando em conjunto com o **pytest-cov** para gerar relatórios da cobertura do código

- O **Testcontainers** é utilizado para subir instâncias temporárias do PostgreSQL em containers Docker durante os testes, garantindo que o ambiente de integração seja perfeitamente isolado e fiel à produção.

- O **Factory Boy** é utilizado para a geração dinâmica e organizada de dados falsos por meio de fixtures para popular o banco nos testes.

- O **Freezegun** foi empregado para "congelar" o tempo no ambiente de testes, garantindo precisão absoluta ao testar regras de negócio temporais (como a expiração de tokens JWT).

### 🐘 PostgreSQL

O PostgreSQL foi o banco de dados relacional escolhido devido à sua alta performance e confiabilidade.

- **Segurança**: As credenciais de acesso ficam protegidas através de variáveis de ambiente.

- **Persistência**: O Docker Compose está configurado com volumes para garantir que os dados cadastrados não sejam perdidos caso o container do banco seja reiniciado.

### 🗃️ SQLAlchemy + psycopg

ORM utilizado para gerenciar e criar as conexões com o banco de dados e realizar consultas utilizando código Python, mapeando tabelas para objetos da linguagem. O driver psycopg foi escolhido para realizar a comunicação eficiente e direta entre o código Python e o PostgreSQL.

### ⚗️ Alembic

O Alembic é uma ferramenta de gerenciamento de migrações ao banco de dados, ele oferece:

- Scripts de migração ficam em `migrations/versions`.
- Gerencia alterações das estruturas de dados presentes no banco.
- Fornece um sistema de criação de scripts de migração para o banco de dados que podem ser gerenciados com:
  - **Upgrade**: atualiza o banco para a nova versão
  - **Downgrade**: reverte a migração executada no banco

### 🐳 Docker + Docker Compose

Toda a aplicação foi containerizada utilizando Docker e Docker Compose para garantir que o projeto funcione perfeitamente em qualquer sistema operacional (Windows, Mac ou Linux).
O projeto conta com dois serviços principais orquestrados juntos:

- **fastmadr-app**: O container da API (FastAPI)
- **fastmadr-postgres**: O container do Banco de Dados (PostgreSQL)

Isso significa que você não precisa instalar o Python ou o PostgreSQL diretamente na sua máquina para rodar o projeto.

### 📦 Poetry

Ferramenta moderna de gerenciamento de dependências e empacotamento em Python.

Ele substitui o tradicional `requirements.txt`, oferecendo um controle rigoroso das versões das bibliotecas através do arquivo `pyproject.toml` e do `poetry.lock`.

---

### 📁 Estrutura do Projeto

``` tree
├─── fast_madr/
│   ├─── routers/
│   │   ├─── auth.py               # Rotas de autenticação
│   │   ├─── authors.py            # Rotas de gerenciamento de autores
│   │   ├─── books.py              # Rotas de gerenciamento de livros
│   │   ├─── monitoring.py         # Rotas de monitoramento de saúde da API
│   │   └─── users.py              # Rotas de gerenciamento de usuários
│   ├─── app.py                    # Entrypoint de inicialização FastAPI
│   ├─── database.py               # Configuração e criação da session do banco
│   ├─── models.py                 # Modelos de dados (Tabelas do SQLAlchemy)
│   ├─── schemas.py                # Schemas de validação de dados do Pydantic
│   ├─── security.py               # Lógica de segurança (hashing e tokens JWT)
│   ├─── settings.py               # Gerenciamento de variáveis de ambiente
│   └─── utils.py                  # Funções auxiliares para validação
├─── migrations/                   # Scripts de migração do banco (Alembic)   
├─── tests/                        # Coleção dos testes automatizados da aplicação
├── docker-compose.yml             # Orquestração da infraestrutura (App + DB)
├── Dockerfile                     # Construção da imagem da API
├── entrypoint.sh                  # Script para execução das migrações e boot do app
├── poetry.lock                    # Configurações do Poetry e dependências
├── pyproject.toml                 # Travamento das versões das bibliotecas
└── README.md                      # Documentação principal do projeto 
```

---

## 🌐 Rotas da API

**Base URL**: `http://localhost:8000`

### 👤 Usuários (/users)

| Método   |  Rota                       |  Descrição                             |
| -------- | --------------------------- | -------------------------------------- |
| `POST`   | `/users`                    | Cadastra um novo usuário               |
| `PUT`    | `/users/{id}`               | Atualiza os dados de um usuário        |
| `DELETE` | `/users/{id}`               | Deleta um usuário                      |
| `GET`    | `/users/me`                 | Busca as informações do usuário logado |
| `POST`   | `/users/me/books/{book_id}` | Adiciona um livro no acervo do usuário |
| `DELETE` | `/users/me/books/{book_id}` | Remove um livro no acervo do usuário   |
| `GET`    | `/users/me/books`           | Busca os livros do acervo do usuário   |

**Parâmetros de filtro e paginação** `GET /users/me/books`

| Parâmetro    | Padrão  | Descrição                       |
| ------------ | ------- | ------------------------------- |
| `offset`     | `0`     | Número da página                |
| `limit`      | `20`    | Quantidade de livros por página |
| `year`       | `None`  | Ano de publicação               |
| `min_year`   | `None`  | Ano mínimo de publicação        |
| `max_year`   | `None`  | Ano máximo de publicação        |
| `title`      | `None`  | Título da obra                  |

### 🔐 Autenticação (/auth)

| Método   |  Rota                 |  Descrição                                                  |
| -------- | --------------------- | ----------------------------------------------------------- |
| `POST`   | `/auth/token`         | Recebe credenciais do usuário e gera um token JWT de acesso |
| `POST`   | `/auth/refresh-token` | Cria um novo token JWT de acesso                            |

### 📚 Livros (/books)

| Método   |  Rota         |  Descrição                                       |
| -------- | ------------- | ------------------------------------------------ |
| `POST`   | `/books`      | Cadastra um novo livro                           |
| `PATCH`  | `/books/{id}` | Atualiza os dados de um livro                    |
| `DELETE` | `/books/{id}` | Deleta um livro (Autorizado somente para admins) |
| `GET`    | `/books`      | Busca os livros do acervo da aplicação           |

**Parâmetros de filtro e paginação** `GET /books`

| Parâmetro    | Padrão  | Descrição                       |
| ------------ | ------- | ------------------------------- |
| `offset`     | `0`     | Número da página                |
| `limit`      | `20`    | Quantidade de livros por página |
| `year`       | `None`  | Ano de publicação               |
| `min_year`   | `None`  | Ano mínimo de publicação        |
| `max_year`   | `None`  | Ano máximo de publicação        |
| `title`      | `None`  | Título da obra                  |

### ✍️ Autores (/authors)

| Método   |  Rota           |  Descrição                                       |
| -------- | --------------- | ------------------------------------------------ |
| `POST`   | `/authors`      | Cadastra um novo autor                           |
| `PATCH`  | `/authors/{id}` | Atualiza os dados de um autor                    |
| `DELETE` | `/authors/{id}` | Deleta um autor (Autorizado somente para admins) |
| `GET`    | `/authors`      | Busca os autores do acervo da aplicação          |
| `GET`    | `/authors/{id}` | Busca um autor por id                            |

**Parâmetros de filtro e paginação** `GET /authors`

| Parâmetro    | Padrão   | Descrição                        |
| ------------ | -------- | -------------------------------- |
| `offset`     | `0`      | Número da página                 |
| `limit`      | `20`     | Quantidade de autores por página |
| `name`       | `None`   | Nome do autor                    |
| `birth_year` | `None`   | Ano de nascimento do autor       |

---

## 🖥️ Como Rodar a Aplicação

### Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e rodando

Para rodar o projeto siga as seguintes etapas:

### Subir todos os containers com Docker Compose

```bash
# Constrói e sobe todos os containers
docker compose up -d --build
```

### Verificar se subiu corretamente

```bash
# Mostra os status dos containers criados
docker compose ps
```

### Derruba os containers

```bash
# Derruba os containers
docker compose down

# Derruba e apaga os dados
docker compose down -v
```

---

## 🔧 Variáveis de Ambiente

| Variável                      | Descrição                         |
| ----------------------------- | --------------------------------- |
| `DATABASE_URL`                | URL de conexão do PostgreSQL      |
| `SECRET_KEY`                  | Senha de criptografia do JWT      |
| `ALGORITHM`                   | Algoritmo de criptografia do JWT  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tempo para expiração do token JWT |
| `POSTGRES_USER`               | Usuário do banco                  |
| `POSTGRES_DB`                 | Nome do banco                     |
| `POSTGRES_PASSWORD`           | Senha do banco                    |

---

## 👨‍💻 Documentação com Swagger

Com a aplicação rodando corretamente, basta acessar:

**`http://localhost:8000/docs`**

Com isso você irá conseguir interagir e testar os endpoints manualmente, com exemplos de request e response documentados

---

## 🧪 Testes com Pytest

### Pré-requisitos (Testes)

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e rodando
- [Poetry](https://python-poetry.org/docs/#installation) instalado corretamente (qualquer versão recente)
- [Python](https://www.python.org/downloads/release/python-31314/) instalado (>= 3.13)

O Pystest é um ótimo pacote de testes para a linguagem Python oferencendo uma ampla gama de recursos, como um coverage da aplicação
Para rodar os testes serão necessárias as seguintes etapas:

### Instala as dependências

Primeiro vamos baixar todas dependências do projeto com poetry

``` bash
poetry install
```

### Roda os testes automatizados

Com isso todas as dependências necessárias foram instaladas e agora podemos rodar os testes

``` bash
# Roda todos os testes e cria o coverage
poetry run task test
```

### Visualiza o coverage do projeto

Para visualizar o coverage do projeto basta rodar o seguinte comando:

``` bash
# Windows
start htmlcov/index.html

# Mac
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

---

## 👨‍💻 Autor

Criado e mantido por **[Filipe Augustto]**.

Se você gostou desse projeto ou tem alguma dúvida, sinta-se à vontade para entrar em contato!

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/filipe-augustto-361850327/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/FilipeAugustto)
[![E-mail](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:filipeaugustto22@gmail.com)
