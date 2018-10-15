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
	
