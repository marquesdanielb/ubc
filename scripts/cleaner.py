import pandas as pd

def clean_student_data(df: pd.DataFrame) -> list:
    """
    Recebe um DataFrame bruto, limpa as colunas, strings e nulos,
    e retorna uma lista de dicionários pronta para o Solr.
    """
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
        'endereco': 'Não Informado',
        'nome_da_mae': 'Não Informado'
    }
    colunas_presentes = {k: v for k, v in valores_padrao.items() if k in df.columns}
    df.fillna(colunas_presentes, inplace=True)
    
    if 'nome' in df.columns:
        df['nome'] = df['nome'].astype(str).str.strip().str.title()
        
    if 'endereco' in df.columns:
        df['endereco'] = df['endereco'].astype(str).str.strip()
        
    if 'idade' in df.columns:
        df['idade'] = pd.to_numeric(df['idade'], errors='coerce').fillna(0).astype(int)
    
    return df.to_dict(orient='records')