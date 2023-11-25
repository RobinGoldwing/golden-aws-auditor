"""
--------------------------------------------------------------------------------
Script Name: AWS Auditor
Author: Ruben Alvarez Mosquera
Created: 24/11/2023
Last Modified: 24/11/2023
Version: 0.1.4 - Feature - agrega funcionalidad de argumentos

Description:
    Este script automatiza la exportación de recursos AWS a archivos CSV.
    Soporta múltiples servicios como Lambda, Step Functions, EventBridge, etc.

Usage:
    bash execute-scriptpython.sh scriptPython.py [options]

Options:
    -all  : Exporta todos los recursos
    -lmb  : Exporta Lambda functions
    -sf   : Exporta Step Functions
    -eb   : Exporta EventBridge rules
    -s3   : Exporta S3 buckets
    -ds   : Exporta DMS Tasks
    -glue : Exporta Glue Jobs


License:
    Copyright 2023 by Ruben Alvarez Mosquera.
    Se concede permiso, de forma gratuita, a cualquier persona que obtenga una copia
    de este software y de los archivos de documentación asociados (el "Software"), para
    utilizar el Software sin restricción, incluyendo sin limitación los derechos
    de usar, copiar, modificar, fusionar, publicar, distribuir, sublicenciar, y/o vender
    copias del Software, y para permitir a las personas a las que se les proporcione el
    Software hacer lo mismo, siempre que se incluya el siguiente aviso de derechos de autor
    y este aviso de permiso en todas las copias o partes sustanciales del Software.

Disclaimer:
    Este script se proporciona "tal cual", sin garantía de ningún tipo, expresa o
    implícita. El uso de este script es bajo su propio riesgo.

--------------------------------------------------------------------------------
"""

"""
--------------------------------------------------------------------------------
SCRIPT HEADER
--------------------------------------------------------------------------------
"""

import boto3
import csv
import sys
from datetime import datetime

"""
--------------------------------------------------------------------------------
FUNCTIONS DEFINITION
--------------------------------------------------------------------------------
"""

# FUNCTION - Devuelve una lista de Lambda y sus configuraciones
   
def list_lambda_functions(lambda_client):
    functions = lambda_client.list_functions()
    function_list = []
    for f in functions['Functions']:
        function_name = f.get('FunctionName', 'N/A')
        runtime = f.get('Runtime', 'N/A')
        memory_size = f.get('MemorySize', 'N/A')
        function_list.append((function_name, runtime, memory_size))
    print(function_list)
    return function_list

# FUNCTION - Devuelve una lista de instancias StepFunctions y sus configuraciones

def list_step_functions(sf_client):
    state_machines = sf_client.list_state_machines()
    sf_list = []
    for sm in state_machines['stateMachines']:
        name = sm.get('name', 'N/A')
        creation_date = sm.get('creationDate', 'N/A').strftime("%Y-%m-%d %H:%M:%S") if sm.get('creationDate') else 'N/A'
        sf_list.append((name, creation_date))
    return sf_list

# FUNCTION - Devuelve una lista de EventBridge Rules y sus configuraciones

def list_eventbridge_rules(events_client):
    rules = events_client.list_rules()
    eb_list = []
    for rule in rules['Rules']:
        name = rule.get('Name', 'N/A')
        state = rule.get('State', 'N/A')
        eb_list.append((name, state))
    return eb_list

# FUNCTION - Devuelve una lista de S3 Buckets y sus configuraciones

def list_s3_buckets(s3_client):
    buckets = s3_client.list_buckets()
    bucket_list = []
    for bucket in buckets['Buckets']:
        name = bucket.get('Name', 'N/A')
        creation_date = bucket.get('CreationDate', 'N/A').strftime("%Y-%m-%d %H:%M:%S") if bucket.get('CreationDate') else 'N/A'
        bucket_list.append((name, creation_date))
    return bucket_list

# FUNCTION - Devuelve una lista de DMS Tasks y sus configuraciones

def list_dms_tasks(dms_client):
    tasks = dms_client.describe_replication_tasks()
    dms_list = []
    for task in tasks['ReplicationTasks']:
        name = task.get('ReplicationTaskIdentifier', 'N/A')
        status = task.get('Status', 'N/A')
        dms_list.append((name, status))
    return dms_list

# FUNCTION - Devuelve una lista de Jobs de Glue y sus configuraciones

def list_glue_jobs(glue_client):
    jobs = glue_client.get_jobs()
    glue_list = []
    for job in jobs['Jobs']:
        name = job.get('Name', 'N/A')
        role = job.get('Role', 'N/A')
        glue_list.append((name, role))
    return glue_list

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

# FUNCTION Crea un nombre unico con timestamp para evitar que las versiones del historico se pisen con las nuevas y tener un historico

def create_unique_filename(base_filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{base_filename.split('.')[0]}_{timestamp}.csv"

# FUNCTION - Procesa el recurso, lo nombre y lo exporta

def process_resource(client, list_function, filename, headers):
    data = list_function(client)
    unique_filename = create_unique_filename(filename)
    export_to_csv(data, unique_filename, headers)
    return unique_filename.split('_')[0]  # Retorna el nombre del recurso

"""
--------------------------------------------------------------------------------
MAIN FUNCTION
--------------------------------------------------------------------------------
"""

def main():
    # Argumentos con los que se ejecuta el script de Python o que le llega desde el script de bash
    args = sys.argv[1:]

    # Crear clientes de AWS dependiendo del recurso(s)
    lambda_client = boto3.client('lambda')
    sf_client = boto3.client('stepfunctions')
    events_client = boto3.client('events')
    s3_client = boto3.client('s3')
    dms_client = boto3.client('dms')
    glue_client = boto3.client('glue')

    # Aqui podremos asignar el nombre de la exportacion
    all_resources = {
        "-lmb": (lambda_client, list_lambda_functions, 'lambda_functions.csv', ['FunctionName', 'Runtime', 'MemorySize']),
        "-sf": (sf_client, list_step_functions, 'step_functions.csv', ['Name', 'CreationDate']),
        "-eb": (events_client, list_eventbridge_rules, 'eventbridge_rules.csv', ['Name', 'State']),
        "-s3": (s3_client, list_s3_buckets, 's3_buckets.csv', ['Name', 'CreationDate']),
        "-ds": (dms_client, list_dms_tasks, 'dms_tasks.csv', ['TaskIdentifier', 'Status']),
        "-glue": (glue_client, list_glue_jobs, 'glue_jobs.csv', ['Name', 'Role'])
    }

    # Creamos variable de expotacion
    exported_resources = []

    # Si esta el argumento -all agrega todos los recursos independientemente de los demas argumentos
    if "-all" in args or len(args) == 0:
        args = all_resources.keys()

    # Revisa los argumentos
    for arg in args:
        # Comprueba que reside en los posibles recursos y lo procesa
        if arg in all_resources:
            client, list_function, filename, headers = all_resources[arg]
            # Lanza la funcion que procesa el recurso y lo exporta
            resource_name = process_resource(client, list_function, filename, headers)
            exported_resources.append(resource_name)

    print("Recursos exportados:")
    for resource in exported_resources:
        print(resource)

    

"""
--------------------------------------------------------------------------------
Script Execution
--------------------------------------------------------------------------------
"""

if __name__ == '__main__':
    main()

"""
--------------------------------------------------------------------------------
End of Script
--------------------------------------------------------------------------------
"""