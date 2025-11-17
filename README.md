
# TruCar - Plataforma de Gerenciamento de Frotas

## Visão Geral do Projeto

O TruCar é uma plataforma completa de gerenciamento de frotas, projetada para fornecer rastreamento em tempo real, otimizar rotas, reduzir custos operacionais e aumentar a eficiência de motoristas e veículos. A plataforma é ideal para diversos setores, como agronegócio, transporte de cargas, serviços e construção civil, oferecendo uma solução robusta e escalável para o monitoramento e gestão de ativos móveis.

## Funcionalidades

A plataforma TruCar oferece uma ampla gama de funcionalidades para auxiliar no gerenciamento eficaz da sua frota:

- **Dashboard Inteligente:** Um painel centralizado para visualizar os principais indicadores de desempenho da sua frota.
- **Controle de Viagens:** Monitore e gerencie todas as viagens da sua frota em tempo real.
- **Gestão de Manutenção:** Agende e acompanhe a manutenção preventiva e corretiva dos seus veículos.
- **Controle de Combustível:** Monitore o consumo de combustível e identifique oportunidades de economia.
- **Ranking de Motoristas:** Classifique seus motoristas com base no desempenho e comportamento ao dirigir.
- **Relatórios Gerenciais:** Gere relatórios detalhados para apoiar seu processo de tomada de decisão.
- **Alertas Automáticos:** Receba alertas automáticos para eventos importantes, como excesso de velocidade ou entrada em área restrita.
- **API para Integração:** Integre o TruCar com seus sistemas existentes usando nossa poderosa API.

## Arquitetura

O projeto TruCar possui uma arquitetura flexível, consistindo em um frontend moderno e duas opções de backend para diferentes necessidades de performance e desenvolvimento.

```


                               +-----------------+
                               |                 |
                               |     Frontend    |
                               | (Quasar/Vue.js) |
                               |                 |
                               +-------+---------+
                                       |
                  +--------------------+--------------------+
                  |                                         |
        +---------v---------+                       +---------v---------+
        |                   |                       |                   |
        |      Backend      |                       |      Backend      |
        |   (Python/FastAPI)|                       |      (Go/Gin)     |
        |                   |                       |                   |
        +-------------------+                       +-------------------+

```
<img width="11480" height="2268" alt="Untitled diagram-2025-11-12-165423" src="https://github.com/user-attachments/assets/e4ea8217-9d77-421f-8262-77a1b10ea0c6" />



- **Frontend:** Uma aplicação web que fornece a interface do usuário para a plataforma, construída com Quasar/Vue.js, garantindo uma experiência de usuário rica e reativa.
- **Backend (Python/FastAPI):** Uma API robusta construída com FastAPI, ideal para desenvolvimento rápido, flexibilidade e um ecossistema Python maduro. É responsável por toda a lógica de negócios e processamento de dados.
- **Backend (Go/Gin):** Uma alternativa de alta performance ao backend Python, construída com Gin. Esta versão oferece maior velocidade e eficiência, sendo ideal para implantações em larga escala e cenários de alta concorrência.

## Como Começar

Esta seção fornece instruções sobre como configurar e executar o projeto TruCar em sua máquina local.

### Pré-requisitos

- Python 3.7+
- pip
- Node.js e npm

### Configuração do Backend (Python)

1. Navegue até o diretório `PyFastAPI/backend`:
   ```bash
   cd PyFastAPI/backend
   ```
   
2. Crie o ambiente virtual:

   ```bash
   python -m venv venv
   .\venv\scripts\activate
   ```

3. Instale os pacotes Python necessários:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute as migrações do banco de dados:
   
   Instale PostgreSQL 17 e crie um banco de dados com o nome Trucar.
   
   ```bash
   alembic revision --autogenerate
   alembic upgrade head
   ```

   Ou

   ```Bash
   python -m app.db.initial_data
   ```

6. Rode o servidor

  ```bash
  uvicorn main:app --reload
  ```

### Configuração do Backend (Go)

1. Navegue até o diretório `Go`:
   ```bash
   cd Go
   ```
2. Baixe as dependências do projeto:
   ```bash
   go mod tidy
   ```
3. Inicie o servidor backend:
   ```bash
   go run cmd/main.go
   ```
   O backend estará rodando em `http://127.0.0.1:8080`.

### Configuração do Frontend

1. Navegue até o diretório `PyFastAPI/FrontEnd`:
   ```bash
   cd PyFastAPI/FrontEnd
   ```
2. Instale as dependências:
   ```bash
   npm install
   ```
3. Inicie o servidor de desenvolvimento:
   ```bash
   quasar dev
   ```

## Documentação da API

O backend do TruCar expõe uma API REST para gerenciamento da plataforma. A URL base da API é `http://127.0.0.1:8000/api/v1`.

## Tecnologias Utilizadas

### Backend (Python)

- **Python 3.7+**
- **FastAPI:** Framework web para construção de APIs.
- **SQLAlchemy:** ORM para interação com o banco de dados.
- **Alembic:** Ferramenta para migrações de banco de dados.
- **Pydantic:** Para validação de dados.
- **Uvicorn:** Servidor ASGI.

### Backend (Go)

- **Go:** Linguagem de programação de alta performance.
- **Gin:** Framework web para construção de APIs.
- **GORM:** ORM para interação com o banco de dados.
- **PostgreSQL Driver:** Para comunicação com o banco de dados PostgreSQL.

### Frontend

- **Quasar Framework:** Framework Vue.js para construção de interfaces de usuário.
- **Vue.js 3:** Framework JavaScript progressivo.
- **Pinia:** Gerenciador de estado para Vue.js.
- **Axios:** Cliente HTTP para requisições à API.
- **Leaflet:** Biblioteca de mapas interativos.
- **ApexCharts & ECharts:** Bibliotecas para visualização de dados.

## Estrutura do Projeto

```
.
├── Go/
│   ├── cmd/
│   └── internal/
├── PyFastAPI/
│   ├── backend/
│   │   ├── app/
│   │   └── ...
│   ├── FrontEnd/
│   │   ├── src/
│   │   └── ...
│   └── docs/
└── ...
```

## Contribuição

Contribuições são bem-vindas! Se você tiver sugestões, correções de bugs ou novas funcionalidades, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## 📜 Licença (EULA)

Este projeto é licenciado sob os termos do Acordo de Licença de Usuário Final (EULA).
**[Clique aqui para ler a licença completa (EULA.txt)](./EULA.txt)**
