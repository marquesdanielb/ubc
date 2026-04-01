# Desafio Técnico: UBC - Engenharia de Dados (Solr & Airflow)

Este repositório contém a solução para o desafio técnico de Engenharia de Dados, focado na orquestração de um pipeline de ETL utilizando **Apache Airflow**, processamento de dados com **Pandas** e indexação no **Apache Solr**, tudo rodando em um ambiente **Docker** totalmente isolado e automatizado.

## 🚀 Tecnologias Utilizadas

* **Orquestração:** Apache Airflow 2.5.1 (CeleryExecutor)
* **Processamento de Dados:** Python 3 + Pandas
* **Motor de Busca / Indexação:** Apache Solr 8
* **Infraestrutura:** Docker & Docker Compose (com redes isoladas)
* **Automação de Setup:** Makefile

## 🏗️ Arquitetura e Decisões Técnicas

Para garantir um ambiente de nível de produção e facilitar a avaliação, as seguintes decisões arquiteturais foram tomadas:

1. **Isolamento de Serviços (Airflow):** Em vez de rodar todos os componentes do Airflow em um único container, a arquitetura foi desmembrada em `webserver`, `scheduler` e `worker`. Isso garante maior estabilidade, escalabilidade e facilita o isolamento de logs.
2. **Rede Dedicada Docker:** Foi criada a rede `ubc_network` (`bridge`) para evitar conflitos de IP e portas com ambientes locais preexistentes do avaliador.
3. **Segurança e Credenciais:** Senhas e chaves de conexão foram totalmente removidas do `docker-compose.yaml`. Foi implementado um sistema baseado em `.env` (com template `.env.example` fornecido) para injeção segura de credenciais.
4. **Automação com Makefile:** O setup inicial (incluindo tratamento de UIDs e permissões de pastas no Linux) foi abstraído no comando `make install`, garantindo uma "Developer Experience" (DX) sem atritos.
5. **Criação Automática do Core (Solr):** O core `alunos` é inicializado automaticamente no boot do container via comando `solr-precreate`, garantindo idempotência.
6. **Pipeline (DAG):**
    * **Task 1 (Limpeza):** Utiliza `pandas` para padronizar nomes, tratar nulos (ex: preenchimento condicional de strings vazias e conversão segura de idades para inteiros) e converter o CSV em dicionários Python.
    * **Task 2 (Carga):** Os dados são passados em memória via `XCom` para a task de carga, que utiliza `pysolr` para realizar um *bulk insert* eficiente no Solr.
7. **Resiliência a Mudanças de Schema (Data Contracts):** Durante o desenvolvimento, notei uma divergência entre a documentação do desafio (que mencionava a coluna **turma**) e o dataset fornecido **(onde a coluna estava ausente)**. Para refletir cenários reais onde os esquemas de dados mudam sem aviso prévio, a lógica do Pandas foi construída de forma dinâmica. O pipeline verifica a existência das colunas antes de aplicar transformações, garantindo que o ETL não falhe abruptamente caso atributos sejam adicionados ou removidos.

## 🛠️ Como Configurar e Executar

### Pré-requisitos
* Docker e Docker Compose instalados.
* Make (opcional, mas recomendado).

### Passo a Passo

1. **Clone o repositório:**
  ```bash
    git clone https://github.com/marquesdanielb/ubc.git
    cd ubc
  ```
2. **Setup Automático (Recomendado):**
  Execute o comando abaixo. Ele criará as pastas necessárias, ajustará permissões (se estiver no Linux), criará o arquivo .env baseado no template e subirá os containers.
  ``` bash
    make install
  ```
  (Caso não use o Make, copie o .env.example para .env, preencha as variáveis e rode docker compose up -d --build).

3. **Acessando os Serviços:**
  - Airflow: http://localhost:8080 (Credenciais padrão definidas no .env: admin / admin)
  - Solr: http://localhost:8983/solr/#/~cores/alunos

4. **Executando o Pipeline:**
  - Acesse o painel do Airflow.
  - Ative a DAG ubc_solr_import_pipeline.
  - Clique em Trigger DAG (botão Play).
  - Acompanhe os logs nas tasks para verificar a limpeza e a indexação.