> [!IMPORTANT]
> This page is not currently maintained and is intended to provide general insight into the ChatML format, not current up-to-date information.

(This document is a preview of the underlying format consumed by
GPT models. As a developer, you can use our [higher-level
API](https://platform.openai.com/docs/guides/chat) and won't need to
interact directly with this format today — but expect to have the
option in the future!)

Traditionally, GPT models consumed unstructured text. ChatGPT models
instead expect a structured format, called Chat Markup Language
(ChatML for short).
ChatML documents consist of a sequence of messages. Each message
contains a header (which today consists of who said it, but in the
future will contain other metadata) and contents (which today is a
text payload, but in the future will contain other datatypes).
We are still evolving ChatML, but the current version (ChatML v0) can
be represented with our upcoming "list of dicts" JSON format as
follows:
```
[
 {"token": "<|im_start|>"},
 "system\nYou are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible.\nKnowledge cutoff: 2021-09-01\nCurrent date: 2023-03-01",
 {"token": "<|im_end|>"}, "\n", {"token": "<|im_start|>"},
 "user\nHow are you",
 {"token": "<|im_end|>"}, "\n", {"token": "<|im_start|>"},
 "assistant\nI am doing well!",
 {"token": "<|im_end|>"}, "\n", {"token": "<|im_start|>"},
 "user\nHow are you now?",
 {"token": "<|im_end|>"}, "\n"
]
```
You could also represent it in the classic "unsafe raw string"
format. However, this format inherently allows injections from user
input containing special-token syntax, similar to SQL injections:
```
<|im_start|>system
You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible.
Knowledge cutoff: 2021-09-01
Current date: 2023-03-01<|im_end|>
<|im_start|>user
How are you<|im_end|>
<|im_start|>assistant
I am doing well!<|im_end|>
<|im_start|>user
How are you now?<|im_end|>
```
## Non-chat use-cases
ChatML can be applied to classic GPT use-cases that are not
traditionally thought of as chat. For example, instruction following
(where a user requests for the AI to complete an instruction) can be
implemented as a ChatML query like the following:
```
[
 {"token": "<|im_start|>"},
 "user\nList off some good ideas:",
 {"token": "<|im_end|>"}, "\n", {"token": "<|im_start|>"},
 "assistant"
]
```
We do not currently allow autocompleting of partial messages, 
```
[
 {"token": "<|im_start|>"},
 "system\nPlease autocomplete the user's message.",
 {"token": "<|im_end|>"}, "\n", {"token": "<|im_start|>"},
 "user\nThis morning I decided to eat a giant"
]
```
Note that ChatML makes explicit to the model the source of each piece
of text, and particularly shows the boundary between human and AI
text. This gives an opportunity to mitigate and eventually solve
injections, as the model can tell which instructions come from the
developer, the user, or its own input.
## Few-shot prompting
In general, we recommend adding few-shot examples using separate
`system` messages with a `name` field of `example_user` or
`example_assistant`. For example, here is a 1-shot prompt:
```
<|im_start|>system
Translate from English to French
<|im_end|>
<|im_start|>system name=example_user
How are you?
<|im_end|>
<|im_start|>system name=example_assistant
Comment allez-vous?
<|im_end|>
<|im_start|>user
{{user input here}}<|im_end|>
```
If adding instructions in the `system` message doesn't work, you can
also try putting them into a `user` message. (In the near future, we
will train our models to be much more steerable via the system
message. But to date, we have trained only on a few system messages,
so the models pay much more attention to user examples.)
