#!/bin/bash
set -e

BRANCH_NAME_DEFAULT="master"

echo 'OSE_VERSIONS eg 1.3 1.4 1.5 3.6 3.7 3.9 (blank for default (usually last one))'
read OSE_VERSIONS

echo "SHUTIT_CLUSTER_CONFIGS eg $(ls cluster_configs) (blank for default)"
read SHUTIT_CLUSTER_CONFIGS

echo 'CHEF_DEPLOY_METHODS (blank for default) eg solo or server'
read CHEF_DEPLOY_METHODS

echo UPGRADE_13_14 - if non-empty and not false, upgrade from 1.3 to 1.4 default false
read UPGRADE_13_14
export UPGRADE_13_14
echo UPGRADE_14_15 - if non-empty and not false, upgrade from 1.4 to 1.5 default false
read UPGRADE_14_15
export UPGRADE_14_15
echo UPGRADE_15_36 - if non-empty and not false, upgrade from 1.5 to 3.6 default false
read UPGRADE_15_36
export UPGRADE_15_36
echo UPGRADE_36_37 - if non-empty and not false, upgrade from 3.6 to 3.7 default false
read UPGRADE_36_37
export UPGRADE_36_37
echo UPGRADE_37_39 - if non-empty and not false, upgrade from 3.7 to 3.9 default false
read UPGRADE_37_39
export UPGRADE_37_39

echo 'LOG_LEVEL eg info debug (blank for default (debug))'
read LOG_LEVEL

echo 'SHUTIT_INTERACTIVE eg 0, 1 (default 0)'
read SHUTIT_INTERACTIVE

echo "BRANCH_NAME - the branch you want to test (default: $BRANCH_NAME_DEFAULT)"
read BRANCH_NAME

echo "CHEF_DEPLOY_CONTAINERIZED - whether to be containerized true or false or 'true false' Default false"
read CHEF_DEPLOY_CONTAINERIZED

echo 'CHEF_VERSION (blank for default)'
read CHEF_VERSION

echo 'CHEF_YUM_COOKBOOK_VERSION (blank for default)'
read CHEF_YUM_COOKBOOK_VERSION

echo 'CHEF_SELINUX_COOKBOOK_VERSION (blank for default)'
read CHEF_SELINUX_COOKBOOK_VERSION

echo 'CHEF_COMPAT_RESOURCE_COOKBOOK_VERSION (blank for default)'
read CHEF_COMPAT_RESOURCE_COOKBOOK_VERSION

echo 'CHEF_INJECT_COMPAT_RESOURCE_COOKBOOK_VERSION (blank for default)'
read CHEF_INJECT_COMPAT_RESOURCE_COOKBOOK_VERSION

echo 'CHEF_IPTABLES_COOKBOOK_VERSION (blank for default)'
read CHEF_IPTABLES_COOKBOOK_VERSION

echo 'DO_ADHOC_UNINSTALL (blank for default (false))'
read DO_ADHOC_UNINSTALL

echo 'DO_ADHOC_RESET (blank for default (false))'
read DO_ADHOC_RESET



(
echo -n '#'
date
echo export BRANCH_NAME=${BRANCH_NAME}
echo export OSE_VERSIONS=${OSE_VERSIONS}
echo export CHEF_VERSION=${CHEF_VERSION}
echo export CHEF_YUM_COOKBOOK_VERSION=${CHEF_YUM_COOKBOOK_VERSION}
echo export CHEF_SELINUX_COOKBOOK_VERSION=${CHEF_SELINUX_COOKBOOK_VERSION}
echo export CHEF_COMPAT_RESOURCE_COOKBOOK_VERSION=${CHEF_COMPAT_RESOURCE_COOKBOOK_VERSION}
echo export CHEF_INJECT_COMPAT_RESOURCE_COOKBOOK_VERSION=${CHEF_INJECT_COMPAT_RESOURCE_COOKBOOK_VERSION}
echo export CHEF_IPTABLES_COOKBOOK_VERSION=${CHEF_IPTABLES_COOKBOOK_VERSION}
echo export CHEF_DEPLOY_METHODS=${CHEF_DEPLOY_METHODS}
echo export SHUTIT_CLUSTER_CONFIGS=${SHUTIT_CLUSTER_CONFIGS}
echo export SHUTIT_INTERACTIVE=${SHUTIT_INTERACTIVE}
echo export DO_ADHOC_UNINSTALL=${DO_ADHOC_UNINSTALL}
echo export UPGRADE_13_14=${UPGRADE_13_14}
echo export UPGRADE_14_15=${UPGRADE_14_15}
echo export UPGRADE_15_36=${UPGRADE_15_36}
echo export UPGRADE_36_37=${UPGRADE_36_37}
echo export DO_ADHOC_RESET=${DO_ADHOC_RESET}
echo export CHEF_DEPLOY_CONTAINERIZED=${CHEF_DEPLOY_CONTAINERIZED}
echo ./run_tests.sh
) >> last_args_interactive
chmod +x last_args_interactive

if [[ $BRANCH_NAME = '' ]]
then
	export BRANCH_NAME="master"
else
	export BRANCH_NAME="$BRANCH_NAME_DEFAULT"
fi

if [[ $OSE_VERSIONS = '' ]]
then
	export OSE_VERSIONS='1.3 1.4 1.5 3.6'
else
	export OSE_VERSIONS="$OSE_VERSIONS"
fi

if [[ $CHEF_VERSION = '' ]]
then
	export CHEF_VERSION='12.16.42-1'
else
	export CHEF_VERSION="$CHEF_VERSION"
fi

if [[ $CHEF_YUM_COOKBOOK_VERSION = '' ]]
then
	export CHEF_YUM_COOKBOOK_VERSION='latest'
else
	export CHEF_YUM_COOKBOOK_VERSION="$CHEF_YUM_COOKBOOK_VERSION"
fi

if [[ $CHEF_SELINUX_COOKBOOK_VERSION = '' ]]
then
	export CHEF_SELINUX_COOKBOOK_VERSION='latest'
else
	export CHEF_SELINUX_COOKBOOK_VERSION="${CHEF_SELINUX_COOKBOOK_VERSION}"
fi
if [[ $CHEF_COMPAT_RESOURCE_COOKBOOK_VERSION = '' ]]
then
	export CHEF_COMPAT_RESOURCE_COOKBOOK_VERSION='latest'
else
	export CHEF_COMPAT_RESOURCE_COOKBOOK_VERSION="${CHEF_COMPAT_RESOURCE_COOKBOOK_VERSION}"
fi
if [[ $CHEF_INJECT_COMPAT_RESOURCE_COOKBOOK_VERSION = '' ]]
then
	export CHEF_INJECT_COMPAT_RESOURCE_COOKBOOK_VERSION='false'
else
	export CHEF_INJECT_COMPAT_RESOURCE_COOKBOOK_VERSION="${CHEF_INJECT_COMPAT_RESOURCE_COOKBOOK_VERSION}"
fi
if [[ $DO_ADHOC_UNINSTALL = '' ]]
then
	export DO_ADHOC_UNINSTALL='false'
else
	export DO_ADHOC_UNINSTALL="${DO_ADHOC_UNINSTALL}"
fi
if [[ $DO_ADHOC_RESET = '' ]]
then
	export DO_ADHOC_RESET='false'
else
	export DO_ADHOC_RESET="${DO_ADHOC_RESET}"
fi
if [[ $CHEF_IPTABLES_COOKBOOK_VERSION = '' ]]
then
	export CHEF_IPTABLES_COOKBOOK_VERSION='latest'
else
	export CHEF_IPTABLES_COOKBOOK_VERSION="${CHEF_IPTABLES_COOKBOOK_VERSION}"
fi
if [[ $CHEF_DEPLOY_METHODS = '' ]]
then
	export CHEF_DEPLOY_METHODS='solo server'
else
	export CHEF_DEPLOY_METHODS="${CHEF_DEPLOY_METHODS}"
fi
if [[ $LOG_LEVEL = '' ]]
then
	export LOG_LEVEL='debug'
else
	export LOG_LEVEL=${LOG_LEVEL}
fi
if [[ $SHUTIT_CLUSTER_CONFIGS = '' ]]
then
	export SHUTIT_CLUSTER_CONFIGS='test_multi_node_basic_cert_server'
else
	export SHUTIT_CLUSTER_CONFIGS="${SHUTIT_CLUSTER_CONFIGS}"
fi
if [[ $SHUTIT_INTERACTIVE = '' ]]
then
	export SHUTIT_INTERACTIVE='1'
else
	export SHUTIT_INTERACTIVE"${SHUTIT_INTERACTIVE}"
fi

if [[ $CHEF_DEPLOY_CONTAINERIZED = '' ]]
then
	export CHEF_DEPLOY_CONTAINERIZED=false
else
	export CHEF_DEPLOY_CONTAINERIZED="${CHEF_DEPLOY_CONTAINERIZED}"
fi

./run_tests.sh --echo
