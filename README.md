Splunk Configuration Management and Deployment with Ansible
==============
Bit of the [Splunk 2015 Conference](https://conf.splunk.com/speakers.html#search=Splunk%20Configuration%20Management%20and%20Deployment%20with%20Ansible&) talk and example demo.

## Expectations

This ansible package expectes your servers to be ubuntu base OS. The splunk binaries currently set are *Splunk 6.2* located under
`playbooks/splunk_binaries`

## Installing Ansible

1. `cd /opt`
2. `git clone git://github.com/ansible/ansible.git --recursive`
7. `cd /etc/ansible`
8. `vim hosts #add your hosts`
9. `source /opt/ansible/hacking/env-setup`
10. `ansible-playbook playbooks/common.yml --list-tasks`

## Ansible Structure
![ansible\_structure](images/Ansible.png)

## Running for the First Time

* Ansible is installed, see above
* Make sure you generate your own set of splunk-admin keys for the splunk-admin user. I have included some as an example but **I recommend you to generate your own using:** `ssh-keygen`
* You have root keys copied over to the server you can use `# ssh-copy-id -i ~/.ssh/id_rsa.pub remote-host` or run ansible for the first time with `-k` and it will prompt for the root password and copy the root key over. 
* Inventory is configured under `hosts` file

## Splunk Default Account Information
**username:** admin 
**password:** conf2015

change at `playbooks/splunk\_creds/passwd`

The cert/key pair deployed are in the same folder. Although I highly recommend you generate your own keypairs

## Configure Checkin
1. add checking script at `extra/checkin.sh` on search head as hourly cron job 
2. configure .gitconfig with use and email to use for checking extra/gitconfig.example 
3. generate a key pair on the server `ssh-keygen -t rsa`
4. add public key `cat /root/.ssh/id_rsa.pub` to search header branch  
