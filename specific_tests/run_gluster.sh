#!/bin/bash
set -x
bash ./destroy_vms.sh
[[ -z "$SHUTIT" ]] && SHUTIT="$1/shutit"
[[ ! -a "$SHUTIT" ]] || [[ -z "$SHUTIT" ]] && SHUTIT="$(which shutit)"
if [[ ! -a "$SHUTIT" ]]
then
	echo "Must have shutit on path, eg export PATH=$PATH:/path/to/shutit_dir"
	exit 1
fi
$SHUTIT build --echo -s tk.shutit.shutit_openshift_cluster.shutit_openshift_cluster test_config_dir test_single_master_embedded_etcd_gluster -d bash -m shutit-library/vagrant -m shutit-library/virtualbox "$@"
if [[ $? != 0 ]]
then
	exit 1
fi
