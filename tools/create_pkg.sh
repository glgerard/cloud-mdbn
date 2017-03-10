#!/usr/bin/env bash

# Create a Python pakage for the lambda function

if [ $# -ne 2 ]; then
   echo "Usage: $0 <python-file> <aws-key>"
fi

pyfile=$1
key=$2

pkgname=`basename $pyfile .py`
echo "Package name: $pkgname"

amiid=$(aws ec2 describe-images --owners amazon --filters Name=architecture,Values=x86_64 \
Name=hypervisor,Values=xen Name=root-device-type,Values=ebs \
Name=description,Values='Amazon Linux AMI 2016.09.1.* x86_64 HVM GP2' \
Name=virtualization-type,Values=hvm Name=block-device-mapping.volume-type,Values=gp2 \
--query 'Images[0].ImageId' --output text)

instance_id=$(aws ec2 describe-instances --filters Name=image-id,Values=$amiid \
--query 'Reservations[0].Instances[0].InstanceId' --output text)

echo "Found instance $instance_id"

if [ -z $instance_id ]; then
   instance_id=$(aws ec2 run-instances --dry-run --image-id $amiid --key-name mykey \
--instance-type t2.micro --security-groups launch-wizard-4 --instance-initiated-shutdown-behavior terminate \
--query 'Instances[0].InstanceId')
fi

public_ip=$(aws ec2 describe-instances --instance-id $instance_id \
	--query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

cat > zip_pkg.sh <<EOF
if [ ! -d ~/shrink_venv ]; then
   sudo yum install python27-devel python27-pip gcc
   virtualenv ~/shrink_venv
   source ~/shrink_venv/bin/activate
   pip install boto3
else
   source ~/shrink_venv/bin/activate
fi
cd \$VIRTUAL_ENV/lib/python2.7/site-packages
zip -r9 ~/${pkgname}.zip *
cd ~
zip -g ${pkgname}.zip ${pkgname}.py
EOF

scp -i $key $pyfile ec2-user@$public_ip:~/$pyfile
scp -i $key zip_pkg.sh ec2-user@$public_ip:~/zip_pkg.sh
ssh -i $key ec2-user@$public_ip "source ~/zip_pkg.sh"
scp -i $key ec2-user@$public_ip:~/${pkgname}.zip ${pkgname}.zip

rm zip_pkg.sh

echo - "Do you want to stop the instance ${instance_id}? (Y/N)"
read reply
if [ $reply == "Y" ] || [ $reply == "y" ]; then
   aws ec2 terminate-instances --instance-id $instance_id
fi
