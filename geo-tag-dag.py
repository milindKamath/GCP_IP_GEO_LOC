from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from google.cloud import pubsub_v1
import json
from google.cloud import bigquery
import pandas as pd

project_id = "peak-emblem-319723"
subscriptionName = "GeoTag_Sub"
topic_name = "IP-GeoTag"


def callback(message):
    print("Message recevied from the topic", message.data)
    with open("/home/airflow/gcs/data/message.json", "w", encoding='utf-8') as file:
        json.dump(json.loads(message.data), file)
    message.ack()


def pullMessage():
    global project_id, subscriptionName, topic_name
    try:
        topicName_created = 'projects/{project_id}/topics/{topic}'.format(
            project_id=project_id,
            topic=topic_name,
        )

        subscriptionName = 'projects/{project_id}/subscriptions/{sub}'.format(
            project_id=project_id,
            sub=subscriptionName,
        )

        with pubsub_v1.SubscriberClient() as subscriber:
            try:
                subscriber.create_subscription(
                    name=subscriptionName, topic=topicName_created)
            except:
                future = subscriber.subscribe(subscriptionName, callback)
                future.result(timeout=2)
    except:
        pass


def insert_bq():
    datasetID = "IP_GeoTag"
    tableID = "IP_info"
    with open("/home/airflow/gcs/data/message.json", 'r', encoding="utf-8") as file:
        data = json.load(file)
    dataDF = pd.DataFrame(data=data)
    bqclient = bigquery.client.Client(project="peak-emblem-319723")
    dataset = bqclient.dataset(datasetID)
    dataset.location = "US"
    try:
        bqclient.create_dataset(dataset)
    except:
        pass
    try:
        bqclient.create_table(tableID)
    except:
        pass
    bqclient.load_table_from_dataframe(dataDF, "peak-emblem-319723.IP_GeoTag.IP_info")


with DAG(
    dag_id='GEO_TAG',
    start_date=days_ago(1),
    schedule_interval=None) as dag:

    # Print the received dag_run configuration.
    # The DAG run configuration contains information about the
    # Cloud Storage object change.
    pullPUBSUB = PythonOperator(
        task_id='pull_message_pubsub',
        python_callable=pullMessage,
        dag=dag)

    insertBQ = PythonOperator(
        task_id="insert_into_bq",
        python_callable=insert_bq,
        dag=dag
    )


    pullPUBSUB >> insertBQ