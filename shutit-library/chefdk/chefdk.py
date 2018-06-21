from shutit_module import ShutItModule

class chefdk(ShutItModule):

	def build(self, shutit):
		# TODO: version number, rpm download
		processor = shutit.send_and_get_output('uname -p')
		if not shutit.command_available('wget'):
			shutit.install('wget')
		if not shutit.command_available('chef-solo'):
			if shutit.get_current_shutit_pexpect_session_environment().install_type == 'apt':
				pw = shutit.get_env_pass('Input your sudo password to install chefdk')
				shutit.send('wget -qO- https://packages.chef.io/files/stable/chefdk/1.1.16/ubuntu/16.04/chefdk_1.1.16-1_amd64.deb > /tmp/chefdk.deb')
				shutit.multisend('sudo dpkg -i /tmp/chefdk.deb',{'assword':pw})
			elif shutit.get_current_shutit_pexpect_session_environment().install_type == 'yum':
				pw = shutit.get_env_pass('Input your sudo password to install chefdk')
				shutit.send('wget -qO- https://packages.chef.io/files/stable/chefdk/1.1.16/el/7/chefdk-1.1.16-1.el7.x86_64.rpm > /tmp/chefdk.rpm')
				shutit.multisend('sudo rpm -i /tmp/chefdk.rpm',{'assword':pw})
			else:
				shutit.install('chefdk')
			# Chef is installed here, but not in path
			shutit.send('pushd /opt/chefdk/bin')
			shutit.send('''echo 'eval "$(./chef shell-init bash)"' >> ~/.bash_profile''')
			shutit.send('''echo 'eval "$(./chef shell-init bash)"' >> ~/.bashrc''')
		return True

def module():
		return chefdk(
			'shutit-library.chefdk.chefdk', 0.1649027060,
			description='',
			maintainer='',
			delivery_methods=['bash'],
			depends=['shutit.tk.setup']
		)


