def do_flux(s):
	s.send('wget https://github.com/weaveworks/flux/releases/download/1.9.0/fluxctl_linux_amd64')
	s.send('chmod +x fluxctl_linux_amd64')
	s.send('mv fluxctl_linux_amd64 fluxctl')
	if not s.command_available('helm'):
		# https://docs.helm.sh/using_helm/#installing-the-helm-client
		s.send('curl https://raw.githubusercontent.com/helm/helm/master/scripts/get | bash')
	# https://github.com/weaveworks/flux/blob/master/site/helm-get-started.md
	# https://github.com/weaveworks/flux/blob/master/site/fluxctl.md
	s.send('helm init --skip-refresh --upgrade --service-account tiller')
	s.send('helm repo add weaveworks https://weaveworks.github.io/flux')
	s.send('kubectl apply -f https://raw.githubusercontent.com/weaveworks/flux/master/deploy-helm/flux-helm-release-crd.yaml')
	s.send('helm upgrade -i flux --set helmOperator.create=true --set helmOperator.createCRD=false --set git.url=git@github.com:imiell/flux-get-started --namespace flux weaveworks/flux')
	s.send('oc adm policy add-scc-to-user anyuid system:serviceaccount:flux:flux')
	s.send('export FLUX_FORWARD_NAMESPACE=flux')
	s.send('fluxctl identity')
	s.pause_point('add flux shutit key above to github and continue https://github.com/YOURUSER/flux-get-started/settings/keys/new')
	#s.send('kubectl create secret generic flux-git-deploy --from-file /tmp/pubkey -n flux')
	#s.pause_point('Now add the secret to the flux-deployment.yaml manifest')
