from shutit_module import ShutItModule

class minikube(ShutItModule):


	def build(self, shutit):
		if not shutit.command_available('kubectl'):
			if shutit.send_and_get_output('uname') == 'Darwin':
				shutit.send('curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/darwin/amd64/kubectl')
			else:
				shutit.send('curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl')
			shutit.send('chmod +x kubectl')
			shutit.send('sudo mv kubectl /usr/local/bin/kubectl')
		def install_minikube():
			if shutit.send_and_get_output('uname') == 'Darwin':
				shutit.send('curl -LO https://storage.googleapis.com/minikube/releases/v$(curl -s https://storage.googleapis.com/minikube/releases/stable.txt)/minikube-darwin-amd64')
				shutit.send('mv minikube-darwin-amd64 minikube')
			else:
				shutit.send('curl -LO https://storage.googleapis.com/minikube/releases/v$(curl -s https://storage.googleapis.com/minikube/releases/stable.txt)/minikube-linux-amd64')
				shutit.send('mv minikube-linux-amd64 minikube')
			shutit.send('chmod +x minikube')
			shutit.send('sudo mv minikube /usr/local/bin/minikube')
		if shutit.command_available('minikube'):
			shutit.pause_point('Want to remove minikube? If so, continue')
			shutit.send('rm -rf ~/.minikube')
			shutit.multisend('minikube delete',{'Y/n':'Y'})
		install_minikube()
		if not shutit.send_and_get_output('''minikube status | grep 'Does Not Exist' | wc -l | awk '{print $1}' ''') == '1':
			shutit.send('minikube start')
		return True

def module():
		return minikube(
			'shutit-library.minikube.minikube', 0.12135426,
			description='',
			maintainer='',
			delivery_methods=['bash'],
			depends=['shutit-library.virtualization.virtualization.virtualization']
		)
