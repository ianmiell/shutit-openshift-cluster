import logging
import time

def test_cluster(shutit, shutit_sessions, shutit_master1_session, test_config_module):

	for machine in test_config_module.machines.keys():
		shutit_session = shutit_sessions[machine]
		shutit_session.send('cd /etc/sysconfig')
		shutit_session.send(r'''for f in $(ls origin*); do sed -i 's/OPTIONS=.*--loglevel=.*/OPTIONS="--loglevel=8"/' $f; done''')
		shutit_session.send(r'''systemctl restart origin-master-api''', check_exit=False)
		shutit_session.send(r'''systemctl restart origin-master-controllers''', check_exit=False)
		shutit_session.send(r'''systemctl restart origin-master''', check_exit=False)
		shutit_session.send(r'''systemctl restart origin-node''', check_exit=False)
		shutit_session.send('cd -')
	shutit_master1_session.send('sleep 600')

	shutit_session = shutit_master1_session
	# Create a mysql application
	if shutit_session.send_and_get_output('oc get projects | grep mysql | wc -l') == '0':
		shutit_session.send('oc adm new-project mysql')
	ok = False
	while not ok:
		count = 80
		shutit.log('Iterations left: ' + str(count),level=logging.INFO)
		# Destroy all...
		shutit_session.send('oc --config=/etc/origin/master/admin.kubeconfig delete svc mysql -n mysql', check_exit=False)
		shutit_session.send('oc --config=/etc/origin/master/admin.kubeconfig delete dc mysql -n mysql', check_exit=False)
		shutit_session.send('oc --config=/etc/origin/master/admin.kubeconfig delete is mysql -n mysql', check_exit=False)
		shutit_session.send('''oc --config=/etc/origin/master/admin.kubeconfig get pods -n mysql | grep mysql | awk '{print $1}' | xargs -n1 oc --config=/etc/origin/master/admin.kubeconfig delete pod -n mysql || true''')
		# --allow-missing-images has been seen to be needed very occasionally.
		shutit_session.send('oc --config=/etc/origin/master/admin.kubeconfig new-app -e=MYSQL_ROOT_PASSWORD=root mysql --allow-missing-images -n mysql')
		while True:
			if count == 0:
				break
			count -= 1
			# Sometimes terminating containers don't go away quickly.
			status = shutit_session.send_and_get_output("""oc --config=/etc/origin/master/admin.kubeconfig get pods -n mysql | grep ^mysql- | grep -v deploy | awk '{print $3}' | grep -v Terminating""")
			if status == 'Running':
				ok = True
				break
			elif status == 'Error':
				break
			elif status == 'ImagePullBackOff':
				shutit_session.send('oc --config=/etc/origin/master/admin.kubeconfig deploy mysql --cancel -n mysql || oc --config=/etc/origin/master/admin.kubeconfig  rollout cancel dc/mysql -n mysql')
				shutit_session.send('sleep 15')
				shutit_session.send('oc --config=/etc/origin/master/admin.kubeconfig deploy mysql --retry -n mysql || oc --config=/etc/origin/master/admin.kubeconfig deploy mysql --latest -n mysql || oc --config=/etc/origin/master/admin.kubeconfig rollout retry dc/mysql -n mysql || oc --config=/etc/origin/master/admin.kubeconfig rollout latest dc/mysql -n mysql')
			# Check on deployment
			deploy_status = shutit_session.send_and_get_output("""oc --config=/etc/origin/master/admin.kubeconfig get pods -n mysql | grep ^mysql- | grep -w deploy | awk '{print $3}' | grep -v Terminating""")
			# If deploy has errored...
			if deploy_status == 'Error':
				# Try and rollout latest, ensure it's been cancelled and roll out again.
				shutit_session.send('oc rollout cancel dc/mysql -n mysql', check_exit=False)
				shutit_session.send('oc rollout latest dc/mysql -n mysql')
			# For debug/info purposes.
			shutit_session.send('oc --config=/etc/origin/master/admin.kubeconfig get pods -n mysql | grep ^mysql',check_exit=False)
			shutit_session.send('sleep 15')
	podname = shutit_session.send_and_get_output("""oc --config=/etc/origin/master/admin.kubeconfig get pods -n mysql | grep mysql | grep -v deploy | awk '{print $1}' | tail -1""")
	time.sleep(30) # pause to allow resolve to work ok
	# exec and check hosts google.com and kubernetes.default.svc.cluster.local
	# ping has been removed!
	shutit_session.send("""oc --config=/etc/origin/master/admin.kubeconfig -n mysql exec -ti """ + podname + """ -- /bin/sh -c 'resolveip google.com'""")
	for addr in ('kubernetes.default.svc','kubernetes.default.svc.cluster.local'):
		if shutit_session.send_and_get_output("""oc --config=/etc/origin/master/admin.kubeconfig -n mysql exec -ti """ + podname + """ -- /bin/sh -c 'resolveip """ + addr + """ -s'""") != '172.30.0.1':
			shutit_session.pause_point('kubernetes.default.svc.cluster.local did not resolve correctly')
