# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from .... import _legacy_response
from ...._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from ...._base_client import make_request_options
from ....types.admin.organization import (
    usage_costs_params,
    usage_images_params,
    usage_embeddings_params,
    usage_completions_params,
    usage_moderations_params,
    usage_vector_stores_params,
    usage_audio_speeches_params,
    usage_audio_transcriptions_params,
    usage_code_interpreter_sessions_params,
)
from ....types.admin.organization.usage_costs_response import UsageCostsResponse
from ....types.admin.organization.usage_images_response import UsageImagesResponse
from ....types.admin.organization.usage_embeddings_response import UsageEmbeddingsResponse
from ....types.admin.organization.usage_completions_response import UsageCompletionsResponse
from ....types.admin.organization.usage_moderations_response import UsageModerationsResponse
from ....types.admin.organization.usage_vector_stores_response import UsageVectorStoresResponse
from ....types.admin.organization.usage_audio_speeches_response import UsageAudioSpeechesResponse
from ....types.admin.organization.usage_audio_transcriptions_response import UsageAudioTranscriptionsResponse
from ....types.admin.organization.usage_code_interpreter_sessions_response import UsageCodeInterpreterSessionsResponse

__all__ = ["Usage", "AsyncUsage"]


class Usage(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UsageWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return UsageWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UsageWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return UsageWithStreamingResponse(self)

    def audio_speeches(
        self,
        *,
        start_time: int,
        api_key_ids: SequenceNotStr[str] | Omit = omit,
        bucket_width: Literal["1m", "1h", "1d"] | Omit = omit,
        end_time: int | Omit = omit,
        group_by: List[Literal["project_id", "user_id", "api_key_id", "model"]] | Omit = omit,
        limit: int | Omit = omit,
        models: SequenceNotStr[str] | Omit = omit,
        page: str | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        user_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsageAudioSpeechesResponse:
        """
        Get audio speeches usage details for the organization.

        Args:
          start_time: Start time (Unix seconds) of the query time range, inclusive.

          api_key_ids: Return only usage for these API keys.

          bucket_width: Width of each time bucket in response. Currently `1m`, `1h` and `1d` are
              supported, default to `1d`.

          end_time: End time (Unix seconds) of the query time range, exclusive.

          group_by: Group the usage data by the specified fields. Support fields include
              `project_id`, `user_id`, `api_key_id`, `model` or any combination of them.

          limit: Specifies the number of buckets to return.

              - `bucket_width=1d`: default: 7, max: 31
              - `bucket_width=1h`: default: 24, max: 168
              - `bucket_width=1m`: default: 60, max: 1440

          models: Return only usage for these models.

          page: A cursor for use in pagination. Corresponding to the `next_page` field from the
              previous response.

          project_ids: Return only usage for these projects.

          user_ids: Return only usage for these users.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/organization/usage/audio_speeches",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "start_time": start_time,
                        "api_key_ids": api_key_ids,
                        "bucket_width": bucket_width,
                        "end_time": end_time,
                        "group_by": group_by,
                        "limit": limit,
                        "models": models,
                        "page": page,
                        "project_ids": project_ids,
                        "user_ids": user_ids,
                    },
                    usage_audio_speeches_params.UsageAudioSpeechesParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            cast_to=UsageAudioSpeechesResponse,
        )

    def audio_transcriptions(
        self,
        *,
        start_time: int,
        api_key_ids: SequenceNotStr[str] | Omit = omit,
        bucket_width: Literal["1m", "1h", "1d"] | Omit = omit,
        end_time: int | Omit = omit,
        group_by: List[Literal["project_id", "user_id", "api_key_id", "model"]] | Omit = omit,
        limit: int | Omit = omit,
        models: SequenceNotStr[str] | Omit = omit,
        page: str | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        user_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsageAudioTranscriptionsResponse:
        """
        Get audio transcriptions usage details for the organization.

        Args:
          start_time: Start time (Unix seconds) of the query time range, inclusive.

          api_key_ids: Return only usage for these API keys.

          bucket_width: Width of each time bucket in response. Currently `1m`, `1h` and `1d` are
              supported, default to `1d`.

          end_time: End time (Unix seconds) of the query time range, exclusive.

          group_by: Group the usage data by the specified fields. Support fields include
              `project_id`, `user_id`, `api_key_id`, `model` or any combination of them.

          limit: Specifies the number of buckets to return.

              - `bucket_width=1d`: default: 7, max: 31
              - `bucket_width=1h`: default: 24, max: 168
              - `bucket_width=1m`: default: 60, max: 1440

          models: Return only usage for these models.

          page: A cursor for use in pagination. Corresponding to the `next_page` field from the
              previous response.

          project_ids: Return only usage for these projects.

          user_ids: Return only usage for these users.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/organization/usage/audio_transcriptions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "start_time": start_time,
                        "api_key_ids": api_key_ids,
                        "bucket_width": bucket_width,
                        "end_time": end_time,
                        "group_by": group_by,
                        "limit": limit,
                        "models": models,
                        "page": page,
                        "project_ids": project_ids,
                        "user_ids": user_ids,
                    },
                    usage_audio_transcriptions_params.UsageAudioTranscriptionsParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            cast_to=UsageAudioTranscriptionsResponse,
        )

    def code_interpreter_sessions(
        self,
        *,
        start_time: int,
        bucket_width: Literal["1m", "1h", "1d"] | Omit = omit,
        end_time: int | Omit = omit,
        group_by: List[Literal["project_id"]] | Omit = omit,
        limit: int | Omit = omit,
        page: str | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsageCodeInterpreterSessionsResponse:
        """
        Get code interpreter sessions usage details for the organization.

        Args:
          start_time: Start time (Unix seconds) of the query time range, inclusive.

          bucket_width: Width of each time bucket in response. Currently `1m`, `1h` and `1d` are
              supported, default to `1d`.

          end_time: End time (Unix seconds) of the query time range, exclusive.

          group_by: Group the usage data by the specified fields. Support fields include
              `project_id`.

          limit: Specifies the number of buckets to return.

              - `bucket_width=1d`: default: 7, max: 31
              - `bucket_width=1h`: default: 24, max: 168
              - `bucket_width=1m`: default: 60, max: 1440

          page: A cursor for use in pagination. Corresponding to the `next_page` field from the
              previous response.

          project_ids: Return only usage for these projects.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/organization/usage/code_interpreter_sessions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "start_time": start_time,
                        "bucket_width": bucket_width,
                        "end_time": end_time,
                        "group_by": group_by,
                        "limit": limit,
                        "page": page,
                        "project_ids": project_ids,
                    },
                    usage_code_interpreter_sessions_params.UsageCodeInterpreterSessionsParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            cast_to=UsageCodeInterpreterSessionsResponse,
        )

    def completions(
        self,
        *,
        start_time: int,
        api_key_ids: SequenceNotStr[str] | Omit = omit,
        batch: bool | Omit = omit,
        bucket_width: Literal["1m", "1h", "1d"] | Omit = omit,
        end_time: int | Omit = omit,
        group_by: List[Literal["project_id", "user_id", "api_key_id", "model", "batch", "service_tier"]] | Omit = omit,
        limit: int | Omit = omit,
        models: SequenceNotStr[str] | Omit = omit,
        page: str | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        user_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsageCompletionsResponse:
        """
        Get completions usage details for the organization.

        Args:
          start_time: Start time (Unix seconds) of the query time range, inclusive.

          api_key_ids: Return only usage for these API keys.

          batch: If `true`, return batch jobs only. If `false`, return non-batch jobs only. By
              default, return both.

          bucket_width: Width of each time bucket in response. Currently `1m`, `1h` and `1d` are
              supported, default to `1d`.

          end_time: End time (Unix seconds) of the query time range, exclusive.

          group_by: Group the usage data by the specified fields. Support fields include
              `project_id`, `user_id`, `api_key_id`, `model`, `batch`, `service_tier` or any
              combination of them.

          limit: Specifies the number of buckets to return.

              - `bucket_width=1d`: default: 7, max: 31
              - `bucket_width=1h`: default: 24, max: 168
              - `bucket_width=1m`: default: 60, max: 1440

          models: Return only usage for these models.

          page: A cursor for use in pagination. Corresponding to the `next_page` field from the
              previous response.

          project_ids: Return only usage for these projects.

          user_ids: Return only usage for these users.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/organization/usage/completions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "start_time": start_time,
                        "api_key_ids": api_key_ids,
                        "batch": batch,
                        "bucket_width": bucket_width,
                        "end_time": end_time,
                        "group_by": group_by,
                        "limit": limit,
                        "models": models,
                        "page": page,
                        "project_ids": project_ids,
                        "user_ids": user_ids,
                    },
                    usage_completions_params.UsageCompletionsParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            cast_to=UsageCompletionsResponse,
        )

    def costs(
        self,
        *,
        start_time: int,
        api_key_ids: SequenceNotStr[str] | Omit = omit,
        bucket_width: Literal["1d"] | Omit = omit,
        end_time: int | Omit = omit,
        group_by: List[Literal["project_id", "line_item", "api_key_id"]] | Omit = omit,
        limit: int | Omit = omit,
        page: str | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsageCostsResponse:
        """
        Get costs details for the organization.

        Args:
          start_time: Start time (Unix seconds) of the query time range, inclusive.

          api_key_ids: Return only costs for these API keys.

          bucket_width: Width of each time bucket in response. Currently only `1d` is supported, default
              to `1d`.

          end_time: End time (Unix seconds) of the query time range, exclusive.

          group_by: Group the costs by the specified fields. Support fields include `project_id`,
              `line_item`, `api_key_id` and any combination of them.

          limit: A limit on the number of buckets to be returned. Limit can range between 1 and
              180, and the default is 7.

          page: A cursor for use in pagination. Corresponding to the `next_page` field from the
              previous response.

          project_ids: Return only costs for these projects.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/organization/costs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "start_time": start_time,
                        "api_key_ids": api_key_ids,
                        "bucket_width": bucket_width,
                        "end_time": end_time,
                        "group_by": group_by,
                        "limit": limit,
                        "page": page,
                        "project_ids": project_ids,
                    },
                    usage_costs_params.UsageCostsParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            cast_to=UsageCostsResponse,
        )

    def embeddings(
        self,
        *,
        start_time: int,
        api_key_ids: SequenceNotStr[str] | Omit = omit,
        bucket_width: Literal["1m", "1h", "1d"] | Omit = omit,
        end_time: int | Omit = omit,
        group_by: List[Literal["project_id", "user_id", "api_key_id", "model"]] | Omit = omit,
        limit: int | Omit = omit,
        models: SequenceNotStr[str] | Omit = omit,
        page: str | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        user_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsageEmbeddingsResponse:
        """
        Get embeddings usage details for the organization.

        Args:
          start_time: Start time (Unix seconds) of the query time range, inclusive.

          api_key_ids: Return only usage for these API keys.

          bucket_width: Width of each time bucket in response. Currently `1m`, `1h` and `1d` are
              supported, default to `1d`.

          end_time: End time (Unix seconds) of the query time range, exclusive.

          group_by: Group the usage data by the specified fields. Support fields include
              `project_id`, `user_id`, `api_key_id`, `model` or any combination of them.

          limit: Specifies the number of buckets to return.

              - `bucket_width=1d`: default: 7, max: 31
              - `bucket_width=1h`: default: 24, max: 168
              - `bucket_width=1m`: default: 60, max: 1440

          models: Return only usage for these models.

          page: A cursor for use in pagination. Corresponding to the `next_page` field from the
              previous response.

          project_ids: Return only usage for these projects.

          user_ids: Return only usage for these users.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/organization/usage/embeddings",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "start_time": start_time,
                        "api_key_ids": api_key_ids,
                        "bucket_width": bucket_width,
                        "end_time": end_time,
                        "group_by": group_by,
                        "limit": limit,
                        "models": models,
                        "page": page,
                        "project_ids": project_ids,
                        "user_ids": user_ids,
                    },
                    usage_embeddings_params.UsageEmbeddingsParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            cast_to=UsageEmbeddingsResponse,
        )

    def images(
        self,
        *,
        start_time: int,
        api_key_ids: SequenceNotStr[str] | Omit = omit,
        bucket_width: Literal["1m", "1h", "1d"] | Omit = omit,
        end_time: int | Omit = omit,
        group_by: List[Literal["project_id", "user_id", "api_key_id", "model", "size", "source"]] | Omit = omit,
        limit: int | Omit = omit,
        models: SequenceNotStr[str] | Omit = omit,
        page: str | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        sizes: List[Literal["256x256", "512x512", "1024x1024", "1792x1792", "1024x1792"]] | Omit = omit,
        sources: List[Literal["image.generation", "image.edit", "image.variation"]] | Omit = omit,
        user_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsageImagesResponse:
        """
        Get images usage details for the organization.

        Args:
          start_time: Start time (Unix seconds) of the query time range, inclusive.

          api_key_ids: Return only usage for these API keys.

          bucket_width: Width of each time bucket in response. Currently `1m`, `1h` and `1d` are
              supported, default to `1d`.

          end_time: End time (Unix seconds) of the query time range, exclusive.

          group_by: Group the usage data by the specified fields. Support fields include
              `project_id`, `user_id`, `api_key_id`, `model`, `size`, `source` or any
              combination of them.

          limit: Specifies the number of buckets to return.

              - `bucket_width=1d`: default: 7, max: 31
              - `bucket_width=1h`: default: 24, max: 168
              - `bucket_width=1m`: default: 60, max: 1440

          models: Return only usage for these models.

          page: A cursor for use in pagination. Corresponding to the `next_page` field from the
              previous response.

          project_ids: Return only usage for these projects.

          sizes: Return only usages for these image sizes. Possible values are `256x256`,
              `512x512`, `1024x1024`, `1792x1792`, `1024x1792` or any combination of them.

          sources: Return only usages for these sources. Possible values are `image.generation`,
              `image.edit`, `image.variation` or any combination of them.

          user_ids: Return only usage for these users.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/organization/usage/images",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "start_time": start_time,
                        "api_key_ids": api_key_ids,
                        "bucket_width": bucket_width,
                        "end_time": end_time,
                        "group_by": group_by,
                        "limit": limit,
                        "models": models,
                        "page": page,
                        "project_ids": project_ids,
                        "sizes": sizes,
                        "sources": sources,
                        "user_ids": user_ids,
                    },
                    usage_images_params.UsageImagesParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            cast_to=UsageImagesResponse,
        )

    def moderations(
        self,
        *,
        start_time: int,
        api_key_ids: SequenceNotStr[str] | Omit = omit,
        bucket_width: Literal["1m", "1h", "1d"] | Omit = omit,
        end_time: int | Omit = omit,
        group_by: List[Literal["project_id", "user_id", "api_key_id", "model"]] | Omit = omit,
        limit: int | Omit = omit,
        models: SequenceNotStr[str] | Omit = omit,
        page: str | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        user_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsageModerationsResponse:
        """
        Get moderations usage details for the organization.

        Args:
          start_time: Start time (Unix seconds) of the query time range, inclusive.

          api_key_ids: Return only usage for these API keys.

          bucket_width: Width of each time bucket in response. Currently `1m`, `1h` and `1d` are
              supported, default to `1d`.

          end_time: End time (Unix seconds) of the query time range, exclusive.

          group_by: Group the usage data by the specified fields. Support fields include
              `project_id`, `user_id`, `api_key_id`, `model` or any combination of them.

          limit: Specifies the number of buckets to return.

              - `bucket_width=1d`: default: 7, max: 31
              - `bucket_width=1h`: default: 24, max: 168
              - `bucket_width=1m`: default: 60, max: 1440

          models: Return only usage for these models.

          page: A cursor for use in pagination. Corresponding to the `next_page` field from the
              previous response.

          project_ids: Return only usage for these projects.

          user_ids: Return only usage for these users.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/organization/usage/moderations",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "start_time": start_time,
                        "api_key_ids": api_key_ids,
                        "bucket_width": bucket_width,
                        "end_time": end_time,
                        "group_by": group_by,
                        "limit": limit,
                        "models": models,
                        "page": page,
                        "project_ids": project_ids,
                        "user_ids": user_ids,
                    },
                    usage_moderations_params.UsageModerationsParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            cast_to=UsageModerationsResponse,
        )

    def vector_stores(
        self,
        *,
        start_time: int,
        bucket_width: Literal["1m", "1h", "1d"] | Omit = omit,
        end_time: int | Omit = omit,
        group_by: List[Literal["project_id"]] | Omit = omit,
        limit: int | Omit = omit,
        page: str | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsageVectorStoresResponse:
        """
        Get vector stores usage details for the organization.

        Args:
          start_time: Start time (Unix seconds) of the query time range, inclusive.

          bucket_width: Width of each time bucket in response. Currently `1m`, `1h` and `1d` are
              supported, default to `1d`.

          end_time: End time (Unix seconds) of the query time range, exclusive.

          group_by: Group the usage data by the specified fields. Support fields include
              `project_id`.

          limit: Specifies the number of buckets to return.

              - `bucket_width=1d`: default: 7, max: 31
              - `bucket_width=1h`: default: 24, max: 168
              - `bucket_width=1m`: default: 60, max: 1440

          page: A cursor for use in pagination. Corresponding to the `next_page` field from the
              previous response.

          project_ids: Return only usage for these projects.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/organization/usage/vector_stores",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "start_time": start_time,
                        "bucket_width": bucket_width,
                        "end_time": end_time,
                        "group_by": group_by,
                        "limit": limit,
                        "page": page,
                        "project_ids": project_ids,
                    },
                    usage_vector_stores_params.UsageVectorStoresParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            cast_to=UsageVectorStoresResponse,
        )


class AsyncUsage(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUsageWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncUsageWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUsageWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncUsageWithStreamingResponse(self)

    async def audio_speeches(
        self,
        *,
        start_time: int,
        api_key_ids: SequenceNotStr[str] | Omit = omit,
        bucket_width: Literal["1m", "1h", "1d"] | Omit = omit,
        end_time: int | Omit = omit,
        group_by: List[Literal["project_id", "user_id", "api_key_id", "model"]] | Omit = omit,
        limit: int | Omit = omit,
        models: SequenceNotStr[str] | Omit = omit,
        page: str | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        user_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsageAudioSpeechesResponse:
        """
        Get audio speeches usage details for the organization.

        Args:
          start_time: Start time (Unix seconds) of the query time range, inclusive.

          api_key_ids: Return only usage for these API keys.

          bucket_width: Width of each time bucket in response. Currently `1m`, `1h` and `1d` are
              supported, default to `1d`.

          end_time: End time (Unix seconds) of the query time range, exclusive.

          group_by: Group the usage data by the specified fields. Support fields include
              `project_id`, `user_id`, `api_key_id`, `model` or any combination of them.

          limit: Specifies the number of buckets to return.

              - `bucket_width=1d`: default: 7, max: 31
              - `bucket_width=1h`: default: 24, max: 168
              - `bucket_width=1m`: default: 60, max: 1440

          models: Return only usage for these models.

          page: A cursor for use in pagination. Corresponding to the `next_page` field from the
              previous response.

          project_ids: Return only usage for these projects.

          user_ids: Return only usage for these users.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/organization/usage/audio_speeches",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "start_time": start_time,
                        "api_key_ids": api_key_ids,
                        "bucket_width": bucket_width,
                        "end_time": end_time,
                        "group_by": group_by,
                        "limit": limit,
                        "models": models,
                        "page": page,
                        "project_ids": project_ids,
                        "user_ids": user_ids,
                    },
                    usage_audio_speeches_params.UsageAudioSpeechesParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            cast_to=UsageAudioSpeechesResponse,
        )

    async def audio_transcriptions(
        self,
        *,
        start_time: int,
        api_key_ids: SequenceNotStr[str] | Omit = omit,
        bucket_width: Literal["1m", "1h", "1d"] | Omit = omit,
        end_time: int | Omit = omit,
        group_by: List[Literal["project_id", "user_id", "api_key_id", "model"]] | Omit = omit,
        limit: int | Omit = omit,
        models: SequenceNotStr[str] | Omit = omit,
        page: str | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        user_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsageAudioTranscriptionsResponse:
        """
        Get audio transcriptions usage details for the organization.

        Args:
          start_time: Start time (Unix seconds) of the query time range, inclusive.

          api_key_ids: Return only usage for these API keys.

          bucket_width: Width of each time bucket in response. Currently `1m`, `1h` and `1d` are
              supported, default to `1d`.

          end_time: End time (Unix seconds) of the query time range, exclusive.

          group_by: Group the usage data by the specified fields. Support fields include
              `project_id`, `user_id`, `api_key_id`, `model` or any combination of them.

          limit: Specifies the number of buckets to return.

              - `bucket_width=1d`: default: 7, max: 31
              - `bucket_width=1h`: default: 24, max: 168
              - `bucket_width=1m`: default: 60, max: 1440

          models: Return only usage for these models.

          page: A cursor for use in pagination. Corresponding to the `next_page` field from the
              previous response.

          project_ids: Return only usage for these projects.

          user_ids: Return only usage for these users.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/organization/usage/audio_transcriptions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "start_time": start_time,
                        "api_key_ids": api_key_ids,
                        "bucket_width": bucket_width,
                        "end_time": end_time,
                        "group_by": group_by,
                        "limit": limit,
                        "models": models,
                        "page": page,
                        "project_ids": project_ids,
                        "user_ids": user_ids,
                    },
                    usage_audio_transcriptions_params.UsageAudioTranscriptionsParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            cast_to=UsageAudioTranscriptionsResponse,
        )

    async def code_interpreter_sessions(
        self,
        *,
        start_time: int,
        bucket_width: Literal["1m", "1h", "1d"] | Omit = omit,
        end_time: int | Omit = omit,
        group_by: List[Literal["project_id"]] | Omit = omit,
        limit: int | Omit = omit,
        page: str | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsageCodeInterpreterSessionsResponse:
        """
        Get code interpreter sessions usage details for the organization.

        Args:
          start_time: Start time (Unix seconds) of the query time range, inclusive.

          bucket_width: Width of each time bucket in response. Currently `1m`, `1h` and `1d` are
              supported, default to `1d`.

          end_time: End time (Unix seconds) of the query time range, exclusive.

          group_by: Group the usage data by the specified fields. Support fields include
              `project_id`.

          limit: Specifies the number of buckets to return.

              - `bucket_width=1d`: default: 7, max: 31
              - `bucket_width=1h`: default: 24, max: 168
              - `bucket_width=1m`: default: 60, max: 1440

          page: A cursor for use in pagination. Corresponding to the `next_page` field from the
              previous response.

          project_ids: Return only usage for these projects.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/organization/usage/code_interpreter_sessions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "start_time": start_time,
                        "bucket_width": bucket_width,
                        "end_time": end_time,
                        "group_by": group_by,
                        "limit": limit,
                        "page": page,
                        "project_ids": project_ids,
                    },
                    usage_code_interpreter_sessions_params.UsageCodeInterpreterSessionsParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            cast_to=UsageCodeInterpreterSessionsResponse,
        )

    async def completions(
        self,
        *,
        start_time: int,
        api_key_ids: SequenceNotStr[str] | Omit = omit,
        batch: bool | Omit = omit,
        bucket_width: Literal["1m", "1h", "1d"] | Omit = omit,
        end_time: int | Omit = omit,
        group_by: List[Literal["project_id", "user_id", "api_key_id", "model", "batch", "service_tier"]] | Omit = omit,
        limit: int | Omit = omit,
        models: SequenceNotStr[str] | Omit = omit,
        page: str | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        user_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsageCompletionsResponse:
        """
        Get completions usage details for the organization.

        Args:
          start_time: Start time (Unix seconds) of the query time range, inclusive.

          api_key_ids: Return only usage for these API keys.

          batch: If `true`, return batch jobs only. If `false`, return non-batch jobs only. By
              default, return both.

          bucket_width: Width of each time bucket in response. Currently `1m`, `1h` and `1d` are
              supported, default to `1d`.

          end_time: End time (Unix seconds) of the query time range, exclusive.

          group_by: Group the usage data by the specified fields. Support fields include
              `project_id`, `user_id`, `api_key_id`, `model`, `batch`, `service_tier` or any
              combination of them.

          limit: Specifies the number of buckets to return.

              - `bucket_width=1d`: default: 7, max: 31
              - `bucket_width=1h`: default: 24, max: 168
              - `bucket_width=1m`: default: 60, max: 1440

          models: Return only usage for these models.

          page: A cursor for use in pagination. Corresponding to the `next_page` field from the
              previous response.

          project_ids: Return only usage for these projects.

          user_ids: Return only usage for these users.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/organization/usage/completions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "start_time": start_time,
                        "api_key_ids": api_key_ids,
                        "batch": batch,
                        "bucket_width": bucket_width,
                        "end_time": end_time,
                        "group_by": group_by,
                        "limit": limit,
                        "models": models,
                        "page": page,
                        "project_ids": project_ids,
                        "user_ids": user_ids,
                    },
                    usage_completions_params.UsageCompletionsParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            cast_to=UsageCompletionsResponse,
        )

    async def costs(
        self,
        *,
        start_time: int,
        api_key_ids: SequenceNotStr[str] | Omit = omit,
        bucket_width: Literal["1d"] | Omit = omit,
        end_time: int | Omit = omit,
        group_by: List[Literal["project_id", "line_item", "api_key_id"]] | Omit = omit,
        limit: int | Omit = omit,
        page: str | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsageCostsResponse:
        """
        Get costs details for the organization.

        Args:
          start_time: Start time (Unix seconds) of the query time range, inclusive.

          api_key_ids: Return only costs for these API keys.

          bucket_width: Width of each time bucket in response. Currently only `1d` is supported, default
              to `1d`.

          end_time: End time (Unix seconds) of the query time range, exclusive.

          group_by: Group the costs by the specified fields. Support fields include `project_id`,
              `line_item`, `api_key_id` and any combination of them.

          limit: A limit on the number of buckets to be returned. Limit can range between 1 and
              180, and the default is 7.

          page: A cursor for use in pagination. Corresponding to the `next_page` field from the
              previous response.

          project_ids: Return only costs for these projects.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/organization/costs",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "start_time": start_time,
                        "api_key_ids": api_key_ids,
                        "bucket_width": bucket_width,
                        "end_time": end_time,
                        "group_by": group_by,
                        "limit": limit,
                        "page": page,
                        "project_ids": project_ids,
                    },
                    usage_costs_params.UsageCostsParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            cast_to=UsageCostsResponse,
        )

    async def embeddings(
        self,
        *,
        start_time: int,
        api_key_ids: SequenceNotStr[str] | Omit = omit,
        bucket_width: Literal["1m", "1h", "1d"] | Omit = omit,
        end_time: int | Omit = omit,
        group_by: List[Literal["project_id", "user_id", "api_key_id", "model"]] | Omit = omit,
        limit: int | Omit = omit,
        models: SequenceNotStr[str] | Omit = omit,
        page: str | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        user_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsageEmbeddingsResponse:
        """
        Get embeddings usage details for the organization.

        Args:
          start_time: Start time (Unix seconds) of the query time range, inclusive.

          api_key_ids: Return only usage for these API keys.

          bucket_width: Width of each time bucket in response. Currently `1m`, `1h` and `1d` are
              supported, default to `1d`.

          end_time: End time (Unix seconds) of the query time range, exclusive.

          group_by: Group the usage data by the specified fields. Support fields include
              `project_id`, `user_id`, `api_key_id`, `model` or any combination of them.

          limit: Specifies the number of buckets to return.

              - `bucket_width=1d`: default: 7, max: 31
              - `bucket_width=1h`: default: 24, max: 168
              - `bucket_width=1m`: default: 60, max: 1440

          models: Return only usage for these models.

          page: A cursor for use in pagination. Corresponding to the `next_page` field from the
              previous response.

          project_ids: Return only usage for these projects.

          user_ids: Return only usage for these users.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/organization/usage/embeddings",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "start_time": start_time,
                        "api_key_ids": api_key_ids,
                        "bucket_width": bucket_width,
                        "end_time": end_time,
                        "group_by": group_by,
                        "limit": limit,
                        "models": models,
                        "page": page,
                        "project_ids": project_ids,
                        "user_ids": user_ids,
                    },
                    usage_embeddings_params.UsageEmbeddingsParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            cast_to=UsageEmbeddingsResponse,
        )

    async def images(
        self,
        *,
        start_time: int,
        api_key_ids: SequenceNotStr[str] | Omit = omit,
        bucket_width: Literal["1m", "1h", "1d"] | Omit = omit,
        end_time: int | Omit = omit,
        group_by: List[Literal["project_id", "user_id", "api_key_id", "model", "size", "source"]] | Omit = omit,
        limit: int | Omit = omit,
        models: SequenceNotStr[str] | Omit = omit,
        page: str | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        sizes: List[Literal["256x256", "512x512", "1024x1024", "1792x1792", "1024x1792"]] | Omit = omit,
        sources: List[Literal["image.generation", "image.edit", "image.variation"]] | Omit = omit,
        user_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsageImagesResponse:
        """
        Get images usage details for the organization.

        Args:
          start_time: Start time (Unix seconds) of the query time range, inclusive.

          api_key_ids: Return only usage for these API keys.

          bucket_width: Width of each time bucket in response. Currently `1m`, `1h` and `1d` are
              supported, default to `1d`.

          end_time: End time (Unix seconds) of the query time range, exclusive.

          group_by: Group the usage data by the specified fields. Support fields include
              `project_id`, `user_id`, `api_key_id`, `model`, `size`, `source` or any
              combination of them.

          limit: Specifies the number of buckets to return.

              - `bucket_width=1d`: default: 7, max: 31
              - `bucket_width=1h`: default: 24, max: 168
              - `bucket_width=1m`: default: 60, max: 1440

          models: Return only usage for these models.

          page: A cursor for use in pagination. Corresponding to the `next_page` field from the
              previous response.

          project_ids: Return only usage for these projects.

          sizes: Return only usages for these image sizes. Possible values are `256x256`,
              `512x512`, `1024x1024`, `1792x1792`, `1024x1792` or any combination of them.

          sources: Return only usages for these sources. Possible values are `image.generation`,
              `image.edit`, `image.variation` or any combination of them.

          user_ids: Return only usage for these users.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/organization/usage/images",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "start_time": start_time,
                        "api_key_ids": api_key_ids,
                        "bucket_width": bucket_width,
                        "end_time": end_time,
                        "group_by": group_by,
                        "limit": limit,
                        "models": models,
                        "page": page,
                        "project_ids": project_ids,
                        "sizes": sizes,
                        "sources": sources,
                        "user_ids": user_ids,
                    },
                    usage_images_params.UsageImagesParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            cast_to=UsageImagesResponse,
        )

    async def moderations(
        self,
        *,
        start_time: int,
        api_key_ids: SequenceNotStr[str] | Omit = omit,
        bucket_width: Literal["1m", "1h", "1d"] | Omit = omit,
        end_time: int | Omit = omit,
        group_by: List[Literal["project_id", "user_id", "api_key_id", "model"]] | Omit = omit,
        limit: int | Omit = omit,
        models: SequenceNotStr[str] | Omit = omit,
        page: str | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        user_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsageModerationsResponse:
        """
        Get moderations usage details for the organization.

        Args:
          start_time: Start time (Unix seconds) of the query time range, inclusive.

          api_key_ids: Return only usage for these API keys.

          bucket_width: Width of each time bucket in response. Currently `1m`, `1h` and `1d` are
              supported, default to `1d`.

          end_time: End time (Unix seconds) of the query time range, exclusive.

          group_by: Group the usage data by the specified fields. Support fields include
              `project_id`, `user_id`, `api_key_id`, `model` or any combination of them.

          limit: Specifies the number of buckets to return.

              - `bucket_width=1d`: default: 7, max: 31
              - `bucket_width=1h`: default: 24, max: 168
              - `bucket_width=1m`: default: 60, max: 1440

          models: Return only usage for these models.

          page: A cursor for use in pagination. Corresponding to the `next_page` field from the
              previous response.

          project_ids: Return only usage for these projects.

          user_ids: Return only usage for these users.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/organization/usage/moderations",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "start_time": start_time,
                        "api_key_ids": api_key_ids,
                        "bucket_width": bucket_width,
                        "end_time": end_time,
                        "group_by": group_by,
                        "limit": limit,
                        "models": models,
                        "page": page,
                        "project_ids": project_ids,
                        "user_ids": user_ids,
                    },
                    usage_moderations_params.UsageModerationsParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            cast_to=UsageModerationsResponse,
        )

    async def vector_stores(
        self,
        *,
        start_time: int,
        bucket_width: Literal["1m", "1h", "1d"] | Omit = omit,
        end_time: int | Omit = omit,
        group_by: List[Literal["project_id"]] | Omit = omit,
        limit: int | Omit = omit,
        page: str | Omit = omit,
        project_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UsageVectorStoresResponse:
        """
        Get vector stores usage details for the organization.

        Args:
          start_time: Start time (Unix seconds) of the query time range, inclusive.

          bucket_width: Width of each time bucket in response. Currently `1m`, `1h` and `1d` are
              supported, default to `1d`.

          end_time: End time (Unix seconds) of the query time range, exclusive.

          group_by: Group the usage data by the specified fields. Support fields include
              `project_id`.

          limit: Specifies the number of buckets to return.

              - `bucket_width=1d`: default: 7, max: 31
              - `bucket_width=1h`: default: 24, max: 168
              - `bucket_width=1m`: default: 60, max: 1440

          page: A cursor for use in pagination. Corresponding to the `next_page` field from the
              previous response.

          project_ids: Return only usage for these projects.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/organization/usage/vector_stores",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "start_time": start_time,
                        "bucket_width": bucket_width,
                        "end_time": end_time,
                        "group_by": group_by,
                        "limit": limit,
                        "page": page,
                        "project_ids": project_ids,
                    },
                    usage_vector_stores_params.UsageVectorStoresParams,
                ),
                security={"admin_api_key_auth": True},
            ),
            cast_to=UsageVectorStoresResponse,
        )


class UsageWithRawResponse:
    def __init__(self, usage: Usage) -> None:
        self._usage = usage

        self.audio_speeches = _legacy_response.to_raw_response_wrapper(
            usage.audio_speeches,
        )
        self.audio_transcriptions = _legacy_response.to_raw_response_wrapper(
            usage.audio_transcriptions,
        )
        self.code_interpreter_sessions = _legacy_response.to_raw_response_wrapper(
            usage.code_interpreter_sessions,
        )
        self.completions = _legacy_response.to_raw_response_wrapper(
            usage.completions,
        )
        self.costs = _legacy_response.to_raw_response_wrapper(
            usage.costs,
        )
        self.embeddings = _legacy_response.to_raw_response_wrapper(
            usage.embeddings,
        )
        self.images = _legacy_response.to_raw_response_wrapper(
            usage.images,
        )
        self.moderations = _legacy_response.to_raw_response_wrapper(
            usage.moderations,
        )
        self.vector_stores = _legacy_response.to_raw_response_wrapper(
            usage.vector_stores,
        )


class AsyncUsageWithRawResponse:
    def __init__(self, usage: AsyncUsage) -> None:
        self._usage = usage

        self.audio_speeches = _legacy_response.async_to_raw_response_wrapper(
            usage.audio_speeches,
        )
        self.audio_transcriptions = _legacy_response.async_to_raw_response_wrapper(
            usage.audio_transcriptions,
        )
        self.code_interpreter_sessions = _legacy_response.async_to_raw_response_wrapper(
            usage.code_interpreter_sessions,
        )
        self.completions = _legacy_response.async_to_raw_response_wrapper(
            usage.completions,
        )
        self.costs = _legacy_response.async_to_raw_response_wrapper(
            usage.costs,
        )
        self.embeddings = _legacy_response.async_to_raw_response_wrapper(
            usage.embeddings,
        )
        self.images = _legacy_response.async_to_raw_response_wrapper(
            usage.images,
        )
        self.moderations = _legacy_response.async_to_raw_response_wrapper(
            usage.moderations,
        )
        self.vector_stores = _legacy_response.async_to_raw_response_wrapper(
            usage.vector_stores,
        )


class UsageWithStreamingResponse:
    def __init__(self, usage: Usage) -> None:
        self._usage = usage

        self.audio_speeches = to_streamed_response_wrapper(
            usage.audio_speeches,
        )
        self.audio_transcriptions = to_streamed_response_wrapper(
            usage.audio_transcriptions,
        )
        self.code_interpreter_sessions = to_streamed_response_wrapper(
            usage.code_interpreter_sessions,
        )
        self.completions = to_streamed_response_wrapper(
            usage.completions,
        )
        self.costs = to_streamed_response_wrapper(
            usage.costs,
        )
        self.embeddings = to_streamed_response_wrapper(
            usage.embeddings,
        )
        self.images = to_streamed_response_wrapper(
            usage.images,
        )
        self.moderations = to_streamed_response_wrapper(
            usage.moderations,
        )
        self.vector_stores = to_streamed_response_wrapper(
            usage.vector_stores,
        )


class AsyncUsageWithStreamingResponse:
    def __init__(self, usage: AsyncUsage) -> None:
        self._usage = usage

        self.audio_speeches = async_to_streamed_response_wrapper(
            usage.audio_speeches,
        )
        self.audio_transcriptions = async_to_streamed_response_wrapper(
            usage.audio_transcriptions,
        )
        self.code_interpreter_sessions = async_to_streamed_response_wrapper(
            usage.code_interpreter_sessions,
        )
        self.completions = async_to_streamed_response_wrapper(
            usage.completions,
        )
        self.costs = async_to_streamed_response_wrapper(
            usage.costs,
        )
        self.embeddings = async_to_streamed_response_wrapper(
            usage.embeddings,
        )
        self.images = async_to_streamed_response_wrapper(
            usage.images,
        )
        self.moderations = async_to_streamed_response_wrapper(
            usage.moderations,
        )
        self.vector_stores = async_to_streamed_response_wrapper(
            usage.vector_stores,
        )
