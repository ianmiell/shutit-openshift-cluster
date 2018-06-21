#!/bin/bash
set -x
rm -rf vagrant_run/*
if [[ $(command -v VBoxManage) != '' ]]
then
	while true
	do
		VBoxManage list runningvms | grep prod_rothko_openshift | awk '{print $1}' | xargs --no-run-if-empty -IXXX VBoxManage controlvm 'XXX' poweroff && VBoxManage list vms | grep prod_rothko_openshift | awk '{print $1}'  | xargs --no-run-if-empty -IXXX VBoxManage unregistervm 'XXX' --delete
		# The xargs removes whitespace
		if [[ $(VBoxManage list vms | grep prod_rothko_openshift | wc -l | xargs) -eq '0' ]]
		then
			break
		else
			ps -ef | grep virtualbox | grep prod_rothko_openshift | awk '{print $2}' | xargs --no-run-if-empty kill
			sleep 10
		fi
	done
fi
if [[ $(command -v virsh) != '' ]]
then
	if [[ $(kvm-ok 2>&1 | command grep 'can be used') != '' ]]
	then
	    virsh list | grep prod_rothko_openshift | awk '{print $1}' | xargs --no-run-if-empty -n1 virsh destroy
	fi
fi
