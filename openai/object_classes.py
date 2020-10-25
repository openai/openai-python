from __future__ import absolute_import, division, print_function

from openai import api_resources
from openai.api_resources.experimental.completion_config import CompletionConfig

OBJECT_CLASSES = {
    "engine": api_resources.Engine,
    "experimental.completion_config": CompletionConfig,
    "snapshot": api_resources.Snapshot,
    "tag": api_resources.Tag,
    "branch": api_resources.Branch,
    "plan": api_resources.Plan,
    "update": api_resources.Update,
    "event": api_resources.Event,
}
