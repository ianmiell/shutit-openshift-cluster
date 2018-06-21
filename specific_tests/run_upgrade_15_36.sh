#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

(
	cd ${DIR}/..
	export UPGRADE_15_36=true
	export OSE_VERSIONS=1.5
	export CHEF_DEPLOY_METHODS="server"
	export SHUTIT_CLUSTER_CONFIGS=test_multi_node_basic_small
	./run_tests.sh $@
)
