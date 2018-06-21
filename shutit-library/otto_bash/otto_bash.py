from shutit_module import ShutItModule

class otto_bash(ShutItModule):

	def build(self, shutit):
		shutit.send('rm -rf /tmp/otto_bash && mkdir -p /tmp/otto_bash && cd /tmp/otto_bash')
		shutit.install('wget unzip')
		# TODO: debian/centos
		version = '0.2.0'
		shutit.send('wget https://releases.hashicorp.com/otto/' + version + '/otto_' + version + '_linux_amd64.zip')
		shutit.send('unzip *zip')
		shutit.send('mv otto /usr/local/bin')
		shutit.send('rm -rf /tmp/otto_bash')
		return True

def module():
	return otto_bash(
		'tk.shutit.otto_bash.otto_bash', 1845506479.00012136247,
		description='',
		maintainer='ian.miell@gmail.com',
		delivery_methods=['bash'],
		depends=['shutit.tk.setup']
	)

