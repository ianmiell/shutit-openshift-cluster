import time

def do_reset(test_config_module, shutit_sessions, chef_deploy_method):
	for machine in test_config_module.machines.keys():
		shutit_session = shutit_sessions[machine]
		shutit_session.send('systemd stop crond')
	time.sleep(300)
	for machine in test_config_module.machines.keys():
		shutit_session = shutit_sessions[machine]
		if chef_deploy_method == 'solo':
			# adhoc reset on it
			shutit_session.send(r'''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3::adhoc_reset]' -c ~/chef-solo-example/solo.rb >> /tmp/chef.adhoc_reset.log.`date "+%H%M%S"` 2>&1 || true''')
			# re-run chef to install everything
			shutit_session.send(r'''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb >> /tmp/chef.adhoc_reset_post.log.`date "+%H%M%S"` 2>&1 || true''')
		else:
			# adhoc reset on it
			shutit_session.send(r'''chef-client -o 'recipe[cookbook-openshift3::adhoc_reset_node]' > /tmp/chef.adhoc_reset.log.`date "+\%H\%M\%S"` 2>&1' | crontab''')
			# re-run chef to install everything
			shutit_session.send(r'''chef-client > /tmp/chef.adhoc_reset_post.log.`date "+\%H\%M\%S"` 2>&1' | crontab''')
	# switch on cronjobs
	for machine in test_config_module.machines.keys():
		shutit_session = shutit_sessions[machine]
		shutit_session.send('systemd start crond')
