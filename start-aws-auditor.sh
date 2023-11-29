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
#     bash start-aws-auditor.sh [options]
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
        echo "Dependency '$dependency' is not installed."
        if [[ $dependency == "python3" ]]
        then
            echo "Please install Python 3."
            echo "Suggested command: apt-get install python3 (or equivalent in your system)"
        elif [[ $dependency == "git" ]]
        then
            echo "Please install Git."
            echo "Suggested command: apt-get install git (or equivalent in your system)"
        fi
        exit 1
    else
        echo "Dependency '$dependency' is correctly installed."
    fi
}

# --------------------------------------------------------------------------------
# MAIN CODE
# --------------------------------------------------------------------------------
echo
echo "========================="
echo "  Bash Script Execution  "
echo "========================="
echo

check_dependency "python3"
check_dependency "git"

if ! python3 -c "import boto3" &> /dev/null; then
    echo "boto3 is not installed."
    echo "You can install it with the following command: < pip install boto3 >"
    exit 1
else
    echo "Dependency 'boto3' is correctly installed."
fi

if [[ -f "aws-auditor.py" ]]; then

    python3 aws-auditor.py "$@"

else

    if [ ! -d "golden-aws-auditor" ]; then
        git clone https://github.com/RobinGoldwing/golden-aws-auditor
    fi

    cd golden-aws-auditor

    python3 aws-auditor.py "$@"
fi

echo
echo "================="
echo " End Bash Script "
echo "================="
echo