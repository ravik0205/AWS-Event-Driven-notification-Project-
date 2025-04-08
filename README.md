📍 Problem Statement
Modern businesses often struggle with processing and analyzing incoming order data in real time. Traditional batch jobs introduce delays, and coupling ingestion with processing reduces flexibility and scalability.


💡 Solution
built a fully event-driven, serverless pipeline that reacts instantly when new orders are received. Orders are:
![image](https://github.com/user-attachments/assets/06f39975-b7ae-43c1-bcd7-520c40592dce)🚚 Real-Time Event-Driven Order Processing Pipeline using AWS

Uploaded to S3

Validated by a Lambda function

Queued in SQS

Processed by AWS Glue (PySpark)

Stored in a processed format on S3

Loaded into Redshift for analysis

Monitored via SNS notifications




🧱 Why This Approach?
Scalable: SQS decouples producers (S3+Lambda) from consumers (Glue), allowing them to scale independently.

Real-time readiness: Events trigger processing as soon as data lands in S3.

Serverless architecture: Minimal maintenance, cost-effective, and ideal for data engineering workflows.

Secure & Modular: IAM roles with scoped permissions and modular components.




🔧 Tech Stack
AWS S3 – Raw and processed data storage

AWS Lambda – Trigger-based validation and routing

Amazon SQS – Event queue to decouple components

AWS Glue (Spark) – ETL job for processing and enrichment

Amazon Redshift – Data warehousing for analytics

Amazon SNS – Alerting and notifications

Python (Boto3, Faker) – Data generation and scripting

