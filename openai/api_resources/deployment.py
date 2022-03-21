from openai.api_resources.abstract import DeletableAPIResource, ListableAPIResource, CreateableAPIResource
from openai.error import InvalidRequestError


class Deployment(CreateableAPIResource, ListableAPIResource, DeletableAPIResource):
    engine_required = False
    OBJECT_NAME = "deployment"

    @classmethod
    def create(cls, *args, **kwargs):
        """
        Creates a new deployment for the provided prompt and parameters.
        """
        if kwargs.get("model", None) is None:
            raise InvalidRequestError(
                "Must provide a 'model' parameter to create a Deployment.",
                param="model",
            )

        scale_settings = kwargs.get("scale_settings", None)
        if scale_settings is None:
            raise InvalidRequestError(
                "Must provide a 'scale_settings' parameter to create a Deployment.",
                param="scale_settings",
            )
        
        if "scale_type" not in scale_settings or "capacity" not in scale_settings:
            raise InvalidRequestError(
                "The 'scale_settings' parameter contains invalid or incomplete values.",
                param="scale_settings",
            )

        return super().create(*args, **kwargs)
