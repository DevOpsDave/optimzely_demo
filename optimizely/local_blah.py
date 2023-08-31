#!/usr/bin/env python3

from optimizely import optimizely
import sys
import os

optimizely_client = optimizely.Optimizely(sdk_key="REDACT")

if not optimizely_client.config_manager.get_config():
    raise Exception("Optimizely client invalid. Verify in Settings>Environments that "
                    "you used the primary environment's SDK key")


def main():
    
    # Who are you?
    script_name = os.path.basename(__file__)[:-3]
    print('Running script: ' + script_name)
    
    # Create optimizely user context that has attributes { account_label: 'local_test}
    user = optimizely_client.create_user_context(user_id='local_user', attributes={'account_label': script_name })
    
    # get the decision for the feature flag 'railway-demo-flag'
    decision = user.decide('railway-demo-flag')
    
    # if we pass the feature flag, we run the code.
    if decision.enabled:
        print('Feature flag is on. Running code.')
        #print(decision.variables['message'])
    else:
        print('Feature flag is off. Not running code.')
        #print(f'value of decision.variables.message is {decision.variables["message"]}')
    


if __name__ == '__main__':
    main()
    sys.exit(0)
