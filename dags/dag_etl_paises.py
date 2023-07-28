from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.email_operator import EmailOperator
from email import message
from airflow.hooks.base_hook import BaseHook
from airflow.models import Variable
import smtplib
from script_etl import  transform_data, get_data, enviar_fallo, enviar_success

QUERY_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS bapintor_coderhouse.ciudades (
    city VARCHAR PRIMARY KEY,
    "Housing" DECIMAL(10, 2),
    "Cost of Living" DECIMAL(10, 2),
    "Startups" DECIMAL(10, 2),
    "Venture Capital" DECIMAL(10, 2),
    "Travel Connectivity" DECIMAL(10, 2),
    "Commute" DECIMAL(10, 2),
    "Business Freedom" DECIMAL(10, 2),
    "Safety" DECIMAL(10, 2),
    "Healthcare" DECIMAL(10, 2),
    "Education" DECIMAL(10, 2),
    "Environmental Quality" DECIMAL(10, 2),
    "Economy" DECIMAL(10, 2),
    "Taxation" DECIMAL(10, 2),
    "Internet Access" DECIMAL(10, 2),
    "Leisure & Culture" DECIMAL(10, 2),
    "Tolerance" DECIMAL(10, 2),
    "Outdoors" DECIMAL(10, 2),
    "process_date" DATETIME DISTKEY
);
"""


SMTP_HOST = Variable.get("SMTP_HOST")
SMTP_PORT = Variable.get("SMTP_PORT")
SMTP_EMAIL_FROM= Variable.get("SMTP_EMAIL_FROM")
SMTP_PASSWORD= Variable.get("SMTP_PASSWORD")
SMTP_EMAIL_TO= Variable.get("SMTP_EMAIL_TO")

default_args = {
    'owner': 'Belenpintor',
    "start_date": datetime(2023, 7, 9),
    "retries": 1,
    'email_on_failure': True,
    'email_on_retry': True,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    default_args=default_args,
    dag_id='dag_con_conexion_postgres',
    description='Entrega 3 Belén Pintor',
    start_date=datetime(2023, 7, 8),
    schedule_interval='0 0 * * *'
) as dag:
    
    task1 = PostgresOperator(
        task_id='crear_tabla_',
        sql=QUERY_CREATE_TABLE, 
        postgres_conn_id='redshift_belen',
        autocommit=True
    )

    task2 = PythonOperator(
        task_id='obtener_datos',
        python_callable=get_data,
        provide_context=True
    )

    task3 = PythonOperator(
        task_id='transformar_datos',
        python_callable=transform_data,
        provide_context=True,
        op_args=[task2.output] 
        
    )
    
    task_fallo=PythonOperator(
        task_id='enviar_fallo',
        python_callable=enviar_fallo,
        trigger_rule='all_failed'
    )
    
    task_succes=PythonOperator(
        task_id='dag_envio_success',
        python_callable=enviar_success,
        trigger_rule='all_success'
    )


task1>>  task2>>  task3>> task_succes
task1>> task_fallo
task2>> task_fallo
task3>>task_fallo