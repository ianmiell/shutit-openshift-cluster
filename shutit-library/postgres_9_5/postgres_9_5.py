"""ShutIt module. See http://shutit.tk
"""

from shutit_module import ShutItModule


class postgres_9_5(ShutItModule):

	def build(self,shutit):
		# From: docker hub, postgres 9.5
		shutit.send("""cat > /root/stop_postgres.sh <<< 'service postgresql stop'""")
		shutit.send('apt-key adv --keyserver ha.pool.sks-keyservers.net --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8')
		shutit.send('''echo 'deb http://apt.postgresql.org/pub/repos/apt/ jessie-pgdg main' 9.5 > /etc/apt/sources.list.d/pgdg.list''')
		shutit.send('apt-get update')
		shutit.install('postgresql-common')
		shutit.send(r'''sed -ri 's/#(create_main_cluster) .*$/\1 = false/' /etc/postgresql-common/createcluster.conf''')
		shutit.install('postgresql-9.5=9.5~alpha2-1.pgdg80+1 postgresql-contrib-9.5=9.5~alpha2-1.pgdg80+1')
		shutit.add_line_to_file('# postgres', '/root/start_postgres.sh')
		shutit.add_line_to_file("echo Setting shmmax for postgres", '/root/start_postgres.sh')
		shutit.add_line_to_file('service postgresql start', '/root/start_postgres.sh', force=True)
		shutit.send("""cat > /root/stop_postgres.sh <<< \\
'service postgresql stop'""")
		shutit.send('chmod +x /root/start_postgres.sh')
		shutit.send('chmod +x /root/stop_postgres.sh')
		return True

	def start(self, shutit):
		shutit.send('/root/start_postgres.sh', check_exit=False)
		return True
	
	def stop(self, shutit):
		shutit.send('/root/stop_postgres.sh', check_exit=False)
		return True

	def get_config(self, shutit):
		return True

	def test(self, shutit):
		# For test cycle part of the ShutIt build.
		return True

	def finalize(self, shutit):
		# Any cleanup required at the end.
		return True
	
	def is_installed(self, shutit):
		return False


def module():
	return postgres_9_5(
		'shutit.tk.postgres_9_5.postgres_9_5', 0.01251252453,
		description='',
		maintainer='',
		delivery_methods=['docker'],
		depends=['shutit.tk.setup']
	)

