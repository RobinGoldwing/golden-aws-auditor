"""
--------------------------------------------------------------------------------
Script Name: AWS Auditor
Author: Ruben Alvarez Mosquera
Created: 25/11/2023
Last Modified: 25/11/2023
Version: 0.1.7c - TEST BRACH

Description:
    Este script automatiza la exportacion de recursos AWS a archivos CSV.
    Soporta multiples servicios como Lambda, Step Functions, EventBridge, etc.

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
    Copyright MIT 2023 by Ruben Alvarez Mosquera.
    Se concede permiso, de forma gratuita, a cualquier persona que obtenga una copia
    de este software y de los archivos de documentacion asociados (el "Software"), para
    utilizar el Software sin restriccion, incluyendo sin limitacion los derechos
    de usar, copiar, modificar, fusionar, publicar, distribuir, sublicenciar, y/o vender
    copias del Software, y para permitir a las personas a las que se les proporcione el
    Software hacer lo mismo, siempre que se incluya el siguiente aviso de derechos de autor
    y este aviso de permiso en todas las copias o partes sustanciales del Software.

Disclaimer:
    Este script se proporciona "tal cual", sin garantia de ningun tipo, expresa o
    implicita. El uso de este script es bajo tu propio riesgo.

Music, Keep Calm & CODE!!

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
-------------------------------------------------------------------------------
SERVICES & ATTR. CONFIGURATION
-------------------------------------------------------------------------------
"""
# MODIFICAR estas listas para incluir o eliminar attributos a exportar en CSV a
#  traves de comentar o añadirlos
###############################################################################

# LAMBDA
lambda_attr = [ # Configuracion de atributos de funciones LAMBDA 
    'FunctionName',
    'Runtime', 
    'Timeout',
    'MemorySize',
    'FunctionArn',
    'Role',
]
lambda_config = { # Configuracion del servicio de AWS
    "client": boto3.client('lambda'),
    "list_method": "list_functions",
    "response_key": "Functions",
    "attributes": lambda_attr
}

# STEP FUNCTION CONFIG ########################################################

sf_attr = [ # Configuracion de atributos de StepFunctions
    'name',
    'stateMachineArn',
    'creationDate',
]
sf_config = { # Configuracion del servicio de AWS
    "client": boto3.client('stepfunctions'),
    "list_method": "list_state_machines",
    "response_key": "stateMachines",
    "attributes": sf_attr
}

# EVENT BRIDGE CONFIG #########################################################

eb_attr = [ # Configuracion de atributos de EventBridge
    'Name',
    'Arn',
    'ScheduleExpression',
    'State',
    'Description',
]
eb_config = { # Configuracion del servicio de AWS
    "client": boto3.client('events'),
    "list_method": "list_rules",
    "response_key": "Rules",
    "attributes": eb_attr
}

# S3 BUCKETS CONFIG ###########################################################

bucket_attr = [  # Configuracion de atributos de Buckets de s3
    'Name',
    'CreationDate',
]

bucket_config = { # Configuracion del servicio de AWS
    "client": boto3.client('s3'),
    "list_method": "list_buckets",
    "response_key": "Buckets",
    "attributes": bucket_attr
}

# DMSTasks CONFIG ###########################################################

dms_attr = [ # Configuracion de atributos de DMS Tasks
    'ReplicationTaskIdentifier',
    'Status',
    'ReplicationTaskArn',
    'StopReason'
    'LastFailureMessage',
    #'TableMappings',
]   
# - HOTFIX > Arreglar DMSTask ya que el atributo TableMappings viene en formato JSON
#     - De momento queda INACTIVO
#     - Se puede codificar en BASE64, pero eso gestionaría más eficientemente la longitud de archivo pero influiría en su legibilidad
#     - Se puede sustitur y codificar los saltos de linea permitiendo una lectura directa del CSV, pero gestionará peor el tamaño el los datos del atributo/columna
#     - Agregar posibilidad de que agregue los subdiccionarios como columnas nuevas (EJEMPLO DMSTasks>ReplicationTaskStats)

dms_config = {
    "client": boto3.client('dms'),
    "list_method": "describe_replication_tasks",
    "response_key": "ReplicationTasks",
    "attributes": dms_attr
}

# GLUE JOBS CONFIG ###########################################################

glue_attr = [ # Configuracion de atributos de Jobs de Glue
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
glue_config = { # Configuracion del servicio de AWS
    "client": boto3.client('glue'),
    "list_method": "get_jobs",
    "response_key": "Jobs",
    "attributes": glue_attr
}


"""
--------------------------------------------------------------------------------
FUNCTIONS DEFINITION
--------------------------------------------------------------------------------
"""
############################################################

# FUNCIÓN GENÉRICA DE LISTADO
def list_aws_resources(client, list_method, response_key, attributes):
    try:
        response = getattr(client, list_method)()
        return [
            [resource.get(attr, 'N/A') for attr in attributes] for resource in response[response_key]
        ]
    except Exception as e:
        print(f"Error al listar recursos: {e}")
        return []
    
############################################################

# FUNCTION - Devuelve una lista de Lambda y sus configuraciones

def list_lambda_functions(lambda_client):

    functions = lambda_client.list_functions()
    function_list = [
        [f.get(attr, 'N/A') for attr in lambda_attr] for f in functions['Functions']
    ]
    return function_list

# FUNCTION - Devuelve una lista de EventBridge Rules y sus configuraciones

def list_step_functions(sf_client):
    state_machines = sf_client.list_state_machines()
    sf_list = [
        [sf.get(attr, 'N/A') for attr in sf_attr] for sf in state_machines['stateMachines']
    ]
    return sf_list

# FUNCTION - Devuelve una lista de EventBridge Rules y sus configuraciones

def list_eventbridge_rules(events_client):
    rules = events_client.list_rules()
    eb_list = [
        [eb.get(attr, 'N/A') for attr in eb_attr] for eb in rules['Rules']
    ]
    return eb_list

# FUNCTION - Devuelve una lista de S3 Buckets y sus configuraciones


def list_s3_buckets(s3_client):
    buckets = s3_client.list_buckets()
    bucket_list = [
        [bu.get(attr, 'N/A') for attr in bucket_attr] for bu in buckets['Buckets']
    ]
    return bucket_list

# FUNCTION - Devuelve una lista de DMS Tasks y sus configuraciones


def list_dms_tasks(dms_client):
    tasks = dms_client.describe_replication_tasks()
    dms_list = [
        [dms.get(attr, 'N/A') for attr in dms_attr] for dms in tasks['ReplicationTasks']
    ]
    return dms_list

# FUNCTION - Devuelve una lista de Jobs de Glue y sus configuraciones


def list_glue_jobs(glue_client):
    jobs = glue_client.get_jobs()
    glue_list = [
        [glu.get(attr, 'N/A') for attr in glue_attr] for glu in jobs['Jobs']
    ]
    return glue_list

"""
-------------------------------------------------------------------------------
ARGS. CONFIGURATION & GENERAL EXPORT NAMING
-------------------------------------------------------------------------------
"""

# Crear clientes de AWS dependiendo del recurso(s)
lambda_client = boto3.client('lambda')
sf_client = boto3.client('stepfunctions')
events_client = boto3.client('events')
s3_client = boto3.client('s3')
dms_client = boto3.client('dms')
glue_client = boto3.client('glue')

# Aqui podremos asignar el argumento, y nombre de la exportacion
all_resources = {
    "-lmb": (lambda_client, list_lambda_functions, 'lambda_functions.csv', lambda_attr),
    "-sf": (sf_client, list_step_functions, 'step_functions.csv', sf_attr),
    "-eb": (events_client, list_eventbridge_rules, 'eventbridge_rules.csv', eb_attr),
    "-s3": (s3_client, list_s3_buckets, 's3_buckets.csv', bucket_attr),
    "-ds": (dms_client, list_dms_tasks, 'dms_tasks.csv', dms_attr),
    "-glue": (glue_client, list_glue_jobs, 'glue_jobs.csv', glue_attr)
}


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

    # Creamos variable de expotacion
    exported_resources = []

    # Si esta el argumento -all agrega todos los recursos independientemente de los demas argumentos
    if "-all" in args or len(args) == 0:
        args = all_resources.keys()

    # Revisa los argumentos
    for arg in args:
        # Comprueba que reside en los posibles recursos y lo procesa
        if arg in all_resources:
            client, list_function, filename , headers= all_resources[arg]
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





"""
--------------------------------------------------------------------------------
OLD VERSIONs:
=============
v0.1.0 - Simple consulta de lista de lambdas y exportación a JSON
v0.1.1 - Feature - exporta también Buckets S3
v0.1.2 - Feature - exporta a CSV
v0.1.3 - Feature - agrega más tipos de recursos
v0.1.4 - Feature - agrega funcionalidad de argumentos
v0.1.5 - Ampliacion de la consulta de Lambdas
v0.1.6 - HOTFIX - Ampliacion de la consulta de atributos y consultas

POSIBLES FEATURES FUTURAS:
==========================
- Agregar posibilidad de que agregue los subdiccionarios como columnas nuevas (EJEMPLO DMSTasks>ReplicationTaskStats)
- Simplificar las funciones en una sola genérica y las configuraciones de attributos estén separados para facilitar la agregación de más o la reducción con un simple comentario



Music, Keep Calm & CODE!!

--------------------------------------------------------------------------------
"""