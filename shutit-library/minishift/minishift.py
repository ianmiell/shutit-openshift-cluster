from shutit_module import ShutItModule

class minishift(ShutItModule):


	def build(self, shutit):
		if not shutit.command_available('minishift'):
			shutit.send('curl -LO https://github.com/minishift/minishift/releases/download/v1.0.0-beta.5/minishift-1.0.0-beta.5-linux-amd64.tgz | tar -zxvf')
		shutit.send('minishift start')
		shutit.add_to_bashrc('PATH=$PATH:~/.minishift/cache/oc/v1.4.1')
		return True

	def get_config(self, shutit):

		return True

	def test(self, shutit):

		return True

	def finalize(self, shutit):

		return True

	def is_installed(self, shutit):

		return False

	def start(self, shutit):

		return True

	def stop(self, shutit):

		return True

def module():
		return minishift(
			'imiell.minishift.minishift', 1412925635.0001,
			description='',
			maintainer='',
			delivery_methods=['bash'],
			depends=['shutit.tk.setup']
		)
