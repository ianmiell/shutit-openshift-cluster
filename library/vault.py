def do_vault(s1):

	# Setup/cleanup of pre-existing art.
	s1.send('xz -d -c vault.xz > vault')
	s1.send('rm -rf credscontroller')
	s1.send('git clone https://github.com/ianmiell/credscontroller')

	s1.send('oc delete project spring-example || true')
	s1.send('oc delete project vault-controller || true')

	# Wait for projects to be deleted before creating new ones.
	s1.send('while true; do oc new-project spring-example   && break; sleep 5; done')
	s1.send('while true; do oc new-project vault-controller && break; sleep 5; done')
	# Is this required?
	s1.send('oc adm policy add-scc-to-user anyuid -z default')
	# Create configmap for vault.
	s1.send('oc create configmap vault-config --from-file=vault-config=./credscontroller/openshift/vault-config.json')
	# Set up vault.
	s1.send('oc create -f ./credscontroller/openshift/vault.yaml')
	# Create a route for vault.
	s1.send('oc create route passthrough vault --port=8200 --service=vault')
	# Set up vault address.
	s1.send(r"""export VAULT_ADDR=https://$(oc get route | grep -m1 vault | awk '{print $2}')""")
	# Wait for vault to start.
	s1.send('sleep 120')

	# Initialising the vault results in two items being output - the keys and the root token. Gather these into variables.
	output = s1.send_and_get_output('./vault init -tls-skip-verify -key-shares=1 -key-threshold=1')
	keys = output.split('\n')[0].split(' ')[-1]
	root = output.split('\n')[1].split(' ')[-1]
	s1.send('export KEYS=' + keys)
	s1.send('export ROOT_TOKEN=' + root)

	# Unseal the vault with key and ROOT_TOKEN
	s1.send('./vault unseal -tls-skip-verify $KEYS')

	# Create the vault controller.
	# Create root token secret.
	s1.send('oc create secret generic vault-controller --from-literal vault-token=$ROOT_TOKEN')
	# Allow project's default service account to view the secret.
	s1.send('oc adm policy add-cluster-role-to-user view system:serviceaccount:vault-controller:default')
	# Run up the vault controller.
	s1.send('oc create -f ./credscontroller/openshift/vault-controller.yaml')
	s1.send_until('oc get pods | grep controller | grep -v deploy | grep -w Running | wc -l','1')

	# Running the Example
	# At this point, you are ready to start deploying pods that use the above approach to inject secrets.
	# The repository comes with two examples - one for a Vault-aware app and one for a legacy app. The instructions below are for the Vault-aware example.
	# In this first example, a Spring Boot app uses the Spring Cloud Vault Config plugin to get part of its configuration from Vault.
	# The Init Container will write the unwrapped Vault token to a well-known location and the app will use that token to authenticate with Vault and retrieve its credentials.
	s1.send('export VAULT_TOKEN=$ROOT_TOKEN')
	# Write the vault policy for the sptring example.
	s1.send('./vault policy-write -tls-skip-verify spring-example ./credscontroller/examples/spring-example/spring-example.hcl')
	# Write a secret to the vault.
	s1.send('./vault write -tls-skip-verify secret/spring-example password=pwd')

	# Move to spring-example project.
	s1.send('oc project spring-example')
	# Run up app.
	s1.send('oc new-build registry.access.redhat.com/redhat-openjdk-18/openjdk18-openshift~https://github.com/raffaelespazzoli/credscontroller --context-dir=examples/spring-example --name spring-example')
	# Join networks so they can 'see' each other.
	s1.send('oc adm pod-network join-projects --to vault-controller spring-example')
	s1.send('oc create -f ./credscontroller/examples/spring-example/spring-example.yaml')
	s1.send('oc expose svc spring-example')
	s1.send("""export SPRING_EXAMPLE_ADDR=http://$(oc get route | grep -m1 spring | awk '{print $2}')""")
	s1.send('curl $SPRING_EXAMPLE_ADDR/secret')
