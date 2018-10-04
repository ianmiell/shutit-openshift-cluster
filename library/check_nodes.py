def check_nodes(shutit_master1_session, test_config_module, vagrantcommand):
	# 1) CHECK NODES COME UP
	shutit_master1_session.send_until('oc --config=/etc/origin/master/admin.kubeconfig get all || tail /tmp/chef.log*','.*kubernetes.*',cadence=60,note='Wait until oc get all returns OK')
	for machine in test_config_module.machines.keys():
		if test_config_module.machines[machine]['is_node']:
				while not shutit_master1_session.send_until('oc --config=/etc/origin/master/admin.kubeconfig get nodes',machine + '.* Ready.*',cadence=60,retries=10,note='Wait until oc get all returns OK'):
					shutit_master1_session.logout()
					shutit_master1_session.logout()
					# Reboot the machine - this resolves some problems
					shutit_master1_session.send(vagrantcommand + ' halt ' + machine)
					shutit_master1_session.multisend(vagrantcommand + ' up --provider ' + vagrant_provider + ' ' + machine,{'assword for':pw})
					shutit_master1_session.login(command=vagrantcommand + ' ssh master1')
					shutit_master1_session.login(command='sudo su - ')
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
				
