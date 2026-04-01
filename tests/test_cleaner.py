import pandas as pd
from scripts.cleaner import clean_student_data

def test_limpeza_de_colunas_e_caracteres():
    dados_mock = {
        'Nome da mãe': ['Maria da Silva'],
        ' Endereço ': ['Rua A, 123  ']
    }
    df_sujo = pd.DataFrame(dados_mock)
    
    resultado = clean_student_data(df_sujo)
    
    linha_limpa = resultado[0]
    
    assert 'nome_da_mae' in linha_limpa
    assert 'endereco' in linha_limpa
    assert 'Nome da mãe' not in linha_limpa
    
    assert linha_limpa['endereco'] == 'Rua A, 123'

def test_tratamento_de_nulos():
    df_sujo = pd.DataFrame({'idade': [None]})
    resultado = clean_student_data(df_sujo)
    
    assert resultado[0]['idade'] == 0