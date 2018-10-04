import check_nodes
import logging

def do_run_apps(shutit_master1_session, shutit):
	while True:
		ok = False
		count = 20
		shutit.log('Iterations left: ' + str(count),level=logging.INFO)
		while True:
			status = shutit_master1_session.send_and_get_output("""oc --config=/etc/origin/master/admin.kubeconfig get pods | grep ^router- | grep -v deploy | awk '{print $3}' | grep -v Terminating""")
			if count == 0:
				break
			count -= 1
			if status == 'Running':
				shutit_master1_session.send('#' + status)
				status = shutit_master1_session.send_and_get_output("""oc --config=/etc/origin/master/admin.kubeconfig get pods | grep ^router- | grep -v deploy | awk '{print $3}' | grep -v Terminating""")
				ok = True
				break
			elif status in ('Error','ImagePullBackOff'):
				shutit_master1_session.send('oc --config=/etc/origin/master/admin.kubeconfig deploy router --cancel || oc --config=/etc/origin/master/admin.kubeconfig rollout cancel dc/router')
				shutit_master1_session.send('sleep 15')
				shutit_master1_session.send('oc --config=/etc/origin/master/admin.kubeconfig deploy router --retry || oc --config=/etc/origin/master/admin.kubeconfig deploy router --latest || oc --config=/etc/origin/master/admin.kubeconfig rollout retry dc/router || oc --config=/etc/origin/master/admin.kubeconfig rollout latest dc/router')
			else:
				shutit_master1_session.send('sleep 15')
				shutit_master1_session.send('oc --config=/etc/origin/master/admin.kubeconfig describe pods || true')
		shutit.log('router while loop done.')
		if ok:
			shutit.log('Broken out of outer loop, router should now be OK.')
			break
		shutit_master1_session.send("""oc --config=/etc/origin/master/admin.kubeconfig get pods | grep -w ^router | awk '{print $1}' | xargs oc --config=/etc/origin/master/admin.kubeconfig delete pod || true""")
		shutit_master1_session.send('oc --config=/etc/origin/master/admin.kubeconfig deploy router --retry || oc --config=/etc/origin/master/admin.kubeconfig deploy router --latest || oc --config=/etc/origin/master/admin.kubeconfig rollout retry dc/router || oc --config=/etc/origin/master/admin.kubeconfig rollout latest dc/router')
		check_nodes.schedule_nodes(test_config_module, shutit_master1_session)
	while True:
		ok = False
		count = 20
		shutit.log('Iterations left: ' + str(count),level=logging.INFO)
		while True:
			# Either registry or docker-registry (more recently?)
			status = shutit_master1_session.send_and_get_output("""oc --config=/etc/origin/master/admin.kubeconfig get pods | grep ^registry- | grep -v deploy | awk '{print $3}' | grep -v Terminating""")
			if status == '':
				status = shutit_master1_session.send_and_get_output("""oc --config=/etc/origin/master/admin.kubeconfig get pods | grep ^docker-registry- | grep -v deploy | awk '{print $3}' | grep -v Terminating""")
			if count == 0:
				break
			count -= 1
			if status == 'Running':
				ok = True
				break
			if status in ('Error','ImagePullBackOff'):
				shutit_master1_session.send('oc --config=/etc/origin/master/admin.kubeconfig deploy docker-registry --cancel || oc --config=/etc/origin/master/admin.kubeconfig rollout cancel dc/docker-registry')
				shutit_master1_session.send('sleep 14')
				shutit_master1_session.send('oc --config=/etc/origin/master/admin.kubeconfig deploy docker-registry --retry || oc --config=/etc/origin/master/admin.kubeconfig deploy docker-registry --latest || oc --config=/etc/origin/master/admin.kubeconfig rollout retry dc/docker-registry || oc --config=/etc/origin/master/admin.kubeconfig rollout latest dc/docker-registry')
			else:
				shutit_master1_session.send('sleep 14')
				deploy_status = shutit_master1_session.send_and_get_output("""oc --config=/etc/origin/master/admin.kubeconfig get pods | grep ^registry- | grep -w deploy | awk '{print $3}' | grep -v Terminating""")
				if deploy_status == 'Error':
					shutit_session.send('oc rollout latest dc/docker-registry')
			shutit.log('registry while loop done.')
		if ok:
			shutit.log('Broken out of outer loop, registry should now be OK.')
			break
		else:
			# Try and rectify
			shutit_master1_session.send("""oc --config=/etc/origin/master/admin.kubeconfig get pods | grep -w registry | awk '{print $1}' | xargs oc --config=/etc/origin/master/admin.kubeconfig delete pod || true""")
			shutit_master1_session.send('oc --config=/etc/origin/master/admin.kubeconfig deploy docker-registry --retry || oc --config=/etc/origin/master/admin.kubeconfig deploy docker-registry --latest || oc --config=/etc/origin/master/admin.kubeconfig rollout retry dc/docker-registry || oc --config=/etc/origin/master/admin.kubeconfig rollout latest dc/docker-registry')
			check_nodes.schedule_nodes(test_config_module, shutit_master1_session)

