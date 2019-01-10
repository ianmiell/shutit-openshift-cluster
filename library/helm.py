def do_helm(s):
	if not s.command_available('helm'):
		# https://docs.helm.sh/using_helm/#installing-the-helm-client
		s.send('curl https://raw.githubusercontent.com/helm/helm/master/scripts/get | bash')
	s.send('helm init')
	s.send('kubectl get pods --namespace kube-system')
