from shutit_module import ShutItModule

class phantomjs(ShutItModule):

	def build(self, shutit):
		shutit.send('pushd /opt')
		shutit.install('tar') # required for centos image
		shutit.install('curl')
		shutit.install('bzip2')
		shutit.install('git')
		shutit.install('build-essential')
		shutit.install('g++')
		shutit.install('flex')
		shutit.install('bison')
		shutit.install('gperf')
		shutit.install('ruby')
		shutit.install('perl')
		shutit.install('libsqlite3-dev')
		shutit.install('libfontconfig1-dev')
		shutit.install('libicu-dev')
		shutit.install('libfreetype6')
		shutit.install('libssl-dev')
		shutit.install('libpng-dev')
		shutit.install('libjpeg-dev')
		shutit.install('libqt5webkit5-dev')
		phantom_js_tag = '2.0.0'
		shutit.send('git clone https://github.com/ariya/phantomjs.git /tmp/phantomjs')
		shutit.send('cd /tmp/phantomjs && git checkout $PHANTOM_JS_TAG')
		shutit.send('./build.sh --confirm')
		shutit.send('mv bin/phantomjs /usr/local/bin')
		shutit.send('rm -rf /tmp/phantomjs')
		return True

	def remove(self, shutit):
		shutit.send('rm -rf /opt/phantomjs')
		return True


def module():
	return phantomjs(
		'shutit.tk.phantomjs.phantomjs', 0.319,
		description='see http://phantomjs.org/',
		depends=['shutit.tk.setup']
	)

