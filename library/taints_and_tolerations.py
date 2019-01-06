def do_taints_and_tolerations_example(s):
	# https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/#example-use-cases
	# TODO: require n nodes, where n>1?
	s.send('mkdir taint_example')
	s.send('cd taint_example')
	# TODO: create a specific namespace
	s.send('kubectl taint nodes node1 dedicated=postgresql:NoSchedule')
	# https://docs.openshift.com/enterprise/3.1/using_images/db_images/postgresql.html
	s.send('oc new-app -e POSTGRESQL_USER=<username>,POSTGRESQL_PASSWORD=postgresql,POSTGRESQL_DATABASE=mydb registry.access.redhat.com/rhscl/postgresql-94-rhel7')
	# TODO: edit the pod, and check node1 status
	s.pause_point('# TODO: edit the pod, and check node1 status')
