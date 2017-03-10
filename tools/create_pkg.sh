#!/usr/bin/env bash

NETCAT=nc

function check_ssh {
    $NETCAT -z -G 5 $1 22 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "connected"
    fi
}

# Create a Python pakage for the lambda function

if [ $# -ne 2 ]; then
   echo "Usage: $0 <python-file> <aws-key>"
   exit -1
fi

pyfile=$1
key=$2

pkgname=`basename $pyfile .py`
echo "Package name: $pkgname"

# Get the AMI image id

amiid=$(aws ec2 describe-images --owners amazon --filters Name=architecture,Values=x86_64 \
Name=hypervisor,Values=xen Name=root-device-type,Values=ebs \
Name=description,Values='Amazon Linux AMI 2016.09.1.* x86_64 HVM GP2' \
Name=virtualization-type,Values=hvm Name=block-device-mapping.volume-type,Values=gp2 \
--query 'Images[0].ImageId' --output text)

# Check if an EC2 instance with the AMI id is already running otherwise create one

instance_id=$(aws ec2 describe-instances --filters Name=image-id,Values=$amiid \
Name=instance-state-code,Values=16 --query 'Reservations[0].Instances[0].InstanceId' --output text)

if [ "$instance_id" != "None" ]; then
   echo "Found instance with ID $instance_id"
else
   echo "Create a new AMI instance"
   instance_id=$(aws ec2 run-instances --image-id $amiid --key-name mykey \
--instance-type t2.micro --security-groups launch-wizard-4 --instance-initiated-shutdown-behavior terminate \
--query 'Instances[0].InstanceId' --output text)
    echo "New instance created. ID: $instance_id"
fi

echo "Check the EC2 instance is available..."

while [[ `aws ec2 describe-instances --instance-id $instance_id --query 'Reservations[0].Instances[0].State.Code' \
          --output text` -ne 16 ]]; do
  echo -n "*"
  sleep 10
done
echo""

# Create the package

cat > zip_pkg.sh <<EOF
if [ ! -d ~/shrink_venv ]; then
   sudo yum install -y python27-devel python27-pip gcc
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

# Get the instance public IP

public_ip=$(aws ec2 describe-instances --instance-id $instance_id \
	--query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

# Wait for the SSH port to be available

echo "Wait for the IP network to come up"
while [[ `check_ssh $public_ip` != "connected" ]]; do
    echo -n "."
    sleep 5
done

scp -i $key $pyfile ec2-user@$public_ip:~/$pyfile
scp -i $key zip_pkg.sh ec2-user@$public_ip:~/zip_pkg.sh
ssh -i $key ec2-user@$public_ip "source ~/zip_pkg.sh"
scp -i $key ec2-user@$public_ip:~/${pkgname}.zip ${pkgname}.zip

# Cleanup

rm zip_pkg.sh

read -p "Do you want to stop the instance ${instance_id} (yes/no)? " reply
if [ $reply == "yes" ] || [ $reply == "YES" ]; then
   aws ec2 terminate-instances --instance-id $instance_id
fi
