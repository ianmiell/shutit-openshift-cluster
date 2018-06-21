from shutit_module import ShutItModule

class aws(ShutItModule):

	def build(self, shutit):
		return True
                                 
	def get_config(self, shutit):
		shutit.get_config(self.module_id,'access_key')
		shutit.get_config(self.module_id,'secret_key')
		return True

def module():
		return aws(
			'tk.shutit.aws.aws', 0.0218611513,   
			description='',
			maintainer='',
			delivery_methods=['bash','docker','dockerfile','ssh'],
			depends=['shutit.tk.setup']
		)
