Traditionally, GPT models consumed unstructured text. ChatGPT models
instead expect a structured format, called Chat Markup Language
(ChatML for short).

ChatML documents consists of a sequence of messages. Each message
contains a header (which today consists of who said it, but in the
future will contain other metadata) and contents (which today is a
text payload, but in the future will contain other datatypes).

On the wire, we represent ChatML with JSON as follows:

```
[
 {"token": "<|start|>"}, "system", {"token": "<|message|>"},
 "You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible.\nKnowledge cutoff: 2021-09-01\nCurrent date: 2023-03-01",
 {"token": "<|end_message|>"},
 {"token": "<|start|>"}, "user", {"token": "<|message|>"},
 "How are you",
 {"token": "<|end_message|>"},
 {"token": "<|start|>"}, "assistant", {"token": "<|message|>”},
 "I am doing well!",
 {"token": "<|end_message|>"},
 {"token": "<|start|>"}, "user", {"token": "<|end_message|>"},
 "How are you now?",
 {"token": "<|end_message|>"}
]
```

For the rest of this document, for reading clarity we will represent
multi-line strings with real newlines, even though this is not
actually valid JSON. That is, when sending to the API, you'll need to
submit as `"foo\nbar"` rather than ```foo
bar```

## Grammar

More formally, you can think of ChatML being defined with the
following grammar:

```
Text ::= any string of text not including special tokens.
<|special_token|> ::= any special token.
RoleName ::= {"user", "assistant", "system", "system:example_user", "system:example_assistant"}

MessageHeader ::= <|start|>RoleName<|message|>

Message ::= MessageHeader + Text + MessageFooter
MessageFooter ::= <|end_message|>

CompletionRequest ::= MessageHeader + (Text) | <|start|>Assistant # Can supply a partial message if you'd like, or even let the model complete the Assistant's header

FormattedRequest ::= CompletionRequest | [Message] + FormattedRequest # the final string passed to the model.
FormattedCompletion ::= Text + MessageFooter # In our Python implementation, we pass this to the user-supplied parse function
```

## Truncations

When a conversation exceeds a certain token budget, it's up to the
user to decide how to truncate the conversation for the model. Our
[Python
library](https://github.com/openai/chat/blob/main/chat/renderer/truncation.py)
uses one truncation convention where it preserves the system message
and then uses a heuristic to decide which messages to drop. It also
always truncates any message that's beyond 2k tokens.

Our models are currently trained using this truncation
system. However, we do not think it is optimal, and we plan to vary
the truncation in the future so that the model is open to essentially
any truncation scheme. We recommend that developers play with
different truncation schemes to try to figure out how to best present
the most important information in giant conversations for the model.

In upcoming releases, we expect to have more concrete recommendations
on truncations, but for now it's worth experimenting broadly!

## Non-chat use-cases

ChatML can be applied to classic GPT use-cases that are not
traditionally thought of as chat. For example, instruction following
(where a user requests for the AI to complete an instruction) can be
implemented as a ChatML query like the following:

```
[
 {"token": "<|start|>"}, "user", {"token": "<|message|>"},
 "List off some good ideas:",
 {"token": "<|end_message|>"},
 {"token": "<|start|>"}, "assistant", {"token": "<|message|>"},
]
```

Autocomplete can be implemented as follows:

```
[
 {"token": "<|start|>"}, "user", {"token": "<|message|>"},
 "This morning I decided to eat a giant",
]
```

Note that ChatML explicit to the model the source of each piece of
text, and particularly shows the boundary between human and AI
text. This gives an opportunity to mitigate and eventually solve
injections, as the model can tell which instructions come from the
developer, the user, or its own input.

## Few-shot prompting

In the future, we will train our models to adhere more closely to the
system message. Today, we have trained only on few system messages, so
the models pay much most attention to user examples. However, we've
also found that the models are reasonably steerable via instructions
in the system message. So often the best way to implement few-shot
prompting is as follows (this example is a 1-shot prompt, i.e. one
full example of the task):

```
[
 {"token": "<|start|>"}, "system", {"token": "<|message|>"},
 "You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible.
Knowledge cutoff: 2021-09-01
Current date: 2023-03-01

Your job is to translate from English to French",
 {"token": "<|end_message|>"},
 {"token": "<|start|>"}, "system:example_user", {"token": "<|message|>"},
"How are you?",
 {"token": "<|end_message|>"},
 {"token": "<|start|>"}, "assistant:example_user", {"token": "<|message|>”},
"Comment allez-vous?",
 {"token": "<|end_message|>"},
 {"token": "<|start|>"}, "user", {"token": "<|end_message|>"},
"{{user input here}}",
]
```
