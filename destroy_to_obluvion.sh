#!/usr/bin/bash

usage()
{
    cat <<EOF
Usage: ${0##*/} -p <PREFIX> \\
                [-c <CLOUD_NAME>] \\
                [-d] [-h]

Description: Destroy the resource related to your bastion host.  All
the instance bootstraped by nodepool related that bastion host.

Parameters:
  Mandatory
   -p: prefix to use for cloud related ressource, default to ${USER}-reproducer
  Optional:
   -c: the name of cloud entry definition in clouds.yaml, default to openstack.

EOF

}

error_arg()
{
    local arg=$1
    echo "ERROR: Missing or invalid argument $arg"
    echo
    echo "Use ${0##*/} -h for a description of the valid args"
    exit 2
}

CLOUD_NAME="openstack"
DEBUG=""
DELETE_KEY="False"
DELETE_APPCRED="False"
NOOP="False"
VERBOSE="-v"

while getopts c:p:kandh OPT; do
    case $OPT in
        p)
            PREFIX="$OPTARG"
            ;;
        c)
            CLOUD_NAME="$OPTARG"
            ;;
        d)
            DEBUG="echo"
            ;;
        k)
            DELETE_KEY="True"
            ;;
        a)
            DELETE_APPCRED="True"
            ;;
        n)
            NOOP="True"
            VERBOSE=""
            ;;
        h)
            usage
            exit 0
            ;;
        *)
            error_arg "$OPTARG"
            usage
            exit 2
    esac
done
shift $(( OPTIND - 1 ))
OPTIND=1

for opt in PREFIX; do
    if eval test -z "\$$opt"; then
        error_arg $opt
    fi
done

$DEBUG ansible-playbook \
       ${VERBOSE} \
       -e '{"prefix": "'${PREFIX}\
'", "cloud_name": "'${CLOUD_NAME}\
'", "delete_key": "'${DELETE_KEY}\
'", "delete_appcred": "'${DELETE_APPCRED}\
'", "noop": "'${NOOP}\
'"}' \
./destroy-reproducer.yaml
