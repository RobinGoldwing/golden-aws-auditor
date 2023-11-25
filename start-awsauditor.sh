#!/bin/bash

# Verificar si se ha proporcionado un argumento
if [ "$#" -ne 1 ]; then
    echo "Uso: $0 <script_python.py>"
    exit 1
fi

# Asignar el argumento a una variable
script_python="$1"

# Verificar si el archivo del script existe
if [ ! -f "$script_python" ]; then
    echo "Error: El archivo '$script_python' no existe."
    exit 1
fi

# Ejecutar el script de Python
python3 "$script_python"