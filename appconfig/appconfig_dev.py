#!/usr/bin/env python3
# Script to do a test of AWS App Config Feature Flags.

from datetime import datetime, timedelta
import json
import sys, os
import boto3

APPCONFIG_APPLICATION_NAME = 'TestApp'
APPCONFIG_CONFIG_PROFILE_NAME = 'FeatureFlagConfigProfile'
APPCONFIG_ENVIRONMENT_NAME = 'Dev'
APPCONFIG_FEATURE_FLAG_NAME = 'myNewFeature'
AWS_REGION = 'us-east-1'

cached_config_data = {}
cached_config_token = None
cached_token_expiration_time = None

def get_config():
    global cached_config_token
    global cached_config_data
    global cached_token_expiration_time
    appconfigdata = boto3.client('appconfigdata', region_name=AWS_REGION)
    
    # If we don't have a token yet, call start_configuration_session to get one
    if not cached_config_token or datetime.now() >= cached_token_expiration_time:
        start_session_response = appconfigdata.start_configuration_session(
            ApplicationIdentifier=APPCONFIG_APPLICATION_NAME,
            EnvironmentIdentifier=APPCONFIG_ENVIRONMENT_NAME,
            ConfigurationProfileIdentifier=APPCONFIG_CONFIG_PROFILE_NAME,
        )
        cached_config_token = start_session_response["InitialConfigurationToken"]

    get_config_response = appconfigdata.get_latest_configuration(
        ConfigurationToken=cached_config_token
    )
    # Response always includes a fresh token to use in next call
    cached_config_token = get_config_response["NextPollConfigurationToken"]
    # Token will expire if not refreshed within 24 hours, so keep track of
    # the expected expiration time minus a bit of padding
    cached_token_expiration_time = datetime.now() + timedelta(hours=23, minutes=59)
    # 'Configuration' in the response will only be populated the first time we
    # call GetLatestConfiguration or if the config contents have changed since
    # the last time we called. So if it's empty we know we already have the latest
    # config, otherwise we need to update our cache.
    content = get_config_response["Configuration"].read()
    if content:
        try:
            cached_config_data = json.loads(content.decode("utf-8"))
            print("received new config data:", cached_config_data)
        except json.JSONDecodeError as error:
            raise ValueError(error.msg) from error

    return cached_config_data


def main():
    script_name = os.path.basename(__file__)[:-3]
    print('Running script: ' + script_name)
    
    # Get the config data
    config_data = get_config()
    
    # Get the feature flag value
    feature_flag_obj = config_data[APPCONFIG_FEATURE_FLAG_NAME]
    
    if feature_flag_obj['enabled']:
        print('Feature flag is on. Running code.')
    else:
        print('Feature flag is off. Not running code.')
    

if __name__ == '__main__':
    main()
    sys.exit(0)