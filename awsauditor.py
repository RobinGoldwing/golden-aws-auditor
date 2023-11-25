"""
-------------------------------------------------------------------------------
Script Name: AWS Auditor
Author: Ruben Alvarez Mosquera @RobinGoldwing
Created: 25/11/2023
Last Modified: 25/11/2023
Version: 0.1.8 - REFACTORING Unificar las funciones de consulta de sevicios y externalizar la configuración de servicios y los nombres propios asociados


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

-------------------------------------------------------------------------------
"""

"""
-------------------------------------------------------------------------------
SCRIPT HEADER
-------------------------------------------------------------------------------
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

# STEP FUNCTION CONFIG #######################################

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

# EVENT BRIDGE CONFIG #######################################

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

# S3 BUCKETS CONFIG #######################################

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

# DMSTasks CONFIG #######################################

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

# GLUE JOBS CONFIG #######################################

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
-------------------------------------------------------------------------------
ARGS. CONFIGURATION & GENERAL EXPORT NAMING
-------------------------------------------------------------------------------
"""

# Aqui podremos asignar el argumento, y nombre de la exportacion
all_resources = {
    "-lmb":     ('lambda_functions.csv', lambda_config),
    "-sf":      ('step_functions.csv', sf_config),
    "-eb":      ('eventbridge_rules.csv', eb_config),
    "-s3":      ('s3_buckets.csv', bucket_config),
    "-ds":      ('dms_tasks.csv', dms_config),
    "-glue":    ('glue_jobs.csv', glue_config)
}


"""
-------------------------------------------------------------------------------
HELPER FUNCTIONS
-------------------------------------------------------------------------------
"""
# FUNCTION Crea la lista de recursos

def list_aws_resources(client, resource_attr, list_method, response_key):
    try:
        response = getattr(client, list_method)() # Consulta las Lambda del RESPONSE
        resource_list = [   # Formacion de la lista de funciones Lambda
            [res.get(attr, 'N/A') for attr in resource_attr] for res in response[response_key]
        ]
    # Lanza error si detecta algun servicio inexistente(devolviendo la lista vacía)
    except AttributeError as e: 
        print(f"Método {list_method} no encontrado en el cliente AWS.")
        print("-----------------------------------------------------")
        print(f"Error : {e}")
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        resource_list = []
    return resource_list

# FUNCTION Crea un nombre unico con timestamp para evitar que las versiones del historico se pisen con las nuevas y tener un historico

def create_name(base_filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{base_filename.split('.')[0]}_{timestamp}.csv"

# FUNCTION - Procesa el recurso, lo nombre y lo exporta

def process_resource(client, list_function, filename, headers):
    data = list_function(client)
    timestamp_filename = create_name(filename)
    export_to_csv(data, timestamp_filename, headers)
    return timestamp_filename.split('_')[0]  # Retorna el nombre del recurso

# FUNCTION - Exporta en formato CSV

def export_to_csv(data, filename, headers):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)

"""
-------------------------------------------------------------------------------
MAIN FUNCTION
-------------------------------------------------------------------------------
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
        if arg in all_resources:
            filename, config = all_resources[arg]
            data = list_aws_resources(config["client"], config["attributes"], config["list_method"], config["response_key"])
            unique_filename = create_name(filename)
            export_to_csv(data, unique_filename, config["attributes"])
            exported_resources.append(unique_filename.split('_')[0])



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
-------------------------------------------------------------------------------
Script Execution
-------------------------------------------------------------------------------
"""

if __name__ == '__main__':
    main()

"""
-------------------------------------------------------------------------------
End of Script
-------------------------------------------------------------------------------
"""





"""
-------------------------------------------------------------------------------
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


FUTURE FEATUREs:
==========================
- REFACTORING > Cambiar a modelo da CLASES para los servicios
- HOTFIX > Arreglar DMSTask ya que el atributo TableMappings viene en formato JSON
    - De momento queda INACTIVO
    - Se puede codificar en BASE64, pero eso gestionaría más eficientemente la longitud de archivo pero influiría en su legibilidad
    - Se puede sustitur y codificar los saltos de linea permitiendo una lectura directa del CSV, pero gestionará peor el tamaño el los datos del atributo/columna
    - Agregar posibilidad de que agregue los subdiccionarios como columnas nuevas (EJEMPLO DMSTasks>ReplicationTaskStats)
- Unificar la función de servicios con una parte de configuración de servicios de consulta por AWS
- Posibilidad de externalizar la configuracion a traves de un archivo config, para no tocar el codigo
- Posibilidad de comprimir los archivos en ZIP
- Subir el programa a un repositorio
        - crear script de bash adecuado generado por un excel para únicamente pegarlo en la consola y lanzarlo
        - baje el repositorio y active el comando asociado a la elección de argumentos


Music, Keep Calm & CODE!! @RobinGoldwing

-------------------------------------------------------------------------------
"""