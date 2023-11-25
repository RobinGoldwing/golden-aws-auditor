"""
--------------------------------------------------------------------------------
Script Name: AWS Auditor
Author: Ruben Alvarez Mosquera @RobinGoldwing
Created: 25/11/2023
Last Modified: 25/11/2023
Version: 0.1.9 - FINAL REFACTORING Unificar las funciones de consulta de sevicios y externalizar la configuración de servicios y los nombres propios asociados


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

Music, Keep Calm & CODE!! @RobinGoldwing

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

ATTRIBUTES_CONFIG = {
    "lambda": ['FunctionName', 'Runtime', 'Timeout', 'MemorySize', 'FunctionArn', 'Role'],
    "stepfunctions": ['name', 'stateMachineArn', 'creationDate'],
    "eventbridge": ['Name', 'Arn', 'ScheduleExpression', 'State', 'Description'],
    "s3": ['Name', 'CreationDate'],
    "dms": ['ReplicationTaskIdentifier', 'Status', 'ReplicationTaskArn', 'StopReason', 'LastFailureMessage',
            # 'TableMappings'
            ],
    "glue": ['Name', 'Role', 'CreatedOn', 'LastModifiedOn', 'MaxRetries', 'AllocatedCapacity', 'Timeout', 'MaxCapacity', 'WorkerType', 'NumberOfWorkers', 'GlueVersion']
}


# Crear clientes de AWS
clients = {
    "lambda": boto3.client('lambda'),
    "stepfunctions": boto3.client('stepfunctions'),
    "eventbridge": boto3.client('events'),
    "s3": boto3.client('s3'),
    "dms": boto3.client('dms'),
    "glue": boto3.client('glue')
}

# Configuración de recursos
resources_config = {
    "-lmb": ("lambda_functions.csv", "lambda", "list_functions", "Functions"),
    "-sf": ("step_functions.csv", "stepfunctions", "list_state_machines", "stateMachines"),
    "-eb": ("eventbridge_rules.csv", "eventbridge", "list_rules", "Rules"),
    "-s3": ("s3_buckets.csv", "s3", "list_buckets", "Buckets"),
    "-ds": ("dms_tasks.csv", "dms", "describe_replication_tasks", "ReplicationTasks"),
    "-glue": ("glue_jobs.csv", "glue", "get_jobs", "Jobs")
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
def create_unique_filename(base_filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{base_filename.split('.')[0]}_{timestamp}.csv"


"""
--------------------------------------------------------------------------------
MAIN FUNCTION
--------------------------------------------------------------------------------
"""
# FUNCTION - PRINCIPAL
def main():
    args = sys.argv[1:]

    # Si esta el argumento -all agrega todos los recursos independientemente de los demas argumentos
    if "-all" in args or len(args) == 0:
        args = resources_config.keys()

    exported_resources = []

    for arg in args:
        if arg in resources_config:
            # print('>>> for : arg >>>', arg) #### TEST
            filename, service, list_method, response_key = resources_config[arg]
            # print('>>> for : resources >>>',resources_config[arg] ) #### TEST
            client = clients[service]
            # print('>>> for : client >>>',client ) #### TEST
            attributes = ATTRIBUTES_CONFIG[service]
            # print('>>> for : Attrb. >>>',attributes ) #### TEST
            data = list_aws_resources(client, list_method, response_key, attributes)
            unique_filename = create_unique_filename(filename)
            export_to_csv(data, unique_filename, attributes)
            exported_resources.append((unique_filename.split('_')[0],unique_filename))

    print("Recursos exportados:")
    for resource in exported_resources:
        print(resource[0]," >>> File >>> ", resource[1])


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
v0.1.7 - HOTFIX - Ampliacion de la consulta de atributos y consultas
v0.1.7a - TEST BRACH
v0.1.8 - REFACTORING Unificar las funciones de consulta de sevicios y externalizar la configuración de servicios y los nombres propios asociados

FUTURE FEATUREs:
==========================
- HOTFIX > Arreglar DMSTask ya que el atributo TableMappings viene en formato JSON
    - De momento queda INACTIVO
    - Se puede codificar en BASE64, pero eso gestionaría más eficientemente la longitud de archivo pero influiría en su legibilidad
    - Se puede sustitur y codificar los saltos de linea permitiendo una lectura directa del CSV, pero gestionará peor el tamaño el los datos del atributo/columna
    - Agregar posibilidad de que agregue los subdiccionarios como columnas nuevas (EJEMPLO DMSTasks>ReplicationTaskStats)
- Posibilidad de externalizar la configuracion a traves de un archivo config, para no tocar el codigo
- Posibilidad de comprimir los archivos en ZIP
- Subir el programa a un repositorio
        - crear script de bash adecuado generado por un excel para únicamente pegarlo en la consola y lanzarlo
        - baje el repositorio y active el comando asociado a la elección de argumentos


Music, Keep Calm & CODE!! @RobinGoldwing

--------------------------------------------------------------------------------
"""