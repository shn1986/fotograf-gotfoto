import airflow
from datetime import timedelta
from airflow import DAG
from airflow.operators.mysql_operator import MySqlOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from utils.load_csv import fn_load_csv

default_args = {
        'owner': 'airflow',    
        #'start_date': airflow.utils.dates.days_ago(2),
        # 'end_date': datetime(),
        # 'depends_on_past': False,
        # 'email': ['airflow@example.com'],
        #'email_on_failure': False,
        #'email_on_retry': False,
        # If a task fails, retry it once after waiting
        # at least 5 minutes
        #'retries': 1,
        'retry_delay': timedelta(minutes=5),
        }

dag_load_data = DAG(
        dag_id='load_data',
        default_args=default_args,
        # schedule_interval='0 0 * * *',
        schedule_interval='@once',
        start_date=days_ago(1),
        dagrun_timeout=timedelta(minutes=60),
        description='Executing sql scripts and output as json file',
    )
create_table = MySqlOperator(
    sql="sql/create_schema.sql",
    task_id="createtable_task", 
    mysql_conn_id="local_mysql",
    dag=dag_load_data
)

python_task = PythonOperator(
    task_id='python_task', 
    python_callable=fn_load_csv, 
    dag=dag_load_data)

#Task sequence
create_table>>python_task