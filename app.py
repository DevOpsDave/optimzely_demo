# Copyright 2016-2017, 2019-2021 Optimizely
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import random
from functools import reduce
from optimizely import optimizely
from optimizely import notification_center
from optimizely.config_manager import PollingConfigManager
from optimizely.helpers import enums
from optimizely.event import event_processor
from optimizely import event_dispatcher as optimizely_event_dispatcher


DATAFILE_URL = 'https://cdn.optimizely.com/onboarding/8wj0JgOlR8OlmdMBOaRHOw.json'
DEBUG_TEXT_ON = '[DEBUG: Feature [36mON[0m]'
DEBUG_TEXT_OFF = '[DEBUG: Feature [33mOFF[0m]'


def get_experience(optimizely_client, user_id):
  # create a user and decide a flag rule (such as an A/B test) for them
  user = optimizely_client.create_user_context(user_id)
  decision = user.decide("product_sort")

  # the text that is printed comes from feature variables
  if decision.enabled:
    # mocks config values with print statements like "Variation 1 shows popular products first!"
    text = decision.variables["sort_method"]
  # default fallback if flag off for user
  else:
    text = 'Flag off. User saw the product list sorted alphabetically by default.'

  return {
    'text': text,
    'is_enabled': decision.enabled,
    'debug_text': DEBUG_TEXT_ON if decision.enabled else DEBUG_TEXT_OFF,
  }


def get_percentage(count, total_value):
  return round(count * 100 / total_value)


def run_product_sorter(optimizely_client):
  # generate random user ids. each user will get randomly & deterministically bucketed into a flag variation
  random.seed()
  user_ids = []
  for i in range(100):
    user_ids.append(str(random.randrange(10000)))

  print("\n\nWelcome to our product catalog!")
  print("Let's see what product sorting the visitors experience!\n")

  # for each user, decide the feature flag experience they get
  experiences = [get_experience(optimizely_client, user_id) for user_id in user_ids]

  on_variations = [experience for experience in experiences if experience['is_enabled']]
  if len(on_variations) > 0:
    reports = ['Visitor #%s: %s %s' % (i, experience['debug_text'], experience['text']) for
               i, experience in enumerate(experiences)]
  else:
    reports = ['Visitor #%s: %s' % (i, experience['text']) for i, experience in
               enumerate(experiences)]

  # print the feature flag experiences visitors received
  print("\n".join(reports))
  print()

  def count_frequency(accum, value):
    text = value['text']
    accum[text] = accum[text] + 1 if text in accum.keys() else 1
    return accum

  frequency_map = reduce(count_frequency, experiences, {})

  num_on_variations = len(on_variations)
  total = len(user_ids)

  if len(on_variations) > 0:
    print("{0} out of {1} visitors (~{2}%) had the feature flag enabled\n".format(
      num_on_variations,
      total,
      get_percentage(num_on_variations, total)
    )
    )

  total = len(user_ids)
  for text, _ in frequency_map.items():
    perc = get_percentage(frequency_map[text], total)
    print("%s visitors (~%s%%) got the experience: '%s'" % (frequency_map[text], perc, text))


def main():
  n_center = notification_center.NotificationCenter()

  conf_manager = PollingConfigManager(
    update_interval=5,
    url=DATAFILE_URL,
    notification_center=n_center
  )

  event_dispatcher = optimizely_event_dispatcher.EventDispatcher

  # define asynchronous event processing for faster processing of variation distribution
  batch_processor = event_processor.BatchEventProcessor(
      event_dispatcher,
      batch_size=15,
      flush_interval=50,
      start_on_init = True,
      notification_center=n_center
  )

  optimizely_client = optimizely.Optimizely(config_manager=conf_manager,
                                            notification_center=n_center,
                                            event_processor=batch_processor)

  run_product_sorter(optimizely_client)

  # fetch any datafile changes, which result from configuration updates you make to traffic percentage sliders
  # flag variable values, etc. in the UI part of the tutorial.
  # notification listener listens for those datafile updates and re-runs the calculation
  def on_config_update_listener(*args):
    run_product_sorter(optimizely_client)

  optimizely_client.notification_center.add_notification_listener(
    enums.NotificationTypes.OPTIMIZELY_CONFIG_UPDATE, on_config_update_listener)


if __name__ == '__main__':
  main()
  input("Press Enter to quit.")
  sys.exit()

