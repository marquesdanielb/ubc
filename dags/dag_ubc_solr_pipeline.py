import logging
import pandas as pd
import pysolr
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from scripts.cleaner import clean_student_data

# ==========================================
# CONFIGURAÇÕES E CONSTANTES
# ==========================================
CSV_PATH = '/opt/airflow/data/data/aluno.csv'
SOLR_URL = 'http://solr:8983/solr/alunos'

# ==========================================
# FUNÇÕES DE PROCESSAMENTO (ETL)
# ==========================================
def extract_and_clean_data(**kwargs):
    """
    Orquestra a leitura do arquivo e chama a função de limpeza externa.
    """
    logging.info(f"Iniciando a leitura do arquivo: {CSV_PATH}")
    
    try:
        df = pd.read_csv(CSV_PATH)
        logging.info(f"Arquivo lido com sucesso. Total de linhas: {len(df)}")
        
        registros = clean_student_data(df)
        
        logging.info(f"Limpeza concluída via scripts.cleaner. {len(registros)} registros prontos.")
        return registros
        
    except FileNotFoundError:
        logging.error(f"ERRO: Arquivo não encontrado no caminho {CSV_PATH}.")
        raise
    except Exception as e:
        logging.error(f"Erro inesperado no processamento: {e}")
        raise

def load_to_solr(**kwargs):
    ti = kwargs['ti']
    registros = ti.xcom_pull(task_ids='task_clean_data')
    
    if not registros:
        logging.warning("Nenhum dado recebido da task de limpeza.")
        return

    try:
        solr = pysolr.Solr(SOLR_URL, always_commit=True, timeout=10)
        solr.add(registros)
        logging.info(f"Sucesso! {len(registros)} registros indexados no Solr.")
    except Exception as e:
        logging.error(f"Falha ao inserir no Solr: {e}")
        raise

# ==========================================
# DEFINIÇÃO DA DAG
# ==========================================
default_args = {
    'owner': 'daniel_barbosa',
    'depends_on_past': False,
    'start_date': datetime(2026, 4, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='ubc_solr_import_pipeline',
    default_args=default_args,
    description='ETL: Pipeline utilizando lógica de limpeza externa e testável',
    schedule_interval=None,
    catchup=False,
    tags=['ubc', 'etl', 'solr', 'ci-cd'],
) as dag:

    task_clean = PythonOperator(
        task_id='task_clean_data',
        python_callable=extract_and_clean_data,
        provide_context=True
    )

    task_load = PythonOperator(
        task_id='task_load_to_solr',
        python_callable=load_to_solr,
        provide_context=True
    )

    task_clean >> task_load