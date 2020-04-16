import boto3
import os
import traceback

# Initialize Glue client
glue_client = boto3.client("glue")

def handler(event, context):
    for record in event["Records"]:
        source_bucket = record["s3"]["bucket"]["name"]
        source_key = record["s3"]["object"]["key"]

        # Extract partition info from S3 key 
        table, year, month, day, hour, _ = source_key.split("/")

        # Form date for 'date' partition column
        date = "{}-{}-{}".format(year, month, day)

        # Form S3 location for partition
        s3_location = 's3://{}/{}/{}/{}/{}'.format(source_bucket, table, year, month, day, hour)

        # Form the partition input
        partition = {
            'Values': [
                date,
                hour
            ],
            "StorageDescriptor": {
                "NumberOfBuckets" : -1,
                "Columns": [
                    {
                        "Name": "timestamp",
                        "Type": "string"
                    },
                    {
                        "Name": "event_version",
                        "Type": "string"
                    },
                    {
                        "Name": "build_status",
                        "Type": "string"
                    },
                    {
                        "Name": "project_name",
                        "Type": "string"
                    },
                    {
                        "Name": "build_id",
                        "Type": "string"
                    },
                    {
                        "Name": "current_phase",
                        "Type": "string"
                    },
                    {
                        "Name": "current_phase_context",
                        "Type": "string"
                    },
                    {
                        "Name": "version",
                        "Type": "string"
                    },
                    {
                        "Name": "additional_information",
                        "Type": "struct<artifact:struct<md5sum:string,sha256sum:string,location:string>,environment:struct<image:string,privileged_mode:boolean,compute_type:string,type:string,environment_variables:array<struct<name:string,type:string,value:string>>>,timeout_in_minutes:float,build_complete:boolean,initiator:string,build_start_time:string,source:struct<location:string,type:string>,logs:struct<group_name:string,stream_name:string,deep_link:string>,phases:struct<phase_context:array<string>,start_time:string,end_time:string,duration_in_seconds:float,phase_type:string,phase_status:string>>"
                    }
                ],
                "Location": s3_location,
                "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
                "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                "Compressed": False,
                "SerdeInfo": {
                    "SerializationLibrary": "org.openx.data.jsonserde.JsonSerDe",
                    "Parameters": {
                        "serialization.format": "1"
                    }
                },
                "BucketColumns": [],
                "SortColumns": [],
                "Parameters": {},
                "SkewedInfo": {
                    "SkewedColumnNames": [],
                    "SkewedColumnValues": [],
                    "SkewedColumnValueLocationMaps": {}
                },
                "StoredAsSubDirectories": False
            }
        }

        # Attempt to create partition; Print exception if partition already exists or for any other error
        try:
            glue_client.create_partition(DatabaseName=os.environ["DATABASE_NAME"], TableName=table, PartitionInput=partition)
        except:
            traceback.print_exc()