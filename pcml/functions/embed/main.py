# coding=utf-8
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""PubSub-triggered media embedding."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tempfile
import base64
import json

from messages import EmbedTriggerMessage

FUNCTION_NAME = "embed"


def embed(event, context):

  if 'data' not in event:
    raise ValueError("Received event trigger without PubSub message data.")

  msg_data_raw = json.loads(base64.b64decode(event['data']).decode('utf-8'))
  msg_data = EmbedTriggerMessage(**msg_data_raw)
  print("Received datagen request: {}".format(msg_data.__dict__))

  # TODO

  print("Finished function.")