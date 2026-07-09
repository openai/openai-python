from __future__ import annotations

from openai import OpenAI
from openai.types.beta import BetaResponseOutputItem

PROMPT = """Compare these fictional proposals on speed, cost, reliability, and security.
Proposal Alpha: 2-week launch, $40k, managed vendor, 99.9% SLA, data leaves the VPC.
Proposal Beta: 6-week launch, $70k, self-hosted, 99.5% target, data stays in the VPC.
Delegate each proposal to a separate agent, then compare their evidence and recommend one."""


def agent_name(item: BetaResponseOutputItem) -> str:
    return item.agent.agent_name if item.agent else "/root"


client = OpenAI()

stream = client.beta.responses.create(
    model="gpt-5.6-sol",
    input=PROMPT,
    multi_agent={"enabled": True},
    stream=True,
    betas=["responses_multi_agent=v1"],
)

item_agents: dict[int, str] = {}
labeled_items: set[int] = set()
for event in stream:
    if event.type == "response.output_item.added":
        item_agents[event.output_index] = agent_name(event.item)
    elif event.type == "response.output_text.delta":
        name = item_agents.get(event.output_index, "/root")
        if event.output_index not in labeled_items:
            separator = "\n\n" if labeled_items else ""
            role = "Coordinator" if name == "/root" else "Agent"
            print(f"{separator}━━━ {role}: {name} ━━━\n")
            labeled_items.add(event.output_index)
        print(event.delta, end="", flush=True)

print()
