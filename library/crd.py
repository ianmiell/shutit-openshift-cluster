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
	s.send('oc create -f resourcedefinition.yaml')
	s.send('''cat > my-crontab.yaml << END
apiVersion: "stable.example.com/v1"
kind: CronTab
metadata:
  name: my-new-cron-object
spec:
  cronSpec: "* * * * */5"
  image: my-awesome-cron-image
END''')
	s.send('oc create -f my-crontab.yaml')
	s.send('oc get crontab')
	s.send('oc get ct -o yaml')
	s.send('popd')
