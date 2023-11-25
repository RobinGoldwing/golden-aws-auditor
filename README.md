# AWS Auditor

## Overview
This Python script is your go-to utility for a quick, clean, and organized audit of your AWS resources.

This project wants to solve the problem when an agent wants to audit all AWS resources (many of them without TAGs) and wants to avoid the tedious task of cherry picking them through the administration center like "Resource Groups & Tags Editor" or so.

Another issue with this is the fact that most of the time we cannot use AWS CLI on our machines (VPN, account permissions, etc), neither Clou9 environments, and we can only use a limited CloudShell terminal to connect.

So I do these steps in two scripts:
- Bash script: To copy/paste directly over a terminal, with run the awsCLI consults and exports.
- A Python script to transform/export a JSON response to a csv format.

## Features
- Easy extraction of resource details from AWS services like Lambda, S3, Step Functions, EventBridge, DMS, and Glue.
- Exports data into neatly formatted CSV files.
- Timestamp-based unique file naming system to preserve historical data.
- Modular design for easy addition of new AWS services.
- Error handling: Consider adding error handling to catch and handle possible exceptions, such as connection errors or insufficient permissions.

## How to Use
Simply run the bash or Python script with the desired service flags, and voilà! You get all the information you need, conveniently packed into CSV files.

Bash:
```
bash start-awsauditor.sh [options]
```

Python:
```
Python3 asauditor.py [options]
```

### Options
- `-all`: Exports all resources.
- `-lmb`: Exports Lambda functions.
- `-sf`: Exports Step Functions.
- `-eb`: Exports EventBridge rules.
- `-s3`: Exports S3 buckets.
- `-ds`: Exports DMS Tasks.
- `-glue`: Exports Glue Jobs.

## Requirements
AWS CLI and Boto3 are configured: Ensure that AWS CLI is installed and configured with the correct credentials, and that Boto3 is installed in your Python environment.
- Python 3
- Boto3
- CloudShell or AWS CLI (configured with appropriate permissions)

## Configuration
IAM Permissions: Your AWS user must have the necessary permissions to perform the actions the script intends (such as listing Lambda functions, EventBridge rules, etc.).
https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html
https://docs.aws.amazon.com/cli/latest/reference/configure/

```
aws configure [--profile profile-name]
```

## Installation
Clone the repository and install the dependencies:

```
git clone https://github.com/RobinGoldwing/golden-aws-auditor
cd golden-aws-auditor
pip install boto3
```

## Contribution
Got an idea or a bugfix? Contributions are welcome! Just fork the repo, make your changes, and submit a pull request.

## License
MIT License - feel free to use and modify as you like.

## Disclaimer
This script is provided "as is", with no warranty. Use at your own risk.

## Credits
Created with :heart: by RobinGoldwing.

---

*"Music, Keep Calm & CODE!!"* - RobinGoldwing

## OLD VERSIONS:
=============
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

## FUTURE FEATUREs:
================
- Possibility to externalize the configuration through a config file, so as not to touch the code.
- HOTFIX > Fix DMSTask since the TableMappings attribute comes in JSON format.
    - For the moment it is INACTIVE
    - It is possible to encode in BASE64, but this would manage file length more efficiently but would affect readability.
    - Line breaks can be replaced and encoded allowing a direct reading of the CSV, but it will handle the size of the attribute/column data worse.
    - Add the possibility to add the sub-divisions as new columns (EXAMPLE DMSTasks>ReplicationTaskStats)