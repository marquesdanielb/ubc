# Desafio Técnico: Importação de Dados para o Solr com Orquestração usando Airflow e Configuração via Docker

## Descrição

Seu objetivo é criar um **pipeline de dados** orquestrado pelo **Apache Airflow** que realiza as seguintes tarefas:

### 1. Formatar o CSV

- O pipeline deve ler um arquivo CSV fornecido e realizar a **formatação dos dados** para garantir consistência e correção.
- Considere que o arquivo CSV pode conter **campos mal formatados**, **dados ausentes** ou outros problemas típicos em conjuntos de dados do mundo real.

### 2. Inserir no Solr

- Após a formatação, o pipeline deve **inserir os dados** no **Apache Solr**.
- Certifique-se de **mapear corretamente** os campos do CSV para os campos correspondentes no esquema do Solr.

## Requisitos Técnicos

- Use a biblioteca **pandas** para manipulação de dados CSV em Python.
- Utilize a biblioteca **pysolr** para interagir com o Solr a partir do script Python.
- O pipeline deve ser orquestrado usando o **Apache Airflow**.
- **Docker** deve ser utilizado para configurar e executar tanto o Solr quanto o Airflow.
- Hospede seu projeto no **GitHub**, fornecendo instruções claras sobre como configurar e executar o pipeline.

## Configuração do Solr usando Docker

Execute o seguinte comando para criar uma instância do Solr no Docker:

```bash
docker run -d -p 8983:8983 --name solr_instance -t solr
```

- Isso iniciará um container Docker com o Solr rodando na porta `8983`.
- Acesse a interface administrativa do Solr em [http://localhost:8983/solr](http://localhost:8983/solr).

## Configuração do Airflow usando Docker

Para configurar o Airflow usando Docker, siga os passos abaixo:

### 1. Criar um diretório para o projeto Airflow

Crie um diretório chamado `airflow` para armazenar todos os arquivos relacionados ao Airflow:

```bash
mkdir airflow
cd airflow
```

### 2. Criar o arquivo `docker-compose.yml`

Crie um arquivo chamado `docker-compose.yml` com o seguinte conteúdo:

```yaml
version: '3'
services:
  postgres:
    image: postgres:13
    environment:
      - POSTGRES_USER=airflow
      - POSTGRES_PASSWORD=airflow
      - POSTGRES_DB=airflow
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:latest

  airflow:
    image: apache/airflow:2.5.1
    depends_on:
      - postgres
      - redis
    environment:
      - AIRFLOW__CORE__EXECUTOR=CeleryExecutor
      - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
      - AIRFLOW__CELERY__BROKER_URL=redis://redis:6379/0
      - AIRFLOW__CELERY__RESULT_BACKEND=db+postgresql://airflow:airflow@postgres/airflow
      - AIRFLOW__CORE__FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
      - AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=False
      - AIRFLOW__CORE__LOAD_EXAMPLES=False
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    ports:
      - "8080:8080"
    command: >
      bash -c "
      airflow db init &&
      airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com &&
      airflow scheduler &
      airflow webserver
      "

volumes:
  postgres_data:
```

### 3. Criar os diretórios necessários

Crie os diretórios `dags`, `logs` e `plugins`:

```bash
mkdir dags logs plugins
```

### 4. Iniciar o Airflow

Execute o seguinte comando para iniciar o Airflow:

```bash
docker-compose up -d
```

- Isso iniciará todos os serviços necessários para o Airflow, incluindo PostgreSQL e Redis.
- A interface web do Airflow estará disponível em [http://localhost:8080](http://localhost:8080).

### 5. Verificar se o Airflow está em execução

Acesse a interface web do Airflow em [http://localhost:8080](http://localhost:8080) e faça login com as credenciais:

- **Username**: `admin`
- **Password**: `admin`

### 6. Colocar suas DAGs no diretório apropriado

- As DAGs devem ser colocadas no diretório `dags`, que está mapeado para o container do Airflow.
- Certifique-se de que o seu script Python contendo a DAG esteja nesse diretório para que o Airflow possa detectá-lo.

## Arquivo CSV de Exemplo (Alunos de uma Escola Primária)

- Utilize o arquivo [alunos.csv](https://github.com/Uniao-brasileira-dos-Compositores/desafio-engenheiro-dados_airflow/blob/main/aluno.csv) com os dados fictícios representando alunos de uma escola primária. 

- O arquivo deve conter campos como:

  - Nome
  - Idade
  - Turma
  - Notas
  - Endereço
  - Outros campos relevantes

## Pontos Extras

- **Tratamento de Erros**: Lidar com situações de erro durante a formatação e inserção no Solr.
- **Logs**: Implementar logs adequados para rastrear o progresso e eventuais problemas.
- **Performance**: Garantir que o pipeline seja eficiente, mesmo para grandes conjuntos de dados.
- **Boas Práticas**: Seguir boas práticas de programação e estruturação de código.

## Instruções

1. **Baixe o arquivo CSV de exemplo** contendo dados fictícios de alunos de uma escola primária.

2. **Desenvolva o pipeline** usando Python, Airflow e Docker:

   - Crie os scripts necessários para cada tarefa.
   - Configure a DAG no Airflow e coloque-a no diretório `dags`.
   - Utilize o Docker para executar o Solr e o Airflow.

3. **Documentação**:

   - Documente claramente como o pipeline deve ser executado, incluindo dependências e configurações.
   - Inclua instruções sobre como configurar o Solr e o Airflow usando Docker.
   - Forneça exemplos de como executar os comandos necessários.

4. **Hospedagem no GitHub**:

   - Crie um repositório público no GitHub.
   - Certifique-se de não incluir informações sensíveis (credenciais, senhas, chaves de acesso).
   - Forneça o link do repositório.

## Avaliação

Você será avaliado com base nos seguintes critérios:

- **Funcionalidade**: O pipeline atende a todos os requisitos especificados.
- **Qualidade do Código**: Código bem estruturado, legível e seguindo boas práticas de programação.
- **Eficiência**: Solução otimizada para performance e escalabilidade.
- **Uso do Airflow e Docker**: Implementação eficaz dos recursos do Airflow para orquestração do pipeline e utilização correta do Docker para configuração do ambiente.
- **Tratamento de Erros**: Capacidade de lidar com situações não ideais nos dados e erros durante a execução.
- **Documentação**: Instruções claras e detalhadas que facilitam a compreensão e a execução do projeto.
- **Uso do GitHub**: Organização do repositório e clareza nas instruções.

---

Boa sorte no desafio! Estamos ansiosos para ver sua solução inovadora e eficiente.
