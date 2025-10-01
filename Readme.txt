1. Visão Geral do Projeto
O TruCar é uma plataforma completa de gerenciamento de frotas, projetada para fornecer rastreamento em tempo real, otimizar rotas, reduzir custos operacionais e aumentar a eficiência de motoristas e veículos. A plataforma é adequada para diversos setores, incluindo agronegócio, transporte de cargas, serviços e construção civil.

2. Funcionalidades
A plataforma TruCar oferece uma ampla gama de funcionalidades para auxiliar no gerenciamento eficaz da sua frota:

Dashboard Inteligente: Um painel centralizado para visualizar os principais indicadores de desempenho da sua frota.

Controle de Viagens: Monitore e gerencie todas as viagens da sua frota em tempo real.

Gestão de Manutenção: Agende e acompanhe a manutenção preventiva e corretiva dos seus veículos.

Controle de Combustível: Monitore o consumo de combustível e identifique oportunidades de economia.

Ranking de Motoristas: Classifique seus motoristas com base no desempenho e comportamento ao dirigir.

Relatórios Gerenciais: Gere relatórios detalhados para apoiar seu processo de tomada de decisão.

Alertas Automáticos: Receba alertas automáticos para eventos importantes, como excesso de velocidade ou entrada em área restrita.

API para Integração: Integre o TruCar com seus sistemas existentes usando nossa poderosa API.

3. Arquitetura
O projeto TruCar é composto por três componentes principais: uma aplicação frontend, um servidor backend e um simulador de veículo.

Frontend: Uma aplicação web que fornece a interface do usuário para a plataforma, construída com Quasar/Vue.js.

Backend: Uma aplicação em Python construída com o framework FastAPI, que expõe uma API REST para ser consumida pelo frontend e pelo simulador. É responsável pelo processamento e armazenamento de dados de telemetria, bem como por toda a lógica de negócios da plataforma.

Simulador: Um script em Python que simula um veículo real enviando dados de telemetria para a API do backend, útil para fins de teste e desenvolvimento.

4. Como Começar
Esta seção fornece instruções sobre como configurar e executar o projeto TruCar em sua máquina local.

4.1. Pré-requisitos
Python 3.7+

pip

Node.js e npm

4.2. Configuração do Backend
Navegue até o diretório backend:

Bash

cd backend
Instale os pacotes Python necessários:

Bash

pip install fastapi uvicorn sqlalchemy alembic pydantic python-jose passlib bcrypt
Execute as migrações do banco de dados:

Bash

alembic upgrade head
Inicie o servidor backend:

Bash

python -m uvicorn main:app --reload
O backend estará rodando em http://127.0.0.1:8000.

4.3. Configuração do Frontend
Navegue até o diretório FrontEnd:

Bash

cd FrontEnd
Instale as dependências:

Bash

npm install
Inicie o servidor de desenvolvimento:

Bash

quasar dev
4.4. Simulador
Abra um novo terminal e navegue até a raiz do projeto.

Execute o script do simulador:

Bash

python simulator.py
O simulador começará a enviar dados de telemetria para o backend.

5. Documentação da API
O backend do TruCar expõe uma API REST para gerenciamento da plataforma. A URL base da API é http://127.0.0.1:8000/api/v1.

5.1. Telemetria
Este endpoint é usado para reportar dados de telemetria de um veículo.

URL: /telemetry/report

Método: POST

Corpo da Requisição:

O corpo da requisição deve ser um objeto JSON com a seguinte estrutura:

JSON

{
  "device_id": "string",
  "timestamp": "string (formato ISO 8601)",
  "latitude": "float",
  "longitude": "float",
  "engine_hours": "float"
}
Resposta:

204 No Content: Os dados de telemetria foram recebidos e processados com sucesso.

422 Unprocessable Entity: O corpo da requisição é inválido.
