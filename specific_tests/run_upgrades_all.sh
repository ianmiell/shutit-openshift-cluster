#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

(
	cd ${DIR}/..
	export UPGRADE_13_14=true
	export UPGRADE_14_15=true
	export UPGRADE_15_36=true
	export UPGRADE_36_37=true
	export OSE_VERSIONS=1.3
	export CHEF_DEPLOY_METHODS="solo server"
	export SHUTIT_CLUSTER_CONFIGS=test_multi_node_basic_small
	./run_tests.sh $@
)
