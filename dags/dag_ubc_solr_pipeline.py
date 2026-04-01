import logging
import pandas as pd
import pysolr
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

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
    Lê o CSV, aplica regras de limpeza e padronização com Pandas.
    """
    logging.info(f"Iniciando a leitura do arquivo: {CSV_PATH}")
    
    try:
        df = pd.read_csv(CSV_PATH)
        logging.info(f"Arquivo lido com sucesso. Total de linhas: {len(df)}")
        
        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(' ', '_', regex=False)
            .str.normalize('NFKD')
            .str.encode('ascii', errors='ignore')
            .str.decode('utf-8')
        )
        
        valores_padrao = {
            'nome': 'Desconhecido',
            'idade': 0,
            'turma': 'Não Atribuída',
            'notas': 0.0,
            'endereco': 'Não Informado'
        }
        
        colunas_presentes = {k: v for k, v in valores_padrao.items() if k in df.columns}
        df.fillna(colunas_presentes, inplace=True)
        
        if 'nome' in df.columns:
            df['nome'] = df['nome'].astype(str).str.strip().str.title()
            
        if 'endereco' in df.columns:
            df['endereco'] = df['endereco'].astype(str).str.strip()
            
        if 'idade' in df.columns:
            df['idade'] = pd.to_numeric(df['idade'], errors='coerce').fillna(0).astype(int)
        
        registros = df.to_dict(orient='records')
        logging.info(f"Limpeza concluída. {len(registros)} registros prontos.")
        
        return registros
        
    except FileNotFoundError:
        logging.error(f"ERRO: Arquivo não encontrado no caminho {CSV_PATH}. Verifique os volumes do Docker.")
        raise
    except Exception as e:
        logging.error(f"Erro inesperado no processamento: {e}")
        raise


def load_to_solr(**kwargs):
    """
    Recupera os dados via XCom e faz o bulk insert no Apache Solr.
    """
    ti = kwargs['ti']
    registros = ti.xcom_pull(task_ids='task_clean_data')
    
    if not registros:
        logging.warning("Nenhum dado recebido da task de limpeza. Encerrando.")
        return

    logging.info(f"Conectando ao Solr em: {SOLR_URL}")
    
    try:
        solr = pysolr.Solr(SOLR_URL, always_commit=True, timeout=10)
        
        solr.add(registros)
        
        logging.info(f"Sucesso absoluto! {len(registros)} registros indexados no Solr.")
        
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
    description='ETL: Limpeza de CSV de alunos com Pandas e carga no Solr',
    schedule_interval=None,
    catchup=False,
    tags=['ubc', 'etl', 'solr'],
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