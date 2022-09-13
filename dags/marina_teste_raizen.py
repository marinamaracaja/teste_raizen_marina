from urllib import request
import datetime as dt
from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
import pandas as pd
import os

os.system('pip install fastparquet')
os.system('pip install requests')


urlPetroleo = 'https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/vdpb/vendas-derivados-petroleo-e-etanol/vendas-derivados-petroleo-etanol-m3-1990-2022.csv'
filePetroleo = 'D:\Documentos\DEV\Airflow docker\Dados\Raw\Vendas-derivados-petroleo-etanol-m3-1990-2022.csv'

urlDiesel = 'https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/vdpb/vct/vendas-oleo-diesel-tipo-m3-2013-2022.csv'
fileDiesel = 'D:\Documentos\DEV\Airflow docker\Dados\Raw\Vendas-oleo-diesel-tipo-m3-2013-2022.csv'

#Função para extrair dados:
def extract_data():
    request.urlretrieve(urlPetroleo , filePetroleo)
    request.urlretrieve(urlDiesel, fileDiesel)

#Função que carrega o dataframe, e por fim chama a função transform_dataframe, passando os respectivos df como parâmetro:
def transform_data():
    #Abrindo o arquivo em um dataframe:
    dfPetroleo = pd.read_csv(filePetroleo, sep=';')
    dfDiesel = pd.read_csv(fileDiesel, sep=';')
    
    dfPetroleoTransformed = transform_dataframe(dfPetroleo)
    dfDieselTransformed = transform_dataframe(dfDiesel)

    dfPetroleoTransformed.to_csv('D:\Documentos\DEV\Airflow docker\Dados\IntermediateData\PetroleoTransformed.csv', sep=';')
    dfDieselTransformed.to_csv('D:\Documentos\DEV\Airflow docker\Dados\IntermediateData\DieselTransformed.csv', sep=';')
    
#Função que faz todas as transformações necessárias:
def transform_dataframe(df): 
    df['unit'] = '(m3)'
    
    df['MÊS'].replace(['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ'],
                            ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'], inplace=True)
    
    df.drop(['GRANDE REGIÃO'], axis=1, inplace=True)
    
    df.rename(columns={"UNIDADE DA FEDERAÇÃO": "uf", "PRODUTO": "product", "VENDAS": "volume" }, inplace=True)

    df['year_month'] = df['ANO'].map(str) + '-' + df['MÊS'].map(str)

    df.drop(['ANO', 'MÊS'],axis=1,inplace=True)

    df['created_at'] = dt.datetime.now()

    df = df[['year_month', 'uf', 'product', 'unit', 'volume', 'created_at']]

    df['year_month'] = pd.to_datetime(df['year_month'])

    df['volume'] = df['volume'].str.replace(",",".")
    df['volume'] = df['volume'].astype(float)
    return df

#Função para exportar dados:
def load_data():
    dfPetroleoTransform = pd.read_csv('D:\Documentos\DEV\Airflow docker\Dados\IntermediateData\PetroleoTransformed.csv', sep=';')
    dfDieselTransform = pd.read_csv('D:\Documentos\DEV\Airflow docker\Dados\IntermediateData\DieselTransformed.csv', sep=';')

    dfPetroleoTransform.to_parquet('D:\Documentos\DEV\Airflow docker\Dados\FinalData\Petroleo.parquet', engine='fastparquet')
    dfDieselTransform.to_parquet('D:\Documentos\DEV\Airflow docker\Dados\FinalData\Diesel.parquet', engine='fastparquet')
    

#Função para validação dos dados de origem com os dados tratados
def valid_data():
    dfPetroleoSrc = pd.read_csv(filePetroleo, sep=';')
    dfDieselSrc = pd.read_csv(fileDiesel, sep=';')
    dfPetroleoTransform = pd.read_csv('D:\Documentos\DEV\Airflow docker\Dados\IntermediateData\PetroleoTransformed.csv', sep=';')
    dfDieselTransform = pd.read_csv('D:\Documentos\DEV\Airflow docker\Dados\IntermediateData\DieselTransformed.csv', sep=';')

    if dfPetroleoSrc.shape[0] == dfPetroleoTransform.shape[0] and dfDieselSrc.shape[0] == dfDieselTransform.shape[0]:
        return 'validados'
    return 'invalidados'


with DAG('marina_teste_raizen', start_date = datetime(2022,9,10), schedule_interval = '30 * * * *', catchup=False) as dag:

  extract_data = PythonOperator(
      task_id = 'extract_data',
      python_callable = extract_data
  )
  transform_data = PythonOperator(
      task_id = 'transform_data',
      python_callable = transform_data
  )
  load_data = PythonOperator(
      task_id = 'load_data',
      python_callable = load_data
  )
  valid_data = BranchPythonOperator(
      task_id = 'valid_data',
      python_callable = valid_data
  )    
  validados = BashOperator(
      task_id = 'validados',
      bash_command ="echo 'Arquivos validados' " 
  )
  invalidados = BashOperator(
      task_id = 'invalidados',
      bash_command ="echo 'Arquivos inválidos' " 
  )

  
  
extract_data >> transform_data >> load_data >> valid_data >> [validados, invalidados]  
