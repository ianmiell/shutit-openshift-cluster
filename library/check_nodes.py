import logging
def check_nodes(shutit_master1_session, test_config_module, vagrantcommand, vagrant_provider, pw):
	# 1) CHECK NODES COME UP
	shutit_master1_session.send_until('oc --config=/etc/origin/master/admin.kubeconfig get all || tail /tmp/chef.log*','.*kubernetes.*',cadence=60,note='Wait until oc get all returns OK')
	for machine in test_config_module.machines.keys():
		if test_config_module.machines[machine]['is_node']:
			while True:
				output = shutit_master1_session.send_and_get_output('oc --config=/etc/origin/master/admin.kubeconfig get nodes | grep ' + machine)
				if output.find(' Ready') != -1:
					break
				shutit_master1_session.send('sleep 10')
		else:
			shutit_master1_session.log(machine + ' is not a node?', level=logging.WARNING)


def label_nodes(shutit_master1_session, test_config_module):
	for machine in test_config_module.machines.keys():
		if test_config_module.machines[machine]['is_node'] and test_config_module.machines[machine]['region'] not in ('NA',''):
			shutit_master1_session.send('oc --config=/etc/origin/master/admin.kubeconfig label node ' + test_config_module.machines[machine]['fqdn'] + ' region=' + test_config_module.machines[machine]['region'] + ' --overwrite')


# SET UP CORE APPS
def schedule_nodes(test_config_module, shutit_master1_session):
	"""Sometimes nodes get unschedulable, so force them temporarily to get mysql app through
	"""
	if shutit_master1_session.send_and_get_output('oc --config=/etc/origin/master/admin.kubeconfig get nodes | grep SchedulingDisabled'):
		for machine in test_config_module.machines.keys():
			if test_config_module.machines[machine]['is_node']:
				shutit_master1_session.send('oc --config=/etc/origin/master/admin.kubeconfig adm manage-node --schedulable ' + machines[machine]['fqdn'])
