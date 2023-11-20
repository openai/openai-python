# Changelog

## 1.3.3 (2023-11-17)

Full Changelog: [v1.3.2...v1.3.3](https://github.com/openai/openai-python/compare/v1.3.2...v1.3.3)

### Chores

* **internal:** update type hint for helper function ([#846](https://github.com/openai/openai-python/issues/846)) ([9a5966c](https://github.com/openai/openai-python/commit/9a5966c70fce620a183de580938556730564a405))

## 1.3.2 (2023-11-16)

Full Changelog: [v1.3.1...v1.3.2](https://github.com/openai/openai-python/compare/v1.3.1...v1.3.2)

### Documentation

* **readme:** minor updates ([#841](https://github.com/openai/openai-python/issues/841)) ([7273ad1](https://github.com/openai/openai-python/commit/7273ad1510043d3e264969c72403a1a237401910))

## 1.3.1 (2023-11-16)

Full Changelog: [v1.3.0...v1.3.1](https://github.com/openai/openai-python/compare/v1.3.0...v1.3.1)

### Chores

* **internal:** add publish script ([#838](https://github.com/openai/openai-python/issues/838)) ([3ea41bc](https://github.com/openai/openai-python/commit/3ea41bcede374c4e5c92d85108281637c3382e12))

## 1.3.0 (2023-11-15)

Full Changelog: [v1.2.4...v1.3.0](https://github.com/openai/openai-python/compare/v1.2.4...v1.3.0)

### Features

* **api:** add gpt-3.5-turbo-1106 ([#813](https://github.com/openai/openai-python/issues/813)) ([9bb3c4e](https://github.com/openai/openai-python/commit/9bb3c4ed88c890db2605a793aa39fffa1d84e8ef))
* **client:** support reading the base url from an env variable ([#829](https://github.com/openai/openai-python/issues/829)) ([ca5fdc6](https://github.com/openai/openai-python/commit/ca5fdc6ca006a3550cc5eeea70dd3d96b9ba305a))


### Bug Fixes

* **breaking!:** correct broken type names in moderation categories  ([#811](https://github.com/openai/openai-python/issues/811)) ([0bc211f](https://github.com/openai/openai-python/commit/0bc211fd46f4fcc1f7687bdfdce26894b679cb4f))


### Chores

* fix typo in docs and add request header for function calls ([#807](https://github.com/openai/openai-python/issues/807)) ([cbef703](https://github.com/openai/openai-python/commit/cbef7030c7b21a0c766fe83c62657cea1cd8d31c))
* **internal:** fix devcontainer interpeter path ([#810](https://github.com/openai/openai-python/issues/810)) ([0acc07d](https://github.com/openai/openai-python/commit/0acc07dd8281ba881f91689b8a5e4254e8743fbc))


### Documentation

* add azure env vars ([#814](https://github.com/openai/openai-python/issues/814)) ([bd8e32a](https://github.com/openai/openai-python/commit/bd8e32a380218d0c9ff43643ccc1a25b3c35120d))
* fix code comment typo ([#790](https://github.com/openai/openai-python/issues/790)) ([8407a27](https://github.com/openai/openai-python/commit/8407a27e848ae611eb087c8d10632447d7c55498))
* **readme:** fix broken azure_ad notebook link ([#781](https://github.com/openai/openai-python/issues/781)) ([3b92cdf](https://github.com/openai/openai-python/commit/3b92cdfa5490b50a72811bec2f6e54e070847961))

## 1.2.4 (2023-11-13)

Full Changelog: [v1.2.3...v1.2.4](https://github.com/openai/openai-python/compare/v1.2.3...v1.2.4)

### Bug Fixes

* **client:** retry if SSLWantReadError occurs in the async client ([#804](https://github.com/openai/openai-python/issues/804)) ([be82288](https://github.com/openai/openai-python/commit/be82288f3c88c10c9ac20ba3b8cb53b5c7a4e2f9))

## 1.2.3 (2023-11-10)

Full Changelog: [v1.2.2...v1.2.3](https://github.com/openai/openai-python/compare/v1.2.2...v1.2.3)

### Bug Fixes

* **cli/audio:** file format detection failing for whisper ([#733](https://github.com/openai/openai-python/issues/733)) ([01079d6](https://github.com/openai/openai-python/commit/01079d6dca13e0ec158dff81e0706d8a9d6c02ef))
* **client:** correctly flush the stream response body ([#771](https://github.com/openai/openai-python/issues/771)) ([0d52731](https://github.com/openai/openai-python/commit/0d5273165c96286f8456ae04b9eb0de5144e52f8))
* **client:** serialise pydantic v1 default fields correctly in params ([#776](https://github.com/openai/openai-python/issues/776)) ([d4c49ad](https://github.com/openai/openai-python/commit/d4c49ad2be9c0d926eece5fd33f6836279ea21e2))
* **models:** mark unknown fields as set in pydantic v1 ([#772](https://github.com/openai/openai-python/issues/772)) ([ae032a1](https://github.com/openai/openai-python/commit/ae032a1ba4efa72284a572bfaf0305af50142835))
* prevent IndexError in fine-tunes CLI ([#768](https://github.com/openai/openai-python/issues/768)) ([42f1633](https://github.com/openai/openai-python/commit/42f16332cf0f96f243f9797d6406283865254355))


### Documentation

* reword package description ([#764](https://github.com/openai/openai-python/issues/764)) ([9ff10df](https://github.com/openai/openai-python/commit/9ff10df30ca2d44978eb5f982ccf039c9f1bf1bf))

## 1.2.2 (2023-11-09)

Full Changelog: [v1.2.1...v1.2.2](https://github.com/openai/openai-python/compare/v1.2.1...v1.2.2)

### Bug Fixes

* **client:** correctly assign error properties ([#759](https://github.com/openai/openai-python/issues/759)) ([ef264d2](https://github.com/openai/openai-python/commit/ef264d2293b77784f69039291ca2a17a454851cb))


### Documentation

* **readme:** link to migration guide ([#761](https://github.com/openai/openai-python/issues/761)) ([ddde839](https://github.com/openai/openai-python/commit/ddde8392be19e7ad77280374806667ecaef612da))

## 1.2.1 (2023-11-09)

Full Changelog: [v1.2.0...v1.2.1](https://github.com/openai/openai-python/compare/v1.2.0...v1.2.1)

### Documentation

* **readme:** fix nested params example ([#756](https://github.com/openai/openai-python/issues/756)) ([ffbe5ec](https://github.com/openai/openai-python/commit/ffbe5eca0f8790ebcdb27ffe845da178a3ef4c45))


### Refactors

* **client:** deprecate files.retrieve_content in favour of files.content ([#753](https://github.com/openai/openai-python/issues/753)) ([eea5bc1](https://github.com/openai/openai-python/commit/eea5bc173466f63a6e84bd2d741b4873ca056b4c))

## 1.2.0 (2023-11-08)

Full Changelog: [v1.1.2...v1.2.0](https://github.com/openai/openai-python/compare/v1.1.2...v1.2.0)

### Features

* **api:** unify function types ([#741](https://github.com/openai/openai-python/issues/741)) ([ed16c4d](https://github.com/openai/openai-python/commit/ed16c4d2fec6cf4e33235d82b05ed9a777752204))
* **client:** support passing chunk size for binary responses ([#747](https://github.com/openai/openai-python/issues/747)) ([c0c89b7](https://github.com/openai/openai-python/commit/c0c89b77a69ef098900e3a194894efcf72085d36))


### Bug Fixes

* **api:** update embedding response object type ([#739](https://github.com/openai/openai-python/issues/739)) ([29182c4](https://github.com/openai/openai-python/commit/29182c4818e2c56f46e961dba33e31dc30c25519))
* **client:** show a helpful error message if the v0 API is used ([#743](https://github.com/openai/openai-python/issues/743)) ([920567c](https://github.com/openai/openai-python/commit/920567cb04df48a7f6cd2a3402a0b1f172c6290e))


### Chores

* **internal:** improve github devcontainer setup ([#737](https://github.com/openai/openai-python/issues/737)) ([0ac1abb](https://github.com/openai/openai-python/commit/0ac1abb07ec687a4f7b1150be10054dbd6e7cfbc))


### Refactors

* **api:** rename FunctionObject to FunctionDefinition ([#746](https://github.com/openai/openai-python/issues/746)) ([1afd138](https://github.com/openai/openai-python/commit/1afd13856c0e586ecbde8b24fe4f4bad9beeefdf))

## 1.1.2 (2023-11-08)

Full Changelog: [v1.1.1...v1.1.2](https://github.com/openai/openai-python/compare/v1.1.1...v1.1.2)

### Bug Fixes

* **api:** accidentally required params, add new models & other fixes ([#729](https://github.com/openai/openai-python/issues/729)) ([03c3e03](https://github.com/openai/openai-python/commit/03c3e03fc758cf4e59b81edf73a2618d80b560b7))
* asssitant_deleted -&gt; assistant_deleted ([#711](https://github.com/openai/openai-python/issues/711)) ([287b51e](https://github.com/openai/openai-python/commit/287b51e4f7cede9667c118007de1275eb04772c6))


### Chores

* **docs:** fix github links ([#719](https://github.com/openai/openai-python/issues/719)) ([0cda8ca](https://github.com/openai/openai-python/commit/0cda8cab718d53d7dc0604d9fac52838c9391565))
* **internal:** fix some typos ([#718](https://github.com/openai/openai-python/issues/718)) ([894ad87](https://github.com/openai/openai-python/commit/894ad874aaa5d74530f561896ff31f68693418da))
