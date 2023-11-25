# AWS Auditor

This project wants to solve the problem when an agent wants to audit all AWS resources (many of them without TAGs) and wants to avoid the tedious task of cherry picking them through the administration center like "Resource Groups & Tags Editor" or so.

Another issue with this is the fact that most of the time we cannot use AWS CLI on our machines (VPN, account permissions, etc). 

So I do these steps in two scripts:
- Bash script: To run the awsCLI consults and exports.
- A Python script to transform/export a JSON response to a csv format.

The script should work correctly if the following requirements are met:

AWS CLI and Boto3 are configured: Ensure that AWS CLI is installed and configured with the correct credentials, and that Boto3 is installed in your Python environment.

IAM Permissions: Your AWS user must have the necessary permissions to perform the actions the script intends (such as listing Lambda functions, EventBridge rules, etc.).

Error handling: Consider adding error handling to catch and handle possible exceptions, such as connection errors or insufficient permissions.

Otherwise, the script seems well designed for its purpose of listing AWS resources and exporting them to CSV files. The code structure is clear, and the comments and documentation are adequate and helpful.