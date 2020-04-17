# aws-codebuild-event-logs
AWS CodeBuild event logs stored in S3 and query-able by Athena

## Architecture

![enter image description here](https://d50daux61fgb.cloudfront.net/aws-codebuild-event-logs/solution-architecture.png)

An EventBridge event rule for the default event bus tracks CodeBuild build state change events. The event rule targets a Kinesis Firehose delivery stream that will put log files into an S3 bucket. A Lambda function is used by the delivery stream to transform the CloudWatch event payload into the log file format. After a log file is placed in the bucket, a Lambda function is run that creates a partition for the Glue table, if one does not exist.

## Log Format

 - **timestamp** *(string)* - The ISO 8601 format of the timestamp of the event
 - **event_version** *(string)* - The version of the event format
 - **build_status** *(string)* - The status of the build
 - **build_id** *(string)* - The ARN of the build
 - **current_phase** *(string)* - The name of the current phase
 - **current_phase_context** *(string)* - A JSON string describing context for the current phase. The content in this JSON can be extracted in Athena queries using [Presto functions](https://prestodb.io/docs/0.172/functions/json.html).
 - **additional_information** *(string)* - A JSON string containing information about the build and the build project. The content in this JSON can be extracted in Athena queries using [Presto functions](https://prestodb.io/docs/0.172/functions/json.html).


## Log Partitions

All Glue tables are partitioned by the date and hour that the log arrives in S3. It is highly recommended that Athena queries on Glue database filter based on these paritions, as it will greatly reduce quety execution time and the amount of data processed by the query.


## Build and Deploy

To deploy the application, use the `cloudformation package` command from the AWS CLI. 
 
#### Example:

`aws cloudformation package --template templates/root.yaml --s3-bucket $S3_BUCKET --s3-prefix $S3_PREFIX --output-template template-export.yaml`