from __future__ import absolute_import, division, print_function

from openai import error, six, util
from openai.six.moves.urllib.parse import quote_plus
from openai.api_resources.abstract import (
    CreateableAPIResource,
    DeletableAPIResource,
    ListableAPIResource,
)


class Collection(
    CreateableAPIResource,
    ListableAPIResource,
    DeletableAPIResource,
):
    OBJECT_NAME = "collection"

    def __init__(self, name, *args, **kwargs):
        self.name = name
        super().__init__(*args, name=self.name, **kwargs)

    @classmethod
    def retrieve(cls, name, api_key=None, request_id=None, **params):
        instance = cls(name, api_key, **params)
        instance.refresh(request_id=request_id)
        return instance

    def instance_url(self):
        # collections are normally called by their name, not their id
        name = self.get("name")

        if not isinstance(name, six.string_types):
            raise error.InvalidRequestError(
                "Could not determine which URL to request: %s instance "
                "has invalid ID: %r, %s. ID should be of type `str` (or"
                " `unicode`)" % (type(self).__name__, name, type(name)),
                "name",
            )

        id = util.utf8(name)
        base = self.class_url()
        extn = quote_plus(id)
        return "%s/%s" % (base, extn)
