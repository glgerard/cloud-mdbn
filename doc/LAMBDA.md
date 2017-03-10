## AWS Lambda deployment

Lambda function deployment package was created as in [Deployment Package](http://docs.aws.amazon.com/lambda/latest/dg/with-s3-example-deployment-pkg.html)
starting from `src/CreateEC2Instance.py`.
This is all automated in the script `tools/create_pkg.sh`.

The exec role is defined as in [Execution Role](http://docs.aws.amazon.com/lambda/latest/dg/with-s3-example-create-iam-role.html)
however the extra Custom Policy `PassRole` has been defined and attached for the
lambda function to be able to pass the `aws-mdbn-ec2` role to the new
EC2 instance.

`PassRole` is defined as

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "Stmt1489132640000",
                "Effect": "Allow",
                "Action": [
                    "iam:PassRole"
                ],
                "Resource": [
                    "*"
                ]
            }
        ]
    }

The Lambda function is created by invoking `tools/create_lambda.sh` .

