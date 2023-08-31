#!/usr/bin/env python3

# Script to manage Optimizely audiences.
# Script is subcommand based and will take the following subcommands:
# subcommand: create, update, delete, list, get:
#   - Create audience: takes a well-formed JSON file and creates an audience in Optimizely.  Will not overwrite an existing audience.
#   - Update audience: takes a well-formed JSON file and updates an audience in Optimizely.
#   - Delete audience: uses the audience name to delete an audience in Optimizely
#   - List audiences: lists all audiences in Optimizely
#   - Get audience: outputs the JSON for a single audience in Optimizely

import argparse
import json
import os
import sys
import time
import requests
from optimizely import optimizely
from optimizely import config_manager
from optimizely import logger
from optimizely import event_builder
from optimizely import decision_service
from optimizely import user_profile_service
from optimizely import error_handler
from optimizely.helpers import enums
from optimizely.helpers import validator
from optimizely.helpers import event_tag_utils
from optimizely.helpers import audience_utils
from optimizely.helpers import condition_evaluator
