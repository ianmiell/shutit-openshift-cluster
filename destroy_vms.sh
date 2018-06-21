#!/bin/bash
set -x
rm -rf vagrant_run/*
vagrant global-status --prune
XARGS_ARG='--no-run-if-empty'
if [[ $(uname) = 'Darwin' ]]
then
	XARGS_ARG=''
fi
if [[ $(command -v VBoxManage) != '' ]]
then
	while true
	do
		VBoxManage list runningvms | grep shutit_openshift_cluster | awk '{print $1}' | xargs --no-run-if-empty -n1 -IXXX VBoxManage controlvm 'XXX' poweroff && VBoxManage list vms | grep shutit_openshift_cluster | awk '{print $1}'  | xargs --no-run-if-empty -IXXX VBoxManage unregistervm 'XXX' --delete
		# The xargs removes whitespace
		if [[ $(VBoxManage list vms | grep shutit_openshift_cluster | wc -l | xargs) -eq '0' ]]
		then
			break
		else
			ps -ef | grep virtualbox | grep shutit_openshift_cluster | awk '{print $2}' | xargs ${XARGS_ARG} -n1 kill
			sleep 10
		fi
	done
fi
# Clean up landrush
vagrant landrush vms | awk '{print $2}' | egrep '(^master|^etcd|^node)' | sed 's/.*/vagrant landrush rm \0/g' | sh

#VIRSHCMD='sudo virsh'
#if [[ $(command -v virsh) != '' ]]
#then
#	if [[ $(kvm-ok 2>&1 | command grep 'can be used') != '' ]]
#	then
#	    ${VIRSHCMD} list | grep shutit_openshift_cluster | awk '{print $2}' | xargs ${XARGS_ARG} -n1 ${VIRSHCMD} destroy
#	fi
#fi
