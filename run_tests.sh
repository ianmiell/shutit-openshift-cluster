#!/bin/bash
set -x
set -e
./destroy_vms.sh
[[ -z "$SHUTIT" ]] && SHUTIT="$1/shutit"
[[ ! -a "$SHUTIT" ]] || [[ -z "$SHUTIT" ]] && SHUTIT="$(which shutit)"
if [[ ! -a "$SHUTIT" ]]
then
	echo "Must have shutit on path, eg export PATH=$PATH:/path/to/shutit_dir"
	exit 1
fi

SHUTIT_MODULE_NAME='tk.shutit.shutit_openshift_cluster.shutit_openshift_cluster'

############
# VARIABLES
############
# BRANCH_NAME - defaults to master
# OSE_VERSIONS - OSE versions to test, eg 1.4, 1.5, 3.6 etc
# CHEF_DEPLOY_CONTAINERIZED
#  - deployment methods to use, can be 'true', 'false', or 'true false' if you
#    want to test both methods. defaults to 'false'
# CHEF_DEPLOY_METHODS
#  - chef method of provisioning, 'solo' and/or 'server' 'solo server' is default
# CHEF_YUM_COOKBOOK_VERSION - yum cookbook version to use
# CHEF_SELINUX_COOKBOOK_VERSION - selinux cookbook version
# CHEF_IPTABLES_COOKBOOK_VERSION - iptables cookbook version
# CHEF_COMPAT_RESOURCE_COOKBOOK_VERSION - compat resource cookbook version
# CHEF_INJECT_COMPAT_RESOURCE_COOKBOOK_VERSION
#  - compat resource cookbook version
# LOG_LEVEL - ShutIt log level, default 'debug'
# SHUTIT_CLUSTER_CONFIGS - default 'test_multi_node_separate_etcd'
# SHUTIT_INTERACTIVE
#  - Whether to run interactively 0 (non), or 1 (give pause point)
# UPGRADE_13_14 - if non-empty and not false, upgrade from 1.3 to 1.4
# UPGRADE_14_15 - if non-empty and not false, upgrade from 1.4 to 1.5
# UPGRADE_15_36 - if non-empty and not false, upgrade from 1.5 to 3.6
# UPGRADE_36_37 - if non-empty and not false, upgrade from 3.6 to 3.7
# UPGRADE_37_39 - if non-empty and not false, upgrade from 3.7 to 3.9

if [[ $BRANCH_NAME = '' ]]
then
	BRANCH_NAME="master"
fi

if [[ $OSE_VERSIONS = '' ]]
then
	OSE_VERSIONS='1.3 3.6 3.7 3.9'
fi

if [[ $CHEF_YUM_COOKBOOK_VERSION = '' ]]
then
	CHEF_YUM_COOKBOOK_VERSION='latest'
fi

if [[ $CHEF_DEPLOY_CONTAINERIZED = '' ]] || [[ $CHEF_DEPLOY_CONTAINERIZED = 'false' ]]
then
	CHEF_DEPLOY_CONTAINERIZED='false'
else
	CHEF_DEPLOY_CONTAINERIZED='true'
fi

if [[ $DO_ADHOC_UNINSTALL = '' ]] || [[ $DO_ADHOC_UNINSTALL = 'false' ]]
then
	DO_ADHOC_UNINSTALL='false'
else
	DO_ADHOC_UNINSTALL='true'
fi

if [[ $DO_ADHOC_RESET = '' ]] || [[ $DO_ADHOC_RESET = 'false' ]]
then
	DO_ADHOC_RESET='false'
else
	DO_ADHOC_RESET='true'
fi

if [[ $CHEF_SELINUX_COOKBOOK_VERSION = '' ]]
then
	CHEF_SELINUX_COOKBOOK_VERSION='latest'
fi
if [[ $CHEF_COMPAT_RESOURCE_COOKBOOK_VERSION = '' ]]
then
	CHEF_COMPAT_RESOURCE_COOKBOOK_VERSION='latest'
fi
if [[ $CHEF_INJECT_COMPAT_RESOURCE_COOKBOOK_VERSION = '' ]]
then
	CHEF_INJECT_COMPAT_RESOURCE_COOKBOOK_VERSION='false'
fi
if [[ $CHEF_IPTABLES_COOKBOOK_VERSION = '' ]]
then
	CHEF_IPTABLES_COOKBOOK_VERSION='latest'
fi
if [[ $CHEF_DEPLOY_METHODS = '' ]]
then
	CHEF_DEPLOY_METHODS='solo server'
fi
if [[ $LOG_LEVEL = '' ]]
then
	LOG_LEVEL='debug'
fi
if [[ $SHUTIT_CLUSTER_CONFIGS = '' ]]
then
	SHUTIT_CLUSTER_CONFIGS='test_multi_node_colocated_etcd'
fi

if [[ $SHUTIT_INTERACTIVE = '' ]] || ! echo $- | grep i
then
	SHUTIT_INTERACTIVE=0
	NOCOLOR='--nocolor'
else
	NOCOLOR=''
fi

# If upgrades are set to anything, it's assumed to be true.
if [[ $UPGRADE_13_14 = '' ]] || [[ $UPGRADE_13_14 = 'false' ]]
then
	UPGRADE_13_14='false'
else
	UPGRADE_13_14='true'
fi

if [[ $UPGRADE_14_15 = '' ]] || [[ $UPGRADE_14_15 = 'false' ]]
then
	UPGRADE_14_15='false'
else
	UPGRADE_14_15='true'
fi

if [[ $UPGRADE_15_36 = '' ]] || [[ $UPGRADE_15_36 = 'false' ]]
then
	UPGRADE_15_36='false'
else
	UPGRADE_15_36='true'
fi

if [[ $UPGRADE_36_37 = '' ]] || [[ $UPGRADE_36_37 = 'false' ]]
then
	UPGRADE_36_37='false'
else
	UPGRADE_36_37='true'
fi

if [[ $UPGRADE_37_39 = '' ]] || [[ $UPGRADE_37_39 = 'false' ]]
then
	UPGRADE_37_39='false'
else
	UPGRADE_37_39='true'
fi

echo ================================================================================
echo "Running test at: $(date)"
env | egrep '(CHEF|SHUTIT|LOG_LEVEL)' || true
echo ================================================================================

if [[ $(uname) != 'Darwin' ]]
then
	echo "CHECKING TO SEE WHETHER NODE $(hostname) IS 'CLEAN'"
	if vagrant global-status | grep virtualbox >/dev/null 2>&1
	then
		vagrant global-status
		echo VMs running on this machine, so failing run. Consider running destroy_vms.sh
		exit 1
	fi
else
	echo "ON DARWIN, SO _NOT_ CHECKING TO SEE WHETHER NODE $(hostname) IS 'CLEAN'"
fi

for deploy_containerized in ${CHEF_DEPLOY_CONTAINERIZED}
do
	for deploy_method in ${CHEF_DEPLOY_METHODS}
	do
		for ose_major_version in ${OSE_VERSIONS}
		do
			for test_dir in ${SHUTIT_CLUSTER_CONFIGS}
			do
				# see http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin/
				if [[ $ose_major_version == '3.9' ]]
				then
					ose_version="3.9.0-1.el7.git.0.ba7faec"
					ose_docker_image_version="v3.9.0"
				elif [[ $ose_major_version == '3.7' ]]
				then
					ose_version="3.7.2-1.el7.git.0.cd74924"
					ose_docker_image_version="v3.7.2"
				elif [[ $ose_major_version == '3.6' ]]
				then
					ose_version="3.6.1-1.0.008f2d5"
					ose_docker_image_version="v3.6.1"
				elif [[ $ose_major_version == '1.5' ]]
				then
					ose_version="1.5.1-1.el7"
					ose_docker_image_version="v1.5.1"
				elif [[ $ose_major_version == '1.4' ]]
				then
					ose_version="1.4.1-1.el7"
					ose_docker_image_version="v1.4.1"
				elif [[ $ose_major_version == '1.3' ]]
				then
					ose_version="1.3.3-1.el7"
					ose_docker_image_version="v1.3.3"
				fi
				$SHUTIT build \
					-l ${LOG_LEVEL} \
					-d bash \
					--echo \
					--pane \
					--interactive ${SHUTIT_INTERACTIVE} \
					-m shutit-library/vagrant:shutit-library/virtualbox \
					-s ${SHUTIT_MODULE_NAME} test_config_dir                       ${test_dir} \
					-s ${SHUTIT_MODULE_NAME} ose_version                           ${ose_version} \
					-s ${SHUTIT_MODULE_NAME} ose_major_version                     ${ose_major_version} \
					-s ${SHUTIT_MODULE_NAME} cookbook_branch                       ${BRANCH_NAME} \
					-s ${SHUTIT_MODULE_NAME} chef_yum_cookbook_version             ${CHEF_YUM_COOKBOOK_VERSION} \
					-s ${SHUTIT_MODULE_NAME} chef_iptables_cookbook_version        ${CHEF_IPTABLES_COOKBOOK_VERSION} \
					-s ${SHUTIT_MODULE_NAME} chef_selinux_policy_cookbook_version  ${CHEF_SELINUX_COOKBOOK_VERSION} \
					-s ${SHUTIT_MODULE_NAME} chef_compat_resource_cookbook_version ${CHEF_COMPAT_RESOURCE_COOKBOOK_VERSION} \
					-s ${SHUTIT_MODULE_NAME} inject_compat_resource                ${CHEF_INJECT_COMPAT_RESOURCE_COOKBOOK_VERSION} \
					-s ${SHUTIT_MODULE_NAME} chef_deploy_method                    ${deploy_method} \
					-s ${SHUTIT_MODULE_NAME} chef_deploy_containerized             ${deploy_containerized} \
					-s ${SHUTIT_MODULE_NAME} do_upgrade_13_14                      ${UPGRADE_13_14} \
					-s ${SHUTIT_MODULE_NAME} do_upgrade_14_15                      ${UPGRADE_14_15} \
					-s ${SHUTIT_MODULE_NAME} do_upgrade_15_36                      ${UPGRADE_15_36} \
					-s ${SHUTIT_MODULE_NAME} do_upgrade_36_37                      ${UPGRADE_36_37} \
					-s ${SHUTIT_MODULE_NAME} do_upgrade_37_39                      ${UPGRADE_37_39} \
					-s ${SHUTIT_MODULE_NAME} openshift_docker_image_version        ${ose_docker_image_version} \
					-s ${SHUTIT_MODULE_NAME} adhoc_uninstall                       ${DO_ADHOC_UNINSTALL} \
					-s ${SHUTIT_MODULE_NAME} adhoc_reset                           ${DO_ADHOC_RESET} \
					${NOCOLOR} \
					"$@"
				./destroy_vms.sh
			done
		done
	done
done
