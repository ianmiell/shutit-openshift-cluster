from shutit_module import ShutItModule

class docker(ShutItModule):

	def build(self, shutit):
		if shutit.get_current_environment()['distro'] == 'ubuntu':
			shutit.send('apt-get update')
			shutit.send('apt-get install apt-transport-https ca-certificates')
			shutit.send('apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070A')
			shutit.send('''cat > /etc/apt/sources.list.d/docker.list << END
deb https://apt.dockerproject.org/repo ubuntu-$(lsb-release -c -s) main
END''')
		else:
			shutit.install('docker.io')
		return True


def module():
	return docker(
		'shutit.tk.docker.docker', 0.396,
		description="docker server (communicates with host's docker daemon)",
		depends=['shutit.tk.setup']
	)

