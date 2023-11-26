#!/bin/bash


# --------------------------------------------------------------------------------
# Script Name: AWS Auditor
# Author: Ruben Alvarez Mosquera //  GitHub@RobinGoldwing
# Created: 25/11/2023
# Last Modified: 25/11/2023
#
# Version: 0.2 
#   - Check dependencies
#   - Clone repository
#   - Execute Python Script
#
# Description:
#     This script launches the Python script witch automates the export of AWS resources to CSV files.
#     It supports multiple services like Lambda, Step Functions, EventBridge, etc.
#
# Usage:
#     bash start-awsauditor.sh [options]
#
# Options:
#     -all  : Exports all resources
#     -lmb  : Exports Lambda functions
#     -sf   : Exports Step Functions
#     -eb   : Exports EventBridge rules
#     -s3   : Exports S3 buckets
#     -ds   : Exports DMS Tasks
#     -glue : Exports Glue Jobs
#
# License:
#     Copyright MIT 2023 by Ruben Alvarez Mosquera // GitHub@RobinGoldwing
#     Permission is hereby granted, free of charge, to any person obtaining a copy
#     of this software and associated documentation files (the "Software"), to deal
#     in the Software without restriction, including without limitation the rights
#     to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#     copies of the Software, and to permit persons to whom the Software is
#     furnished to do so, subject to the following conditions:
#
#     The above copyright notice and this permission notice shall be included in all
#     copies or substantial portions of the Software.
#
# Disclaimer:
#     This script is provided "as is", without warranty of any kind, express or
#     implied. Use at your own risk.
#
# Music, Keep Calm & CODE!! GitHub@RobinGoldwing
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
# FUNCTION
# --------------------------------------------------------------------------------

# Funcion para verificar dependencias
check_dependency() {
    dependency=$1
    if ! command -v $dependency &> /dev/null
    then
        echo "La dependencia '$dependency' no está instalada."
        if [[ $dependency == "python3" ]]
        then
            echo "Por favor, instale Python 3."
            echo "Comando sugerido: apt-get install python3 (o equivalente en su sistema)"
        elif [[ $dependency == "git" ]]
        then
            echo "Por favor, instale Git."
            echo "Comando sugerido: apt-get install git (o equivalente en su sistema)"
        fi
        exit 1
    else
        echo "La dependencia '$dependency' está instalada correctamente."
    fi
}

# --------------------------------------------------------------------------------
# MAIN CODE
# --------------------------------------------------------------------------------

# Verificar Python3 y Git
check_dependency "python3"
check_dependency "git"

# Verificar boto3
if ! python3 -c "import boto3" &> /dev/null; then
    echo "boto3 no está instalado."
    echo "Puede hacerlo con el siguiente comando: < pip install boto3 >"
    exit 1
else
    echo "La dependencia 'boto3' está instalada correctamente."
fi

# Verificar si awsauditor.py esta en el directorio actual
if [[ -f "awsauditor.py" ]]; then
    # Ejecutar el script de Python directamente
    python3 awsauditor.py "$@"

else
    # Clonar el repositorio si aun no esta clonado
    if [ ! -d "golden-aws-auditor" ]; then
        git clone https://github.com/RobinGoldwing/golden-aws-auditor
    fi

    # Cambiar al directorio del repositorio
    cd golden-aws-auditor

    # Ejecutar el script de Python con los argumentos pasados al script de Bash
    python3 awsauditor.py "$@"
fi
