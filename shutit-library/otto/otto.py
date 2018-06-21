"""ShutIt module. See http://shutit.tk
"""

from shutit_module import ShutItModule


class otto(ShutItModule):

	def build(self, shutit):
		shutit.install('git')
		shutit.install('golang')
		shutit.install('golang-golang-x-tools')
		shutit.install('build-essential')
		shutit.install('zip')
		shutit.install('golang-golang-x-net-dev')
		shutit.add_to_bashrc('export GOPATH=/usr/share/go')
		shutit.add_to_bashrc('export PATH=$PATH:/usr/lib/go/bin')
		shutit.send('export GOPATH=/usr/share/go')
		shutit.send('export PATH=$PATH:/usr/lib/go/bin')
		shutit.send('mkdir -p /usr/share/go/bin')
		shutit.send('mkdir -p /usr/lib/go/src/github.com/hashicorp/')
		shutit.send('cd /usr/lib/go/src/github.com/hashicorp/')
		shutit.send('git clone https://github.com/hashicorp/otto.git')
		shutit.send('cd otto')
		shutit.send('make updatedeps')
		shutit.send('make dev')
		return True

	def get_config(self, shutit):
		return True

def module():
	return otto(
		'shutit.tk.otto.otto.otto', 789610974.00,
		description='',
		maintainer='',
		delivery_methods=['docker','dockerfile'],
		depends=['shutit.tk.setup']
	)

