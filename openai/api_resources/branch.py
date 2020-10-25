from openai import util
from openai.api_resources.abstract.engine_api_resource import EngineAPIResource
from openai.six.moves.urllib.parse import quote_plus


class Branch(EngineAPIResource):
    OBJECT_NAME = "branch"

    @classmethod
    def class_url(cls, engine):
        assert engine is not None
        engine = util.utf8(engine)
        extn = quote_plus(engine)
        return "/%s/engines/%s/branches" % (cls.api_prefix, extn)

    def make_encoding(self):
        try:
            from openai_finetune import encoding
        except ImportError as e:
            raise RuntimeError(
                'Failed to import openai_finetune: {}. (HINT: try "pip install openai-finetune".)'.format(
                    e
                )
            )
        return encoding.get(self.encoding)
