#!/bin/bash

cd configuration
pip install -r requirements.txt
env

ip=$(python playbooks/ec2.py | jq -r '."tag_Name_prod-edx-worker"[0] | strings')
ssh="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
manage="cd /edx/app/edxapp/edx-platform && sudo -u www-data /edx/bin/python.edxapp ./manage.py"

echo "$username" > /tmp/username.txt

if [ $addremove=add ]; then
  for x in $(cat /tmp/username.txt); do
    echo "Adding $x"
    $ssh ubuntu@"$ip" "$manage lms cert_whitelist --add $x -c $course_id --settings aws"
  done
elif [ $addremove=remove ]; then
  for x in $(cat /tmp/username.txt); do
    echo "Removing $x"
    $ssh ubuntu@"$ip" "$manage lms cert_whitelist --del $x -c $course_id --settings aws"
  done
fi

rm /tmp/username.txt
