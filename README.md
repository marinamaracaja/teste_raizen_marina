# Desafio Engenheiro de Dados Raízen 
O teste consiste em desenvolver uma pipeline de orquestração de dados ETL que extraia relatórios consolidados sobre vendas de combustíveis do site da ANP (Agência Nacional do Petróleo, Gás Natural e Biocombustíveis), transforme os dados fazendo uma limpeza e estruturação dos campos, exporte os arquivos em um formato de big data e valide a integridade dos dados brutos (raw data) com os dados tratados.

As tabelas que deverão ser extraídas do site da ANP são:
- Vendas de combustíveis derivados de petróleo por UF e por produto;
- Vendas de diesel por UF e por tipo;

Os dados deverão ser armazenados nos seguintes formatos:

| Coluna       | Tipo        |
| ------------ | ----------- |
| `year_month` | `date`      |
| `uf`         | `string`    |
| `product`    | `string`    |
| `unit`       | `string`    |
| `volume`     | `double`    |
| `created_at` | `timestamp` |

Os dados brutos estão disponíveis no site da ANP: https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/vendas-de-derivados-de-petroleo-e-biocombustiveis

Para mais informações, segue o link do repositório contendo o teste da Raízen: https://github.com/raizen-analytics/data-engineering-test

## Ferramentas utilizadas:
- Google Colab: Ambiente em nuvem utilizado para executar de forma rápida os códigos e funções em python. Toda limpeza e tratamento inicial dos dados foi realizado nessa ferramenta que permitiu uma rápida visualização dos dataframes criados.
- VS Code: IDE utilizada para integrar o código criado em python com a ferramenta airflow através do uso de DAGs(Directed Acyclic Graph).
- Apache Airflow: Orquestrador de pipelines que possibilitou o gerenciamento e a automatização do fluxo de tarefas criado.
- Docker: Ferramenta container escalável que permitiu a criação do ambiente onde o airflow foi executado.

## Desenvolvimento:
O primeiro passo para execução da atividade foi extrair diretamente do site da ANP as tabelas desejadas e realizar o tratamento dos dados conforme solicitado no enuciado do desafio, para tanto foi escolhido o Google Colab que permitiu uma rápida visualização das transformações:

![image](https://user-images.githubusercontent.com/86935693/189779772-d8a00b29-07ad-4c2d-93df-3ca529a1c234.png)

O resultado foram dois dataframes contendo os dados tratados, sendo eles: **dfPetroleo** que contém os dados da tabela "Vendas de combustíveis derivados de petróleo por UF e por produto", e o **dfDiesel** que contém os dados da tabela "Vendas de combustíveis derivados de petróleo por UF e por produto"

```
dfPetroleo.head()
```
![image](https://user-images.githubusercontent.com/86935693/189780730-6256aefe-25ec-451b-a888-769845e74a97.png)

```
dfDiesel.head()
```
![image](https://user-images.githubusercontent.com/86935693/189780221-65651e7e-a1e6-4e2f-8127-27d0f7fb1d14.png)

## Pipeline:
Uma vez que foi definido quais tratamentos serão aplicados nos dataframes, utilizando o Vs Code foi criado um arquivo .py contendo as funções de ETL e a DAG que irá definir as tasks e o fluxo de atividades no Airflow:
```
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
```

Desenho do fluxo da DAG no airflow:

![image](https://user-images.githubusercontent.com/86935693/189781732-5f3a15a6-b790-4a02-9373-6e918fc3552a.png)


## Fluxo de trabalho:
O fluxo de trabalho desenvolvido extrai os dados brutos do site da ANP, carrega localmente uma cópia de cada dataframe, **dfPetroleo** e **dfDiesel**, faz as transformações solicitadas nos dados, exporta os arquivos para o formato big data escolhido: *parquet* e, por fim valida a integridade dos dados brutos em comparação com os dados finais tratados.

## Execução do projeto:
Para executar o projeto via Docker, deve-se:

- Clonar o atual repositório:
git clone https://github.com/marinamaracaja/teste_raizen_marina.git

- Upar o arquivo do airflow bem como todas as pastas do projeto e na pasta raíz "airflow docker" rodar via terminal os seguintes comandos:
```
docker-compose up airflow-init
```
```
docker-compose up
```
- Acessar no navegador web:
http://localhost:8080/

- Buscar a DAG: marina_teste_raizen
- Executar o fluxo de tarefas.

## Possíveis melhorias:
- Tornar o código reaproveitável para outros projetos;
- Otimizar o processamento do fluxo visando economia de recursos de máquina.

## Conclusão:
Trabalhar com Airflow e Docker foi desafiador, uma vez que este foi meu primeiro contato com a ferramenta, mas sei que é através de desafios que conseguimos evoluir e encontrar caminhos e soluções para crescer nos estudos e profissionalmente. 
##

### Autora:
[Marina Maracajá](https://www.linkedin.com/in/marinamaracaja/)

##
<img align="right" alt="grogu" height="50" style="border-radius:50px;" src="https://ada-site-frontend.s3.sa-east-1.amazonaws.com/home/header-logo.svg">


