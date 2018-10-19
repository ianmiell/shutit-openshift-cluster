def do_controller(s):
	s.send('go version')
	s.send('go env')
	s.send('go get k8s.io/sample-controller')
	s.send('cd ${GOPATH}/src/k8s.io/sample-controller')
	# Build crd
	s.send('kubectl apply -f artifacts/examples/crd-validation.yaml')
	# Build the controller.
	s.send('go build .')
	s.send('nohup ./sample-controller -kubeconfig ~/.kube/config -logtostderr=true &')
	s.send('kubectl apply -f artifacts/examples/example-foo.yaml')
	s.pause_point('')


Try on Friday 19th Oct:
go get k8s.io/sample-controller
cd $GOPATH/src/k8s.io/sample-controller
go build -o ctrl .
kubectl apply -f artifacts/examples/crd-validation.yaml
nohup ./ctrl -kubeconfig ~/.kube/config  -logtostderr=true &
kubectl apply -f artifacts/examples/example-foo.yaml
kubectl get pods
