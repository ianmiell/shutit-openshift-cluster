"""ShutIt module. See http://shutit.tk
"""

from shutit_module import ShutItModule


class httpdiff(ShutItModule):


	def build(self, shutit):
		shutit.install('git build-essential')
		shutit.send('git clone https://github.com/jgrahamc/httpdiff')
		shutit.pause_point('')
		return True

def module():
	return httpdiff(
		'shutit.tk.httpdiff.httpdiff', 0.151352136461,
		description='',
		maintainer='',
		depends=['shutit.tk.setup']
	)

