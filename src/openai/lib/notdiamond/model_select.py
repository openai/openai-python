import copy
import json

import ppdeep
import requests


def model_select(messages: list, llm_providers: list, api_key: str):
    url = "https://not-diamond-server.onrender.com/v1/optimizer/modelSelect"

    prompt_payload_part = transform_messages(copy.deepcopy(messages))
    final_payload = {
        **prompt_payload_part,
        "llm_providers": transformed_providers(llm_providers),
        "metric": "accuracy",
        "max_model_depth": len(llm_providers),
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    try:
        response = requests.post(url, data=json.dumps(final_payload), headers=headers)
    except Exception as e:
        print(f"ND API error for modelSelect: {e}")
        return None

    if response.status_code == 200:
        response_json = response.json()

        result_providers = response_json["providers"]
        top_provider = result_providers[0]

        return top_provider["model"]
    else:
        print(f"ND API error: {response.status_code}")
        return None


def transform_messages(messages: list):
    template = """SYSTEM: {system_prompt}
    CONTEXT: {context_prompt}
    QUERY: {user_query}
    """
    user_query = messages.pop()[1]
    system_prompt = ""
    context_prompt = ""

    for k, v in messages:
        if k == "system":
            system_prompt += f"{v}\n"
        elif k == "user":
            context_prompt += f"User: {v}\n"
        elif k == "assistant":
            context_prompt += f"Assistant: {v}\n"

    return {
        "prompt_template": template,
        "formatted_prompt": nd_hash(
            template.format(system_prompt=system_prompt, context_prompt=context_prompt, user_query=user_query)
        ),
        "components": {
            "system_prompt": {"module_type": "NDPrompt", "content": nd_hash(system_prompt)},
            "context_prompt": {"module_type": "NDContext", "content": nd_hash(context_prompt)},
            "user_query": {"module_type": "NDQuery", "content": nd_hash(user_query)},
        },
    }


def transformed_providers(llm_providers: list):
    result = []
    for v in llm_providers:
        splits = v.split("/")
        result.append({"provider": splits[0], "model": splits[1]})
    return result


def nd_hash(s: str) -> str:
    """
    Source of library from: https://github.com/elceef/ppdeep
    """
    return ppdeep.hash(s)
