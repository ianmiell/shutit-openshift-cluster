from shutit_module import ShutItModule

class berkshelf(ShutItModule):


	def build(self, shutit):
		if not shutit.command_available('berks'):
			if shutit.send('whoami') != 'root':
				shutit.fail('must be root')
			if not shutit.command_exists('gem'):
				shutit.fail('gem must be available')
			shutit.send('gem install berkshelf')
		return True

def module():
		return berkshelf(
			'inspec.berkshelf.berkshelf', 0.9561256125,
			description='',
			maintainer='',
			delivery_methods=['bash'],
			depends=['shutit-library.chefdk.chefdk']
		)
