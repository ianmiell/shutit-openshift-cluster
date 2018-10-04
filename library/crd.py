def do_crd_simple(s):
	s.send('mkdir crd_simple')
	s.send('pushd crd_simple')
	s.send('''cat > resourcedefinition.yaml << END
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomeResourceDefinition
metadata:
  # Name must be plural.group
  name: crontabs.stable.example.com
spec:
  # See name above. group matches api: /apis/<group>/<version>, eg /apis/stable.example.com/v1
  group: stable.example.com
  versions:
    - name: v1
    # Whether switched on or not
    served: true
    # Storage version is the current one (?)
    storage: true
scope: Namespaced
names:
  plural: crontabs
  singular: crontab
  # Resource manifests use this
  kind: CronTab
  shortnames:
  - ct
END''')
	s.send('kubectl create -f resourcedefinition.yaml')
	s.send('popd')

def do_sample_controller(s):
