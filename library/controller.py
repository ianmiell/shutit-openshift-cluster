def do_controller(s):
	s.send('wget -qO- https://dl.google.com/go/go1.10.3.linux-amd64.tar.gz | tar -zxvf -')
	s.send('mv go /usr/local')
	s.send('mkdir /root/go')
	s.send('export GOROOT=/usr/local/go')
	s.send('export GOPATH=/root/go')
	s.send('export PATH=$GOPATH/bin:$GOROOT/bin:$PATH')
	s.send('''cat >> /root/.profile << END
export GOROOT=/usr/local/go
export GOPATH=/root/go
export PATH=$GOPATH/bin:$GOROOT/bin:$PATH
END''')
	s.send('go version')
	s.send('go env')
	s.send('cd /root')
	s.send('git clone https://github.com/kubernetes/code-generator')
	s.send('git clone https://github.com/kubernetes/sample-controller')
	s.send('go get k8s.io/sample-controller')
	s.send('cd $GOROOT/src/k8s.io/sample-controller')
	s.send('go build .')
	s.pause_point('')
