#!/usr/bin/env -S rye run python

from openai import OciOpenAI, OciSessionAuth

client = OciOpenAI(
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    auth=OciSessionAuth(profile_name="<profile name>"),
    compartment_id="<compartment ocid>",
)

completion = client.chat.completions.create(
    model="<model name>",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.model_dump_json())
