
# For 3.7 upgrade, docker upgrade requires a redeploy to ensure all is ok
def redeploy_components(shutit_session,apptype='both'):
	if apptype in ('both','registry'):
        shutit_session.send('oc rollout latest docker-registry')
	if apptype in ('both','router'):
        shutit_session.send('oc rollout latest router')
