#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

(
	cd ${DIR}/..
	export OSE_VERSIONS=1.3
	export CHEF_DEPLOY_METHODS="server"
	export SHUTIT_CLUSTER_CONFIGS=test_single_node
	./run_tests.sh $@
)
