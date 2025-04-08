# 📂 generate_orders.py
import json
import random
import uuid
from faker import Faker
import boto3
from datetime import datetime

fake = Faker()
s3 = boto3.client('s3')
bucket_name = 'order-processing-raw-ravi'

products = ['Coffee', 'Tea', 'Juice', 'Smoothie']

for _ in range(5):
    order = {
        'order_id': str(uuid.uuid4()),
        'customer_name': fake.name(),
        'product': random.choice(products),
        'quantity': random.randint(1, 5),
        'timestamp': datetime.utcnow().isoformat()
    }
    file_name = f"order_{order['order_id']}.json"
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=json.dumps(order))
    print(f"Uploaded: {file_name}")


# 📂 lambda_function.py
import json
import boto3
import os

sqs = boto3.client('sqs')
queue_url = os.environ['QUEUE_URL']

def lambda_handler(event, context):
    for record in event['Records']:
        payload = record['s3']['object']['key']
        print(f"Validating and pushing: {payload}")

        message = {
            'bucket': record['s3']['bucket']['name'],
            'key': payload
        }
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message)
        )
    return {'statusCode': 200}


# 📂 glue_job_script.py (PySpark)
import sys
import boto3
import json
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read messages from SQS
sqs = boto3.client('sqs')
queue_url = 'SQS_QUEUE_URL'
response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)

records = []
if 'Messages' in response:
    for message in response['Messages']:
        body = json.loads(message['Body'])
        s3_path = f"s3://{body['bucket']}/{body['key']}"
        df = spark.read.json(s3_path)
        records.append(df)

    if records:
        full_df = records[0]
        for df in records[1:]:
            full_df = full_df.union(df)

        # Transformations
        full_df = full_df.withColumnRenamed("timestamp", "order_time")

        # Save to S3 processed bucket
        full_df.write.mode("append").json("s3://order-processing-processed-ravi/")

        # Save to Redshift
        full_df.write \
            .format("jdbc") \
            .option("url", "jdbc:redshift://redshift-cluster-url:5439/dev") \
            .option("dbtable", "orders") \
            .option("user", "username") \
            .option("password", "password") \
            .option("driver", "com.amazon.redshift.jdbc.Driver") \
            .mode("append") \
            .save()

job.commit()


# 📂 sns_notification.py (Set in Glue Job Parameters or Lambda)
import boto3

sns = boto3.client('sns')

def notify(status, job_name):
    topic_arn = 'SNS_TOPIC_ARN'
    message = f"Glue Job '{job_name}' completed with status: {status}"
    sns.publish(TopicArn=topic_arn, Message=message)
