from openai import util
from openai.api_resources.abstract import (
    DeletableAPIResource,
    ListableAPIResource,
    CreateableAPIResource,
)
from openai.error import InvalidRequestError, APIError


class Deployment(CreateableAPIResource, ListableAPIResource, DeletableAPIResource):
    OBJECT_NAME = "deployments"

    @classmethod
    def create(cls, *args, **kwargs):
        """
        Creates a new deployment for the provided prompt and parameters.
        """
        typed_api_type, _ = cls._get_api_type_and_version(
            kwargs.get("api_type", None), None
        )
        if typed_api_type not in (util.ApiType.AZURE, util.ApiType.AZURE_AD):
            raise APIError(
                "Deployment operations are only available for the Azure API type."
            )

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

        if "scale_type" not in scale_settings or (
            scale_settings["scale_type"].lower() == "manual"
            and "capacity" not in scale_settings
        ):
            raise InvalidRequestError(
                "The 'scale_settings' parameter contains invalid or incomplete values.",
                param="scale_settings",
            )

        return super().create(*args, **kwargs)

    @classmethod
    def list(cls, *args, **kwargs):
        typed_api_type, _ = cls._get_api_type_and_version(
            kwargs.get("api_type", None), None
        )
        if typed_api_type not in (util.ApiType.AZURE, util.ApiType.AZURE_AD):
            raise APIError(
                "Deployment operations are only available for the Azure API type."
            )

        return super().list(*args, **kwargs)

    @classmethod
    def delete(cls, *args, **kwargs):
        typed_api_type, _ = cls._get_api_type_and_version(
            kwargs.get("api_type", None), None
        )
        if typed_api_type not in (util.ApiType.AZURE, util.ApiType.AZURE_AD):
            raise APIError(
                "Deployment operations are only available for the Azure API type."
            )

        return super().delete(*args, **kwargs)

    @classmethod
    def retrieve(cls, *args, **kwargs):
        typed_api_type, _ = cls._get_api_type_and_version(
            kwargs.get("api_type", None), None
        )
        if typed_api_type not in (util.ApiType.AZURE, util.ApiType.AZURE_AD):
            raise APIError(
                "Deployment operations are only available for the Azure API type."
            )

        return super().retrieve(*args, **kwargs)
