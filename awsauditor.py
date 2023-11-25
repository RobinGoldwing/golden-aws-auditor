"""
--------------------------------------------------------------------------------
Script Name: AWS Auditor
Author: Ruben Alvarez Mosquera
Created: 23/11/2023
Last Modified: 23/11/2023
Version: 0.1.1  - Feature - exporta también Buckets S3

Description:
    Este script automatiza la exportación de recursos AWS a archivos CSV.
    Soporta múltiples servicios como Lambda, Step Functions, EventBridge, etc.

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


import boto3
import csv

def export_to_csv(data, filename, headers):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)

def list_lambda_functions(lambda_client):
    functions = lambda_client.list_functions()
    print(functions)
    return # [(f['FunctionName'], f['Runtime'], f['MemorySize']) for f in functions['Functions']]

# def list_s3_buckets(s3_client):
#    response = s3_client.list_buckets()
#    return [(bucket['Name'],) for bucket in response['Buckets']]

def main():
    # Crear clientes para cada servicio
    lambda_client = boto3.client('lambda')
    # s3_client = boto3.client('s3')

    # Listar funciones de Lambda y buckets de S3
    lambda_functions = list_lambda_functions(lambda_client)
    # s3_buckets = list_s3_buckets(s3_client)

    # Exportar a CSV
    # export_to_csv(lambda_functions, 'lambda_functions.csv', ['FunctionName', 'Runtime', 'MemorySize'])
    # export_to_csv(s3_buckets, 's3_buckets.csv', ['BucketName'])

if __name__ == '__main__':
    main()
