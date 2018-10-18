def do_controller(s):
	s.send('go version')
	s.send('go env')
	s.send('go get github.com/kubernetes/sample-controller')
	s.send('cd $GOROOT/src/k8s.io/sample-controller')
	s.send('go build .')
	s.pause_point('')
