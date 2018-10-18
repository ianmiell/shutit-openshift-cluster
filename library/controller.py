def do_controller(s):
	s.send('go version')
	s.send('go env')
	s.send('go get k8s.io/sample-controller')
	s.send('go get github.com/kubernetes/sample-controller')
	s.send('cd $GOROOT/src/k8s.io/sample-controller')
	# Build crd
	s.send('kubectl apply -f artifacts/examples/crd-validation.yaml')
	# Build the controller.
	s.send('go build .')
	s.send('nohup ./sample-controller -kubeconfig ~/.kube/config -logtostderr=true &')
	s.send('kubectl apply -f artifacts/examples/example-foo.yaml')
	s.pause_point('')
