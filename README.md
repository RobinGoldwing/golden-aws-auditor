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
bash start-aws-auditor.sh [options]
```

Python:
```
python3 aws-auditor.py [options]
```

### Options
- `-all`: Exports all resources.

- `-lb`: Exports Lambda functions.
- `-sf`: Exports Step Functions.
- `-eb`: Exports EventBridge rules.
- `-s3`: Exports S3 buckets.
- `-ds`: Exports DMS Tasks.
- `-gl`: Exports Glue Jobs.

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