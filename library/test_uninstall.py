def do_uninstall(shutit, test_config_module, shutit_sessions, chef_deploy_method):
	for machine in test_config_module.machines.keys():
		# 1) pick the first node (break at end)
		if test_config_module.machines[machine]['is_node']:
			shutit_session = shutit_sessions[machine]
			# 2) switch off cronjobs
			shutit_session.send('systemd stop crond')
			if chef_deploy_method == 'solo':
				# 3) adhoc uninstall on it
				shutit_session.send(r'''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3::adhoc_uninstall_node]' -c ~/chef-solo-example/solo.rb >> /tmp/chef.adhoc_uninstall.log.`date "+%H%M%S"` 2>&1 || true''')
				# 4) re-run chef to install everything
				shutit_session.send(r'''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb >> /tmp/chef.adhoc_uninstall_post.log.`date "+%H%M%S"` 2>&1 || true''')
			else:
				# 3) adhoc uninstall on it
				shutit_session.send(r'''chef-client -o 'recipe[cookbook-openshift3::adhoc_uninstall_node]' > /tmp/chef.adhoc_uninstall.log.`date "+\%H\%M\%S"` 2>&1' | crontab''')
				# 4) re-run chef to install everything
				shutit_session.send(r'''chef-client > /tmp/chef.adhoc_uninstall_post.log.`date "+\%H\%M\%S"` 2>&1' | crontab''')
			# 4b) check lv no longer exists
			if shutit_session.send_and_get_output('lvs | grep docker-pool | wc -l') != '0':
				shutit.fail('docker-pool lv is there after an uninstall')
			# 6) switch on cronjobs
			shutit_session.send('systemd start crond')
			break
# 5) check node is ok
# TODO
		################################################################################
