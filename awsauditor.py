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

# Evitar que los Warnings aparezcan por terminal
import warnings
warnings.filterwarnings("ignore")

"""
--------------------------------------------------------------------------------
VERSION & GENERAL CONFIGURATIONS
--------------------------------------------------------------------------------
"""
# Version actual, ultima modificacion y cambios realizados
version = {
    'Name' : 'AWS Auditor',
    'ActualVersion' : 'v0.3.2',
    'LastModification': '26/11/2023',
    'Changes' : [
        'Avoid warnings in console',
    ]
}

# Nombre del directorio de exportacion de los archivos CSV
csv_dir_name = 'csv-files'

# Nombre del archivo ZIP y su directorio de exportacion
zip_dir_name = 'zip-files'
zip_filename = 'AWS_export_data'

# Titulo del Script por consola
console_title = f'''
#=========================#
   {version['Name']} - {version['ActualVersion']} 
#=========================#

'''


"""
-------------------------------------------------------------------------------
SERVICES & ATTR. CONFIGURATION
-------------------------------------------------------------------------------
"""
# MODIFICAR estas listas para incluir o eliminar attributos a exportar en CSV a
#  traves de comentar o añadirlos
###############################################################################

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

# Configuracion clientes de AWS
clients = {
    "lambda": boto3.client('lambda'),
    "stepfunctions": boto3.client('stepfunctions'),
    "eventbridge": boto3.client('events'),
    "s3": boto3.client('s3'),
    "dms": boto3.client('dms'),
    "glue": boto3.client('glue')
}

# Configuracion argumentos y de recursos asociados
resources_config = {
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
FUNCTIONS DEFINITION
--------------------------------------------------------------------------------
"""

# FUNCTION - Devuelve una lista con los recursos del servicio 
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

# FUNCTION - Exporta en formato CSV
def export_to_csv(data, filename, headers):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)

# FUNCTION Crea un nombre unico con timestamp para tener un historico
def create_unique_filename(base_filename, extension):
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    return f"{base_filename}_{timestamp}.{extension}"

# FUNTION - Crea directorio de exportacion
def create_export_directory(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

# FUNCTION - Comprime archivos CSV en un archivo ZIP
def zip_files(filenames_list, zip_filename):
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file in filenames_list:
            zipf.write(file, os.path.basename(file))

"""
--------------------------------------------------------------------------------
MAIN FUNCTION
--------------------------------------------------------------------------------
"""
# FUNCTION - PRINCIPAL
def main():
    # os.system('cls' if os.name == 'nt' else 'clear') # Limpiar el terminal
    
    # Encabezado del terminal 
    print(console_title)

    args = sys.argv[1:] # Obtiene lista de argumentos
    exported_resources = [] # Crea lista de recursos a exportar
    create_export_directory(csv_dir_name) # Crea el directorio de exportacon CSV si no existe
    create_export_directory(zip_dir_name) # Crea el directorio de exportacon ZIP si no existe

    # Si existe el argumento -all agrega todos los recursos independientemente de los demas argumentos
    if "-all" in args or len(args) == 0:
        args = resources_config.keys()
   
    # Bucle principal que itera por los argumentos y servicios configurados
    for arg in args:
        if arg in resources_config:
            filename, service, list_method, response_key = resources_config[arg] # Obtiene la configuracion del servicio
            client = clients[service] # Obtiene el cliente del servicio
            attributes = ATTRIBUTES_CONFIG[service] # Obtiene los atributos del servicio
            data = list_aws_resources(client, list_method, response_key, attributes) # Obtiene el listado de los recursos del servicio
            unique_filename =  os.path.join(csv_dir_name, create_unique_filename(filename, 'csv')) # Crea un nombre único con un timestamp
            export_to_csv(data, unique_filename, attributes) # Exporta el resultado
            exported_resources.append((unique_filename.split('_')[0],unique_filename)) # agrega un tupla del nombre del recurso y el archivo

    # Crea lista de recursos exportados
    exported_filename = [resource[1] for resource in exported_resources]

    # Comprime los archivos CSV en ZIP
    unique_zip_filename = os.path.join(zip_dir_name, create_unique_filename(zip_filename,'zip')) # Genera TimeStamp y concatena con extension de archivo
    zip_files(exported_filename, unique_zip_filename)

    # Imprime los recursos exportados y el nombre del archivo generado, así como el archivo comprimido
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





"""
OLD VERSIONs:
============
--------------------------------------------------------------------------------

v0.1.0 - Simple lambdas list query and export to JSON
v0.1.1 - Feature - export also S3 Buckets
v0.1.2 - Feature - export to CSV
v0.1.3 - Feature - add more resource types
v0.1.4 - Feature - adds arguments functionality
v0.1.5 - Lambdas query enhancement
v0.1.6 - HOTFIX - Attribute and query query query extension
v0.1.7 - HOTFIX - Attribute and query query query extension
v0.1.7a - TEST BRACH
v0.1.7b - TEST BRACH
v0.1.7c - STABLE VERSION
v0.1.8 - REFACTORING Unify service query functions and externalize service configuration and associated proper nouns
v0.1.9 - REFACTORING 2 Unify service query functions and externalize service configuration and associated proper nouns
v0.2 - STABLE VERSION
v0.3 - Add ZIP capability
v0.3.1 - Create export&zip data folders
--------------------------------------------------------------------------------
"""




"""
FUTURE FEATUREs:
===============
--------------------------------------------------------------------------------
- FEATURE - Added ability to compress files into ZIP format, with a new argument
- Possibility to externalize the configuration through a config file, so as not to touch the code.
- HOTFIX > Fix DMSTask since the TableMappings attribute comes in JSON format.
    - For the moment it is INACTIVE
    - It is possible to encode in BASE64, but this would manage file length more efficiently but would affect readability.
    - Line breaks can be replaced and encoded allowing a direct reading of the CSV, but it will handle the size of the attribute/column data worse.
    - Add the possibility to add the sub-divisions as new columns (EXAMPLE DMSTasks>ReplicationTaskStats)

Music, Keep Calm & CODE!! - GitHub@RobinGoldwing

--------------------------------------------------------------------------------
"""





"""
NOTES:
--------------------------------------------------------------------------------

# print('>>> for : arg >>>', arg) #### TEST

--------------------------------------------------------------------------------
"""
