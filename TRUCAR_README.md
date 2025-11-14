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

O projeto TruCar é composto por três componentes principais: uma aplicação frontend, um servidor backend e um simulador de veículo.

```
+-----------------+      +------------------+      +-----------------+
|                 |      |                  |      |                 |
|     Frontend    |----->|      Backend     |<-----|    Simulator    |
| (Quasar/Vue.js) |      |    (FastAPI)     |      |    (Python)     |
|                 |      |                  |      |                 |
+-----------------+      +------------------+      +-----------------+
```

- **Frontend:** Uma aplicação web que fornece a interface do usuário para a plataforma, construída com Quasar/Vue.js.
- **Backend:** Uma aplicação em Python construída com o framework FastAPI, que expõe uma API REST para ser consumida pelo frontend e pelo simulador. É responsável pelo processamento e armazenamento de dados de telemetria, bem como por toda a lógica de negócios da plataforma.
- **Simulador:** Um script em Python que simula um veículo real enviando dados de telemetria para a API do backend, útil para fins de teste e desenvolvimento.

## Como Começar

Esta seção fornece instruções sobre como configurar e executar o projeto TruCar em sua máquina local.

### Pré-requisitos

- Python 3.7+
- pip
- Node.js e npm

### Configuração do Backend

1. Navegue até o diretório `backend`:
   ```bash
   cd backend
   ```
2. Instale os pacotes Python necessários:
   ```bash
   pip install fastapi uvicorn sqlalchemy alembic pydantic python-jose passlib bcrypt
   ```
3. Execute as migrações do banco de dados:
   ```bash
   alembic upgrade head
   ```
4. Inicie o servidor backend:
   ```bash
   python -m uvicorn main:app --reload
   ```
   O backend estará rodando em `http://127.0.0.1:8000`.

### Configuração do Frontend

1. Navegue até o diretório `FrontEnd`:
   ```bash
   cd FrontEnd
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

### Telemetria

Este endpoint é usado para reportar dados de telemetria de um veículo.

- **URL:** `/telemetry/report`
- **Método:** `POST`
- **Corpo da Requisição:**

  O corpo da requisição deve ser um objeto JSON com a seguinte estrutura:

  ```json
  {
    "device_id": "string",
    "timestamp": "string (formato ISO 8601)",
    "latitude": "float",
    "longitude": "float",
    "engine_hours": "float"
  }
  ```

- **Resposta:**
  - **204 No Content:** Os dados de telemetria foram recebidos e processados com sucesso.
  - **422 Unprocessable Entity:** O corpo da requisição é inválido.

## Tecnologias Utilizadas

### Backend

- **Python 3.7+**
- **FastAPI:** Framework web para construção de APIs.
- **SQLAlchemy:** ORM para interação com o banco de dados.
- **Alembic:** Ferramenta para migrações de banco de dados.
- **Pydantic:** Para validação de dados.
- **Uvicorn:** Servidor ASGI.

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
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   └── schemas/
│   ├── static/
│   └── tests/
├── FrontEnd/
│   ├── public/
│   └── src/
│       ├── assets/
│       ├── components/
│       ├── layouts/
│       ├── pages/
│       ├── router/
│       └── stores/
├── docs/
└── simulator.py
```

## Contribuição

Contribuições são bem-vindas! Se você tiver sugestões, correções de bugs ou novas funcionalidades, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto está licenciado sob a Licença MIT.
