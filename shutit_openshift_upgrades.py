import time
import shutit_openshift_cluster_test

def do_upgrades(shutit, test_config_module, shutit_sessions, check_version, shutit_chefwkstn_session, shutit_master1_session, module_id):

	def crontab_off(shutit_session):
		shutit_session.send('systemctl stop crond')

	def crontab_on(shutit_session):
		shutit_session.send('systemctl start crond')

	# For 3.7 upgrade, docker upgrade requires a redeploy to ensure all is ok
	def redeploy_components(shutit_session):
		shutit_session.send('oc rollout latest docker-registry')
		shutit_session.send('oc rollout latest router')

	# 1.3 => 1.4
	if shutit.cfg[module_id]['do_upgrade_13_14']:
		assert check_version(shutit_sessions['master1'],'1.3'), shutit.pause_point("assertion failure: shutit_sessions['master1'],'1.3'")
		if shutit.cfg[module_id]['chef_deploy_method'] == 'solo':
			# Control plane first (master, etcd, certserver).
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				crontab_off(shutit_session)
				# Change the environment file
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session.send('rm -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak && cp /root/chef-solo-example/environments/ocp-cluster-environment.json /root/chef-solo-example/environments/ocp-cluster-environment.json.bak')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send(r'''sed -i '/      "openshift_hosted_managed_registry": false,/a "control_upgrade": true, "control_upgrade_version": "14", "control_upgrade_flag": "/tmp/ready14", "upgrade_repos": [ { "name": "centos-openshift-origin14", "baseurl": "http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin14/", "gpgcheck": false } ],' /root/chef-solo-example/environments/ocp-cluster-environment.json''')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
			for machine in sorted(test_config_module.machines.keys()):
				# Touch files
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_sessions[machine].send('touch /tmp/ready14')
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb | tee /tmp/chef.log.upgrade_13_14_control_plane.`date "+%H%M%S"` 2>&1''')
					shutit_session.send('mv -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak /root/chef-solo-example/environments/ocp-cluster-environment.json')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send('rm -f /tmp/ready14')
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
			# Nodes
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_node']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('rm -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak && cp /root/chef-solo-example/environments/ocp-cluster-environment.json /root/chef-solo-example/environments/ocp-cluster-environment.json.bak')
					shutit_session.send(r'''sed -i '/      "openshift_hosted_managed_registry": false,/a "control_upgrade": true, "control_upgrade_version": "14", "control_upgrade_flag": "/tmp/ready14", "upgrade_repos": [ { "name": "centos-openshift-origin14", "baseurl": "http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin14/", "gpgcheck": false } ],' /root/chef-solo-example/environments/ocp-cluster-environment.json''')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					if shutit.cfg[module_id]['chef_deploy_containerized']:
						shutit_session.send("""sed -i 's/      "openshift_docker_image_version": .*/      "openshift_docker_image_version": "v1.4.1",/' /root/chef-solo-example/environments/ocp-cluster-environment.json""")
						shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send('touch /tmp/ready14')
					shutit_session.send('''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb | tee /tmp/chef.log.upgrade_13_14_node.`date "+%H%M%S"` 2>&1''')
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_node']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('mv -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak /root/chef-solo-example/environments/ocp-cluster-environment.json')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send('rm -f /tmp/ready14')
			for machine in sorted(test_config_module.machines.keys()):
				# Revert
				if (test_config_module.machines[machine]['is_master'] or
				    test_config_module.machines[machine]['is_etcd'] or
				    test_config_module.machines[machine]['is_certificate_server'] or
				    test_config_module.machines[machine]['is_node']):
					shutit_session = shutit_sessions[machine]
					shutit_session.send("""sed -i 's/      "ose_major_version": "1.3",/      "ose_major_version": "1.4",/' /root/chef-solo-example/environments/ocp-cluster-environment.json""")
					shutit_session.send("""sed -i 's/      "ose_version": "1.3.*",/      "ose_version": "1.4.1-1.el7",/' /root/chef-solo-example/environments/ocp-cluster-environment.json""")
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					if shutit.cfg[module_id]['chef_deploy_containerized']:
						shutit_session.send("""sed -i 's/      "openshift_docker_image_version": .*/      "openshift_docker_image_version": "v1.4.1",/' /root/chef-solo-example/environments/ocp-cluster-environment.json""")
						shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				shutit_session.send('''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb | tee /tmp/chef.log.upgrade_13_14_post_upgrade.`date "+%H%M%S"` 2>&1''')
				shutit_session.send(r'''echo '*/5 * * * * PATH=${PATH}:/usr/sbin chef-client > /tmp/chef.log.`date "+\%H\%M\%S"` 2>&1' | crontab''',note='switch crontab on ' + machine)
		else:
			# As above, but just for role.json
			shutit_chefwkstn_session.send('rm -f /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json.bak && cp /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json.bak')
			shutit_chefwkstn_session.send(r'''sed -i '/      "openshift_hosted_managed_registry": false,/a "control_upgrade": true, "control_upgrade_version": "14", "control_upgrade_flag": "/tmp/ready14", "upgrade_repos": [ { "name": "centos-openshift-origin14", "baseurl": "http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin14/", "gpgcheck": false } ],' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json''')
			shutit_chefwkstn_session.send('cat /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json && cat /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json | python -m json.tool')
			shutit_chefwkstn_session.send('knife role from file /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json')
			# Control plane first (master, etcd, certserver).
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				crontab_off(shutit_session)
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session.send('touch /tmp/ready14')
					shutit_session.send(r'chef-client | tee /tmp/chef.log.upgrade_13_14_control_plane.`date "+%H%M%S"` 2>&1')
			# Nodes: then go round nodes, add trigger file, run chef.
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_node']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('touch /tmp/ready14')
					shutit_session.send(r'chef-client | tee /tmp/chef.log.upgrade_13_14_node.`date "+%H%M%S"` 2>&1')
			# Then remove files, then revert and update and upload role.json on workstation.
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				shutit_session.send('rm -f /tmp/ready14')
			shutit_chefwkstn_session.send('rm -f /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json && mv /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json.bak /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json')
			shutit_chefwkstn_session.send("""sed -i 's/      "ose_major_version": "1.3",/      "ose_major_version": "1.4",/' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json""")
			shutit_chefwkstn_session.send("""sed -i 's/      "ose_version": "1.3.*",/      "ose_version": "1.4.1-1.el7",/' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json""")
			if shutit.cfg[module_id]['chef_deploy_containerized']:
				shutit_chefwkstn_session.send("""sed -i 's/      "openshift_docker_image_version": .*/      "openshift_docker_image_version": "v1.4.1",/' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json""")
			shutit_chefwkstn_session.send('knife role from file /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json')
			# Re-run chef-client to ensure upgrade has gone ok and chef can re-run.
			for machine in sorted(test_config_module.machines.keys()):
				if (test_config_module.machines[machine]['is_master'] or
				    test_config_module.machines[machine]['is_etcd'] or
				    test_config_module.machines[machine]['is_certificate_server'] or
				    test_config_module.machines[machine]['is_node']):
					shutit_session = shutit_sessions[machine]
					shutit_session.send(r'chef-client | tee /tmp/chef.log.upgrade_13_14_post_upgrade.`date "+%H%M%S"` 2>&1')
		# Now we are ready to run tests.
		# have we upgraded? TODO: across all boxen?
		for machine in sorted(test_config_module.machines.keys()):
			assert check_version(shutit_sessions['master1'],'1.4'), shutit.pause_point("assertion failure: shutit_sessions['master1'],'1.4'")
			shutit_session = shutit_sessions[machine]
			crontab_on(shutit_session)
		shutit_openshift_cluster_test.test_cluster(shutit, shutit_sessions, shutit_master1_session, test_config_module)

	# 1.4 => 1.5
	if shutit.cfg[module_id]['do_upgrade_14_15']:
		assert check_version(shutit_sessions['master1'],'1.4'), shutit.pause_point("assertion failure: shutit_sessions['master1'],'1.4'")
		if shutit.cfg[module_id]['chef_deploy_method'] == 'solo':
			# Control plane first (master, etcd, certserver).
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				crontab_off(shutit_session)
				# Change the environment file
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('rm -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak && cp /root/chef-solo-example/environments/ocp-cluster-environment.json /root/chef-solo-example/environments/ocp-cluster-environment.json.bak')
					shutit_session.send(r'''sed -i '/      "openshift_hosted_managed_registry": false,/a "control_upgrade": true, "control_upgrade_version": "15", "control_upgrade_flag": "/tmp/ready15", "upgrade_repos": [ { "name": "centos-openshift-origin15", "baseurl": "http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin15/", "gpgcheck": false } ],' /root/chef-solo-example/environments/ocp-cluster-environment.json''')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
			for machine in sorted(test_config_module.machines.keys()):
				# Touch files
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('touch /tmp/ready15')
			for machine in sorted(test_config_module.machines.keys()):
				# Touch files
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb | tee /tmp/chef.log.upgrade_14_15_control_plane.`date "+%H%M%S"` 2>&1''')
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('mv -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak /root/chef-solo-example/environments/ocp-cluster-environment.json')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send('rm -f /tmp/ready15')
			# Nodes
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_node']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('rm -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak && cp /root/chef-solo-example/environments/ocp-cluster-environment.json /root/chef-solo-example/environments/ocp-cluster-environment.json.bak')
					shutit_session.send(r'''sed -i '/      "openshift_hosted_managed_registry": false,/a "control_upgrade": true, "control_upgrade_version": "15", "control_upgrade_flag": "/tmp/ready15", "upgrade_repos": [ { "name": "centos-openshift-origin15", "baseurl": "http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin15/", "gpgcheck": false } ],' /root/chef-solo-example/environments/ocp-cluster-environment.json''')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send('touch /tmp/ready15')
					shutit_session.send('''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb | tee /tmp/chef.log.upgrade_14_15_node.`date "+%H%M%S"` 2>&1''')
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_node']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('mv -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak /root/chef-solo-example/environments/ocp-cluster-environment.json')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send('rm -f /tmp/ready15')
			for machine in sorted(test_config_module.machines.keys()):
				# Revert
				if (test_config_module.machines[machine]['is_master'] or
				    test_config_module.machines[machine]['is_etcd'] or
				    test_config_module.machines[machine]['is_certificate_server'] or
				    test_config_module.machines[machine]['is_node']):
					shutit_session = shutit_sessions[machine]
					shutit_session.send("""sed -i 's/      "ose_major_version": "1.4",/      "ose_major_version": "1.5",/' /root/chef-solo-example/environments/ocp-cluster-environment.json""")
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send("""sed -i 's/      "ose_version": "1.4.*",/      "ose_version": "1.5.1-1.el7",/' /root/chef-solo-example/environments/ocp-cluster-environment.json""")
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					if shutit.cfg[module_id]['chef_deploy_containerized']:
						shutit_session.send("""sed -i 's/      "openshift_docker_image_version": .*/      "openshift_docker_image_version": "v1.5.1",/' /root/chef-solo-example/environments/ocp-cluster-environment.json""")
						shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				shutit_session.send('''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb | tee /tmp/chef.log.upgrade_14_15_post_upgrade.`date "+%H%M%S"` 2>&1''')
		else:
			# As above, but just for role.json
			shutit_chefwkstn_session.send('rm -f /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json.bak && cp /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json.bak')
			shutit_chefwkstn_session.send(r'''sed -i '/      "openshift_hosted_managed_registry": false,/a "control_upgrade": true, "control_upgrade_version": "15", "control_upgrade_flag": "/tmp/ready15", "upgrade_repos": [ { "name": "centos-openshift-origin15", "baseurl": "http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin15/", "gpgcheck": false } ],' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json''')
			shutit_chefwkstn_session.send('cat /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json && cat /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json | python -m json.tool')
			shutit_chefwkstn_session.send('knife role from file /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json')
			# Control plane first (master, etcd, certserver).
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				crontab_off(shutit_session)
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('touch /tmp/ready15')
					shutit_session.send(r'chef-client | tee /tmp/chef.log.upgrade_14_15_control_plane.`date "+%H%M%S"` 2>&1')
			# Nodes: then go round nodes, add trigger file, run chef.
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_node']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('touch /tmp/ready15')
					shutit_session.send(r'chef-client | tee /tmp/chef.log.upgrade_14_15_node.`date "+%H%M%S"` 2>&1')
			# Then remove files, then revert and update and upload role.json on workstation.
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				shutit_session.send('rm -f /tmp/ready15')
			shutit_chefwkstn_session.send('rm -f /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json && mv /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json.bak /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json')
			shutit_chefwkstn_session.send("""sed -i 's/      "ose_major_version": "1.4",/      "ose_major_version": "1.5",/' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json""")
			shutit_chefwkstn_session.send("""sed -i 's/      "ose_version": "1.4.*",/      "ose_version": "1.5.1-1.el7",/' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json""")
			if shutit.cfg[module_id]['chef_deploy_containerized']:
				shutit_chefwkstn_session.send("""sed -i 's/      "openshift_docker_image_version": .*/      "openshift_docker_image_version": "v1.5.1",/' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json""")
			shutit_chefwkstn_session.send('knife role from file /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json')
			# Re-run chef-client to ensure upgrade has gone ok and chef can re-run.
			for machine in sorted(test_config_module.machines.keys()):
				if (test_config_module.machines[machine]['is_master'] or
				    test_config_module.machines[machine]['is_etcd'] or
				    test_config_module.machines[machine]['is_certificate_server'] or
				    test_config_module.machines[machine]['is_node']):
					shutit_session = shutit_sessions[machine]
					shutit_session.send(r'chef-client | tee /tmp/chef.log.upgrade_14_15_post_upgrade.`date "+%H%M%S"` 2>&1')
		# Now we are ready to run tests.
		for machine in sorted(test_config_module.machines.keys()):
			assert check_version(shutit_sessions['master1'],'1.5'), shutit.pause_point("assertion failure: shutit_sessions['master1'],'1.5'")
			shutit_session = shutit_sessions[machine]
			crontab_on(shutit_session)
		shutit_openshift_cluster_test.test_cluster(shutit, shutit_sessions, shutit_master1_session, test_config_module)

	# 1.5 => 3.6
	if shutit.cfg[module_id]['do_upgrade_15_36']:
		assert check_version(shutit_sessions['master1'],'1.5'), shutit.pause_point("assertion failure: shutit_sessions['master1'],'1.5'")
		# https://buildlogs.centos.org/centos/7/paas/x86_64/openshift-origin/
		# 3.6.1-1.0
		if shutit.cfg[module_id]['chef_deploy_method'] == 'solo':
			# Control plane first (master, etcd, certserver).
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				crontab_off(shutit_session)
				# Change the environment file
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('rm -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak && cp /root/chef-solo-example/environments/ocp-cluster-environment.json /root/chef-solo-example/environments/ocp-cluster-environment.json.bak')
					shutit_session.send(r'''sed -i '/      "openshift_hosted_managed_registry": false,/a "control_upgrade": true, "control_upgrade_version": "36", "control_upgrade_flag": "/tmp/ready36", "upgrade_repos": [ { "name": "centos-openshift-origin36", "baseurl": "http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin36/", "gpgcheck": false } ],' /root/chef-solo-example/environments/ocp-cluster-environment.json''')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
			for machine in sorted(test_config_module.machines.keys()):
				# Touch files
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('touch /tmp/ready36')
			for machine in sorted(test_config_module.machines.keys()):
				# Touch files
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb | tee /tmp/chef.log.upgrade_15_36_control_plane.`date "+%H%M%S"` 2>&1''')
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('mv -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak /root/chef-solo-example/environments/ocp-cluster-environment.json')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send('rm -f /tmp/ready36')
			# Nodes
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_node']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('rm -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak && cp /root/chef-solo-example/environments/ocp-cluster-environment.json /root/chef-solo-example/environments/ocp-cluster-environment.json.bak')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send(r'''sed -i '/      "openshift_hosted_managed_registry": false,/a "control_upgrade": true, "control_upgrade_version": "36", "control_upgrade_flag": "/tmp/ready36", "upgrade_repos": [ { "name": "centos-openshift-origin36", "baseurl": "http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin36/", "gpgcheck": false } ],' /root/chef-solo-example/environments/ocp-cluster-environment.json''')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send('touch /tmp/ready36')
					shutit_session.send('''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb | tee /tmp/chef.log.upgrade_15_36_node.`date "+%H%M%S"` 2>&1''')
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_node']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('mv -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak /root/chef-solo-example/environments/ocp-cluster-environment.json')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send('rm -f /tmp/ready36')
			for machine in sorted(test_config_module.machines.keys()):
				# Revert
				if (test_config_module.machines[machine]['is_master'] or
				    test_config_module.machines[machine]['is_etcd'] or
				    test_config_module.machines[machine]['is_certificate_server'] or
				    test_config_module.machines[machine]['is_node']):
					shutit_session = shutit_sessions[machine]
					shutit_session.send("""sed -i 's/      "ose_major_version": "1.5",/      "ose_major_version": "3.6",/' /root/chef-solo-example/environments/ocp-cluster-environment.json""")
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send("""sed -i 's/      "ose_version": "1.5.*",/      "ose_version": "3.6.1-1.0.008f2d5",/' /root/chef-solo-example/environments/ocp-cluster-environment.json""")
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					if shutit.cfg[module_id]['chef_deploy_containerized']:
						shutit_session.send("""sed -i 's/      "openshift_docker_image_version": .*/      "openshift_docker_image_version": "v3.6.1",/' /root/chef-solo-example/environments/ocp-cluster-environment.json""")
						shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				shutit_session.send('''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb | tee /tmp/chef.log.upgrade_15_36_post_upgrade.`date "+%H%M%S"` 2>&1''')
		else:
			# As above, but just for role.json
			shutit_chefwkstn_session.send('rm -f /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json.bak && cp /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json.bak')
			shutit_chefwkstn_session.send(r'''sed -i '/      "openshift_hosted_managed_registry": false,/a "control_upgrade": true, "control_upgrade_version": "36", "control_upgrade_flag": "/tmp/ready36", "upgrade_repos": [ { "name": "centos-openshift-origin36", "baseurl": "http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin36/", "gpgcheck": false } ],' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json''')
			shutit_chefwkstn_session.send('cat /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json && cat /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json | python -m json.tool')
			shutit_chefwkstn_session.send('knife role from file /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json')
			# Control plane first (master, etcd, certserver).
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				crontab_off(shutit_session)
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('touch /tmp/ready36')
					shutit_session.send(r'chef-client | tee /tmp/chef.log.upgrade_15_36_control_plane.`date "+%H%M%S"` 2>&1')
			# Nodes: then go round nodes, add trigger file, run chef.
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_node']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('touch /tmp/ready36')
					shutit_session.send(r'chef-client | tee /tmp/chef.log.upgrade_15_36_node.`date "+%H%M%S"` 2>&1')
			# Then remove files, then revert and update and upload role.json on workstation.
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				shutit_session.send('rm -f /tmp/ready36')
			shutit_chefwkstn_session.send('rm -f /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json && mv /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json.bak /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json')
			shutit_chefwkstn_session.send("""sed -i 's/      "ose_major_version": "1.5",/      "ose_major_version": "3.6",/' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json""")
			shutit_chefwkstn_session.send("""sed -i 's/      "ose_version": "1.5.*",/      "ose_version": "3.6.1-1.0.008f2d5",/' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json""")
			if shutit.cfg[module_id]['chef_deploy_containerized']:
				shutit_chefwkstn_session.send("""sed -i 's/      "openshift_docker_image_version": .*/      "openshift_docker_image_version": "v3.6.1",/' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json""")
			shutit_chefwkstn_session.send('knife role from file /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json')
			# Re-run chef-client to ensure upgrade has gone ok and chef can re-run.
			for machine in sorted(test_config_module.machines.keys()):
				if (test_config_module.machines[machine]['is_master'] or
				    test_config_module.machines[machine]['is_etcd'] or
				    test_config_module.machines[machine]['is_certificate_server'] or
				    test_config_module.machines[machine]['is_node']):
					shutit_session = shutit_sessions[machine]
					shutit_session.send(r'chef-client | tee /tmp/chef.log.upgrade_15_36_post_upgrade.`date "+%H%M%S"` 2>&1')
		# Now we are ready to run tests.
		for machine in sorted(test_config_module.machines.keys()):
			assert check_version(shutit_sessions['master1'],'3.6'), shutit.pause_point("assertion failure: shutit_sessions['master1'],'3.6'")
			shutit_session = shutit_sessions[machine]
			crontab_on(shutit_session)
		shutit_openshift_cluster_test.test_cluster(shutit, shutit_sessions, shutit_master1_session, test_config_module)

	# 3.6 => 3.7
	if shutit.cfg[module_id]['do_upgrade_36_37']:
		assert check_version(shutit_sessions['master1'],'3.6'), shutit.pause_point("assertion failure: shutit_sessions['master1'],'3.6'")
		# https://buildlogs.centos.org/centos/7/paas/x86_64/openshift-origin/
		# origin-3.7.1-2.el7
		if shutit.cfg[module_id]['chef_deploy_method'] == 'solo':
			# Control plane first (master, etcd, certserver).
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				crontab_off(shutit_session)
				# Change the environment file
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('rm -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak && cp /root/chef-solo-example/environments/ocp-cluster-environment.json /root/chef-solo-example/environments/ocp-cluster-environment.json.bak')
					shutit_session.send(r'''sed -i '/      "openshift_hosted_managed_registry": false,/a "control_upgrade": true, "control_upgrade_version": "37", "control_upgrade_flag": "/tmp/ready37", "upgrade_repos": [ { "name": "centos-openshift-origin37", "baseurl": "http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin37/", "gpgcheck": false } ],' /root/chef-solo-example/environments/ocp-cluster-environment.json''')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
			for machine in sorted(test_config_module.machines.keys()):
				# Touch files
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('touch /tmp/ready37')
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_etcd']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb | tee /tmp/chef.log.upgrade_36_37_upgrade_etcd.`date "+%H%M%S"` 2>&1''')
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb | tee /tmp/chef.log.upgrade_36_37_upgrade_control_plane.`date "+%H%M%S"` 2>&1''')
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('mv -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak /root/chef-solo-example/environments/ocp-cluster-environment.json')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send('rm -f /tmp/ready37')
			# Nodes
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_node']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('rm -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak && cp /root/chef-solo-example/environments/ocp-cluster-environment.json /root/chef-solo-example/environments/ocp-cluster-environment.json.bak')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send(r'''sed -i '/      "openshift_hosted_managed_registry": false,/a "control_upgrade": true, "control_upgrade_version": "37", "control_upgrade_flag": "/tmp/ready37", "upgrade_repos": [ { "name": "centos-openshift-origin37", "baseurl": "http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin37/", "gpgcheck": false } ],' /root/chef-solo-example/environments/ocp-cluster-environment.json''')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send('touch /tmp/ready37')
					shutit_session.send('''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb | tee /tmp/chef.log.upgrade_36_37_upgrade_node.`date "+%H%M%S"` 2>&1''')
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_node']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('mv -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak /root/chef-solo-example/environments/ocp-cluster-environment.json')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send('rm -f /tmp/ready37')
			for machine in sorted(test_config_module.machines.keys()):
				# Revert
				if (test_config_module.machines[machine]['is_master'] or
				    test_config_module.machines[machine]['is_etcd'] or
				    test_config_module.machines[machine]['is_certificate_server'] or
				    test_config_module.machines[machine]['is_node']):
					shutit_session = shutit_sessions[machine]
					shutit_session.send(r"""sed -i 's/      "ose_major_version": "3.6",/      "ose_major_version": "3.7",/' /root/chef-solo-example/environments/ocp-cluster-environment.json""")
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send("""sed -i 's/      "ose_version": "3.6.*",/      "ose_version": "3.7.2-1.el7.git.0.cd74924",/' /root/chef-solo-example/environments/ocp-cluster-environment.json""")
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					if shutit.cfg[module_id]['chef_deploy_containerized']:
						shutit_session.send("""sed -i 's/      "openshift_docker_image_version": .*/      "openshift_docker_image_version": "v3.7.2",/' /root/chef-solo-example/environments/ocp-cluster-environment.json""")
						shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				shutit_session.send('''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb | tee /tmp/chef.log.upgrade_36_37_post_upgrade.`date "+%H%M%S"` 2>&1''')
		else:
			# As above, but just for role.json
			shutit_chefwkstn_session.send('rm -f /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json.bak && cp /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json.bak')
			shutit_chefwkstn_session.send(r'''sed -i '/      "openshift_hosted_managed_registry": false,/a "control_upgrade": true, "control_upgrade_version": "37", "control_upgrade_flag": "/tmp/ready37", "upgrade_repos": [ { "name": "centos-openshift-origin37", "baseurl": "http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin37/", "gpgcheck": false } ],' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json''')
			shutit_chefwkstn_session.send('cat /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json && cat /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json | python -m json.tool')
			shutit_chefwkstn_session.send('knife role from file /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json')
			# Control plane first (master, etcd, certserver).
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				crontab_off(shutit_session)
				if test_config_module.machines[machine]['is_etcd']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('touch /tmp/ready37')
					shutit_session.send(r'chef-client | tee /tmp/chef.log.upgrade_36_37_upgrade_etcd.`date "+%H%M%S"` 2>&1')
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('touch /tmp/ready37')
					shutit_session.send(r'chef-client | tee /tmp/chef.log.upgrade_36_37_control_plane.`date "+%H%M%S"` 2>&1')
			# Nodes: then go round nodes, add trigger file, run chef.
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_node']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('touch /tmp/ready37')
					shutit_session.send(r'chef-client | tee /tmp/chef.log.upgrade_36_37_node.`date "+%H%M%S"` 2>&1')
			# Nodes: then go round nodes, add trigger file, run chef.
			# Then remove files, then revert and update and upload role.json on workstation.
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				shutit_session.send('rm -f /tmp/ready37')
			shutit_chefwkstn_session.send('rm -f /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json && mv /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json.bak /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json')
			shutit_chefwkstn_session.send(r"""sed -i 's/      "ose_major_version": "3.6",/      "ose_major_version": "3.7",/' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json""")
			shutit_chefwkstn_session.send("""sed -i 's/      "ose_version": "3.6.*",/      "ose_version": "3.7.2-1.el7.git.0.cd74924",/' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json""")
			if shutit.cfg[module_id]['chef_deploy_containerized']:
				shutit_chefwkstn_session.send("""sed -i 's/      "openshift_docker_image_version": .*/      "openshift_docker_image_version": "v3.7.2",/' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json""")
			shutit_chefwkstn_session.send('knife role from file /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json')
			# Re-run chef-client to ensure upgrade has gone ok and chef can re-run.
			for machine in sorted(test_config_module.machines.keys()):
				if (test_config_module.machines[machine]['is_master'] or
				    test_config_module.machines[machine]['is_etcd'] or
				    test_config_module.machines[machine]['is_certificate_server'] or
				    test_config_module.machines[machine]['is_node']):
					shutit_session = shutit_sessions[machine]
					shutit_session.send(r'chef-client | tee /tmp/chef.log.upgrade_36_37_post_upgrade.`date "+%H%M%S"` 2>&1')
		for machine in sorted(test_config_module.machines.keys()):
			assert check_version(shutit_sessions['master1'],'3.7'), shutit.pause_point("assertion failure: shutit_sessions['master1'],'3.7'")
		# IWT-5106 - restart on 3.7 as docker upgrade is disruptive
		for machine in sorted(test_config_module.machines.keys()):
			shutit_session = shutit_sessions[machine]
			if test_config_module.machines[machine]['is_master']:
				shutit_session.send('systemctl restart origin-master-api')
				shutit_session.send('systemctl restart origin-master-controllers')
			if test_config_module.machines[machine]['is_node']:
				shutit_session.send('systemctl restart origin-node',check_exit=False)
			crontab_on(shutit_session)
		redeploy_components(shutit_master1_session)
		time.sleep(2*60)
		shutit_openshift_cluster_test.test_cluster(shutit, shutit_sessions, shutit_master1_session, test_config_module)

	# 3.7 => 3.9
	if shutit.cfg[module_id]['do_upgrade_37_39']:
		assert check_version(shutit_sessions['master1'],'3.7'), shutit.pause_point("assertion failure: shutit_sessions['master1'],'3.7'")
		# https://buildlogs.centos.org/centos/7/paas/x86_64/openshift-origin/
		# https://buildlogs.centos.org/centos/7/paas/x86_64/openshift-origin39/
		# origin-master-3.9.0-1.el7.git.0.ba7faec.x86_64.rpm
		if shutit.cfg[module_id]['chef_deploy_method'] == 'solo':
			# Control plane first (master, etcd, certserver).
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				crontab_off(shutit_session)
				# Change the environment file
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('rm -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak && cp /root/chef-solo-example/environments/ocp-cluster-environment.json /root/chef-solo-example/environments/ocp-cluster-environment.json.bak')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send(r'''sed -i '/      "openshift_hosted_managed_registry": false,/a "control_upgrade": true, "control_upgrade_version": "39", "control_upgrade_flag": "/tmp/ready39", "upgrade_repos": [ { "name": "centos-openshift-origin38", "baseurl": "http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin38/", "gpgcheck": false }, { "name": "centos-openshift-origin39", "baseurl": "http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin39/", "gpgcheck": false } ],' /root/chef-solo-example/environments/ocp-cluster-environment.json''')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
			for machine in sorted(test_config_module.machines.keys()):
				# Touch files
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('touch /tmp/ready39')
					shutit_session.send(r'''#echo '*/5 * * * * PATH=${PATH}:/usr/sbin chef-client > /tmp/chef.log.`date "+\%H\%M\%S"` 2>&1' | crontab''',note='switch off crontab on ' + machine)
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_etcd']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb | tee /tmp/chef.log.upgrade_37_39_upgrade_etcd.`date "+%H%M%S"` 2>&1''')
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb | tee /tmp/chef.log.upgrade_37_39_upgrade_control_plane.`date "+%H%M%S"` 2>&1''')
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_etcd'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('mv -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak /root/chef-solo-example/environments/ocp-cluster-environment.json')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send('rm -f /tmp/ready39')
			# Nodes
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_node']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('rm -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak && cp /root/chef-solo-example/environments/ocp-cluster-environment.json /root/chef-solo-example/environments/ocp-cluster-environment.json.bak')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send(r'''sed -i '/      "openshift_hosted_managed_registry": false,/a "control_upgrade": true, "control_upgrade_version": "39", "control_upgrade_flag": "/tmp/ready39", "upgrade_repos": [ { "name": "centos-openshift-origin38", "baseurl": "http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin38/", "gpgcheck": false }, { "name": "centos-openshift-origin39", "baseurl": "http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin39/", "gpgcheck": false } ],' /root/chef-solo-example/environments/ocp-cluster-environment.json''')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send('touch /tmp/ready39')
					shutit_session.send('''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb | tee /tmp/chef.log.upgrade_37_39_upgrade_node.`date "+%H%M%S"` 2>&1''')
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_node']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('mv -f /root/chef-solo-example/environments/ocp-cluster-environment.json.bak /root/chef-solo-example/environments/ocp-cluster-environment.json')
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send('rm -f /tmp/ready39')
			for machine in sorted(test_config_module.machines.keys()):
				# Revert
				if (test_config_module.machines[machine]['is_master'] or
				    test_config_module.machines[machine]['is_etcd'] or
				    test_config_module.machines[machine]['is_certificate_server'] or
				    test_config_module.machines[machine]['is_node']):
					shutit_session = shutit_sessions[machine]
					shutit_session.send(r"""sed -i 's/      "ose_major_version": "3.7",/      "ose_major_version": "3.9",/' /root/chef-solo-example/environments/ocp-cluster-environment.json""")
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					shutit_session.send("""sed -i 's/      "ose_version": "3.7.*",/      "ose_version": "3.9.0-1.el7.git.0.ba7faec",/' /root/chef-solo-example/environments/ocp-cluster-environment.json""")
					shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
					if shutit.cfg[module_id]['chef_deploy_containerized']:
						shutit_session.send("""sed -i 's/      "openshift_docker_image_version": .*/      "openshift_docker_image_version": "v3.9.0",/' /root/chef-solo-example/environments/ocp-cluster-environment.json""")
						shutit_session.send('cat /root/chef-solo-example/environments/ocp-cluster-environment.json && cat /root/chef-solo-example/environments/ocp-cluster-environment.json | python -m json.tool')
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				shutit_session.send('''chef-solo --environment ocp-cluster-environment -o 'recipe[cookbook-openshift3]' -c ~/chef-solo-example/solo.rb | tee /tmp/chef.log.upgrade_37_39_post_upgrade.`date "+%H%M%S"` 2>&1''')
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				shutit_session.send(r'''echo '*/5 * * * * PATH=${PATH}:/usr/sbin chef-client > /tmp/chef.log.`date "+\%H\%M\%S"` 2>&1' | crontab''',note='switch crontab on ' + machine)
		else:
			# As above, but just for role.json
			shutit_chefwkstn_session.send('rm -f /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json.bak && cp /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json.bak')
			shutit_chefwkstn_session.send(r'''sed -i '/      "openshift_hosted_managed_registry": false,/a "control_upgrade": true, "control_upgrade_version": "39", "control_upgrade_flag": "/tmp/ready39", "upgrade_repos": [ { "name": "centos-openshift-origin38", "baseurl": "http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin38/", "gpgcheck": false }, { "name": "centos-openshift-origin39", "baseurl": "http://mirror.centos.org/centos/7/paas/x86_64/openshift-origin39/", "gpgcheck": false } ],' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json''')
			shutit_chefwkstn_session.send('cat /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json && cat /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json | python -m json.tool')
			shutit_chefwkstn_session.send('knife role from file /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json')
			# Control plane first (master, etcd, certserver).
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				crontab_off(shutit_session)
				if test_config_module.machines[machine]['is_etcd']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('touch /tmp/ready39')
					shutit_session.send(r'chef-client | tee /tmp/chef.log.upgrade_37_39_upgrade_etcd.`date "+%H%M%S"` 2>&1')
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_master'] or test_config_module.machines[machine]['is_certificate_server']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('touch /tmp/ready39')
					shutit_session.send(r'chef-client | tee /tmp/chef.log.upgrade_37_39_control_plane.`date "+%H%M%S"` 2>&1')
			# Nodes: then go round nodes, add trigger file, run chef.
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_node']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('touch /tmp/ready39')
					shutit_session.send(r'chef-client | tee /tmp/chef.log.upgrade_37_39_node.`date "+%H%M%S"` 2>&1')
			# Nodes: then go round nodes, add trigger file, run chef.
			for machine in sorted(test_config_module.machines.keys()):
				if test_config_module.machines[machine]['is_node']:
					shutit_session = shutit_sessions[machine]
					shutit_session.send('touch /tmp/ready39')
					shutit_session.send(r'chef-client | tee /tmp/chef.log.upgrade_37_39_node.`date "+%H%M%S"` 2>&1')
			# Nodes: then go round nodes, add trigger file, run chef.
			# Then remove files, then revert and update and upload role.json on workstation.
			for machine in sorted(test_config_module.machines.keys()):
				shutit_session = shutit_sessions[machine]
				shutit_session.send('rm -f /tmp/ready39')
			shutit_chefwkstn_session.send('rm -f /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json && mv /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json.bak /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json')
			shutit_chefwkstn_session.send(r"""sed -i 's/      "ose_major_version": "3.7",/      "ose_major_version": "3.9",/' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json""")
			shutit_chefwkstn_session.send("""sed -i 's/      "ose_version": "3.7.*",/      "ose_version": "3.9.0-1.el7.git.0.ba7faec",/' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json""")
			if shutit.cfg[module_id]['chef_deploy_containerized']:
				shutit_chefwkstn_session.send("""sed -i 's/      "openshift_docker_image_version": .*/      "openshift_docker_image_version": "v3.9.0",/' /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json""")
			shutit_chefwkstn_session.send('knife role from file /root/chef-repo/cookbooks/cookbook-openshift3/roles/role.json')
			# Re-run chef-client to ensure upgrade has gone ok and chef can re-run.
			for machine in sorted(test_config_module.machines.keys()):
				if (test_config_module.machines[machine]['is_master'] or
				    test_config_module.machines[machine]['is_etcd'] or
				    test_config_module.machines[machine]['is_certificate_server'] or
				    test_config_module.machines[machine]['is_node']):
					shutit_session = shutit_sessions[machine]
					shutit_session.send(r'chef-client | tee /tmp/chef.log.upgrade_37_39_post_upgrade.`date "+%H%M%S"` 2>&1')
		for machine in sorted(test_config_module.machines.keys()):
			assert check_version(shutit_sessions['master1'],'3.9'), shutit.pause_point("assertion failure: shutit_sessions['master1'],'3.9'")
			shutit_session = shutit_sessions[machine]
			crontab_on(shutit_session)
		shutit_openshift_cluster_test.test_cluster(shutit, shutit_sessions, shutit_master1_session, test_config_module)

