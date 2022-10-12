# reproducer_bootstrap
## KNOWN LIMITATIONS

Currently, only "one node" jobs are working. Setup with multiple
controller and compute fail as the network setup (ovn vxlan) doesn't
work for "some reason".

SSH key handling is messy at best as we need to populate the
reproducer node with real key to get access to rdo and opendev
repos. The reproducer is expected to be local to the laptop not a vm
in a shared environment.

Seting up the reproducer on PSI faces rate limit image download from
gitlab. We present a way to overcome this in this doc, but again this
point to the reproducer being something that run from a laptop not
from a shared plateforme.

A clearer workflow description is needed to detail how to trigger jobs
against review and how to create job.

## DESCRIPTION

Bootstrap a bastion host with all needed requirements to
have the reproducer setup works properly.

It will create a bastion hosts that will be properly configured to
received a podman based deployment of the quickstart reproducer setup
on CentOS 8.

Then you will be able to log in and run the job testing part of the
quickstart reproducer.

The point of entry is the `get_me_da_env` script.

## REQUIREMENTS

You need a pair of ssh keys that are able to log in in your account on
review.opendev.org and on https://review.rdoproject.org/r.

Create a new ssh key and push it to <gerrit system url>/settings/#SSHKeys.

This is what the instance *private*. There is no way to setup the
reproducer without giving away this ssh key. And those ssh key have
read/write access to your account.

Creating a new key mitigate this, but still.

## USAGE

    python -mvenv venv
    pip install -r requirements.txt
    . ./venv/bin/activate
    openstack --os-cloud openstack user show <CLOUD_USER_NAME> -f value -c domain_id
    # 52cf1b5bc006389db89e2b0ebfb55f53
    ssh-keygen -f reproducer -C reproducer@cloud
    ./get_me_da_env -h
    ./get_me_da_env \
        -p chem-reproducer \
        -u chem -r sathlan \
        -a AppCredPassword \
        -k ~/.ssh/created_ssh_key \
        -b ~/.ssh/created_ssh_key.pub \
        -m ./reproducer.pub \
        -n chem-in-the-cloud \
        -i 52cf1b5bc006389db89e2b0ebfb55f53
        
When it's done you should have bastion host with all the services
configured.

    ssh -i reproducer -oUserKnownHostsFile=/dev/null -oStrictHostKeyChecking=no centos@<public_ip>
    $ sudo podman ps
    CONTAINER ID  IMAGE                                             COMMAND               CREATED     STATUS         PORTS                                     NAMES
    6540125abec7  docker.io/library/httpd:2.4.39-alpine             httpd-foreground      4 days ago  Up 4 days ago  0.0.0.0:8000->80/tcp, 0.0.0.0:79->79/tcp  logs
    e44f3f322d39  docker.io/library/zookeeper:3.4.14                zkServer.sh start...  4 days ago  Up 4 days ago  0.0.0.0:8000->80/tcp, 0.0.0.0:79->79/tcp  zk
    524abfd85a28  docker.io/rdoci/zuul-merger:stable                sh -c  cd /usr/sr...  4 days ago  Up 4 days ago  0.0.0.0:8000->80/tcp, 0.0.0.0:79->79/tcp  merger3
    48e7461896a5  docker.io/rdoci/zuul-merger:stable                sh -c  cd /usr/sr...  4 days ago  Up 4 days ago  0.0.0.0:8000->80/tcp, 0.0.0.0:79->79/tcp  merger2
    5272475b59ae  docker.io/rdoci/zuul-merger:stable                sh -c  cd /usr/sr...  4 days ago  Up 4 days ago  0.0.0.0:8000->80/tcp, 0.0.0.0:79->79/tcp  merger1
    15f77c09d19c  docker.io/rdoci/zuul-merger:stable                sh -c  cd /usr/sr...  4 days ago  Up 4 days ago  0.0.0.0:8000->80/tcp, 0.0.0.0:79->79/tcp  merger0
    c6a8b6a9971a  docker.io/rdoci/nodepool-launcher:stable          nodepool-launcher...  4 days ago  Up 4 days ago  0.0.0.0:8000->80/tcp, 0.0.0.0:79->79/tcp  launcher
    597569756cb8  docker.io/rdoci/zuul-fingergw:stable              zuul-fingergw -d      4 days ago  Up 4 days ago  0.0.0.0:8000->80/tcp, 0.0.0.0:79->79/tcp  fingergw
    edcdd424f05c  docker.io/rdoci/zuul-executor:stable              sh -c cd /usr/src...  4 days ago  Up 4 days ago  0.0.0.0:8000->80/tcp, 0.0.0.0:79->79/tcp  executor
    b789f8288b9b  docker.io/rdoci/zuul-web:stable                   sh -c pip install...  4 days ago  Up 4 days ago  0.0.0.0:8000->80/tcp, 0.0.0.0:79->79/tcp  web
    3b34aa16653f  docker.io/rdoci/zuul-scheduler:stable             sh -c pip install...  4 days ago  Up 4 days ago  0.0.0.0:8000->80/tcp, 0.0.0.0:79->79/tcp  scheduler
    c840efee3ebc  docker.io/library/mariadb:10.3.14-bionic          mysqld                4 days ago  Up 4 days ago  0.0.0.0:8000->80/tcp, 0.0.0.0:79->79/tcp  mysql
    f60c52f58024  docker.io/gerritcodereview/gerrit:2.16.7-centos7  /bin/sh -c git co...  4 days ago  Up 4 days ago  0.0.0.0:8000->80/tcp, 0.0.0.0:79->79/tcp  gerrit
    
Now you can create a job associated with your cloud using the
=job_example.yaml= create on the bastion host and the =create_job.py=
helper script.

Say you want to trigger a =tripleo-ci-centos-8-content-provider=
job for this review =https://review.opendev.org/757845=

    create_job.py -r 757845 -t ./job_template.yaml -j tripleo-ci-centos-8-content-provider > reproducer.yaml
    
    rsync -e 'ssh -oUserKnownHostsFile=/dev/null -oStrictHostKeyChecking=no -i reproducer' reproducer.yaml centos@<public_ip>:

    ansible-playbook -v --skip-tags start,install ./reproducer.yaml
    
    Using /etc/ansible/ansible.cfg as config file
    [WARNING]: provided hosts list is empty, only localhost is available. Note that the implicit localhost does not match 'all'
    
    PLAY [Set up reproducer] *******************************************************************************************************************************************************************************************************************************************************************
    
    ....
    
    
Now you can point your browser to =<public_ip>:9000= and
=<public_ip>:8080= to watch the job in your own little zuul/gerrit
stack.

## What service do we have access to: gerrit and zuul.

Get the public interface of the vm you've just created. Here's one way
to get it back.

    openstack --os-cloud openstack_dev server list |grep chem
    | 8f12d5d2-a7d0-464e-b799-d4c4d4abefef | chem-reproducer-5             | ACTIVE | chem-reproducer-5-net=10.0.190.124, 192.168.0.185                                                                                   | CentOS-8-GenericCloud-8.4.2105 | ci.standard.xl   |

10.0.190.124 is the public ip.

Now, you can reach gerrit part of the setup there: 10.0.190.124:8080
and the zuul part 10.0.190.124:9000.

For gerrit I recommand that you follow those instructions to setup
your user
(https://zuul-ci.org/docs/zuul/latest/tutorials/quick-start.html)[zuul-quickstart]

## Trigger a job - part 1

I went through
(https://zuul-ci.org/docs/zuul/latest/tutorials/quick-start.html)[zuul-quickstart]
to create the "chem" user in gerrit.  Then:

    git clone "ssh://chem@127.0.0.1:29418/test1" && scp -p -P 29418 chem@127.0.0.1:hooks/commit-msg "test1/.git/hooks/"
    cd test1
    git config --local http.sslverify false
    git config --local user.name chem
    git config --local user.email sathlang@redhat.com
    git remote add gerrit ssh://admin@127.0.0.1:29418/test1

Modify zuul.yaml with the existing job you want to trigger.

For instance the resulting zuul.yaml could be:

    - project
        check:
           jobs:
             - tripleo-ci-centos-9-scenario007-multinode-oooq-container


And then commit and send it to review:


    git commit -am'Add centos-9 Job'
    sudo dnf install git-review
    git review
    
You should be able to see your job there http://10.0.190.124:8080/dashboard/self

The started instance will be name something like:

	centos-9-stream-chem-reproducer-5-openstack_dev-0000000000
	centos-9-stream-chem-reproducer-5-openstack_dev-0000000001
    
Of course the chem-reproducer-5 part will be different.

Then we can log to the server using (from the laptop)

    ssh zuul@10.0.190.214 -i ~/.ssh/<your specially created ssh key for rdo and opendev>

Next we want to keep the server if something bad happens.

## Put the started instance on hold.

Zuul can keep the server if there is an error using the autohold command.

In this context this would give:


    podman exec -ti tripleo-reproducer-scheduler \
       /usr/local/bin/zuul autohold \
       --project test1 \
       --tenant tripleo-ci-reproducer \
       --job tripleo-ci-centos-9-scenario007-multinode-oooq-container \
       --reason 'reproducer_forensic'

And then get the list using:

    podman exec -ti tripleo-reproducer-scheduler \
       /usr/local/bin/zuul autohold-list \
       --tenant tripleo-ci-reproducer

There are other option that one can explore using 

    podman exec -ti tripleo-reproducer-scheduler \
       /usr/local/bin/zuul autohold --help


After the failure I can get information about what's autoheld.


    [centos@chem-reproducer-5 ~]$ podman exec -ti tripleo-reproducer-scheduler /usr/local/bin/zuul autohold-list --tenant tripleo-ci-reproducer
 +------------+-----------------------+--------------+----------------------------------------------------------+------------+-----------+---------------------+
    |     ID     |         Tenant        |   Project    |                           Job                            | Ref Filter | Max Count |        Reason       |
    +------------+-----------------------+--------------+----------------------------------------------------------+------------+-----------+---------------------+
    | 0000000000 | tripleo-ci-reproducer | gerrit/test1 | tripleo-ci-centos-9-scenario007-multinode-oooq-container |     .*     |     1     | reproducer_forensic |
    +------------+-----------------------+--------------+----------------------------------------------------------+------------+-----------+---------------------+
    [centos@chem-reproducer-5 ~]$ podman exec -ti tripleo-reproducer-scheduler /usr/local/bin/zuul autohold-info 0000000000
    ID: 0000000000
    Tenant: tripleo-ci-reproducer
    Project: gerrit/test1
    Job: tripleo-ci-centos-9-scenario007-multinode-oooq-container
    Ref Filter: .*
    Max Count: 1
    Current Count: 1
    Node Expiration: 0
    Request Expiration: Tue May  3 12:05:39 2022
    Reason: reproducer_forensic
    Held Nodes: [{'build': '7f47c002fe6f4c0796588046f0255d26', 'nodes': ['0000000000', '0000000001']}]


This match the scheme of the created vm with the nodes list.

So now I can inspect the live to check the failure.

## Get the list of the defined jobs


Note about the job, this:

    curl 10.0.190.124:9000/api/tenant/tripleo-ci-reproducer/jobs | jq '.' > jobs.json

gives you the jobs configured in zuul. But, for some reason the
previous job that can be found in any upstream build, is there but
with the "periodic-" prefix and the "<branch>" suffix.

## FAQ
### The flavor is not correct

`Nodepool` takes the flavor name as an indication, not a fixed
parameter. Basically it loads all the flavors and takes the first one
where the flavor string in submatch. So if you specified `x1.large`
and the flavor list has `x1.large.ephemeral` then you cannot be
certain that the `x1.large.ephemeral` won't be choosen.

So if you want to be certain, you need to get a flavor name that is
not matched by any other flavor string.

### How to change the nodepool flavor.

The nodepool configuration is in
`tripleo-ci-reproducer/etc_nodepool/nodepool.yaml`

Look for `flavor:`, adjust, and restart the service (not sure it's
required, but it works)

    sudo podman restart launcher


### os_application_credentials fails

Try:

    ansible-galaxy collection install  openstack.cloud
    
    
### Pulling all images for podman fail 

This might be because the cloud you're in has already reached the pull
limit from Docker.io.

You need to make a reverse sock5 tunnel so that you pull the image
from your laptop.

    ssh -i chem-reproducer-5 -R 8181 centos@10.0.108.113
    sudo dnf install proxychains-ng nmap-ncat
    cat > proxychain.conf <<EOF
    [ProxyList]
    socks5 127.0.0.1 8181
    EOF
    proxychains4 -f proxychain.conf ncat -4 -l 3128 --proxy-type http &
    env https_proxy=http://127.0.0.1:3128 http_proxy=http://127.0.0.1:3128 ansible-playbook -v boostrap_reproducer.yaml --skip-tags launch > repro.log.1 &
    
### TASK [/home/centos/ansible-role-tripleo-ci-reproducer : Get link of the tenant] fails.

If you used the previous hack to get the image working then that task
will fail.

The problem is that the ansible uri module will honor the proxy
setting and try to check:

    curl -v http://localhost:9000/api/tenant/tripleo-ci-reproducer/status
    
through the proxy, ie through your local host.

One can change the task like this in tasks/start.yaml


    - name: Wait for zuul tenant
      block:
    
        - name: Get link of the tenant
          uri:
            url: "http://localhost:9000/api/tenant/tripleo-ci-reproducer/status"
            method: GET
            return_content: true
            status_code: 200
            body_format: json
            use_proxy: no  # Doesn't work until ansible get this
                           # https://github.com/ansible/ansible/pull/77312
          environment:    # Workaround for the above
             http_proxy: ''
             https_proxy: ''
             no_proxy: ''
          register: result
          retries: "{{ 60 if ci_job is defined else 120 }}"
          delay: "{{ 15 if not full_repos_set|default(false)|bool else 30 }}"
          until: result.status == 200 and result.json["zuul_version"] is defined
          changed_when: false

or use no_proxy=localhost,127.0.0.1,api.rhos-01.prod.psi.rdu2.redhat.com.

This is a way to test that it's working:
1. without proxy:

    curl -v http://localhost:9000/api/tenant/tripleo-ci-reproducer/status

1. with proxy, but no no_proxy:

    env https_proxy=http://127.0.0.1:3128 http_proxy=http://127.0.0.1:3128 curl -v http://localhost:9000/api/tenant/tripleo-ci-reproducer/status

1. with proxy and no_proxy setting:

    env no_proxy=localhost,127.0.0.1,api.rhos-01.prod.psi.rdu2.redhat.com https_proxy=http://127.0.0.1:3128 http_proxy=http://127.0.0.1:3128 curl -v http://localhost:9000/api/tenant/tripleo-ci-reproducer/status

##  Log Stream did not terminate error while watching the build

Don't know how or why this error, but the job is running fine behind
the scene.

If you have access to the zuul plateforme you can follow the job using:

    podman logs -f --tail=200 tripleo-reproducer-executor 2>&1 |grep 9abb075c4b374d18bbe5cd9e8f37d2ad

Replace 9abb075c4b374d18bbe5cd9e8f37d2ad with the relevant build id.

## Debug tripleo-quickstart

If you have the "undercloud" you'll have all the necessary file to
re-run the tripleo-quickstart command and be able to debug further.

    export OPT_WORKDIR=/home/zuul/workspace/.quickstart
    export LOCAL_WORKING_DIR=$OPT_WORKDIR
    export ANSIBLE_COLLECTIONS_PATHS="$OPT_WORKDIR/share/ansible/collections:~/.ansible/collections:/usr/share/ansible/collections"
    export OOOQ_DIR=/home/zuul/src/opendev.org/openstack/tripleo-quickstart
    export ANSIBLE_CONFIG=$OOOQ_DIR/ansible.cfg
    
    cd /home/zuul/workspace/.quickstart
    . bin/activate
    
    /home/zuul/workspace/.quickstart/bin/ansible-playbook --tags build,undercloud-setup,undercloud-scripts,undercloud-install,undercloud-post-install,tripleo-validations,overcloud-scripts,overcloud-prep-config,overcloud-prep-containers,overcloud-deploy,overcloud-post-deploy,overcloud-validate \
     --extra-vars @/home/zuul/workspace/.quickstart/config/release/tripleo-ci/CentOS-9/master.yml \
     --extra-vars @/home/zuul/src/opendev.org/openstack/tripleo-quickstart/config/nodes/1ctlr.yml \
     --extra-vars @/home/zuul/src/opendev.org/openstack/tripleo-quickstart/config/general_config/featureset-multinode-common.yml \
     --extra-vars @/home/zuul/src/opendev.org/openstack/tripleo-quickstart/config/general_config/featureset030.yml \
     --extra-vars @/home/zuul/src/opendev.org/openstack/tripleo-ci/toci-quickstart/config/testenv/multinode.yml \
     --extra-vars @/home/zuul/workspace/logs/role-vars.yaml \
     -e toci_vxlan_networking='false' -e vxlan_networking='false' \
     --extra-vars local_working_dir=/home/zuul/workspace/.quickstart \
     --extra-vars virthost=127.0.0.2 \
     --inventory /home/zuul/workspace/.quickstart/hosts 
     --extra-vars tripleo_root=/home/zuul/src/opendev.org/openstack 
     --extra-vars working_dir=/home/zuul 
     --extra-vars tripleo_generate_scripts=true \
     --skip-tags tripleo-validations,teardown-all \
     /home/zuul/workspace/.quickstart/playbooks/multinode.yml \
     --extra-vars validation_args=' --validation-errors-nonfatal' 
     --extra-vars @/home/zuul/workspace/logs/zuul-variables.yaml 
     --extra-vars @/home/zuul/workspace/logs/hostvars-variables.yaml -vvv
     
      # --tags build,undercloud-setup,undercloud-scripts,undercloud-install,undercloud-post-install,tripleo-validations,overcloud-scripts,overcloud-prep-config,overcloud-prep-containers,overcloud-deploy,overcloud-post-deploy,overcloud-validate,overcloud-update \
         /home/zuul/workspace/.quickstart/bin/ansible-playbook \
            --tags overcloud-scripts,overcloud-deploy \
            --extra-vars @/home/zuul/workspace/.quickstart/config/release/tripleo-ci/CentOS-9/master.yml -e dlrn_hash=c9dc3faf773b2761b7cb1368df0ef98c -e get_build_command=c9dc3faf773b2761b7cb1368df0ef98c \
            --extra-vars @/home/zuul/src/opendev.org/openstack/tripleo-quickstart/config/nodes/3ctlr_1comp.yml \
            --extra-vars @/home/zuul/src/opendev.org/openstack/tripleo-quickstart/config/general_config/featureset-multinode-common.yml \
            --extra-vars @/home/zuul/src/opendev.org/openstack/tripleo-quickstart/config/general_config/featureset037.yml \
            --extra-vars @/home/zuul/src/opendev.org/openstack/tripleo-ci/toci-quickstart/config/testenv/multinode-psi.yml \
            --extra-vars @/home/zuul/workspace/logs/role-vars.yaml                  -e toci_vxlan_networking='false' -e vxlan_networking='false' \
            --extra-vars local_working_dir=/home/zuul/workspace/.quickstart \
            --extra-vars virthost=127.0.0.2 \
            --inventory /home/zuul/workspace/.quickstart/hosts \
            --extra-vars tripleo_root=/home/zuul/src/opendev.org/openstack \
            --extra-vars working_dir=/home/zuul \
            --extra-vars tripleo_generate_scripts=true  \
            --skip-tags tripleo-validations,teardown-all \
            /home/zuul/workspace/.quickstart/playbooks/multinode-overcloud.yml \
            --extra-vars @/home/zuul/workspace/logs/zuul-variables.yaml \
            --extra-vars @/home/zuul/workspace/logs/hostvars-variables.yaml
    
        /home/zuul/workspace/.quickstart/bin/ansible-playbook --tags overcloud-deploy --extra-vars @/home/zuul/workspace/.quickstart/config/release/tripleo-ci/CentOS-9/master.yml --extra-vars @/home/zuul/src/opendev.org/openstack/tripleo-quickstart/config/nodes/1ctlr.yml --extra-vars @/home/zuul/src/opendev.org/openstack/tripleo-quickstart/config/general_config/featureset-multinode-common.yml --extra-vars @/home/zuul/src/opendev.org/openstack/tripleo-quickstart/config/general_config/featureset030.yml --extra-vars @/home/zuul/src/opendev.org/openstack/tripleo-ci/toci-quickstart/config/testenv/multinode.yml --extra-vars @/home/zuul/workspace/logs/role-vars.yaml                  -e toci_vxlan_networking='false' -e vxlan_networking='false' --extra-vars local_working_dir=/home/zuul/workspace/.quickstart --extra-vars virthost=127.0.0.2 --inventory /home/zuul/workspace/.quickstart/hosts --extra-vars tripleo_root=/home/zuul/src/opendev.org/openstack --extra-vars working_dir=/home/zuul --extra-vars tripleo_generate_scripts=true --skip-tags tripleo-validations,teardown-all          /home/zuul/workspace/.quickstart/playbooks/multinode.yml --extra-vars validation_args=' --validation-errors-nonfatal' --extra-vars @/home/zuul/workspace/logs/zuul-variables.yaml --extra-vars @/home/zuul/workspace/logs/hostvars-variables.yaml -vvv

One more relevant directory on the undercloud is

    /home/zuul/src/opendev.org/openstack/tripleo-ci
    
If you modify the yaml there it will immediately reflect in your
ansible-playbook run, for instance to hack a featureset, a multinode
configuraton or a architecture.

### Some container fails to start after reboot of the host.

Inspecting the logs should show a lot of permission denied error:


    podman ps --all
    podman logs --tail 20 tripleo-reproducer-merger1

This is a selinux issue. The easy way out is:

   sudo setenforce 0
   podman pod start tripleo-reproducer

### Undercloud deployment fail on "Wait for cloud-init to finish, if enabled" tasks.

We check two things for cloud-init and one of them is it's enable.

    - name: Check cloud-init status
      shell: systemctl is-active cloud-init.service || systemctl is-enabled cloud-init.service
      failed_when: false
      become: true
      register: cloud_init_enabled

From https://opendev.org/openstack/tripleo-heat-templates/src/branch/master/common/deploy-steps-tasks-step-0.j2.yaml#L10-L14

and even with:


              runcmd:
              - [ dnf, remove, -y, cloud-init ]
              - [ dnf, update, -y ]
              - reboot
              
From tripleo-ci-reproducer/etc_nodepool/nodepool.yaml the service is
still enabled for some reason, certainly because cloud-init tries do
delete cloud-init?

Anyway, the fix is:

              runcmd:
              - [ systemctl, disable, cloud-init ]
              - [ dnf, remove, -y, cloud-init ]
              - [ dnf, update, -y ]
              - reboot
              
No need to restart nodepool the change is taken into account
automatically.

recheck ...

I seems to have encounter the issue even with this modification.

This one seems more logical/robust:
           runcmd:
              - [ systemctl, disable, '--now', cloud-init ]
              - [ systemctl, is-active, cloud-init.service ]
              - [ dnf, update, -y ]
              - [ shutdown, -r, +2, "Rebooting from cloud-init" ]
              - [ dnf, remove, -y, cloud-init ]

in tripleo-ci-reproducer/etc_nodepool/nodepool.yaml. No need to
restart anything it's taken automatically into account.

### Ping the gateway doesn't work during undercloud install.

Most likely the security group is missing from the port.

      pool:
        security-groups:
          - chem-reproducer-5-security-group
          
Make sure that tripleo-ci-reproducer/etc_nodepool/nodepool.yaml has this line.


Oups ... is that enought to get it done ... I had to add it to the
interface manually.
