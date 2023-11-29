"""
--------------------------------------------------------------------------------
Script Name: AWS Auditor
Author: Ruben Alvarez Mosquera AKA GitHub@RobinGoldwing
Created: 23/11/2023

Description:
    This script automates the export of AWS resources to CSV files.
    Supports multiple services including Lambda, Step Functions, EventBridge, etc.

Usage :
    Usage Bash   >>>  bash start-awsauditor.sh [options]
    Usage Python >>>  python3 awsauditor.py [options]

Options:
    -all  : Exports all resources
    -lb   : Exports Lambda functions
    -sf   : Exports Step Functions
    -eb   : Exports EventBridge rules
    -s3   : Exports S3 buckets
    -ds   : Exports DMS Tasks
    -gl   : Exports Glue Jobs



License:
    Copyright (c) MIT 2023 by Ruben Alvarez Mosquera AKA GitHub@RobinGoldwing
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

Disclaimer:
    This script is provided "as is", without warranty of any kind, express or
    implied. Use of this script is at your own risk.


Music, Keep Calm & CODE!! // GitHub@RobinGoldwing

--------------------------------------------------------------------------------
"""

"""
--------------------------------------------------------------------------------
SCRIPT HEADER - IMPORTS
--------------------------------------------------------------------------------
"""

import boto3
import csv
import sys
import os
import zipfile
from datetime import datetime

import warnings
warnings.filterwarnings("ignore")

"""
--------------------------------------------------------------------------------
CONSTANTS CONFIGURATION
--------------------------------------------------------------------------------
"""
# VERSION & GENERAL CONFIGURATIONS
VERSION = {
    'Name' : 'AWS Auditor',
    'ActualVersion' : 'v0.3.2',
    'LastModification': '26/11/2023',
    'Changes' : [
        'Avoid warnings in console',
    ]
}

CSV_DIR_NAME = 'csv-files'
ZIP_DIR_NAME = 'zip-files'
ZIP_FILENAME = 'AWS_export_data'

# Console title
CONSOLE_TITLE = f'''
#=========================#
   {VERSION['Name']} - {VERSION['ActualVersion']} 
#=========================#

'''


"""
-------------------------------------------------------------------------------
SERVICES & ATTR. CONFIGURATION
-------------------------------------------------------------------------------
"""
# Add/remove consults and/or add/remove columns to show in exported CSV files

ATTRIBUTES_CONFIG = {

    "lambda": [
        'FunctionName',
        'Runtime',
        'Timeout',
        'MemorySize',
        'FunctionArn',
        'Role',
        ],

    "stepfunctions": [
        'name', 
        'stateMachineArn', 
        'creationDate', 
        ],

    "eventbridge": [
        'Name', 
        'Arn', 
        'ScheduleExpression', 
        'State', 
        'Description',
        ],

    "s3": [
        'Name', 
        'CreationDate',
        ],

    "dms": [
        'ReplicationTaskIdentifier', 
        'Status', 
        'ReplicationTaskArn', 
        'StopReason', 
        'LastFailureMessage',
        # 'TableMappings'
        ],

    "glue": [
        'Name', 
        'Role', 
        'CreatedOn', 
        'LastModifiedOn', 
        'MaxRetries', 
        'AllocatedCapacity', 
        'Timeout', 
        'MaxCapacity', 
        'WorkerType', 
        'NumberOfWorkers', 
        'GlueVersion',
        ]
}
CLIENTS = {
    "lambda": boto3.client('lambda'),
    "stepfunctions": boto3.client('stepfunctions'),
    "eventbridge": boto3.client('events'),
    "s3": boto3.client('s3'),
    "dms": boto3.client('dms'),
    "glue": boto3.client('glue')
}

RESOURCES_CONFIG = {
    # arg :  FileName           Service    AWS CLI Method   Response Key
    "-lb": ("lambda_functions", "lambda", "list_functions", "Functions"),
    "-sf": ("step_functions", "stepfunctions", "list_state_machines", "stateMachines"),
    "-eb": ("eventbridge_rules", "eventbridge", "list_rules", "Rules"),
    "-s3": ("s3_buckets", "s3", "list_buckets", "Buckets"),
    "-ds": ("dms_tasks", "dms", "describe_replication_tasks", "ReplicationTasks"),
    "-gl": ("glue_jobs", "glue", "get_jobs", "Jobs")
}

"""
--------------------------------------------------------------------------------
DEV FUNCTIONS #1
--------------------------------------------------------------------------------
"""
lambda_client = boto3.client('lambda')

def get_lambda_function_simple(function_name):
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        return {
            'FunctionName': response['Configuration']['FunctionName'],
            'Runtime': response['Configuration']['Runtime'],
            'Role': response['Configuration']['Role'],
            'Handler': response['Configuration']['Handler'],
            'Description': response['Configuration'].get('Description', 'N/A'),
            'Timeout': response['Configuration']['Timeout'],
            'MemorySize': response['Configuration']['MemorySize'],
            'LastModified': response['Configuration']['LastModified'],
            'CodeSize': response['Configuration']['CodeSize'],
            'Environment': response['Configuration'].get('Environment', {}),
            'TracingConfig': response['Configuration'].get('TracingConfig', {}),
            'CodeLocation': response['Code']['Location'],
        }
    except Exception as e:
        return {'Error': str(e)}

"""
--------------------------------------------------------------------------------
DEV FUNCTIONS 2
--------------------------------------------------------------------------------
"""
from botocore.exceptions import ClientError

lambda_client = boto3.client('lambda')
iam_client = boto3.client('iam')
cloudwatch_client = boto3.client('cloudwatch')

def get_lambda_function_multiple(function_name):
    try:
        # Lambda details
        response = lambda_client.get_function(FunctionName=function_name)
        function_details = response['Configuration']

        # IAM policy details
        role_name = function_details['Role'].split('/')[-1]
        policy = iam_client.get_role_policy(RoleName=role_name, PolicyName=role_name)

        # CloudWatch metrics
        metrics = cloudwatch_client.get_metric_data(
            MetricDataQueries=[
                {
                    'Id': 'invocations',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Lambda',
                            'MetricName': 'Invocations',
                            'Dimensions': [
                                {
                                    'Name': 'FunctionName',
                                    'Value': function_name
                                },
                            ]
                        },
                        'Period': 3600,
                        'Stat': 'Sum',
                    },
                    'ReturnData': True,
                },
            ],
            # Last 14 days
            StartTime='2023-01-01T00:00:00Z',
            EndTime='2023-01-14T00:00:00Z',
        )

        # Lambda Tags
        tags = lambda_client.list_tags(Resource=function_details['FunctionArn'])

        return {
            'BasicDetails': function_details,
            'IAMRolePolicy': policy,
            'CloudWatchMetrics': metrics,
            'Tags': tags
        }
    except ClientError as e:
        return {'Error': str(e)}

"""
--------------------------------------------------------------------------------
FUNCTIONS DEFINITION
--------------------------------------------------------------------------------
"""
# Return a list of all resources and attributes configured in constants configure section
def list_aws_resources(client, list_method, response_key, attributes):
    try:
        response = getattr(client, list_method)()
        return [
            [resource.get(attr, 'N/A') for attr in attributes] for resource in response[response_key]
        ]
    except Exception as e:
        print(f"Error al listar recursos: {e}")
        return []

"""
--------------------------------------------------------------------------------
HELPER FUNCTIONS
--------------------------------------------------------------------------------
"""
def export_to_csv(data, filename, headers):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)

def create_unique_filename(base_filename, extension):
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    return f"{base_filename}_{timestamp}.{extension}"

def create_export_directory(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

def zip_files(filenames_list, zip_filename):
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file in filenames_list:
            zipf.write(file, os.path.basename(file))

"""
--------------------------------------------------------------------------------
MAIN FUNCTION
--------------------------------------------------------------------------------
"""
def main():

    # os.system('cls' if os.name == 'nt' else 'clear') # Limpiar el terminal
    print(CONSOLE_TITLE)

    create_export_directory(CSV_DIR_NAME) 
    create_export_directory(ZIP_DIR_NAME)

    exported_resources = []

    args = sys.argv[1:] 
    if "-all" in args or len(args) == 0:
        args = RESOURCES_CONFIG.keys()
   
    # Main loop
    for arg in args:
        if arg in RESOURCES_CONFIG:
            filename, service, list_method, response_key = RESOURCES_CONFIG[arg] 
            client = CLIENTS[service] 
            attributes = ATTRIBUTES_CONFIG[service] 
            data = list_aws_resources(client, list_method, response_key, attributes) 
            unique_filename =  os.path.join(CSV_DIR_NAME, create_unique_filename(filename, 'csv')) 
            export_to_csv(data, unique_filename, attributes) 
            exported_resources.append((unique_filename.split('_')[0],unique_filename)) 

    exported_filename = [resource[1] for resource in exported_resources]

    unique_zip_filename = os.path.join(ZIP_DIR_NAME, create_unique_filename(ZIP_FILENAME,'zip'))
    zip_files(exported_filename, unique_zip_filename)

    print("Exported Resources:")
    print("====================\n")
    print("{:<25} {:<10} {:<50}".format("Resource", ">>>", "Exported File"))
    print("-" * 80)
    for resource in exported_resources:
        print("{:<25} {:<10} {:<50}".format(resource[0], ">>>", resource[1]))
    print(f"\nAll files compressed at : {unique_zip_filename}")
    print("\n\n")

"""
--------------------------------------------------------------------------------
SCRIPT EXECUTION
--------------------------------------------------------------------------------
"""
if __name__ == '__main__':
    main()
"""
--------------------------------------------------------------------------------
End of Script
--------------------------------------------------------------------------------
"""