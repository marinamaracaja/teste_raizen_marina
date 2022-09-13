FROM apache/airflow:2.3.3
USER airflow

#instalando biblioteca
RUN pip install fastparquet

