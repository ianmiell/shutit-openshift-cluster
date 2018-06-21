from shutit_module import ShutItModule

class virtualization(ShutItModule):

	def build(self, shutit):
		cfg = shutit.cfg
		virt_method = shutit.cfg[self.module_id]['virt_method']
		if virt_method == 'virtualbox':
			if not shutit.command_available('VBoxManage'):
				if shutit.get_current_shutit_pexpect_session_environment().install_type == 'apt': 
					shutit.send('echo "deb http://download.virtualbox.org/virtualbox/debian $(lsb_release -s -c) contrib" >> /etc/apt/sources.list ')
					shutit.send('wget -qO- https://www.virtualbox.org/download/oracle_vbox.asc | sudo apt-key add -')
					shutit.send('apt-get update')
					shutit.install('virtualbox-5.0')
				else:
					shutit.install('virtualbox')
		elif virt_method == 'libvirt':
			# Is this a good enough test of whether virsh exists?
			if not shutit.command_available('virsh'):
				shutit.install('kvm')
				shutit.install('libvirt')
				shutit.install('libvirt-devel')
				shutit.install('qemu-kvm')
				shutit.send('systemctl start libvirtd')
			# TODO: do we need to ensure 'vagrant plugin vagrant-libvirt installed' as well?
		else:
			shutit.fail(self.module_id + ' requires virt_method to be set correctly (virtualbox or libvirt)')
		return True

                                                                                                   
	def get_config(self, shutit):                                                                                                             
		shutit.get_config(self.module_id,'virt_method',default='virtualbox')
		return True                      

def module():
	return virtualization(
		'shutit-library.virtualization.virtualization.virtualization', 0.8024250901,
		description='Virtualization (choose VBox or LibVirt)',
		maintainer='ian.miell@gmail.com',
		delivery_methods=['bash'],
		depends=['shutit.tk.setup']
	)

