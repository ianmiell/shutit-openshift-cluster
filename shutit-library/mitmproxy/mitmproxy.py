"""ShutIt module. See http://shutit.tk
"""

from shutit_module import ShutItModule


class mitmproxy(ShutItModule):


	def build(self, shutit):
		shutit.install('python-pip python-dev libxml2-dev libxslt-dev libz-dev libffi-dev libssl-dev')
		shutit.send('ln -s /usr/include/libxml2/libxml /usr/include/libxml')
		shutit.send('pip install mitmproxy')
		shutit.add_to_bashrc('export LANG=en_US.UTF-8')
		return True

def module():
	return mitmproxy(
		'shutit.tk.mitmproxy.mitmproxy', 782914092.01,
		description='http://mitmproxy.org/',
		maintainer='ian.miell@gmail.com',
		depends=['shutit.tk.setup']
	)

