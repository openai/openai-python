# Changelog

## 1.93.3 (2025-07-09)

Full Changelog: [v1.93.2...v1.93.3](https://github.com/openai/openai-python/compare/v1.93.2...v1.93.3)

### Bug Fixes

* **parsing:** correctly handle nested discriminated unions ([fc8a677](https://github.com/openai/openai-python/commit/fc8a67715d8f1b45d8639b8b6f9f6590fe358734))

## 1.93.2 (2025-07-08)

Full Changelog: [v1.93.1...v1.93.2](https://github.com/openai/openai-python/compare/v1.93.1...v1.93.2)

### Chores

* **internal:** bump pinned h11 dep ([4fca6ae](https://github.com/openai/openai-python/commit/4fca6ae2d0d7f27cbac8d06c3917932767c8c6b8))
* **package:** mark python 3.13 as supported ([2229047](https://github.com/openai/openai-python/commit/2229047b8a549df16c617bddfe3b4521cfd257a5))

## 1.93.1 (2025-07-07)

Full Changelog: [v1.93.0...v1.93.1](https://github.com/openai/openai-python/compare/v1.93.0...v1.93.1)

### Bug Fixes

* **ci:** correct conditional ([de6a9ce](https://github.com/openai/openai-python/commit/de6a9ce078731d60b0bdc42a9322548c575f11a3))
* **responses:** add missing arguments to parse ([05590ec](https://github.com/openai/openai-python/commit/05590ec2a96399afd05baf5a3ee1d9a744f09c40))
* **vector stores:** add missing arguments to files.create_and_poll ([3152134](https://github.com/openai/openai-python/commit/3152134510532ec7c522d6b50a820deea205b602))
* **vector stores:** add missing arguments to files.upload_and_poll ([9d4f425](https://github.com/openai/openai-python/commit/9d4f42569d5b59311453b1b11ee1dd2e8a271268))


### Chores

* **ci:** change upload type ([cd4aa88](https://github.com/openai/openai-python/commit/cd4aa889c50581d861728c9606327992485f0d0d))
* **ci:** only run for pushes and fork pull requests ([f89c7eb](https://github.com/openai/openai-python/commit/f89c7eb46c6f081254715d75543cbee3ffa83822))
* **internal:** codegen related update ([bddb8d2](https://github.com/openai/openai-python/commit/bddb8d2091455920e8526068d64f3f8a5cac7ae6))
* **tests:** ensure parse method is in sync with create ([4f58e18](https://github.com/openai/openai-python/commit/4f58e187c12dc8b2c33e9cca284b0429e5cc4de5))
* **tests:** ensure vector store files create and poll method is in sync ([0fe75a2](https://github.com/openai/openai-python/commit/0fe75a28f6109b2d25b015dc99472a06693e0e9f))

## 1.93.0 (2025-06-27)

Full Changelog: [v1.92.3...v1.93.0](https://github.com/openai/openai-python/compare/v1.92.3...v1.93.0)

### Features

* **cli:** add support for fine_tuning.jobs ([#1224](https://github.com/openai/openai-python/issues/1224)) ([e362bfd](https://github.com/openai/openai-python/commit/e362bfd10dfd04176560b964470ab0c517c601f3))

## 1.92.3 (2025-06-27)

Full Changelog: [v1.92.2...v1.92.3](https://github.com/openai/openai-python/compare/v1.92.2...v1.92.3)

### Bug Fixes

* **client:** avoid encoding error with empty API keys ([5a3e64e](https://github.com/openai/openai-python/commit/5a3e64e0cc761dbaa613fb22ec16e7e73c3bcf72))


### Documentation

* **examples/realtime:** mention macOS requirements ([#2142](https://github.com/openai/openai-python/issues/2142)) ([27bf6b2](https://github.com/openai/openai-python/commit/27bf6b2a933c61d5ec23fd266148af888f69f5c1))

## 1.92.2 (2025-06-26)

Full Changelog: [v1.92.1...v1.92.2](https://github.com/openai/openai-python/compare/v1.92.1...v1.92.2)

### Chores

* **api:** remove unsupported property ([ec24408](https://github.com/openai/openai-python/commit/ec2440864e03278144d7f58b97c31d87903e0843))

## 1.92.1 (2025-06-26)

Full Changelog: [v1.92.0...v1.92.1](https://github.com/openai/openai-python/compare/v1.92.0...v1.92.1)

### Chores

* **client:** sync stream/parse methods over ([e2536cf](https://github.com/openai/openai-python/commit/e2536cfd74224047cece9c2ad86f0ffe51c0667c))
* **docs:** update README to include links to docs on Webhooks ([ddbf9f1](https://github.com/openai/openai-python/commit/ddbf9f1dc47a32257716189f2056b45933328c9c))

## 1.92.0 (2025-06-26)

Full Changelog: [v1.91.0...v1.92.0](https://github.com/openai/openai-python/compare/v1.91.0...v1.92.0)

### Features

* **api:** webhook and deep research support ([d3bb116](https://github.com/openai/openai-python/commit/d3bb116f34f470502f902b88131deec43a953b12))
* **client:** move stream and parse out of beta ([0e358ed](https://github.com/openai/openai-python/commit/0e358ed66b317038705fb38958a449d284f3cb88))


### Bug Fixes

* **ci:** release-doctor — report correct token name ([ff8c556](https://github.com/openai/openai-python/commit/ff8c5561e44e8a0902732b5934c97299d2c98d4e))


### Chores

* **internal:** add tests for breaking change detection ([710fe8f](https://github.com/openai/openai-python/commit/710fe8fd5f9e33730338341680152d3f2556dfa0))
* **tests:** skip some failing tests on the latest python versions ([93ccc38](https://github.com/openai/openai-python/commit/93ccc38a8ef1575d77d33d031666d07d10e4af72))

## 1.91.0 (2025-06-23)

Full Changelog: [v1.90.0...v1.91.0](https://github.com/openai/openai-python/compare/v1.90.0...v1.91.0)

### Features

* **api:** update api shapes for usage and code interpreter ([060d566](https://github.com/openai/openai-python/commit/060d5661e4a1fcdb953c52facd3e668ee80f9295))

## 1.90.0 (2025-06-20)

Full Changelog: [v1.89.0...v1.90.0](https://github.com/openai/openai-python/compare/v1.89.0...v1.90.0)

### Features

* **api:** make model and inputs not required to create response ([11bd62e](https://github.com/openai/openai-python/commit/11bd62eb7e46eec748edaf2e0cecf253ffc1202c))

## 1.89.0 (2025-06-20)

Full Changelog: [v1.88.0...v1.89.0](https://github.com/openai/openai-python/compare/v1.88.0...v1.89.0)

### Features

* **client:** add support for aiohttp ([9218b07](https://github.com/openai/openai-python/commit/9218b07727bf6f6eb00953df66de6ab061fecddb))


### Bug Fixes

* **tests:** fix: tests which call HTTP endpoints directly with the example parameters ([35bcc4b](https://github.com/openai/openai-python/commit/35bcc4b80bdbaa31108650f2a515902e83794e5a))


### Chores

* **readme:** update badges ([68044ee](https://github.com/openai/openai-python/commit/68044ee85d1bf324b17d3f60c914df4725d47fc8))

## 1.88.0 (2025-06-17)

Full Changelog: [v1.87.0...v1.88.0](https://github.com/openai/openai-python/compare/v1.87.0...v1.88.0)

### Features

* **api:** manual updates ([5d18a84](https://github.com/openai/openai-python/commit/5d18a8448ecbe31597e98ec7f64d7050c831901e))


### Chores

* **ci:** enable for pull requests ([542b0ce](https://github.com/openai/openai-python/commit/542b0ce98f14ccff4f9e1bcbd3a9ea5e4f846638))
* **internal:** minor formatting ([29d723d](https://github.com/openai/openai-python/commit/29d723d1f1baf2a5843293c8647dc7baa16d56d1))

## 1.87.0 (2025-06-16)

Full Changelog: [v1.86.0...v1.87.0](https://github.com/openai/openai-python/compare/v1.86.0...v1.87.0)

### Features

* **api:** add reusable prompt IDs ([36bfe6e](https://github.com/openai/openai-python/commit/36bfe6e8ae12a31624ba1a360d9260f0aeec448a))


### Bug Fixes

* **client:** update service_tier on `client.beta.chat.completions` ([aa488d5](https://github.com/openai/openai-python/commit/aa488d5cf210d8640f87216538d4ff79d7181f2a))


### Chores

* **internal:** codegen related update ([b1a31e5](https://github.com/openai/openai-python/commit/b1a31e5ef4387d9f82cf33f9461371651788d381))
* **internal:** update conftest.py ([bba0213](https://github.com/openai/openai-python/commit/bba0213842a4c161f2235e526d50901a336eecef))
* **tests:** add tests for httpx client instantiation & proxies ([bc93712](https://github.com/openai/openai-python/commit/bc9371204f457aee9ed9b6ec1b61c2084f32faf1))

## 1.86.0 (2025-06-10)

Full Changelog: [v1.85.0...v1.86.0](https://github.com/openai/openai-python/compare/v1.85.0...v1.86.0)

### Features

* **api:** Add o3-pro model IDs ([d8dd80b](https://github.com/openai/openai-python/commit/d8dd80b1b4e6c73687d7acb6c3f62f0bf4b8282c))

## 1.85.0 (2025-06-09)

Full Changelog: [v1.84.0...v1.85.0](https://github.com/openai/openai-python/compare/v1.84.0...v1.85.0)

### Features

* **api:** Add tools and structured outputs to evals ([002cc7b](https://github.com/openai/openai-python/commit/002cc7bb3c315d95b81c2e497f55d21be7fd26f8))


### Bug Fixes

* **responses:** support raw responses for `parse()` ([d459943](https://github.com/openai/openai-python/commit/d459943cc1c81cf9ce5c426edd3ef9112fdf6723))

## 1.84.0 (2025-06-03)

Full Changelog: [v1.83.0...v1.84.0](https://github.com/openai/openai-python/compare/v1.83.0...v1.84.0)

### Features

* **api:** add new realtime and audio models, realtime session options ([0acd0da](https://github.com/openai/openai-python/commit/0acd0da6bc0468c6c857711bc5e77d0bc6d31be6))


### Chores

* **api:** update type names ([1924559](https://github.com/openai/openai-python/commit/192455913b38bf0323ddd0e2b1499b114e2111a1))

## 1.83.0 (2025-06-02)

Full Changelog: [v1.82.1...v1.83.0](https://github.com/openai/openai-python/compare/v1.82.1...v1.83.0)

### Features

* **api:** Config update for pakrym-stream-param ([88bcf3a](https://github.com/openai/openai-python/commit/88bcf3af9ce8ffa8347547d4d30aacac1ceba939))
* **client:** add follow_redirects request option ([26d715f](https://github.com/openai/openai-python/commit/26d715f4e9b0f2b19e2ac16acc796a949338e1e1))


### Bug Fixes

* **api:** Fix evals and code interpreter interfaces ([2650159](https://github.com/openai/openai-python/commit/2650159f6d01f6eb481cf8c7942142e4fd21ce44))
* **client:** return binary content from `get /containers/{container_id}/files/{file_id}/content` ([f7c80c4](https://github.com/openai/openai-python/commit/f7c80c4368434bd0be7436375076ba33a62f63b5))


### Chores

* **api:** mark some methods as deprecated ([3e2ca57](https://github.com/openai/openai-python/commit/3e2ca571cb6cdd9e15596590605b2f98a4c5a42e))
* deprecate Assistants API ([9d166d7](https://github.com/openai/openai-python/commit/9d166d795e03dea49af680ec9597e9497522187c))
* **docs:** remove reference to rye shell ([c7978e9](https://github.com/openai/openai-python/commit/c7978e9f1640c311022988fcd716cbb5c865daa8))

## 1.82.1 (2025-05-29)

Full Changelog: [v1.82.0...v1.82.1](https://github.com/openai/openai-python/compare/v1.82.0...v1.82.1)

### Bug Fixes

* **responses:** don't include `parsed_arguments` when re-serialising ([6d04193](https://github.com/openai/openai-python/commit/6d041937963ce452affcfb3553146ee51acfeb7a))


### Chores

* **internal:** fix release workflows ([361a909](https://github.com/openai/openai-python/commit/361a909a0cc83e5029ea425fd72202ffa8d1a46a))

## 1.82.0 (2025-05-22)

Full Changelog: [v1.81.0...v1.82.0](https://github.com/openai/openai-python/compare/v1.81.0...v1.82.0)

### Features

* **api:** new streaming helpers for background responses ([2a65d4d](https://github.com/openai/openai-python/commit/2a65d4de0aaba7801edd0df10f225530fd4969bd))


### Bug Fixes

* **azure:** mark images/edits as a deployment endpoint [#2371](https://github.com/openai/openai-python/issues/2371) ([5d1d5b4](https://github.com/openai/openai-python/commit/5d1d5b4b6072afe9fd7909b1a36014c8c11c1ad6))


### Documentation

* **readme:** another async example fix ([9ec8289](https://github.com/openai/openai-python/commit/9ec8289041f395805c67efd97847480f84eb9dac))
* **readme:** fix async example ([37d0b25](https://github.com/openai/openai-python/commit/37d0b25b6e82cd381e5d1aa6e28f1a1311d02353))

## 1.81.0 (2025-05-21)

Full Changelog: [v1.80.0...v1.81.0](https://github.com/openai/openai-python/compare/v1.80.0...v1.81.0)

### Features

* **api:** add container endpoint ([054a210](https://github.com/openai/openai-python/commit/054a210289d7e0db22d2d2a61bbe4d4d9cc0cb47))

## 1.80.0 (2025-05-21)

Full Changelog: [v1.79.0...v1.80.0](https://github.com/openai/openai-python/compare/v1.79.0...v1.80.0)

### Features

* **api:** new API tools ([d36ae52](https://github.com/openai/openai-python/commit/d36ae528d55fe87067c4b8c6b2c947cbad5e5002))


### Chores

* **docs:** grammar improvements ([e746145](https://github.com/openai/openai-python/commit/e746145a12b5335d8841aff95c91bbbde8bae8e3))

## 1.79.0 (2025-05-16)

Full Changelog: [v1.78.1...v1.79.0](https://github.com/openai/openai-python/compare/v1.78.1...v1.79.0)

### Features

* **api:** further updates for evals API ([32c99a6](https://github.com/openai/openai-python/commit/32c99a6f5885d4bf3511a7f06b70000edd274301))
* **api:** manual updates ([25245e5](https://github.com/openai/openai-python/commit/25245e5e3d0713abfb65b760aee1f12bc61deb41))
* **api:** responses x eval api ([fd586cb](https://github.com/openai/openai-python/commit/fd586cbdf889c9a5c6b9be177ff02fbfffa3eba5))
* **api:** Updating Assistants and Evals API schemas ([98ba7d3](https://github.com/openai/openai-python/commit/98ba7d355551213a13803f68d5642eecbb4ffd39))


### Bug Fixes

* fix create audio transcription endpoint ([e9a89ab](https://github.com/openai/openai-python/commit/e9a89ab7b6387610e433550207a23973b7edda3a))


### Chores

* **ci:** fix installation instructions ([f26c5fc](https://github.com/openai/openai-python/commit/f26c5fc85d98d700b68cb55c8be5d15983a9aeaf))
* **ci:** upload sdks to package manager ([861f105](https://github.com/openai/openai-python/commit/861f1055768168ab04987a42efcd32a07bc93542))

## 1.78.1 (2025-05-12)

Full Changelog: [v1.78.0...v1.78.1](https://github.com/openai/openai-python/compare/v1.78.0...v1.78.1)

### Bug Fixes

* **internal:** fix linting due to broken __test__ annotation ([5a7d7a0](https://github.com/openai/openai-python/commit/5a7d7a081138c6473bff44e60d439812ecb85cdf))
* **package:** support direct resource imports ([2293fc0](https://github.com/openai/openai-python/commit/2293fc0dd23a9c756067cdc22b39c18448f35feb))

## 1.78.0 (2025-05-08)

Full Changelog: [v1.77.0...v1.78.0](https://github.com/openai/openai-python/compare/v1.77.0...v1.78.0)

### Features

* **api:** Add reinforcement fine-tuning api support ([bebe361](https://github.com/openai/openai-python/commit/bebe36104bd3062d09ab9bbfb4bacfc99e737cb2))


### Bug Fixes

* ignore errors in isinstance() calls on LazyProxy subclasses ([#2343](https://github.com/openai/openai-python/issues/2343)) ([52cbbdf](https://github.com/openai/openai-python/commit/52cbbdf2207567741f16d18f1ea1b0d13d667375)), closes [#2056](https://github.com/openai/openai-python/issues/2056)


### Chores

* **internal:** update proxy tests ([b8e848d](https://github.com/openai/openai-python/commit/b8e848d5fb58472cbfa27fb3ed01efc25a05d944))
* use lazy imports for module level client ([4d0f409](https://github.com/openai/openai-python/commit/4d0f409e79a18cce9855fe076f5a50e52b8bafd8))
* use lazy imports for resources ([834813c](https://github.com/openai/openai-python/commit/834813c5cb1a84effc34e5eabed760393e1de806))

## 1.77.0 (2025-05-02)

Full Changelog: [v1.76.2...v1.77.0](https://github.com/openai/openai-python/compare/v1.76.2...v1.77.0)

### Features

* **api:** add image sizes, reasoning encryption ([473469a](https://github.com/openai/openai-python/commit/473469afa1a5f0a03f727bdcdadb9fd57872f9c5))


### Bug Fixes

* **parsing:** handle whitespace only strings ([#2007](https://github.com/openai/openai-python/issues/2007)) ([246bc5b](https://github.com/openai/openai-python/commit/246bc5b7559887840717667a0dad465caef66c3b))


### Chores

* only strip leading whitespace ([8467d66](https://github.com/openai/openai-python/commit/8467d666e0ddf1a9f81b8769a5c8a2fef1de20c1))

## 1.76.2 (2025-04-29)

Full Changelog: [v1.76.1...v1.76.2](https://github.com/openai/openai-python/compare/v1.76.1...v1.76.2)

### Chores

* **api:** API spec cleanup ([0a4d3e2](https://github.com/openai/openai-python/commit/0a4d3e2b495d22dd42ce1773b870554c64f9b3b2))

## 1.76.1 (2025-04-29)

Full Changelog: [v1.76.0...v1.76.1](https://github.com/openai/openai-python/compare/v1.76.0...v1.76.1)

### Chores

* broadly detect json family of content-type headers ([b4b1b08](https://github.com/openai/openai-python/commit/b4b1b086b512eecc0ada7fc1efa45eb506982f13))
* **ci:** only use depot for staging repos ([35312d8](https://github.com/openai/openai-python/commit/35312d80e6bbc1a61d06ad253af9a713b5ef040c))
* **ci:** run on more branches and use depot runners ([a6a45d4](https://github.com/openai/openai-python/commit/a6a45d4af8a4d904b37573a9b223d56106b4887d))

## 1.76.0 (2025-04-23)

Full Changelog: [v1.75.0...v1.76.0](https://github.com/openai/openai-python/compare/v1.75.0...v1.76.0)

### Features

* **api:** adding new image model support ([74d7692](https://github.com/openai/openai-python/commit/74d7692e94c9dca96db8793809d75631c22dbb87))


### Bug Fixes

* **pydantic v1:** more robust `ModelField.annotation` check ([#2163](https://github.com/openai/openai-python/issues/2163)) ([7351b12](https://github.com/openai/openai-python/commit/7351b12bc981f56632b92342d9ef26f6fb28d540))
* **pydantic v1:** more robust ModelField.annotation check ([eba7856](https://github.com/openai/openai-python/commit/eba7856db55afb8cb44376a0248587549f7bc65f))


### Chores

* **ci:** add timeout thresholds for CI jobs ([0997211](https://github.com/openai/openai-python/commit/09972119df5dd4c7c8db137c721364787e22d4c6))
* **internal:** fix list file params ([da2113c](https://github.com/openai/openai-python/commit/da2113c60b50b4438459325fcd38d55df3f63d8e))
* **internal:** import reformatting ([b425fb9](https://github.com/openai/openai-python/commit/b425fb906f62550c3669b09b9d8575f3d4d8496b))
* **internal:** minor formatting changes ([aed1d76](https://github.com/openai/openai-python/commit/aed1d767898324cf90328db329e04e89a77579c3))
* **internal:** refactor retries to not use recursion ([8cb8cfa](https://github.com/openai/openai-python/commit/8cb8cfab48a4fed70a756ce50036e7e56e1f9f87))
* **internal:** update models test ([870ad4e](https://github.com/openai/openai-python/commit/870ad4ed3a284d75f44b825503750129284c7906))
* update completion parse signature ([a44016c](https://github.com/openai/openai-python/commit/a44016c64cdefe404e97592808ed3c25411ab27b))

## 1.75.0 (2025-04-16)

Full Changelog: [v1.74.1...v1.75.0](https://github.com/openai/openai-python/compare/v1.74.1...v1.75.0)

### Features

* **api:** add o3 and o4-mini model IDs ([4bacbd5](https://github.com/openai/openai-python/commit/4bacbd5503137e266c127dc643ebae496cb4f158))

## 1.74.1 (2025-04-16)

Full Changelog: [v1.74.0...v1.74.1](https://github.com/openai/openai-python/compare/v1.74.0...v1.74.1)

### Chores

* **internal:** base client updates ([06303b5](https://github.com/openai/openai-python/commit/06303b501f8c17040c495971a4ee79ae340f6f4a))
* **internal:** bump pyright version ([9fd1c77](https://github.com/openai/openai-python/commit/9fd1c778c3231616bf1331cb1daa86fdfca4cb7f))

## 1.74.0 (2025-04-14)

Full Changelog: [v1.73.0...v1.74.0](https://github.com/openai/openai-python/compare/v1.73.0...v1.74.0)

### Features

* **api:** adding gpt-4.1 family of model IDs ([d4dae55](https://github.com/openai/openai-python/commit/d4dae5553ff3a2879b9ab79a6423661b212421f9))


### Bug Fixes

* **chat:** skip azure async filter events ([#2255](https://github.com/openai/openai-python/issues/2255)) ([fd3a38b](https://github.com/openai/openai-python/commit/fd3a38b1ed30af0a9f3302c1cfc6be6b352e65de))


### Chores

* **client:** minor internal fixes ([6071ae5](https://github.com/openai/openai-python/commit/6071ae5e8b4faa465afc8d07370737e66901900a))
* **internal:** update pyright settings ([c8f8beb](https://github.com/openai/openai-python/commit/c8f8bebf852380a224701bc36826291d6387c53d))

## 1.73.0 (2025-04-12)

Full Changelog: [v1.72.0...v1.73.0](https://github.com/openai/openai-python/compare/v1.72.0...v1.73.0)

### Features

* **api:** manual updates ([a3253dd](https://github.com/openai/openai-python/commit/a3253dd798c1eccd9810d4fc593e8c2a568bcf4f))


### Bug Fixes

* **perf:** optimize some hot paths ([f79d39f](https://github.com/openai/openai-python/commit/f79d39fbcaea8f366a9e48c06fb1696bab3e607d))
* **perf:** skip traversing types for NotGiven values ([28d220d](https://github.com/openai/openai-python/commit/28d220de3b4a09d80450d0bcc9b347bbf68f81ec))


### Chores

* **internal:** expand CI branch coverage ([#2295](https://github.com/openai/openai-python/issues/2295)) ([0ae783b](https://github.com/openai/openai-python/commit/0ae783b99122975be521365de0b6d2bce46056c9))
* **internal:** reduce CI branch coverage ([2fb7d42](https://github.com/openai/openai-python/commit/2fb7d425cda679a54aa3262090479fd747363bb4))
* slight wording improvement in README ([#2291](https://github.com/openai/openai-python/issues/2291)) ([e020759](https://github.com/openai/openai-python/commit/e0207598d16a2a9cb3cb3a8e8e97fa9cfdccd5e8))
* workaround build errors ([4e10c96](https://github.com/openai/openai-python/commit/4e10c96a483db28dedc2d8c2908765fb7317e049))

## 1.72.0 (2025-04-08)

Full Changelog: [v1.71.0...v1.72.0](https://github.com/openai/openai-python/compare/v1.71.0...v1.72.0)

### Features

* **api:** Add evalapi to sdk ([#2287](https://github.com/openai/openai-python/issues/2287)) ([35262fc](https://github.com/openai/openai-python/commit/35262fcef6ccb7d1f75c9abdfdc68c3dcf87ef53))


### Chores

* **internal:** fix examples ([#2288](https://github.com/openai/openai-python/issues/2288)) ([39defd6](https://github.com/openai/openai-python/commit/39defd61e81ea0ec6b898be12e9fb7e621c0e532))
* **internal:** skip broken test ([#2289](https://github.com/openai/openai-python/issues/2289)) ([e2c9bce](https://github.com/openai/openai-python/commit/e2c9bce1f59686ee053b495d06ea118b4a89e09e))
* **internal:** slight transform perf improvement ([#2284](https://github.com/openai/openai-python/issues/2284)) ([746174f](https://github.com/openai/openai-python/commit/746174fae7a018ece5dab54fb0b5a15fcdd18f2f))
* **tests:** improve enum examples ([#2286](https://github.com/openai/openai-python/issues/2286)) ([c9dd81c](https://github.com/openai/openai-python/commit/c9dd81ce0277e8b1f5db5e0a39c4c2bcd9004bcc))

## 1.71.0 (2025-04-07)

Full Changelog: [v1.70.0...v1.71.0](https://github.com/openai/openai-python/compare/v1.70.0...v1.71.0)

### Features

* **api:** manual updates ([bf8b4b6](https://github.com/openai/openai-python/commit/bf8b4b69906bfaea622c9c644270e985d92e2df2))
* **api:** manual updates ([3e37aa3](https://github.com/openai/openai-python/commit/3e37aa3e151d9738625a1daf75d6243d6fdbe8f2))
* **api:** manual updates ([dba9b65](https://github.com/openai/openai-python/commit/dba9b656fa5955b6eba8f6910da836a34de8d59d))
* **api:** manual updates ([f0c463b](https://github.com/openai/openai-python/commit/f0c463b47836666d091b5f616871f1b94646d346))


### Chores

* **deps:** allow websockets v15 ([#2281](https://github.com/openai/openai-python/issues/2281)) ([19c619e](https://github.com/openai/openai-python/commit/19c619ea95839129a86c19d5b60133e1ed9f2746))
* **internal:** only run examples workflow in main repo ([#2282](https://github.com/openai/openai-python/issues/2282)) ([c3e0927](https://github.com/openai/openai-python/commit/c3e0927d3fbbb9f753ba12adfa682a4235ba530a))
* **internal:** remove trailing character ([#2277](https://github.com/openai/openai-python/issues/2277)) ([5a21a2d](https://github.com/openai/openai-python/commit/5a21a2d7994e39bb0c86271eeb807983a9ae874a))
* Remove deprecated/unused remote spec feature ([23f76eb](https://github.com/openai/openai-python/commit/23f76eb0b9ddf12bcb04a6ad3f3ec5e956d2863f))

## 1.70.0 (2025-03-31)

Full Changelog: [v1.69.0...v1.70.0](https://github.com/openai/openai-python/compare/v1.69.0...v1.70.0)

### Features

* **api:** add `get /responses/{response_id}/input_items` endpoint ([4c6a35d](https://github.com/openai/openai-python/commit/4c6a35dec65362a6a738c3387dae57bf8cbfcbb2))

## 1.69.0 (2025-03-27)

Full Changelog: [v1.68.2...v1.69.0](https://github.com/openai/openai-python/compare/v1.68.2...v1.69.0)

### Features

* **api:** add `get /chat/completions` endpoint ([e6b8a42](https://github.com/openai/openai-python/commit/e6b8a42fc4286656cc86c2acd83692b170e77b68))


### Bug Fixes

* **audio:** correctly parse transcription stream events ([16a3a19](https://github.com/openai/openai-python/commit/16a3a195ff31f099fbe46043a12d2380c2c01f83))


### Chores

* add hash of OpenAPI spec/config inputs to .stats.yml ([515e1cd](https://github.com/openai/openai-python/commit/515e1cdd4a3109e5b29618df813656e17f22b52a))
* **api:** updates to supported Voice IDs ([#2261](https://github.com/openai/openai-python/issues/2261)) ([64956f9](https://github.com/openai/openai-python/commit/64956f9d9889b04380c7f5eb926509d1efd523e6))
* fix typos ([#2259](https://github.com/openai/openai-python/issues/2259)) ([6160de3](https://github.com/openai/openai-python/commit/6160de3e099f09c2d6ee5eeee4cbcc55b67a8f87))

## 1.68.2 (2025-03-21)

Full Changelog: [v1.68.1...v1.68.2](https://github.com/openai/openai-python/compare/v1.68.1...v1.68.2)

### Refactors

* **package:** rename audio extra to voice_helpers ([2dd6cb8](https://github.com/openai/openai-python/commit/2dd6cb87489fe12c5e45128f44d985c3f49aba1d))

## 1.68.1 (2025-03-21)

Full Changelog: [v1.68.0...v1.68.1](https://github.com/openai/openai-python/compare/v1.68.0...v1.68.1)

### Bug Fixes

* **client:** remove duplicate types ([#2235](https://github.com/openai/openai-python/issues/2235)) ([063f7d0](https://github.com/openai/openai-python/commit/063f7d0684c350ca9d766e2cb150233a22a623c8))
* **helpers/audio:** remove duplicative module ([f253d04](https://github.com/openai/openai-python/commit/f253d0415145f2c4904ea2e7b389d31d94e45a54))
* **package:** make sounddevice and numpy optional dependencies ([8b04453](https://github.com/openai/openai-python/commit/8b04453f0483736c13f0209a9f8f3618bc0e86c9))


### Chores

* **ci:** run workflows on next too ([67f89d4](https://github.com/openai/openai-python/commit/67f89d478aab780d1481c9bf6682c6633e431137))

## 1.68.0 (2025-03-20)

Full Changelog: [v1.67.0...v1.68.0](https://github.com/openai/openai-python/compare/v1.67.0...v1.68.0)

### Features

* add audio helpers ([423655c](https://github.com/openai/openai-python/commit/423655ca9077cfd258f1e52f6eb386fc8307fa5f))
* **api:** new models for TTS, STT, + new audio features for Realtime ([#2232](https://github.com/openai/openai-python/issues/2232)) ([ab5192d](https://github.com/openai/openai-python/commit/ab5192d0a7b417ade622ec94dd48f86beb90692c))

## 1.67.0 (2025-03-19)

Full Changelog: [v1.66.5...v1.67.0](https://github.com/openai/openai-python/compare/v1.66.5...v1.67.0)

### Features

* **api:** o1-pro now available through the API ([#2228](https://github.com/openai/openai-python/issues/2228)) ([40a19d8](https://github.com/openai/openai-python/commit/40a19d8592c1767d6318230fc93e37c360d1bcd1))

## 1.66.5 (2025-03-18)

Full Changelog: [v1.66.4...v1.66.5](https://github.com/openai/openai-python/compare/v1.66.4...v1.66.5)

### Bug Fixes

* **types:** improve responses type names ([#2224](https://github.com/openai/openai-python/issues/2224)) ([5f7beb8](https://github.com/openai/openai-python/commit/5f7beb873af5ccef2551f34ab3ef098e099ce9c6))


### Chores

* **internal:** add back releases workflow ([c71d4c9](https://github.com/openai/openai-python/commit/c71d4c918eab3532b36ea944b0c4069db6ac2d38))
* **internal:** codegen related update ([#2222](https://github.com/openai/openai-python/issues/2222)) ([f570d91](https://github.com/openai/openai-python/commit/f570d914a16cb5092533e32dfd863027d378c0b5))

## 1.66.4 (2025-03-17)

Full Changelog: [v1.66.3...v1.66.4](https://github.com/openai/openai-python/compare/v1.66.3...v1.66.4)

### Bug Fixes

* **ci:** ensure pip is always available ([#2207](https://github.com/openai/openai-python/issues/2207)) ([3f08e56](https://github.com/openai/openai-python/commit/3f08e56a48a04c2b7f03a4ad63f38228e25810e6))
* **ci:** remove publishing patch ([#2208](https://github.com/openai/openai-python/issues/2208)) ([dd2dab7](https://github.com/openai/openai-python/commit/dd2dab7faf2a003da3e6af66780bd250be6e7f3f))
* **types:** handle more discriminated union shapes ([#2206](https://github.com/openai/openai-python/issues/2206)) ([f85a9c6](https://github.com/openai/openai-python/commit/f85a9c633dcb9b64c0eb47d20151894742bbef22))


### Chores

* **internal:** bump rye to 0.44.0 ([#2200](https://github.com/openai/openai-python/issues/2200)) ([2dd3139](https://github.com/openai/openai-python/commit/2dd3139df6e7fe6307f9847e6527073e355e5047))
* **internal:** remove CI condition ([#2203](https://github.com/openai/openai-python/issues/2203)) ([9620fdc](https://github.com/openai/openai-python/commit/9620fdcf4f2d01b6753ecc0abc16e5239c2b41e1))
* **internal:** remove extra empty newlines ([#2195](https://github.com/openai/openai-python/issues/2195)) ([a1016a7](https://github.com/openai/openai-python/commit/a1016a78fe551e0f0e2562a0e81d1cb724d195da))
* **internal:** update release workflows ([e2def44](https://github.com/openai/openai-python/commit/e2def4453323aa1cf8077df447fd55eb4c626393))

## 1.66.3 (2025-03-12)

Full Changelog: [v1.66.2...v1.66.3](https://github.com/openai/openai-python/compare/v1.66.2...v1.66.3)

### Bug Fixes

* update module level client ([#2185](https://github.com/openai/openai-python/issues/2185)) ([456f324](https://github.com/openai/openai-python/commit/456f3240a0c33e71521c6b73c32e8adc1b8cd3bc))

## 1.66.2 (2025-03-11)

Full Changelog: [v1.66.1...v1.66.2](https://github.com/openai/openai-python/compare/v1.66.1...v1.66.2)

### Bug Fixes

* **responses:** correct reasoning output type ([#2181](https://github.com/openai/openai-python/issues/2181)) ([8cb1129](https://github.com/openai/openai-python/commit/8cb11299acc40c80061af275691cd09a2bf30c65))

## 1.66.1 (2025-03-11)

Full Changelog: [v1.66.0...v1.66.1](https://github.com/openai/openai-python/compare/v1.66.0...v1.66.1)

### Bug Fixes

* **responses:** correct computer use enum value ([#2180](https://github.com/openai/openai-python/issues/2180)) ([48f4628](https://github.com/openai/openai-python/commit/48f4628c5fb18ddd7d71e8730184f3ac50c4ffea))


### Chores

* **internal:** temporary commit ([afabec1](https://github.com/openai/openai-python/commit/afabec1b5b18b41ac870970d06e6c2f152ef7bbe))

## 1.66.0 (2025-03-11)

Full Changelog: [v1.65.5...v1.66.0](https://github.com/openai/openai-python/compare/v1.65.5...v1.66.0)

### Features

* **api:** add /v1/responses and built-in tools ([854df97](https://github.com/openai/openai-python/commit/854df97884736244d46060fd3d5a92916826ec8f))


### Chores

* export more types ([#2176](https://github.com/openai/openai-python/issues/2176)) ([a730f0e](https://github.com/openai/openai-python/commit/a730f0efedd228f96a49467f17fb19b6a219246c))

## 1.65.5 (2025-03-09)

Full Changelog: [v1.65.4...v1.65.5](https://github.com/openai/openai-python/compare/v1.65.4...v1.65.5)

### Chores

* move ChatModel type to shared ([#2167](https://github.com/openai/openai-python/issues/2167)) ([104f02a](https://github.com/openai/openai-python/commit/104f02af371076d5d2498e48ae14d2eacc7df8bd))

## 1.65.4 (2025-03-05)

Full Changelog: [v1.65.3...v1.65.4](https://github.com/openai/openai-python/compare/v1.65.3...v1.65.4)

### Bug Fixes

* **api:** add missing file rank enum + more metadata ([#2164](https://github.com/openai/openai-python/issues/2164)) ([0387e48](https://github.com/openai/openai-python/commit/0387e48e0880e496eb74b60eec9ed76a3171f14d))

## 1.65.3 (2025-03-04)

Full Changelog: [v1.65.2...v1.65.3](https://github.com/openai/openai-python/compare/v1.65.2...v1.65.3)

### Chores

* **internal:** remove unused http client options forwarding ([#2158](https://github.com/openai/openai-python/issues/2158)) ([76ec464](https://github.com/openai/openai-python/commit/76ec464cfe3db3fa59a766259d6d6ee5bb889f86))
* **internal:** run example files in CI ([#2160](https://github.com/openai/openai-python/issues/2160)) ([9979345](https://github.com/openai/openai-python/commit/9979345038594440eec2f500c0c7cc5417cc7c08))

## 1.65.2 (2025-03-01)

Full Changelog: [v1.65.1...v1.65.2](https://github.com/openai/openai-python/compare/v1.65.1...v1.65.2)

### Bug Fixes

* **azure:** azure_deployment use with realtime + non-deployment-based APIs ([#2154](https://github.com/openai/openai-python/issues/2154)) ([5846b55](https://github.com/openai/openai-python/commit/5846b552877f3d278689c521f9a26ce31167e1ea))


### Chores

* **docs:** update client docstring ([#2152](https://github.com/openai/openai-python/issues/2152)) ([0518c34](https://github.com/openai/openai-python/commit/0518c341ee0e19941c6b1d9d60e2552e1aa17f26))

## 1.65.1 (2025-02-27)

Full Changelog: [v1.65.0...v1.65.1](https://github.com/openai/openai-python/compare/v1.65.0...v1.65.1)

### Documentation

* update URLs from stainlessapi.com to stainless.com ([#2150](https://github.com/openai/openai-python/issues/2150)) ([dee4298](https://github.com/openai/openai-python/commit/dee42986eff46dd23ba25b3e2a5bb7357aca39d9))

## 1.65.0 (2025-02-27)

Full Changelog: [v1.64.0...v1.65.0](https://github.com/openai/openai-python/compare/v1.64.0...v1.65.0)

### Features

* **api:** add gpt-4.5-preview ([#2149](https://github.com/openai/openai-python/issues/2149)) ([4cee52e](https://github.com/openai/openai-python/commit/4cee52e8d191b0532f28d86446da79b43a58b907))


### Chores

* **internal:** properly set __pydantic_private__ ([#2144](https://github.com/openai/openai-python/issues/2144)) ([2b1bd16](https://github.com/openai/openai-python/commit/2b1bd1604a038ded67367742a0b1c9d92e29dfc8))

## 1.64.0 (2025-02-22)

Full Changelog: [v1.63.2...v1.64.0](https://github.com/openai/openai-python/compare/v1.63.2...v1.64.0)

### Features

* **client:** allow passing `NotGiven` for body ([#2135](https://github.com/openai/openai-python/issues/2135)) ([4451f56](https://github.com/openai/openai-python/commit/4451f5677f9eaad9b8fee74f71c2e5fe6785c420))


### Bug Fixes

* **client:** mark some request bodies as optional ([4451f56](https://github.com/openai/openai-python/commit/4451f5677f9eaad9b8fee74f71c2e5fe6785c420))


### Chores

* **internal:** fix devcontainers setup ([#2137](https://github.com/openai/openai-python/issues/2137)) ([4d88402](https://github.com/openai/openai-python/commit/4d884020cbeb1ca6093dd5317e3e5812551f7a46))

## 1.63.2 (2025-02-17)

Full Changelog: [v1.63.1...v1.63.2](https://github.com/openai/openai-python/compare/v1.63.1...v1.63.2)

### Chores

* **internal:** revert temporary commit ([#2121](https://github.com/openai/openai-python/issues/2121)) ([72458ab](https://github.com/openai/openai-python/commit/72458abeed3dd95db8aabed94a33bb12a916f8b7))

## 1.63.1 (2025-02-17)

Full Changelog: [v1.63.0...v1.63.1](https://github.com/openai/openai-python/compare/v1.63.0...v1.63.1)

### Chores

* **internal:** temporary commit ([#2121](https://github.com/openai/openai-python/issues/2121)) ([f7f8361](https://github.com/openai/openai-python/commit/f7f83614c8da84c6725d60936f08f9f1a65f0a9e))

## 1.63.0 (2025-02-13)

Full Changelog: [v1.62.0...v1.63.0](https://github.com/openai/openai-python/compare/v1.62.0...v1.63.0)

### Features

* **api:** add support for storing chat completions ([#2117](https://github.com/openai/openai-python/issues/2117)) ([2357a8f](https://github.com/openai/openai-python/commit/2357a8f97246a3fe17c6ac1fb0d7a67d6f1ffc1d))

## 1.62.0 (2025-02-12)

Full Changelog: [v1.61.1...v1.62.0](https://github.com/openai/openai-python/compare/v1.61.1...v1.62.0)

### Features

* **client:** send `X-Stainless-Read-Timeout` header ([#2094](https://github.com/openai/openai-python/issues/2094)) ([0288213](https://github.com/openai/openai-python/commit/0288213fbfa935c9bf9d56416619ea929ae1cf63))
* **embeddings:** use stdlib array type for improved performance ([#2060](https://github.com/openai/openai-python/issues/2060)) ([9a95db9](https://github.com/openai/openai-python/commit/9a95db9154ac98678970e7f1652a7cacfd2f7fdb))
* **pagination:** avoid fetching when has_more: false ([#2098](https://github.com/openai/openai-python/issues/2098)) ([1882483](https://github.com/openai/openai-python/commit/18824832d3a676ae49206cd2b5e09d4796fdf033))


### Bug Fixes

* **api:** add missing reasoning effort + model enums ([#2096](https://github.com/openai/openai-python/issues/2096)) ([e0ca9f0](https://github.com/openai/openai-python/commit/e0ca9f0f6fae40230f8cab97573914ed632920b6))
* **parsing:** don't default to an empty array ([#2106](https://github.com/openai/openai-python/issues/2106)) ([8e748bb](https://github.com/openai/openai-python/commit/8e748bb08d9c0d1f7e8a1af31452e25eb7154f55))


### Chores

* **internal:** fix type traversing dictionary params ([#2097](https://github.com/openai/openai-python/issues/2097)) ([4e5b368](https://github.com/openai/openai-python/commit/4e5b368bf576f38d0f125778edde74ed6d101d7d))
* **internal:** minor type handling changes ([#2099](https://github.com/openai/openai-python/issues/2099)) ([a2c6da0](https://github.com/openai/openai-python/commit/a2c6da0fbc610ee80a2e044a0b20fc1cc2376962))

## 1.61.1 (2025-02-05)

Full Changelog: [v1.61.0...v1.61.1](https://github.com/openai/openai-python/compare/v1.61.0...v1.61.1)

### Bug Fixes

* **api/types:** correct audio duration & role types ([#2091](https://github.com/openai/openai-python/issues/2091)) ([afcea48](https://github.com/openai/openai-python/commit/afcea4891ff85de165ccc2b5497ccf9a90520e9e))
* **cli/chat:** only send params when set ([#2077](https://github.com/openai/openai-python/issues/2077)) ([688b223](https://github.com/openai/openai-python/commit/688b223d9a733d241d50e5d7df62f346592c537c))


### Chores

* **internal:** bummp ruff dependency ([#2080](https://github.com/openai/openai-python/issues/2080)) ([b7a80b1](https://github.com/openai/openai-python/commit/b7a80b1994ab86e81485b88531e4aea63b3da594))
* **internal:** change default timeout to an int ([#2079](https://github.com/openai/openai-python/issues/2079)) ([d3df1c6](https://github.com/openai/openai-python/commit/d3df1c6ca090598701e38fd376a9796aadba88f1))

## 1.61.0 (2025-01-31)

Full Changelog: [v1.60.2...v1.61.0](https://github.com/openai/openai-python/compare/v1.60.2...v1.61.0)

### Features

* **api:** add o3-mini ([#2067](https://github.com/openai/openai-python/issues/2067)) ([12b87a4](https://github.com/openai/openai-python/commit/12b87a4a1e6cb071a6b063d089585dec56a5d534))


### Bug Fixes

* **types:** correct metadata type + other fixes ([12b87a4](https://github.com/openai/openai-python/commit/12b87a4a1e6cb071a6b063d089585dec56a5d534))


### Chores

* **helpers:** section links ([ef8d3cc](https://github.com/openai/openai-python/commit/ef8d3cce40022d3482d341455be604e5f1afbd70))
* **types:** fix Metadata types ([82d3156](https://github.com/openai/openai-python/commit/82d3156e74ed2f95edd10cd7ebea53d2b5562794))
* update api.md ([#2063](https://github.com/openai/openai-python/issues/2063)) ([21964f0](https://github.com/openai/openai-python/commit/21964f00fb104011c4c357544114702052b74548))


### Documentation

* **readme:** current section links ([#2055](https://github.com/openai/openai-python/issues/2055)) ([ef8d3cc](https://github.com/openai/openai-python/commit/ef8d3cce40022d3482d341455be604e5f1afbd70))

## 1.60.2 (2025-01-27)

Full Changelog: [v1.60.1...v1.60.2](https://github.com/openai/openai-python/compare/v1.60.1...v1.60.2)

### Bug Fixes

* **parsing:** don't validate input tools in the asynchronous `.parse()` method ([6fcfe73](https://github.com/openai/openai-python/commit/6fcfe73cd335853c7dd2cd3151a0d5d1785cfc9c))

## 1.60.1 (2025-01-24)

Full Changelog: [v1.60.0...v1.60.1](https://github.com/openai/openai-python/compare/v1.60.0...v1.60.1)

### Chores

* **internal:** minor formatting changes ([#2050](https://github.com/openai/openai-python/issues/2050)) ([9c44192](https://github.com/openai/openai-python/commit/9c44192be5776d9252d36dc027a33c60b33d81b2))


### Documentation

* **examples/azure:** add async snippet ([#1787](https://github.com/openai/openai-python/issues/1787)) ([f60eda1](https://github.com/openai/openai-python/commit/f60eda1c1e8caf0ec2274b18b3fb2252304196db))

## 1.60.0 (2025-01-22)

Full Changelog: [v1.59.9...v1.60.0](https://github.com/openai/openai-python/compare/v1.59.9...v1.60.0)

### Features

* **api:** update enum values, comments, and examples ([#2045](https://github.com/openai/openai-python/issues/2045)) ([e8205fd](https://github.com/openai/openai-python/commit/e8205fd58f0d677f476c577a8d9afb90f5710506))


### Chores

* **internal:** minor style changes ([#2043](https://github.com/openai/openai-python/issues/2043)) ([89a9dd8](https://github.com/openai/openai-python/commit/89a9dd821eaf5300ad11b0270b61fdfa4fd6e9b6))


### Documentation

* **readme:** mention failed requests in request IDs ([5f7c30b](https://github.com/openai/openai-python/commit/5f7c30bc006ffb666c324011a68aae357cb33e35))

## 1.59.9 (2025-01-20)

Full Changelog: [v1.59.8...v1.59.9](https://github.com/openai/openai-python/compare/v1.59.8...v1.59.9)

### Bug Fixes

* **tests:** make test_get_platform less flaky ([#2040](https://github.com/openai/openai-python/issues/2040)) ([72ea05c](https://github.com/openai/openai-python/commit/72ea05cf18caaa7a5e6fe7e2251ab93fa0ba3140))


### Chores

* **internal:** avoid pytest-asyncio deprecation warning ([#2041](https://github.com/openai/openai-python/issues/2041)) ([b901046](https://github.com/openai/openai-python/commit/b901046ddda9c79b7f019e2263c02d126a3b2ee2))
* **internal:** update websockets dep ([#2036](https://github.com/openai/openai-python/issues/2036)) ([642cd11](https://github.com/openai/openai-python/commit/642cd119482c6fbca925ba702ad2579f9dc47bf9))


### Documentation

* fix typo ([#2031](https://github.com/openai/openai-python/issues/2031)) ([02fcf15](https://github.com/openai/openai-python/commit/02fcf15611953089826a74725cb96201d94658bb))
* **raw responses:** fix duplicate `the` ([#2039](https://github.com/openai/openai-python/issues/2039)) ([9b8eab9](https://github.com/openai/openai-python/commit/9b8eab99fdc6a581a1f5cc421c6f74b0e2b30415))

## 1.59.8 (2025-01-17)

Full Changelog: [v1.59.7...v1.59.8](https://github.com/openai/openai-python/compare/v1.59.7...v1.59.8)

### Bug Fixes

* streaming ([c16f58e](https://github.com/openai/openai-python/commit/c16f58ead0bc85055b164182689ba74b7e939dfa))
* **structured outputs:** avoid parsing empty empty content ([#2023](https://github.com/openai/openai-python/issues/2023)) ([6d3513c](https://github.com/openai/openai-python/commit/6d3513c86f6e5800f8f73a45e089b7a205327121))
* **structured outputs:** correct schema coercion for inline ref expansion ([#2025](https://github.com/openai/openai-python/issues/2025)) ([2f4f0b3](https://github.com/openai/openai-python/commit/2f4f0b374207f162060c328b71ec995049dc42e8))
* **types:** correct type for vector store chunking strategy ([#2017](https://github.com/openai/openai-python/issues/2017)) ([e389279](https://github.com/openai/openai-python/commit/e38927950a5cdad99065853fe7b72aad6bb322e9))


### Chores

* **examples:** update realtime model ([f26746c](https://github.com/openai/openai-python/commit/f26746cbcd893d66cf8a3fd68a7c3779dc8c833c)), closes [#2020](https://github.com/openai/openai-python/issues/2020)
* **internal:** bump pyright dependency ([#2021](https://github.com/openai/openai-python/issues/2021)) ([0a9a0f5](https://github.com/openai/openai-python/commit/0a9a0f5d8b9d5457643798287f893305006dd518))
* **internal:** streaming refactors ([#2012](https://github.com/openai/openai-python/issues/2012)) ([d76a748](https://github.com/openai/openai-python/commit/d76a748f606743407f94dfc26758095560e2082a))
* **internal:** update deps ([#2015](https://github.com/openai/openai-python/issues/2015)) ([514e0e4](https://github.com/openai/openai-python/commit/514e0e415f87ab4510262d29ed6125384e017b84))


### Documentation

* **examples/azure:** example script with realtime API ([#1967](https://github.com/openai/openai-python/issues/1967)) ([84f2f9c](https://github.com/openai/openai-python/commit/84f2f9c0439229a7db7136fe78419292d34d1f81))

## 1.59.7 (2025-01-13)

Full Changelog: [v1.59.6...v1.59.7](https://github.com/openai/openai-python/compare/v1.59.6...v1.59.7)

### Chores

* export HttpxBinaryResponseContent class ([7191b71](https://github.com/openai/openai-python/commit/7191b71f3dcbbfcb2f2bec855c3bba93c956384e))

## 1.59.6 (2025-01-09)

Full Changelog: [v1.59.5...v1.59.6](https://github.com/openai/openai-python/compare/v1.59.5...v1.59.6)

### Bug Fixes

* correctly handle deserialising `cls` fields ([#2002](https://github.com/openai/openai-python/issues/2002)) ([089c820](https://github.com/openai/openai-python/commit/089c820c8a5d20e9db6a171f0a4f11b481fe8465))


### Chores

* **internal:** spec update ([#2000](https://github.com/openai/openai-python/issues/2000)) ([36548f8](https://github.com/openai/openai-python/commit/36548f871763fdd7b5ce44903d186bc916331549))

## 1.59.5 (2025-01-08)

Full Changelog: [v1.59.4...v1.59.5](https://github.com/openai/openai-python/compare/v1.59.4...v1.59.5)

### Bug Fixes

* **client:** only call .close() when needed ([#1992](https://github.com/openai/openai-python/issues/1992)) ([bdfd699](https://github.com/openai/openai-python/commit/bdfd699b99522e83f7610b5f98e36fe43ddf8338))


### Documentation

* fix typos ([#1995](https://github.com/openai/openai-python/issues/1995)) ([be694a0](https://github.com/openai/openai-python/commit/be694a097d6cf2668f08ecf94c882773b2ee1f84))
* fix typos ([#1996](https://github.com/openai/openai-python/issues/1996)) ([714aed9](https://github.com/openai/openai-python/commit/714aed9d7eb74a19f6e502fb6d4fe83399f82851))
* more typo fixes ([#1998](https://github.com/openai/openai-python/issues/1998)) ([7bd92f0](https://github.com/openai/openai-python/commit/7bd92f06a75f11f6afc2d1223d2426e186cc74cb))
* **readme:** moved period to inside parentheses ([#1980](https://github.com/openai/openai-python/issues/1980)) ([e7fae94](https://github.com/openai/openai-python/commit/e7fae948f2ba8db23461e4374308417570196847))

## 1.59.4 (2025-01-07)

Full Changelog: [v1.59.3...v1.59.4](https://github.com/openai/openai-python/compare/v1.59.3...v1.59.4)

### Chores

* add missing isclass check ([#1988](https://github.com/openai/openai-python/issues/1988)) ([61d9072](https://github.com/openai/openai-python/commit/61d9072fbace58d64910ec7378c3686ac555972e))
* add missing isclass check for structured outputs ([bcbf013](https://github.com/openai/openai-python/commit/bcbf013e8d825b8b5f88172313dfb6e0313ca34c))
* **internal:** bump httpx dependency ([#1990](https://github.com/openai/openai-python/issues/1990)) ([288c2c3](https://github.com/openai/openai-python/commit/288c2c30dc405cbaa89924f9243442300e95e100))


### Documentation

* **realtime:** fix event reference link ([9b6885d](https://github.com/openai/openai-python/commit/9b6885d50f8d65ba5009642046727d291e0f14fa))

## 1.59.3 (2025-01-03)

Full Changelog: [v1.59.2...v1.59.3](https://github.com/openai/openai-python/compare/v1.59.2...v1.59.3)

### Chores

* **api:** bump spec version ([#1985](https://github.com/openai/openai-python/issues/1985)) ([c6f1b35](https://github.com/openai/openai-python/commit/c6f1b357fcf669065f4ed6819d47a528b0787128))

## 1.59.2 (2025-01-03)

Full Changelog: [v1.59.1...v1.59.2](https://github.com/openai/openai-python/compare/v1.59.1...v1.59.2)

### Chores

* **ci:** fix publish workflow ([0be1f5d](https://github.com/openai/openai-python/commit/0be1f5de0daf807cece564abf061c8bb188bb9aa))
* **internal:** empty commit ([fe8dc2e](https://github.com/openai/openai-python/commit/fe8dc2e97fc430ea2433ed28cfaa79425af223ec))

## 1.59.1 (2025-01-02)

Full Changelog: [v1.59.0...v1.59.1](https://github.com/openai/openai-python/compare/v1.59.0...v1.59.1)

### Chores

* bump license year ([#1981](https://github.com/openai/openai-python/issues/1981)) ([f29011a](https://github.com/openai/openai-python/commit/f29011a6426d3fa4844ecd723ee20561ee60c665))

## 1.59.0 (2024-12-21)

Full Changelog: [v1.58.1...v1.59.0](https://github.com/openai/openai-python/compare/v1.58.1...v1.59.0)

### Features

* **azure:** support for the Realtime API ([#1963](https://github.com/openai/openai-python/issues/1963)) ([9fda141](https://github.com/openai/openai-python/commit/9fda14172abdb66fe240aa7b4dc7cfae4faf1d73))


### Chores

* **realtime:** update docstrings ([#1964](https://github.com/openai/openai-python/issues/1964)) ([3dee863](https://github.com/openai/openai-python/commit/3dee863554d28272103e90a6a199ac196e92ff05))

## 1.58.1 (2024-12-17)

Full Changelog: [v1.58.0...v1.58.1](https://github.com/openai/openai-python/compare/v1.58.0...v1.58.1)

### Documentation

* **readme:** fix example script link ([23ba877](https://github.com/openai/openai-python/commit/23ba8778fd55e0f54f36685e9c5950b452d8e10c))

## 1.58.0 (2024-12-17)

Full Changelog: [v1.57.4...v1.58.0](https://github.com/openai/openai-python/compare/v1.57.4...v1.58.0)

### Features

* add Realtime API support ([#1958](https://github.com/openai/openai-python/issues/1958)) ([97d73cf](https://github.com/openai/openai-python/commit/97d73cf89935ca6098bb889a92f0ec2cdff16989))
* **api:** new o1 and GPT-4o models + preference fine-tuning ([#1956](https://github.com/openai/openai-python/issues/1956)) ([ec22ffb](https://github.com/openai/openai-python/commit/ec22ffb129c524525caa33b088405d27c271e631))


### Bug Fixes

* add reasoning_effort to all methods ([8829c32](https://github.com/openai/openai-python/commit/8829c3202dbe790ca3646476c802ec55ed47d864))
* **assistants:** correctly send `include` query param ([9a4c69c](https://github.com/openai/openai-python/commit/9a4c69c383bc6719b6521a485f2c7e62a9c036a9))
* **cli/migrate:** change grit binaries prefix ([#1951](https://github.com/openai/openai-python/issues/1951)) ([1c396c9](https://github.com/openai/openai-python/commit/1c396c95b040fb3d1a2523b09eaad4ff62d96846))


### Chores

* **internal:** fix some typos ([#1955](https://github.com/openai/openai-python/issues/1955)) ([628dead](https://github.com/openai/openai-python/commit/628dead660c00435bf46e09081c7b90b7bbe4a8a))


### Documentation

* add examples + guidance on Realtime API support ([1cb00f8](https://github.com/openai/openai-python/commit/1cb00f8fed78052aacbb9e0fac997b6ba0d44d2a))
* **readme:** example snippet for client context manager ([#1953](https://github.com/openai/openai-python/issues/1953)) ([ad80255](https://github.com/openai/openai-python/commit/ad802551d8aaf4e6eff711118676ec4e64392638))

## 1.57.4 (2024-12-13)

Full Changelog: [v1.57.3...v1.57.4](https://github.com/openai/openai-python/compare/v1.57.3...v1.57.4)

### Chores

* **internal:** remove some duplicated imports ([#1946](https://github.com/openai/openai-python/issues/1946)) ([f94fddd](https://github.com/openai/openai-python/commit/f94fddd377015764b3c82919fdf956f619447b77))
* **internal:** updated imports ([#1948](https://github.com/openai/openai-python/issues/1948)) ([13971fc](https://github.com/openai/openai-python/commit/13971fc450106746c0ae02ab931e68b770ee105e))

## 1.57.3 (2024-12-12)

Full Changelog: [v1.57.2...v1.57.3](https://github.com/openai/openai-python/compare/v1.57.2...v1.57.3)

### Chores

* **internal:** add support for TypeAliasType ([#1942](https://github.com/openai/openai-python/issues/1942)) ([d3442ff](https://github.com/openai/openai-python/commit/d3442ff28f2394200e14122f683d1f94686e8231))
* **internal:** bump pyright ([#1939](https://github.com/openai/openai-python/issues/1939)) ([190d1a8](https://github.com/openai/openai-python/commit/190d1a805dee7c37fb8f9dcb93b1715caa06cf95))

## 1.57.2 (2024-12-10)

Full Changelog: [v1.57.1...v1.57.2](https://github.com/openai/openai-python/compare/v1.57.1...v1.57.2)

### Bug Fixes

* **azure:** handle trailing slash in `azure_endpoint` ([#1935](https://github.com/openai/openai-python/issues/1935)) ([69b73c5](https://github.com/openai/openai-python/commit/69b73c553b1982277c2f1b9d110ed951ddca689e))


### Documentation

* **readme:** fix http client proxies example ([#1932](https://github.com/openai/openai-python/issues/1932)) ([7a83e0f](https://github.com/openai/openai-python/commit/7a83e0fe4cc29e484ae417448b002c997745e4a3))

## 1.57.1 (2024-12-09)

Full Changelog: [v1.57.0...v1.57.1](https://github.com/openai/openai-python/compare/v1.57.0...v1.57.1)

### Chores

* **internal:** bump pydantic dependency ([#1929](https://github.com/openai/openai-python/issues/1929)) ([5227c95](https://github.com/openai/openai-python/commit/5227c95eff9c7b1395e6d8f14b94652a91ed2ee2))

## 1.57.0 (2024-12-05)

Full Changelog: [v1.56.2...v1.57.0](https://github.com/openai/openai-python/compare/v1.56.2...v1.57.0)

### Features

* **api:** updates ([#1924](https://github.com/openai/openai-python/issues/1924)) ([82ba614](https://github.com/openai/openai-python/commit/82ba6144682b0a6b3a22d4f764231c0c6afdcf6e))


### Chores

* bump openapi url ([#1922](https://github.com/openai/openai-python/issues/1922)) ([a472a8f](https://github.com/openai/openai-python/commit/a472a8fd0ba36b6897dcd02b6005fcf23f98f056))

## 1.56.2 (2024-12-04)

Full Changelog: [v1.56.1...v1.56.2](https://github.com/openai/openai-python/compare/v1.56.1...v1.56.2)

### Chores

* make the `Omit` type public ([#1919](https://github.com/openai/openai-python/issues/1919)) ([4fb8a1c](https://github.com/openai/openai-python/commit/4fb8a1cf1f8df37ce8c027bbaaac85a648bae02a))

## 1.56.1 (2024-12-03)

Full Changelog: [v1.56.0...v1.56.1](https://github.com/openai/openai-python/compare/v1.56.0...v1.56.1)

### Bug Fixes

* **cli:** remove usage of httpx proxies ([0e9fc3d](https://github.com/openai/openai-python/commit/0e9fc3dfbc7dec5b8c8f84dea9d87aad9f3d9cf6))


### Chores

* **internal:** bump pyright ([#1917](https://github.com/openai/openai-python/issues/1917)) ([0e87346](https://github.com/openai/openai-python/commit/0e8734637666ab22bc27fe4ec2cf7c39fddb5d08))

## 1.56.0 (2024-12-02)

Full Changelog: [v1.55.3...v1.56.0](https://github.com/openai/openai-python/compare/v1.55.3...v1.56.0)

### Features

* **client:** make ChatCompletionStreamState public ([#1898](https://github.com/openai/openai-python/issues/1898)) ([dc7f6cb](https://github.com/openai/openai-python/commit/dc7f6cb2618686ff04bfdca228913cda3d320884))

## 1.55.3 (2024-11-28)

Full Changelog: [v1.55.2...v1.55.3](https://github.com/openai/openai-python/compare/v1.55.2...v1.55.3)

### Bug Fixes

* **client:** compat with new httpx 0.28.0 release ([#1904](https://github.com/openai/openai-python/issues/1904)) ([72b6c63](https://github.com/openai/openai-python/commit/72b6c636c526885ef873580a07eff1c18e76bc10))

## 1.55.2 (2024-11-27)

Full Changelog: [v1.55.1...v1.55.2](https://github.com/openai/openai-python/compare/v1.55.1...v1.55.2)

### Chores

* **internal:** exclude mypy from running on tests ([#1899](https://github.com/openai/openai-python/issues/1899)) ([e2496f1](https://github.com/openai/openai-python/commit/e2496f1d274126bdaa46a8256b3dd384b4ae244b))


### Documentation

* **assistants:** correct on_text_delta example ([#1896](https://github.com/openai/openai-python/issues/1896)) ([460b663](https://github.com/openai/openai-python/commit/460b663567ed1031467a8d69eb13fd3b3da38827))

## 1.55.1 (2024-11-25)

Full Changelog: [v1.55.0...v1.55.1](https://github.com/openai/openai-python/compare/v1.55.0...v1.55.1)

### Bug Fixes

* **pydantic-v1:** avoid runtime error for assistants streaming ([#1885](https://github.com/openai/openai-python/issues/1885)) ([197c94b](https://github.com/openai/openai-python/commit/197c94b9e2620da8902aeed6959d2f871bb70461))


### Chores

* remove now unused `cached-property` dep ([#1867](https://github.com/openai/openai-python/issues/1867)) ([df5fac1](https://github.com/openai/openai-python/commit/df5fac1e557f79ed8d0935c48ca7f3f0bf77fa98))
* remove now unused `cached-property` dep ([#1891](https://github.com/openai/openai-python/issues/1891)) ([feebaae](https://github.com/openai/openai-python/commit/feebaae85d76960cb8f1c58dd9b5180136c47962))


### Documentation

* add info log level to readme ([#1887](https://github.com/openai/openai-python/issues/1887)) ([358255d](https://github.com/openai/openai-python/commit/358255d15ed220f8c80a3c0861b98e61e909a7ae))

## 1.55.0 (2024-11-20)

Full Changelog: [v1.54.5...v1.55.0](https://github.com/openai/openai-python/compare/v1.54.5...v1.55.0)

### Features

* **api:** add gpt-4o-2024-11-20 model ([#1877](https://github.com/openai/openai-python/issues/1877)) ([ff64c2a](https://github.com/openai/openai-python/commit/ff64c2a0733854ed8cc1d7dd959a8287b2ec8120))

## 1.54.5 (2024-11-19)

Full Changelog: [v1.54.4...v1.54.5](https://github.com/openai/openai-python/compare/v1.54.4...v1.54.5)

### Bug Fixes

* **asyncify:** avoid hanging process under certain conditions ([#1853](https://github.com/openai/openai-python/issues/1853)) ([3d23437](https://github.com/openai/openai-python/commit/3d234377e7c9cd19db5186688612eb18e68cec8f))


### Chores

* **internal:** minor test changes ([#1874](https://github.com/openai/openai-python/issues/1874)) ([189339d](https://github.com/openai/openai-python/commit/189339d2a09d23ea1883286972f366e19b397f91))
* **internal:** spec update ([#1873](https://github.com/openai/openai-python/issues/1873)) ([24c81f7](https://github.com/openai/openai-python/commit/24c81f729ae09ba3cec5542e5cc955c8b05b0f88))
* **tests:** limit array example length ([#1870](https://github.com/openai/openai-python/issues/1870)) ([1e550df](https://github.com/openai/openai-python/commit/1e550df708fc3b5d903b7adfa2180058a216b676))

## 1.54.4 (2024-11-12)

Full Changelog: [v1.54.3...v1.54.4](https://github.com/openai/openai-python/compare/v1.54.3...v1.54.4)

### Bug Fixes

* don't use dicts as iterables in transform ([#1865](https://github.com/openai/openai-python/issues/1865)) ([76a51b1](https://github.com/openai/openai-python/commit/76a51b11efae50659a562197b1e18c6343964b56))


### Documentation

* bump models in example snippets to gpt-4o ([#1861](https://github.com/openai/openai-python/issues/1861)) ([adafe08](https://github.com/openai/openai-python/commit/adafe0859178d406fa93b38f3547f3d262651331))
* move comments in example snippets ([#1860](https://github.com/openai/openai-python/issues/1860)) ([362cf74](https://github.com/openai/openai-python/commit/362cf74d6c34506f98f6c4fb2304357be21f7691))
* **readme:** add missing asyncio import ([#1858](https://github.com/openai/openai-python/issues/1858)) ([dec9d0c](https://github.com/openai/openai-python/commit/dec9d0c97b702b6bcf9c71f5bdd6172bb5718354))

## 1.54.3 (2024-11-06)

Full Changelog: [v1.54.2...v1.54.3](https://github.com/openai/openai-python/compare/v1.54.2...v1.54.3)

### Bug Fixes

* **logs:** redact sensitive headers ([#1850](https://github.com/openai/openai-python/issues/1850)) ([466608f](https://github.com/openai/openai-python/commit/466608fa56b7a9939c08a4c78be2f6fe4a05111b))

## 1.54.2 (2024-11-06)

Full Changelog: [v1.54.1...v1.54.2](https://github.com/openai/openai-python/compare/v1.54.1...v1.54.2)

### Chores

* **tests:** adjust retry timeout values ([#1851](https://github.com/openai/openai-python/issues/1851)) ([cc8009c](https://github.com/openai/openai-python/commit/cc8009c9de56fe80f2689f69e7b891ff4ed297a3))

## 1.54.1 (2024-11-05)

Full Changelog: [v1.54.0...v1.54.1](https://github.com/openai/openai-python/compare/v1.54.0...v1.54.1)

### Bug Fixes

* add new prediction param to all methods ([6aa424d](https://github.com/openai/openai-python/commit/6aa424d076098312801febd938bd4b5e8baf4851))

## 1.54.0 (2024-11-04)

Full Changelog: [v1.53.1...v1.54.0](https://github.com/openai/openai-python/compare/v1.53.1...v1.54.0)

### Features

* **api:** add support for predicted outputs ([#1847](https://github.com/openai/openai-python/issues/1847)) ([42a4103](https://github.com/openai/openai-python/commit/42a410379a1b5f72424cc2e96dc6ddff22fd00be))
* **project:** drop support for Python 3.7 ([#1845](https://github.com/openai/openai-python/issues/1845)) ([0ed5b1a](https://github.com/openai/openai-python/commit/0ed5b1a9302ccf2f40c3c751cd777740a4749cda))

## 1.53.1 (2024-11-04)

Full Changelog: [v1.53.0...v1.53.1](https://github.com/openai/openai-python/compare/v1.53.0...v1.53.1)

### Bug Fixes

* don't use dicts as iterables in transform ([#1842](https://github.com/openai/openai-python/issues/1842)) ([258f265](https://github.com/openai/openai-python/commit/258f26535744ab3b2f0746991fd29eae72ebd667))
* support json safe serialization for basemodel subclasses ([#1844](https://github.com/openai/openai-python/issues/1844)) ([2b80c90](https://github.com/openai/openai-python/commit/2b80c90c21d3b2468dfa3bf40c08c5b0e0eebffa))


### Chores

* **internal:** bump mypy ([#1839](https://github.com/openai/openai-python/issues/1839)) ([d92f959](https://github.com/openai/openai-python/commit/d92f959aa6f49be56574b4d1d1ac5ac48689dd46))

## 1.53.0 (2024-10-30)

Full Changelog: [v1.52.2...v1.53.0](https://github.com/openai/openai-python/compare/v1.52.2...v1.53.0)

### Features

* **api:** add new, expressive voices for Realtime and Audio in Chat Completions ([7cf0a49](https://github.com/openai/openai-python/commit/7cf0a4958e4c985bef4d18bb919fa3948f389a82))


### Chores

* **internal:** bump pytest to v8 & pydantic ([#1829](https://github.com/openai/openai-python/issues/1829)) ([0e67a8a](https://github.com/openai/openai-python/commit/0e67a8af5daf9da029d2bd4bdf341cc8a494254a))

## 1.52.2 (2024-10-23)

Full Changelog: [v1.52.1...v1.52.2](https://github.com/openai/openai-python/compare/v1.52.1...v1.52.2)

### Chores

* **internal:** update spec version ([#1816](https://github.com/openai/openai-python/issues/1816)) ([c23282a](https://github.com/openai/openai-python/commit/c23282a328c48af90a88673ff5f6cc7a866f8758))

## 1.52.1 (2024-10-22)

Full Changelog: [v1.52.0...v1.52.1](https://github.com/openai/openai-python/compare/v1.52.0...v1.52.1)

### Bug Fixes

* **client/async:** correctly retry in all cases ([#1803](https://github.com/openai/openai-python/issues/1803)) ([9fe3f3f](https://github.com/openai/openai-python/commit/9fe3f3f925e06769b7ef6abbf1314a5e82749b4a))


### Chores

* **internal:** bump ruff dependency ([#1801](https://github.com/openai/openai-python/issues/1801)) ([859c672](https://github.com/openai/openai-python/commit/859c6725865f1b3285698f68693f9491d511f7ea))
* **internal:** remove unused black config ([#1807](https://github.com/openai/openai-python/issues/1807)) ([112dab0](https://github.com/openai/openai-python/commit/112dab0290342654265db612c37d327d652251bb))
* **internal:** update spec version ([#1810](https://github.com/openai/openai-python/issues/1810)) ([aa25b7b](https://github.com/openai/openai-python/commit/aa25b7b88823836b418a63da59491f5f3842773c))
* **internal:** update test syntax ([#1798](https://github.com/openai/openai-python/issues/1798)) ([d3098dd](https://github.com/openai/openai-python/commit/d3098dd0b9fbe627c21a8ad39c119d125b7cdb54))
* **tests:** add more retry tests ([#1806](https://github.com/openai/openai-python/issues/1806)) ([5525a1b](https://github.com/openai/openai-python/commit/5525a1ba536058ecc13411e1f98e88f7ec4bf8b9))

## 1.52.0 (2024-10-17)

Full Changelog: [v1.51.2...v1.52.0](https://github.com/openai/openai-python/compare/v1.51.2...v1.52.0)

### Features

* **api:** add gpt-4o-audio-preview model for chat completions ([#1796](https://github.com/openai/openai-python/issues/1796)) ([fbf1e0c](https://github.com/openai/openai-python/commit/fbf1e0c25c4d163f06b61a43d1a94ce001033a7b))

## 1.51.2 (2024-10-08)

Full Changelog: [v1.51.1...v1.51.2](https://github.com/openai/openai-python/compare/v1.51.1...v1.51.2)

### Chores

* add repr to PageInfo class ([#1780](https://github.com/openai/openai-python/issues/1780)) ([63118ee](https://github.com/openai/openai-python/commit/63118ee3c2481d217682e8a31337bdcc16893127))

## 1.51.1 (2024-10-07)

Full Changelog: [v1.51.0...v1.51.1](https://github.com/openai/openai-python/compare/v1.51.0...v1.51.1)

### Bug Fixes

* **client:** avoid OverflowError with very large retry counts ([#1779](https://github.com/openai/openai-python/issues/1779)) ([fb1dacf](https://github.com/openai/openai-python/commit/fb1dacfa4d9447d123c38ab3d3d433d900d32ec5))


### Chores

* **internal:** add support for parsing bool response content ([#1774](https://github.com/openai/openai-python/issues/1774)) ([aa2e25f](https://github.com/openai/openai-python/commit/aa2e25f9a4a632357051397ea34d269eafba026d))


### Documentation

* fix typo in fenced code block language ([#1769](https://github.com/openai/openai-python/issues/1769)) ([57bbc15](https://github.com/openai/openai-python/commit/57bbc155210cc439a36f4e5cbd082e94c3349d78))
* improve and reference contributing documentation ([#1767](https://github.com/openai/openai-python/issues/1767)) ([a985a8b](https://github.com/openai/openai-python/commit/a985a8b8ab8d0b364bd3c26b6423a7c49ae7b1ce))

## 1.51.0 (2024-10-01)

Full Changelog: [v1.50.2...v1.51.0](https://github.com/openai/openai-python/compare/v1.50.2...v1.51.0)

### Features

* **api:** support storing chat completions, enabling evals and model distillation in the dashboard ([2840c6d](https://github.com/openai/openai-python/commit/2840c6df94afb44cfd80efabe0405898331ee267))


### Chores

* **docs:** fix maxium typo ([#1762](https://github.com/openai/openai-python/issues/1762)) ([de94553](https://github.com/openai/openai-python/commit/de94553f93d71fc6c8187c8d3fbe924a71cc46dd))
* **internal:** remove ds store ([47a3968](https://github.com/openai/openai-python/commit/47a3968f9b318eb02d5602f5b10e7d9e69c3ae84))


### Documentation

* **helpers:** fix method name typo ([#1764](https://github.com/openai/openai-python/issues/1764)) ([e1bcfe8](https://github.com/openai/openai-python/commit/e1bcfe86554017ac63055060153c4fd72e65c0cf))

## 1.50.2 (2024-09-27)

Full Changelog: [v1.50.1...v1.50.2](https://github.com/openai/openai-python/compare/v1.50.1...v1.50.2)

### Bug Fixes

* **audio:** correct types for transcriptions / translations ([#1755](https://github.com/openai/openai-python/issues/1755)) ([76c1f3f](https://github.com/openai/openai-python/commit/76c1f3f318b68003aae124c02efc4547a398a864))

## 1.50.1 (2024-09-27)

Full Changelog: [v1.50.0...v1.50.1](https://github.com/openai/openai-python/compare/v1.50.0...v1.50.1)

### Documentation

* **helpers:** fix chat completion anchor ([#1753](https://github.com/openai/openai-python/issues/1753)) ([956d4e8](https://github.com/openai/openai-python/commit/956d4e8e32507fbce399f4619e06daa9d37a0532))

## 1.50.0 (2024-09-26)

Full Changelog: [v1.49.0...v1.50.0](https://github.com/openai/openai-python/compare/v1.49.0...v1.50.0)

### Features

* **structured outputs:** add support for accessing raw responses ([#1748](https://github.com/openai/openai-python/issues/1748)) ([0189e28](https://github.com/openai/openai-python/commit/0189e28b0b062a28b16343da0460a4f0f4e17a9a))


### Chores

* **pydantic v1:** exclude specific properties when rich printing ([#1751](https://github.com/openai/openai-python/issues/1751)) ([af535ce](https://github.com/openai/openai-python/commit/af535ce6a523eca39438f117a3e55f16064567a9))

## 1.49.0 (2024-09-26)

Full Changelog: [v1.48.0...v1.49.0](https://github.com/openai/openai-python/compare/v1.48.0...v1.49.0)

### Features

* **api:** add omni-moderation model ([#1750](https://github.com/openai/openai-python/issues/1750)) ([05b50da](https://github.com/openai/openai-python/commit/05b50da5428d5c7b5ea09626bcd88f8423762bf8))


### Chores

* **internal:** update test snapshots ([#1749](https://github.com/openai/openai-python/issues/1749)) ([42f054e](https://github.com/openai/openai-python/commit/42f054ee7afa8ce8316c2ecd90608a0f7e13bfdd))

## 1.48.0 (2024-09-25)

Full Changelog: [v1.47.1...v1.48.0](https://github.com/openai/openai-python/compare/v1.47.1...v1.48.0)

### Features

* **client:** allow overriding retry count header ([#1745](https://github.com/openai/openai-python/issues/1745)) ([9f07d4d](https://github.com/openai/openai-python/commit/9f07d4dbd6f24108a1f5e0309037318858f5a229))


### Bug Fixes

* **audio:** correct response_format translations type ([#1743](https://github.com/openai/openai-python/issues/1743)) ([b912108](https://github.com/openai/openai-python/commit/b9121089c696bc943323e2e75d4706401d809aaa))


### Chores

* **internal:** use `typing_extensions.overload` instead of `typing` ([#1740](https://github.com/openai/openai-python/issues/1740)) ([2522bd5](https://github.com/openai/openai-python/commit/2522bd59f7b5e903e4fc856a4c5dbdbe66bba37f))

## 1.47.1 (2024-09-23)

Full Changelog: [v1.47.0...v1.47.1](https://github.com/openai/openai-python/compare/v1.47.0...v1.47.1)

### Bug Fixes

* **pydantic v1:** avoid warnings error ([1e8e7d1](https://github.com/openai/openai-python/commit/1e8e7d1f01a4ab4153085bc20484a19613d993b3))

## 1.47.0 (2024-09-20)

Full Changelog: [v1.46.1...v1.47.0](https://github.com/openai/openai-python/compare/v1.46.1...v1.47.0)

### Features

* **client:** send retry count header ([21b0c00](https://github.com/openai/openai-python/commit/21b0c0043406d81971f87455e5a48b17935dc346))


### Chores

* **types:** improve type name for embedding models ([#1730](https://github.com/openai/openai-python/issues/1730)) ([4b4eb2b](https://github.com/openai/openai-python/commit/4b4eb2b37877728d2124ad5651ceebf615c0ab28))

## 1.46.1 (2024-09-19)

Full Changelog: [v1.46.0...v1.46.1](https://github.com/openai/openai-python/compare/v1.46.0...v1.46.1)

### Bug Fixes

* **client:** handle domains with underscores ([#1726](https://github.com/openai/openai-python/issues/1726)) ([cd194df](https://github.com/openai/openai-python/commit/cd194dfdc418a84589bd903357cba349e9ad3e78))


### Chores

* **streaming:** silence pydantic model_dump warnings ([#1722](https://github.com/openai/openai-python/issues/1722)) ([30f84b9](https://github.com/openai/openai-python/commit/30f84b96081ac37f60e40a75d765dbbf563b61b3))

## 1.46.0 (2024-09-17)

Full Changelog: [v1.45.1...v1.46.0](https://github.com/openai/openai-python/compare/v1.45.1...v1.46.0)

### Features

* **client:** add ._request_id property to object responses ([#1707](https://github.com/openai/openai-python/issues/1707)) ([8b3da05](https://github.com/openai/openai-python/commit/8b3da05a35b33245aec98693a0540ace6218a61b))


### Documentation

* **readme:** add examples for chat with image content ([#1703](https://github.com/openai/openai-python/issues/1703)) ([192b8f2](https://github.com/openai/openai-python/commit/192b8f2b6a49f462e48c1442858931875524ab49))

## 1.45.1 (2024-09-16)

Full Changelog: [v1.45.0...v1.45.1](https://github.com/openai/openai-python/compare/v1.45.0...v1.45.1)

### Chores

* **internal:** bump pyright / mypy version ([#1717](https://github.com/openai/openai-python/issues/1717)) ([351af85](https://github.com/openai/openai-python/commit/351af85c5b813391910301a5049edddc8c9e70dd))
* **internal:** bump ruff ([#1714](https://github.com/openai/openai-python/issues/1714)) ([aceaf64](https://github.com/openai/openai-python/commit/aceaf641eedd092ed42e4aaf031e8cfbf37e4212))
* **internal:** update spec link ([#1716](https://github.com/openai/openai-python/issues/1716)) ([ca58c7f](https://github.com/openai/openai-python/commit/ca58c7f83a7cede0367dec2500127573c9b00d1f))


### Documentation

* update CONTRIBUTING.md ([#1710](https://github.com/openai/openai-python/issues/1710)) ([4d45eb5](https://github.com/openai/openai-python/commit/4d45eb5eb794bcc5076c022be09e06fae103abcc))

## 1.45.0 (2024-09-12)

Full Changelog: [v1.44.1...v1.45.0](https://github.com/openai/openai-python/compare/v1.44.1...v1.45.0)

### Features

* **api:** add o1 models ([#1708](https://github.com/openai/openai-python/issues/1708)) ([06bd42e](https://github.com/openai/openai-python/commit/06bd42e77121a6abd4826a79ce1848812d956576))
* **errors:** include completion in LengthFinishReasonError ([#1701](https://github.com/openai/openai-python/issues/1701)) ([b0e3256](https://github.com/openai/openai-python/commit/b0e32562aff9aceafec994d3b047f7c2a9f11524))


### Bug Fixes

* **types:** correctly mark stream discriminator as optional ([#1706](https://github.com/openai/openai-python/issues/1706)) ([80f02f9](https://github.com/openai/openai-python/commit/80f02f9e5f83fac9cd2f4172b733a92ad01399b2))

## 1.44.1 (2024-09-09)

Full Changelog: [v1.44.0...v1.44.1](https://github.com/openai/openai-python/compare/v1.44.0...v1.44.1)

### Chores

* add docstrings to raw response properties ([#1696](https://github.com/openai/openai-python/issues/1696)) ([1d2a19b](https://github.com/openai/openai-python/commit/1d2a19b0e8acab54c35ef2171d33321943488fdc))


### Documentation

* **readme:** add section on determining installed version ([#1697](https://github.com/openai/openai-python/issues/1697)) ([0255735](https://github.com/openai/openai-python/commit/0255735930d9c657c78e85e7f03fd1eb98a1e378))
* **readme:** improve custom `base_url` example ([#1694](https://github.com/openai/openai-python/issues/1694)) ([05eec8a](https://github.com/openai/openai-python/commit/05eec8a0b7fcdc8651021f2e685214a353b861d1))

## 1.44.0 (2024-09-06)

Full Changelog: [v1.43.1...v1.44.0](https://github.com/openai/openai-python/compare/v1.43.1...v1.44.0)

### Features

* **vector store:** improve chunking strategy type names ([#1690](https://github.com/openai/openai-python/issues/1690)) ([e82cd85](https://github.com/openai/openai-python/commit/e82cd85ac4962e36cb3b139c503069b56918688f))

## 1.43.1 (2024-09-05)

Full Changelog: [v1.43.0...v1.43.1](https://github.com/openai/openai-python/compare/v1.43.0...v1.43.1)

### Chores

* pyproject.toml formatting changes ([#1687](https://github.com/openai/openai-python/issues/1687)) ([3387ede](https://github.com/openai/openai-python/commit/3387ede0b896788bf1197378b01941c75bd6e179))

## 1.43.0 (2024-08-29)

Full Changelog: [v1.42.0...v1.43.0](https://github.com/openai/openai-python/compare/v1.42.0...v1.43.0)

### Features

* **api:** add file search result details to run steps ([#1681](https://github.com/openai/openai-python/issues/1681)) ([f5449c0](https://github.com/openai/openai-python/commit/f5449c07580ac9707f0387f86f4772fbf0a874b6))

## 1.42.0 (2024-08-20)

Full Changelog: [v1.41.1...v1.42.0](https://github.com/openai/openai-python/compare/v1.41.1...v1.42.0)

### Features

* **parsing:** add support for pydantic dataclasses ([#1655](https://github.com/openai/openai-python/issues/1655)) ([101bee9](https://github.com/openai/openai-python/commit/101bee9844f725d2174796c3d09a58d3aa079fad))


### Chores

* **ci:** also run pydantic v1 tests ([#1666](https://github.com/openai/openai-python/issues/1666)) ([af2a1ca](https://github.com/openai/openai-python/commit/af2a1ca408a406098c6c79837aa3561b822e08ec))

## 1.41.1 (2024-08-19)

Full Changelog: [v1.41.0...v1.41.1](https://github.com/openai/openai-python/compare/v1.41.0...v1.41.1)

### Bug Fixes

* **json schema:** remove `None` defaults ([#1663](https://github.com/openai/openai-python/issues/1663)) ([30215c1](https://github.com/openai/openai-python/commit/30215c15df613cf9c36cafd717af79158c9db3e5))


### Chores

* **client:** fix parsing union responses when non-json is returned ([#1665](https://github.com/openai/openai-python/issues/1665)) ([822c37d](https://github.com/openai/openai-python/commit/822c37de49eb2ffe8c05122f7520ba87bd76e30b))

## 1.41.0 (2024-08-16)

Full Changelog: [v1.40.8...v1.41.0](https://github.com/openai/openai-python/compare/v1.40.8...v1.41.0)

### Features

* **client:** add uploads.upload_file helper ([aae079d](https://github.com/openai/openai-python/commit/aae079daa3c1763ab0e46bad766ae5261b475806))

## 1.40.8 (2024-08-15)

Full Changelog: [v1.40.7...v1.40.8](https://github.com/openai/openai-python/compare/v1.40.7...v1.40.8)

### Chores

* **types:** define FilePurpose enum ([#1653](https://github.com/openai/openai-python/issues/1653)) ([3c2eeae](https://github.com/openai/openai-python/commit/3c2eeae32adf5d4ab6bc622be6f9a95a1a298dd3))

## 1.40.7 (2024-08-15)

Full Changelog: [v1.40.6...v1.40.7](https://github.com/openai/openai-python/compare/v1.40.6...v1.40.7)

### Bug Fixes

* **cli/migrate:** change grit binaries download source ([#1649](https://github.com/openai/openai-python/issues/1649)) ([85e8935](https://github.com/openai/openai-python/commit/85e8935d9a123b92964d39a98334a975a06ab845))


### Chores

* **docs:** fix typo in example snippet ([4e83b57](https://github.com/openai/openai-python/commit/4e83b57ffbb64e1c98c19968557dc68a0b65d0b3))
* **internal:** use different 32bit detection method ([#1652](https://github.com/openai/openai-python/issues/1652)) ([5831af6](https://github.com/openai/openai-python/commit/5831af65048af2a5df9e3ea4a48b8fff2e66dd8c))

## 1.40.6 (2024-08-12)

Full Changelog: [v1.40.5...v1.40.6](https://github.com/openai/openai-python/compare/v1.40.5...v1.40.6)

### Chores

* **examples:** minor formatting changes ([#1644](https://github.com/openai/openai-python/issues/1644)) ([e08acf1](https://github.com/openai/openai-python/commit/e08acf1c6edd1501ed70c4634cd884ab1658af0d))
* **internal:** update some imports ([#1642](https://github.com/openai/openai-python/issues/1642)) ([fce1ea7](https://github.com/openai/openai-python/commit/fce1ea72a89ba2737bc77775fe04f3a21ecb28e7))
* sync openapi url ([#1646](https://github.com/openai/openai-python/issues/1646)) ([8ae3801](https://github.com/openai/openai-python/commit/8ae380123ada0bfaca9961e222a0e9c8b585e2d4))
* **tests:** fix pydantic v1 tests ([2623630](https://github.com/openai/openai-python/commit/26236303f0f6de5df887e8ee3e41d5bc39a3abb1))

## 1.40.5 (2024-08-12)

Full Changelog: [v1.40.4...v1.40.5](https://github.com/openai/openai-python/compare/v1.40.4...v1.40.5)

### Documentation

* **helpers:** make async client usage more clear ([34e1edf](https://github.com/openai/openai-python/commit/34e1edf29d6008df7196aaebc45172fa536c6410)), closes [#1639](https://github.com/openai/openai-python/issues/1639)

## 1.40.4 (2024-08-12)

Full Changelog: [v1.40.3...v1.40.4](https://github.com/openai/openai-python/compare/v1.40.3...v1.40.4)

### Bug Fixes

* **json schema:** unravel `$ref`s alongside additional keys ([c7a3d29](https://github.com/openai/openai-python/commit/c7a3d2986acaf3b31844b39608d03265ad87bb04))
* **json schema:** unwrap `allOf`s with one entry ([53d964d](https://github.com/openai/openai-python/commit/53d964defebdf385d7d832ec7f13111b4af13c27))

## 1.40.3 (2024-08-10)

Full Changelog: [v1.40.2...v1.40.3](https://github.com/openai/openai-python/compare/v1.40.2...v1.40.3)

### Chores

* **ci:** bump prism mock server version ([#1630](https://github.com/openai/openai-python/issues/1630)) ([214d8fd](https://github.com/openai/openai-python/commit/214d8fd8d7d43c06c7dfe02680847a6a60988120))
* **ci:** codeowners file ([#1627](https://github.com/openai/openai-python/issues/1627)) ([c059a20](https://github.com/openai/openai-python/commit/c059a20c8cd2124178641c9d8688e276b1cf1d59))
* **internal:** ensure package is importable in lint cmd ([#1631](https://github.com/openai/openai-python/issues/1631)) ([779e6d0](https://github.com/openai/openai-python/commit/779e6d081eb55c158f2aa1962190079eb7f1335e))

## 1.40.2 (2024-08-08)

Full Changelog: [v1.40.1...v1.40.2](https://github.com/openai/openai-python/compare/v1.40.1...v1.40.2)

### Bug Fixes

* **client:** raise helpful error message for response_format misuse ([18191da](https://github.com/openai/openai-python/commit/18191dac8e1437a0f708525d474b7ecfe459d966))
* **json schema:** support recursive BaseModels in Pydantic v1 ([#1623](https://github.com/openai/openai-python/issues/1623)) ([43e10c0](https://github.com/openai/openai-python/commit/43e10c0f251a42f1e6497f360c6c23d3058b3da3))


### Chores

* **internal:** format some docstrings ([d34a081](https://github.com/openai/openai-python/commit/d34a081c30f869646145919b2256ded115241eb5))
* **internal:** updates ([#1624](https://github.com/openai/openai-python/issues/1624)) ([598e7a2](https://github.com/openai/openai-python/commit/598e7a23768e7addbe1319ada2e87caee3cf0d14))

## 1.40.1 (2024-08-07)

Full Changelog: [v1.40.0...v1.40.1](https://github.com/openai/openai-python/compare/v1.40.0...v1.40.1)

### Chores

* **internal:** update OpenAPI spec url ([#1608](https://github.com/openai/openai-python/issues/1608)) ([5392753](https://github.com/openai/openai-python/commit/53927531fc101e96b9e3f5d44f34b298055f496a))
* **internal:** update test snapshots ([a11d1cb](https://github.com/openai/openai-python/commit/a11d1cb5d04aac0bf69dc10a3a21fa95575c0aa0))

## 1.40.0 (2024-08-06)

Full Changelog: [v1.39.0...v1.40.0](https://github.com/openai/openai-python/compare/v1.39.0...v1.40.0)

### Features

* **api:** add structured outputs support ([e8dba7d](https://github.com/openai/openai-python/commit/e8dba7d0e08a7d0de5952be716e0efe9ae373759))


### Chores

* **internal:** bump ruff version ([#1604](https://github.com/openai/openai-python/issues/1604)) ([3e19a87](https://github.com/openai/openai-python/commit/3e19a87255d8e92716689656afaa3f16297773b6))
* **internal:** update pydantic compat helper function ([#1607](https://github.com/openai/openai-python/issues/1607)) ([973c18b](https://github.com/openai/openai-python/commit/973c18b259a0e4a8134223f50a5f660b86650949))

## 1.39.0 (2024-08-05)

Full Changelog: [v1.38.0...v1.39.0](https://github.com/openai/openai-python/compare/v1.38.0...v1.39.0)

### Features

* **client:** add `retries_taken` to raw response class ([#1601](https://github.com/openai/openai-python/issues/1601)) ([777822b](https://github.com/openai/openai-python/commit/777822b39b7f9ebd6272d0af8fc04f9d657bd886))


### Bug Fixes

* **assistants:** add parallel_tool_calls param to runs.stream ([113e82a](https://github.com/openai/openai-python/commit/113e82a82c7390660ad3324fa8f9842f83b27571))


### Chores

* **internal:** bump pyright ([#1599](https://github.com/openai/openai-python/issues/1599)) ([27f0f10](https://github.com/openai/openai-python/commit/27f0f107e39d16adc0d5a50ffe4c687e0e3c42e5))
* **internal:** test updates ([#1602](https://github.com/openai/openai-python/issues/1602)) ([af22d80](https://github.com/openai/openai-python/commit/af22d8079cf44cde5f03a206e78b900f8413dc43))
* **internal:** use `TypeAlias` marker for type assignments ([#1597](https://github.com/openai/openai-python/issues/1597)) ([5907ea0](https://github.com/openai/openai-python/commit/5907ea04d6f5e0ffd17c38ad6a644a720ece8abe))

## 1.38.0 (2024-08-02)

Full Changelog: [v1.37.2...v1.38.0](https://github.com/openai/openai-python/compare/v1.37.2...v1.38.0)

### Features

* extract out `ImageModel`, `AudioModel`, `SpeechModel` ([#1586](https://github.com/openai/openai-python/issues/1586)) ([b800316](https://github.com/openai/openai-python/commit/b800316aee6c8b2aeb609ca4c41972adccd2fa7a))
* make enums not nominal ([#1588](https://github.com/openai/openai-python/issues/1588)) ([ab4519b](https://github.com/openai/openai-python/commit/ab4519bc45f5512c8c5165641c217385d999809c))

## 1.37.2 (2024-08-01)

Full Changelog: [v1.37.1...v1.37.2](https://github.com/openai/openai-python/compare/v1.37.1...v1.37.2)

### Chores

* **internal:** add type construction helper ([#1584](https://github.com/openai/openai-python/issues/1584)) ([cbb186a](https://github.com/openai/openai-python/commit/cbb186a534b520fa5b11a9b371b175e3f6a6482b))
* **runs/create_and_poll:** add parallel_tool_calls request param ([04b3e6c](https://github.com/openai/openai-python/commit/04b3e6c39ee5a7088e0e4dfa4c06f3dcce901a57))

## 1.37.1 (2024-07-25)

Full Changelog: [v1.37.0...v1.37.1](https://github.com/openai/openai-python/compare/v1.37.0...v1.37.1)

### Chores

* **tests:** update prism version ([#1572](https://github.com/openai/openai-python/issues/1572)) ([af82593](https://github.com/openai/openai-python/commit/af8259393673af1ef6ec711da6297eb4ad55b66e))

## 1.37.0 (2024-07-22)

Full Changelog: [v1.36.1...v1.37.0](https://github.com/openai/openai-python/compare/v1.36.1...v1.37.0)

### Features

* **api:** add uploads endpoints ([#1568](https://github.com/openai/openai-python/issues/1568)) ([d877b6d](https://github.com/openai/openai-python/commit/d877b6dabb9b3e8da6ff2f46de1120af54de398d))


### Bug Fixes

* **cli/audio:** handle non-json response format ([#1557](https://github.com/openai/openai-python/issues/1557)) ([bb7431f](https://github.com/openai/openai-python/commit/bb7431f602602d4c74d75809c6934a7fd192972d))


### Documentation

* **readme:** fix example snippet imports ([#1569](https://github.com/openai/openai-python/issues/1569)) ([0c90af6](https://github.com/openai/openai-python/commit/0c90af6412b3314c2257b9b8eb7fabd767f32ef6))

## 1.36.1 (2024-07-20)

Full Changelog: [v1.36.0...v1.36.1](https://github.com/openai/openai-python/compare/v1.36.0...v1.36.1)

### Bug Fixes

* **types:** add gpt-4o-mini to more assistants methods ([39a8a37](https://github.com/openai/openai-python/commit/39a8a372eb3f2d75fd4310d42294d05175a59fd8))

## 1.36.0 (2024-07-19)

Full Changelog: [v1.35.15...v1.36.0](https://github.com/openai/openai-python/compare/v1.35.15...v1.36.0)

### Features

* **api:** add new gpt-4o-mini models ([#1561](https://github.com/openai/openai-python/issues/1561)) ([5672ad4](https://github.com/openai/openai-python/commit/5672ad40aaa3498f6143baa48fc22bb1a3475bea))

## 1.35.15 (2024-07-18)

Full Changelog: [v1.35.14...v1.35.15](https://github.com/openai/openai-python/compare/v1.35.14...v1.35.15)

### Chores

* **docs:** document how to do per-request http client customization ([#1560](https://github.com/openai/openai-python/issues/1560)) ([24c0768](https://github.com/openai/openai-python/commit/24c076873c5cb2abe0d3e285b99aa110451b0f19))
* **internal:** update formatting ([#1553](https://github.com/openai/openai-python/issues/1553)) ([e1389bc](https://github.com/openai/openai-python/commit/e1389bcc26f3aac63fc6bc9bb151c9a330d95b4e))

## 1.35.14 (2024-07-15)

Full Changelog: [v1.35.13...v1.35.14](https://github.com/openai/openai-python/compare/v1.35.13...v1.35.14)

### Chores

* **docs:** minor update to formatting of API link in README ([#1550](https://github.com/openai/openai-python/issues/1550)) ([a6e59c6](https://github.com/openai/openai-python/commit/a6e59c6bbff9e1132aa323c0ecb3be7f0692ae42))
* **internal:** minor formatting changes ([ee1c62e](https://github.com/openai/openai-python/commit/ee1c62ede01872e76156d886af4aab5f8eb1cc64))
* **internal:** minor options / compat functions updates ([#1549](https://github.com/openai/openai-python/issues/1549)) ([a0701b5](https://github.com/openai/openai-python/commit/a0701b5dbeda4ac2d8a4b093aee4bdad9d674ee2))

## 1.35.13 (2024-07-10)

Full Changelog: [v1.35.12...v1.35.13](https://github.com/openai/openai-python/compare/v1.35.12...v1.35.13)

### Bug Fixes

* **threads/runs/create_and_run_stream:** correct tool_resources param ([8effd08](https://github.com/openai/openai-python/commit/8effd08be3ab1cf509bdbfd9f174f9186fdbf71f))


### Chores

* **internal:** add helper function ([#1538](https://github.com/openai/openai-python/issues/1538)) ([81655a0](https://github.com/openai/openai-python/commit/81655a012e28c0240e71cf74b77ad1f9ac630906))

## 1.35.12 (2024-07-09)

Full Changelog: [v1.35.11...v1.35.12](https://github.com/openai/openai-python/compare/v1.35.11...v1.35.12)

### Bug Fixes

* **azure:** refresh auth token during retries ([#1533](https://github.com/openai/openai-python/issues/1533)) ([287926e](https://github.com/openai/openai-python/commit/287926e4c0920b930af2b9d3d8b46a24e78e2979))
* **tests:** fresh_env() now resets new environment values ([64da888](https://github.com/openai/openai-python/commit/64da888ca4d13f0b4b6d9e22ec93a897b2d6bb24))

## 1.35.11 (2024-07-09)

Full Changelog: [v1.35.10...v1.35.11](https://github.com/openai/openai-python/compare/v1.35.10...v1.35.11)

### Chores

* **internal:** minor request options handling changes ([#1534](https://github.com/openai/openai-python/issues/1534)) ([8b0e493](https://github.com/openai/openai-python/commit/8b0e49302b3fcc32cf02393bf28354c577188904))

## 1.35.10 (2024-07-03)

Full Changelog: [v1.35.9...v1.35.10](https://github.com/openai/openai-python/compare/v1.35.9...v1.35.10)

### Chores

* **ci:** update rye to v0.35.0 ([#1523](https://github.com/openai/openai-python/issues/1523)) ([dd118c4](https://github.com/openai/openai-python/commit/dd118c422019df00b153104b7bddf892c2ec7417))

## 1.35.9 (2024-07-02)

Full Changelog: [v1.35.8...v1.35.9](https://github.com/openai/openai-python/compare/v1.35.8...v1.35.9)

### Bug Fixes

* **client:** always respect content-type multipart/form-data if provided ([#1519](https://github.com/openai/openai-python/issues/1519)) ([6da55e1](https://github.com/openai/openai-python/commit/6da55e10c4ba8c78687baedc68d5599ea120d05c))


### Chores

* minor change to tests ([#1521](https://github.com/openai/openai-python/issues/1521)) ([a679c0b](https://github.com/openai/openai-python/commit/a679c0bd1e041434440174daa7a64289746856d1))

## 1.35.8 (2024-07-02)

Full Changelog: [v1.35.7...v1.35.8](https://github.com/openai/openai-python/compare/v1.35.7...v1.35.8)

### Chores

* gitignore test server logs ([#1509](https://github.com/openai/openai-python/issues/1509)) ([936d840](https://github.com/openai/openai-python/commit/936d84094a28ad0a2b4a20e2b3bbf1674048223e))
* **internal:** add helper method for constructing `BaseModel`s ([#1517](https://github.com/openai/openai-python/issues/1517)) ([e5ddbf5](https://github.com/openai/openai-python/commit/e5ddbf554ce4b6be4b59114a36e69f02ca724acf))
* **internal:** add reflection helper function ([#1508](https://github.com/openai/openai-python/issues/1508)) ([6044e1b](https://github.com/openai/openai-python/commit/6044e1bbfa9e46a01faf5a9edf198f86fa4c6dd0))
* **internal:** add rich as a dev dependency ([#1514](https://github.com/openai/openai-python/issues/1514)) ([8a2b4e4](https://github.com/openai/openai-python/commit/8a2b4e4c1233dca916531ebc65d65a8d35fa7b7b))

## 1.35.7 (2024-06-27)

Full Changelog: [v1.35.6...v1.35.7](https://github.com/openai/openai-python/compare/v1.35.6...v1.35.7)

### Bug Fixes

* **build:** include more files in sdist builds ([#1504](https://github.com/openai/openai-python/issues/1504)) ([730c1b5](https://github.com/openai/openai-python/commit/730c1b53b1a61e218a85aa2d1cf3ba4775618755))

## 1.35.6 (2024-06-27)

Full Changelog: [v1.35.5...v1.35.6](https://github.com/openai/openai-python/compare/v1.35.5...v1.35.6)

### Documentation

* **readme:** improve some wording ([#1392](https://github.com/openai/openai-python/issues/1392)) ([a58a052](https://github.com/openai/openai-python/commit/a58a05215b560ebcf3ff3eb1dd997259720a48f3))

## 1.35.5 (2024-06-26)

Full Changelog: [v1.35.4...v1.35.5](https://github.com/openai/openai-python/compare/v1.35.4...v1.35.5)

### Bug Fixes

* **cli/migrate:** avoid reliance on Python 3.12 argument ([be7a06b](https://github.com/openai/openai-python/commit/be7a06b3875e3ecb9229d67a41e290ca218f092d))

## 1.35.4 (2024-06-26)

Full Changelog: [v1.35.3...v1.35.4](https://github.com/openai/openai-python/compare/v1.35.3...v1.35.4)

### Bug Fixes

* **docs:** fix link to advanced python httpx docs ([#1499](https://github.com/openai/openai-python/issues/1499)) ([cf45cd5](https://github.com/openai/openai-python/commit/cf45cd5942cecec569072146673ddfc0e0ec108e))
* temporarily patch upstream version to fix broken release flow ([#1500](https://github.com/openai/openai-python/issues/1500)) ([4f10470](https://github.com/openai/openai-python/commit/4f10470f5f74fc258a78fa6d897d8ab5b70dcf52))


### Chores

* **doc:** clarify service tier default value ([#1496](https://github.com/openai/openai-python/issues/1496)) ([ba39667](https://github.com/openai/openai-python/commit/ba39667c4faa8e10457347be41334ca9639186d4))

## 1.35.3 (2024-06-20)

Full Changelog: [v1.35.2...v1.35.3](https://github.com/openai/openai-python/compare/v1.35.2...v1.35.3)

### Bug Fixes

* **tests:** add explicit type annotation ([9345f10](https://github.com/openai/openai-python/commit/9345f104889056b2ef6646d65375925a0a3bae03))

## 1.35.2 (2024-06-20)

Full Changelog: [v1.35.1...v1.35.2](https://github.com/openai/openai-python/compare/v1.35.1...v1.35.2)

### Bug Fixes

* **api:** add missing parallel_tool_calls arguments ([4041e4f](https://github.com/openai/openai-python/commit/4041e4f6ea1e2316179a82031001308be23a2524))

## 1.35.1 (2024-06-19)

Full Changelog: [v1.35.0...v1.35.1](https://github.com/openai/openai-python/compare/v1.35.0...v1.35.1)

### Bug Fixes

* **client/async:** avoid blocking io call for platform headers ([#1488](https://github.com/openai/openai-python/issues/1488)) ([ae64c05](https://github.com/openai/openai-python/commit/ae64c05cbae76a58b592d913bee6ac1ef9611d4c))

## 1.35.0 (2024-06-18)

Full Changelog: [v1.34.0...v1.35.0](https://github.com/openai/openai-python/compare/v1.34.0...v1.35.0)

### Features

* **api:** add service tier argument for chat completions ([#1486](https://github.com/openai/openai-python/issues/1486)) ([b4b4e66](https://github.com/openai/openai-python/commit/b4b4e660b8bb7ae937787fcab9b40feaeba7f711))

## 1.34.0 (2024-06-12)

Full Changelog: [v1.33.0...v1.34.0](https://github.com/openai/openai-python/compare/v1.33.0...v1.34.0)

### Features

* **api:** updates ([#1481](https://github.com/openai/openai-python/issues/1481)) ([b83db36](https://github.com/openai/openai-python/commit/b83db362f0c9a5a4d55588b954fb1df1a68c98e3))

## 1.33.0 (2024-06-07)

Full Changelog: [v1.32.1...v1.33.0](https://github.com/openai/openai-python/compare/v1.32.1...v1.33.0)

### Features

* **api:** adding chunking_strategy to polling helpers ([#1478](https://github.com/openai/openai-python/issues/1478)) ([83be2a1](https://github.com/openai/openai-python/commit/83be2a13e0384d3de52190d86ccb1b5d7a197d84))

## 1.32.1 (2024-06-07)

Full Changelog: [v1.32.0...v1.32.1](https://github.com/openai/openai-python/compare/v1.32.0...v1.32.1)

### Bug Fixes

* remove erroneous thread create argument ([#1476](https://github.com/openai/openai-python/issues/1476)) ([43175c4](https://github.com/openai/openai-python/commit/43175c40e607d626a77a151691778c35a0e60eec))

## 1.32.0 (2024-06-06)

Full Changelog: [v1.31.2...v1.32.0](https://github.com/openai/openai-python/compare/v1.31.2...v1.32.0)

### Features

* **api:** updates ([#1474](https://github.com/openai/openai-python/issues/1474)) ([87ddff0](https://github.com/openai/openai-python/commit/87ddff0e6e64650691a8e32f7477b7a00e06ed23))

## 1.31.2 (2024-06-06)

Full Changelog: [v1.31.1...v1.31.2](https://github.com/openai/openai-python/compare/v1.31.1...v1.31.2)

### Chores

* **internal:** minor refactor of tests ([#1471](https://github.com/openai/openai-python/issues/1471)) ([b7f2298](https://github.com/openai/openai-python/commit/b7f229866f249d16e995db361b923bb4c0b7f1d4))

## 1.31.1 (2024-06-05)

Full Changelog: [v1.31.0...v1.31.1](https://github.com/openai/openai-python/compare/v1.31.0...v1.31.1)

### Chores

* **internal:** minor change to tests ([#1466](https://github.com/openai/openai-python/issues/1466)) ([cb33e71](https://github.com/openai/openai-python/commit/cb33e7152f25fb16cf4c39a6e4714169c62d6af8))

## 1.31.0 (2024-06-03)

Full Changelog: [v1.30.5...v1.31.0](https://github.com/openai/openai-python/compare/v1.30.5...v1.31.0)

### Features

* **api:** updates ([#1461](https://github.com/openai/openai-python/issues/1461)) ([0d7cc5e](https://github.com/openai/openai-python/commit/0d7cc5e48c565fe10ee6e8ca4d050175eb543bcb))


### Chores

* fix lint ([1886dd4](https://github.com/openai/openai-python/commit/1886dd4c98d7a7b3a679bff739cb38badf5ae96c))

## 1.30.5 (2024-05-29)

Full Changelog: [v1.30.4...v1.30.5](https://github.com/openai/openai-python/compare/v1.30.4...v1.30.5)

### Chores

* **internal:** fix lint issue ([35a1e80](https://github.com/openai/openai-python/commit/35a1e806891c34d5cc13ac8341751e5b15b52319))

## 1.30.4 (2024-05-28)

Full Changelog: [v1.30.3...v1.30.4](https://github.com/openai/openai-python/compare/v1.30.3...v1.30.4)

### Chores

* add missing __all__ definitions ([7fba60f](https://github.com/openai/openai-python/commit/7fba60f2e8adc26e83080aaf3e436eb9891e1253))
* **internal:** fix lint issue ([f423cd0](https://github.com/openai/openai-python/commit/f423cd05d33b3e734eda7c0c008faac14ae96bb7))

## 1.30.3 (2024-05-24)

Full Changelog: [v1.30.2...v1.30.3](https://github.com/openai/openai-python/compare/v1.30.2...v1.30.3)

### Chores

* **ci:** update rye install location ([#1440](https://github.com/openai/openai-python/issues/1440)) ([8a0e5bf](https://github.com/openai/openai-python/commit/8a0e5bf4c03d9c714799fad43be68ac9c2b1f37a))
* **internal:** bump pyright ([#1442](https://github.com/openai/openai-python/issues/1442)) ([64a151e](https://github.com/openai/openai-python/commit/64a151eae705d55484f870df461434c0a6961e2b))
* **internal:** fix lint issue ([#1444](https://github.com/openai/openai-python/issues/1444)) ([b0eb458](https://github.com/openai/openai-python/commit/b0eb4582e050b0a25af3d80d2cb584bfc7cd11ab))


### Documentation

* **contributing:** update references to rye-up.com ([dcc34a2](https://github.com/openai/openai-python/commit/dcc34a26d1a6a0debf440724fad658c77547048c))

## 1.30.2 (2024-05-23)

Full Changelog: [v1.30.1...v1.30.2](https://github.com/openai/openai-python/compare/v1.30.1...v1.30.2)

### Chores

* **ci:** update rye install location ([#1436](https://github.com/openai/openai-python/issues/1436)) ([f7cc4e7](https://github.com/openai/openai-python/commit/f7cc4e7d5d0964a4a5d53e602379770c2576e1aa))

## 1.30.1 (2024-05-14)

Full Changelog: [v1.30.0...v1.30.1](https://github.com/openai/openai-python/compare/v1.30.0...v1.30.1)

### Chores

* **internal:** add slightly better logging to scripts ([#1422](https://github.com/openai/openai-python/issues/1422)) ([43dffab](https://github.com/openai/openai-python/commit/43dffabb3bed4edf8a6e523cbb289f733a5f9b24))

## 1.30.0 (2024-05-14)

Full Changelog: [v1.29.0...v1.30.0](https://github.com/openai/openai-python/compare/v1.29.0...v1.30.0)

### Features

* **api:** add incomplete state ([#1420](https://github.com/openai/openai-python/issues/1420)) ([6484984](https://github.com/openai/openai-python/commit/648498412d1c7740e6b67ed4d0a55b89ff29d3b1))

## 1.29.0 (2024-05-13)

Full Changelog: [v1.28.2...v1.29.0](https://github.com/openai/openai-python/compare/v1.28.2...v1.29.0)

### Features

* **api:** add gpt-4o model ([#1417](https://github.com/openai/openai-python/issues/1417)) ([4f09f8c](https://github.com/openai/openai-python/commit/4f09f8c6cc4450f5e61f158f1bd54c513063a1a8))

## 1.28.2 (2024-05-13)

Full Changelog: [v1.28.1...v1.28.2](https://github.com/openai/openai-python/compare/v1.28.1...v1.28.2)

### Bug Fixes

* **client:** accidental blocking sleep in async code ([#1415](https://github.com/openai/openai-python/issues/1415)) ([0ac6ecb](https://github.com/openai/openai-python/commit/0ac6ecb8d4e52f895bc3ae1f589f22ddaaef6204))


### Chores

* **internal:** bump pydantic dependency ([#1413](https://github.com/openai/openai-python/issues/1413)) ([ed73d1d](https://github.com/openai/openai-python/commit/ed73d1db540714e29a1ba30e3aa6429aae8b1dd8))

## 1.28.1 (2024-05-11)

Full Changelog: [v1.28.0...v1.28.1](https://github.com/openai/openai-python/compare/v1.28.0...v1.28.1)

### Chores

* **docs:** add SECURITY.md ([#1408](https://github.com/openai/openai-python/issues/1408)) ([119970a](https://github.com/openai/openai-python/commit/119970a31b67e88c623d50855290ccf3847c10eb))

## 1.28.0 (2024-05-09)

Full Changelog: [v1.27.0...v1.28.0](https://github.com/openai/openai-python/compare/v1.27.0...v1.28.0)

### Features

* **api:** add message image content ([#1405](https://github.com/openai/openai-python/issues/1405)) ([a115de6](https://github.com/openai/openai-python/commit/a115de60ce1ca503a7659bb9a19c18699d4d9bcb))

## 1.27.0 (2024-05-08)

Full Changelog: [v1.26.0...v1.27.0](https://github.com/openai/openai-python/compare/v1.26.0...v1.27.0)

### Features

* **api:** adding file purposes ([#1401](https://github.com/openai/openai-python/issues/1401)) ([2e9d0bd](https://github.com/openai/openai-python/commit/2e9d0bd0e4bf677ed9b21c6448e804313e026441))

## 1.26.0 (2024-05-06)

Full Changelog: [v1.25.2...v1.26.0](https://github.com/openai/openai-python/compare/v1.25.2...v1.26.0)

### Features

* **api:** add usage metadata when streaming ([#1395](https://github.com/openai/openai-python/issues/1395)) ([3cb064b](https://github.com/openai/openai-python/commit/3cb064b10d661dbcc74b6bc1ed7d8e635ab2876a))

## 1.25.2 (2024-05-05)

Full Changelog: [v1.25.1...v1.25.2](https://github.com/openai/openai-python/compare/v1.25.1...v1.25.2)

### Documentation

* **readme:** fix misleading timeout example value ([#1393](https://github.com/openai/openai-python/issues/1393)) ([3eba8e7](https://github.com/openai/openai-python/commit/3eba8e7573ec1bf4231a304c8eabc8a8d077f46d))

## 1.25.1 (2024-05-02)

Full Changelog: [v1.25.0...v1.25.1](https://github.com/openai/openai-python/compare/v1.25.0...v1.25.1)

### Chores

* **internal:** bump prism version ([#1390](https://github.com/openai/openai-python/issues/1390)) ([a5830fc](https://github.com/openai/openai-python/commit/a5830fc1c5ffd21e2010490905084ad5614212a3))

## 1.25.0 (2024-05-01)

Full Changelog: [v1.24.1...v1.25.0](https://github.com/openai/openai-python/compare/v1.24.1...v1.25.0)

### Features

* **api:** delete messages ([#1388](https://github.com/openai/openai-python/issues/1388)) ([d0597cd](https://github.com/openai/openai-python/commit/d0597cdc1813cddffacbaa50565e86d2420d1873))

## 1.24.1 (2024-04-30)

Full Changelog: [v1.24.0...v1.24.1](https://github.com/openai/openai-python/compare/v1.24.0...v1.24.1)

### Chores

* **internal:** add link to openapi spec ([#1385](https://github.com/openai/openai-python/issues/1385)) ([b315d04](https://github.com/openai/openai-python/commit/b315d04e9624ec3a841d7c51813bb553640c23ce))

## 1.24.0 (2024-04-29)

Full Changelog: [v1.23.6...v1.24.0](https://github.com/openai/openai-python/compare/v1.23.6...v1.24.0)

### Features

* **api:** add required tool_choice ([#1382](https://github.com/openai/openai-python/issues/1382)) ([c558f65](https://github.com/openai/openai-python/commit/c558f651df39f61425cd4109318f78ed94cbf163))


### Chores

* **client:** log response headers in debug mode ([#1383](https://github.com/openai/openai-python/issues/1383)) ([f31a426](https://github.com/openai/openai-python/commit/f31a4261adc4ebd92582cee264e41eb6a6dafc57))
* **internal:** minor reformatting ([#1377](https://github.com/openai/openai-python/issues/1377)) ([7003dbb](https://github.com/openai/openai-python/commit/7003dbb863b6e16381070b8b86ac24aa070a3799))
* **internal:** reformat imports ([#1375](https://github.com/openai/openai-python/issues/1375)) ([2ad0c3b](https://github.com/openai/openai-python/commit/2ad0c3b8e0b746ed20db3c84a9c6a369aa10bf5d))

## 1.23.6 (2024-04-25)

Full Changelog: [v1.23.5...v1.23.6](https://github.com/openai/openai-python/compare/v1.23.5...v1.23.6)

### Chores

* **internal:** update test helper function ([#1371](https://github.com/openai/openai-python/issues/1371)) ([6607c4a](https://github.com/openai/openai-python/commit/6607c4a491fd1912f9222d6fe464ccef6e865eac))

## 1.23.5 (2024-04-24)

Full Changelog: [v1.23.4...v1.23.5](https://github.com/openai/openai-python/compare/v1.23.4...v1.23.5)

### Chores

* **internal:** use actions/checkout@v4 for codeflow ([#1368](https://github.com/openai/openai-python/issues/1368)) ([d1edf8b](https://github.com/openai/openai-python/commit/d1edf8beb806ebaefdcc2cb6e39f99e1811a2668))

## 1.23.4 (2024-04-24)

Full Changelog: [v1.23.3...v1.23.4](https://github.com/openai/openai-python/compare/v1.23.3...v1.23.4)

### Bug Fixes

* **api:** change timestamps to unix integers ([#1367](https://github.com/openai/openai-python/issues/1367)) ([fbc0e15](https://github.com/openai/openai-python/commit/fbc0e15f422971bd15499d4ea5f42a1c885c7004))
* **docs:** doc improvements ([#1364](https://github.com/openai/openai-python/issues/1364)) ([8c3a005](https://github.com/openai/openai-python/commit/8c3a005247ea045b9a95e7459eba2a90067daf71))


### Chores

* **tests:** rename test file ([#1366](https://github.com/openai/openai-python/issues/1366)) ([4204e63](https://github.com/openai/openai-python/commit/4204e63e27584c68ad27825261225603d7a87008))

## 1.23.3 (2024-04-23)

Full Changelog: [v1.23.2...v1.23.3](https://github.com/openai/openai-python/compare/v1.23.2...v1.23.3)

### Chores

* **internal:** restructure imports ([#1359](https://github.com/openai/openai-python/issues/1359)) ([4e5eb37](https://github.com/openai/openai-python/commit/4e5eb374ea0545a6117db657bb05f6417bc62d18))

## 1.23.2 (2024-04-19)

Full Changelog: [v1.23.1...v1.23.2](https://github.com/openai/openai-python/compare/v1.23.1...v1.23.2)

### Bug Fixes

* **api:** correct types for message attachment tools ([#1348](https://github.com/openai/openai-python/issues/1348)) ([78a6261](https://github.com/openai/openai-python/commit/78a6261eaad7839284903287d4f647d9cb4ced0b))

## 1.23.1 (2024-04-18)

Full Changelog: [v1.23.0...v1.23.1](https://github.com/openai/openai-python/compare/v1.23.0...v1.23.1)

### Bug Fixes

* **api:** correct types for attachments ([#1342](https://github.com/openai/openai-python/issues/1342)) ([542d30c](https://github.com/openai/openai-python/commit/542d30c6dad4e139bf3eb443936d42b7b42dad54))

## 1.23.0 (2024-04-18)

Full Changelog: [v1.22.0...v1.23.0](https://github.com/openai/openai-python/compare/v1.22.0...v1.23.0)

### Features

* **api:** add request id property to response classes ([#1341](https://github.com/openai/openai-python/issues/1341)) ([444d680](https://github.com/openai/openai-python/commit/444d680cbb3745adbc27788213ae3312567136a8))


### Documentation

* **helpers:** fix example snippets ([#1339](https://github.com/openai/openai-python/issues/1339)) ([8929088](https://github.com/openai/openai-python/commit/8929088b206a04b4c5b85fb69b0b983fb56f9b03))

## 1.22.0 (2024-04-18)

Full Changelog: [v1.21.2...v1.22.0](https://github.com/openai/openai-python/compare/v1.21.2...v1.22.0)

### Features

* **api:** batch list endpoint ([#1338](https://github.com/openai/openai-python/issues/1338)) ([a776f38](https://github.com/openai/openai-python/commit/a776f387e3159f9a8f4dcaa7d0d3b78c2a884f91))


### Chores

* **internal:** ban usage of lru_cache ([#1331](https://github.com/openai/openai-python/issues/1331)) ([8f9223b](https://github.com/openai/openai-python/commit/8f9223bfe13200c685fc97c25ada3015a69c6df7))
* **internal:** bump pyright to 1.1.359 ([#1337](https://github.com/openai/openai-python/issues/1337)) ([feec0dd](https://github.com/openai/openai-python/commit/feec0dd1dd243941a279c3224c5ca1d727d76676))

## 1.21.2 (2024-04-17)

Full Changelog: [v1.21.1...v1.21.2](https://github.com/openai/openai-python/compare/v1.21.1...v1.21.2)

### Chores

* **internal:** add lru_cache helper function ([#1329](https://github.com/openai/openai-python/issues/1329)) ([cbeebfc](https://github.com/openai/openai-python/commit/cbeebfcca8bf1a3feb4462a79e10099bda5bed84))

## 1.21.1 (2024-04-17)

Full Changelog: [v1.21.0...v1.21.1](https://github.com/openai/openai-python/compare/v1.21.0...v1.21.1)

### Chores

* **api:** docs and response_format response property ([#1327](https://github.com/openai/openai-python/issues/1327)) ([7a6d142](https://github.com/openai/openai-python/commit/7a6d142f013994c4eb9a4f55888464c885f8baf0))

## 1.21.0 (2024-04-17)

Full Changelog: [v1.20.0...v1.21.0](https://github.com/openai/openai-python/compare/v1.20.0...v1.21.0)

### Features

* **api:** add vector stores ([#1325](https://github.com/openai/openai-python/issues/1325)) ([038a3c5](https://github.com/openai/openai-python/commit/038a3c50db7b6a88f54ff1cd1ff6cbaef2caf87f))

## 1.20.0 (2024-04-16)

Full Changelog: [v1.19.0...v1.20.0](https://github.com/openai/openai-python/compare/v1.19.0...v1.20.0)

### Features

* **client:** add header OpenAI-Project ([#1320](https://github.com/openai/openai-python/issues/1320)) ([0c489f1](https://github.com/openai/openai-python/commit/0c489f16a7d9e5ac753da87273b223893edefa69))
* extract chat models to a named enum ([#1322](https://github.com/openai/openai-python/issues/1322)) ([1ccd9b6](https://github.com/openai/openai-python/commit/1ccd9b67322736a4714e58c953d59585322c527d))

## 1.19.0 (2024-04-15)

Full Changelog: [v1.18.0...v1.19.0](https://github.com/openai/openai-python/compare/v1.18.0...v1.19.0)

### Features

* **errors:** add request_id property ([#1317](https://github.com/openai/openai-python/issues/1317)) ([f9eb77d](https://github.com/openai/openai-python/commit/f9eb77dca422b9456f4e3b31c7474046235eec1d))

## 1.18.0 (2024-04-15)

Full Changelog: [v1.17.1...v1.18.0](https://github.com/openai/openai-python/compare/v1.17.1...v1.18.0)

### Features

* **api:** add batch API ([#1316](https://github.com/openai/openai-python/issues/1316)) ([3e6f19e](https://github.com/openai/openai-python/commit/3e6f19e6e7489bf1c94944a5f8f9b1d4535cdc43))
* **api:** updates ([#1314](https://github.com/openai/openai-python/issues/1314)) ([8281dc9](https://github.com/openai/openai-python/commit/8281dc956178f5de345645660081f7d0c15a57a6))

## 1.17.1 (2024-04-12)

Full Changelog: [v1.17.0...v1.17.1](https://github.com/openai/openai-python/compare/v1.17.0...v1.17.1)

### Chores

* fix typo ([#1304](https://github.com/openai/openai-python/issues/1304)) ([1129082](https://github.com/openai/openai-python/commit/1129082955f98d76c0927781ef9e7d0beeda2ec4))
* **internal:** formatting ([#1311](https://github.com/openai/openai-python/issues/1311)) ([8fd411b](https://github.com/openai/openai-python/commit/8fd411b48b6b1eafaab2dac26201525c1ee0b942))

## 1.17.0 (2024-04-10)

Full Changelog: [v1.16.2...v1.17.0](https://github.com/openai/openai-python/compare/v1.16.2...v1.17.0)

### Features

* **api:** add additional messages when creating thread run ([#1298](https://github.com/openai/openai-python/issues/1298)) ([70eb081](https://github.com/openai/openai-python/commit/70eb081804b14cc8c151ebd85458545a50a074fd))
* **client:** add DefaultHttpxClient and DefaultAsyncHttpxClient ([#1302](https://github.com/openai/openai-python/issues/1302)) ([69cdfc3](https://github.com/openai/openai-python/commit/69cdfc319fff7ebf28cdd13cc6c1761b7d97811d))
* **models:** add to_dict & to_json helper methods ([#1305](https://github.com/openai/openai-python/issues/1305)) ([40a881d](https://github.com/openai/openai-python/commit/40a881d10442af8b445ce030f8ab338710e1c4c8))

## 1.16.2 (2024-04-04)

Full Changelog: [v1.16.1...v1.16.2](https://github.com/openai/openai-python/compare/v1.16.1...v1.16.2)

### Bug Fixes

* **client:** correct logic for line decoding in streaming ([#1293](https://github.com/openai/openai-python/issues/1293)) ([687caef](https://github.com/openai/openai-python/commit/687caefa4acf615bf404f16817bfd9a6f285ee5c))

## 1.16.1 (2024-04-02)

Full Changelog: [v1.16.0...v1.16.1](https://github.com/openai/openai-python/compare/v1.16.0...v1.16.1)

### Chores

* **internal:** defer model build for import latency ([#1291](https://github.com/openai/openai-python/issues/1291)) ([bc6866e](https://github.com/openai/openai-python/commit/bc6866eb2335d01532190d0906cad7bf9af28621))

## 1.16.0 (2024-04-01)

Full Changelog: [v1.15.0...v1.16.0](https://github.com/openai/openai-python/compare/v1.15.0...v1.16.0)

### Features

* **api:** add support for filtering messages by run_id ([#1288](https://github.com/openai/openai-python/issues/1288)) ([58d6b77](https://github.com/openai/openai-python/commit/58d6b773218ef1dd8dc6208124a16078e4ac11c1))
* **api:** run polling helpers ([#1289](https://github.com/openai/openai-python/issues/1289)) ([6b427f3](https://github.com/openai/openai-python/commit/6b427f38610847bce3ce5334177f07917bd7c187))


### Chores

* **client:** validate that max_retries is not None ([#1286](https://github.com/openai/openai-python/issues/1286)) ([aa5920a](https://github.com/openai/openai-python/commit/aa5920af6131c49a44352524154ee4a1684e76b2))


### Refactors

* rename createAndStream to stream ([6b427f3](https://github.com/openai/openai-python/commit/6b427f38610847bce3ce5334177f07917bd7c187))

## 1.15.0 (2024-03-31)

Full Changelog: [v1.14.3...v1.15.0](https://github.com/openai/openai-python/compare/v1.14.3...v1.15.0)

### Features

* **api:** adding temperature parameter ([#1282](https://github.com/openai/openai-python/issues/1282)) ([0e68fd3](https://github.com/openai/openai-python/commit/0e68fd3690155785d1fb0ee9a8604f51e6701b1d))
* **client:** increase default HTTP max_connections to 1000 and max_keepalive_connections to 100 ([#1281](https://github.com/openai/openai-python/issues/1281)) ([340d139](https://github.com/openai/openai-python/commit/340d1391e3071a265ed12c0a8d70d4d73a860bd8))
* **package:** export default constants ([#1275](https://github.com/openai/openai-python/issues/1275)) ([fdc126e](https://github.com/openai/openai-python/commit/fdc126e428320f1bed5eabd3eed229f08ab9effa))


### Bug Fixes

* **project:** use absolute github links on PyPi ([#1280](https://github.com/openai/openai-python/issues/1280)) ([94cd528](https://github.com/openai/openai-python/commit/94cd52837650e5b7e115119d69e6b1c7ba1f6bf1))


### Chores

* **internal:** bump dependencies ([#1273](https://github.com/openai/openai-python/issues/1273)) ([18dcd65](https://github.com/openai/openai-python/commit/18dcd654d9f54628b5fe21a499d1fef500e15f7f))


### Documentation

* **readme:** change undocumented params wording ([#1284](https://github.com/openai/openai-python/issues/1284)) ([7498ef1](https://github.com/openai/openai-python/commit/7498ef1e9568200086ba3efb99ea100feb05e3f0))

## 1.14.3 (2024-03-25)

Full Changelog: [v1.14.2...v1.14.3](https://github.com/openai/openai-python/compare/v1.14.2...v1.14.3)

### Bug Fixes

* revert regression with 3.7 support ([#1269](https://github.com/openai/openai-python/issues/1269)) ([37aed56](https://github.com/openai/openai-python/commit/37aed564143dc7281f1eaa6ab64ec5ca334cf25e))


### Chores

* **internal:** construct error properties instead of using the raw response ([#1257](https://github.com/openai/openai-python/issues/1257)) ([11dce5c](https://github.com/openai/openai-python/commit/11dce5c66395722b245f5d5461ce379ca7b939e4))
* **internal:** formatting change ([#1258](https://github.com/openai/openai-python/issues/1258)) ([b907dd7](https://github.com/openai/openai-python/commit/b907dd7dcae895e4209559da061d0991a8d640a6))
* **internal:** loosen input type for util function ([#1250](https://github.com/openai/openai-python/issues/1250)) ([fc8b4c3](https://github.com/openai/openai-python/commit/fc8b4c37dc91dfcc0535c19236092992171784a0))


### Documentation

* **contributing:** fix typo ([#1264](https://github.com/openai/openai-python/issues/1264)) ([835cb9b](https://github.com/openai/openai-python/commit/835cb9b2f92e2aa3329545b4677865dcd4fd00f0))
* **readme:** consistent use of sentence case in headings ([#1255](https://github.com/openai/openai-python/issues/1255)) ([519f371](https://github.com/openai/openai-python/commit/519f371af779b5fa353292ff5a2d3332afe0987e))
* **readme:** document how to make undocumented requests ([#1256](https://github.com/openai/openai-python/issues/1256)) ([5887858](https://github.com/openai/openai-python/commit/5887858a7b649dfde5b733ef01e5cffcf953b2a7))

## 1.14.2 (2024-03-19)

Full Changelog: [v1.14.1...v1.14.2](https://github.com/openai/openai-python/compare/v1.14.1...v1.14.2)

### Performance Improvements

* cache TypeAdapters ([#1114](https://github.com/openai/openai-python/issues/1114)) ([41b6fee](https://github.com/openai/openai-python/commit/41b6feec70d3f203e36ba9a92205389bafce930c))
* cache TypeAdapters ([#1243](https://github.com/openai/openai-python/issues/1243)) ([2005076](https://github.com/openai/openai-python/commit/2005076f500bef6e0a6cc8f935b9cc9fef65ab5b))


### Chores

* **internal:** update generated pragma comment ([#1247](https://github.com/openai/openai-python/issues/1247)) ([3eeb9b3](https://github.com/openai/openai-python/commit/3eeb9b3a71e01c2593be443a97a353371466d01a))


### Documentation

* assistant improvements ([#1249](https://github.com/openai/openai-python/issues/1249)) ([e7a3176](https://github.com/openai/openai-python/commit/e7a3176b7606822bd5ad8f7fece87de6aad1e5b6))
* fix typo in CONTRIBUTING.md ([#1245](https://github.com/openai/openai-python/issues/1245)) ([adef57a](https://github.com/openai/openai-python/commit/adef57ae5c71734873ba49bccd92fa7f28068d28))

## 1.14.1 (2024-03-15)

Full Changelog: [v1.14.0...v1.14.1](https://github.com/openai/openai-python/compare/v1.14.0...v1.14.1)

### Documentation

* **readme:** assistant streaming ([#1238](https://github.com/openai/openai-python/issues/1238)) ([0fc30a2](https://github.com/openai/openai-python/commit/0fc30a23030b4ff60f27cd2f472517926ed0f300))

## 1.14.0 (2024-03-13)

Full Changelog: [v1.13.4...v1.14.0](https://github.com/openai/openai-python/compare/v1.13.4...v1.14.0)

### Features

* **assistants:** add support for streaming ([#1233](https://github.com/openai/openai-python/issues/1233)) ([17635dc](https://github.com/openai/openai-python/commit/17635dccbeddf153f8201dbca18b44e16a1799b2))

## 1.13.4 (2024-03-13)

Full Changelog: [v1.13.3...v1.13.4](https://github.com/openai/openai-python/compare/v1.13.3...v1.13.4)

### Bug Fixes

* **streaming:** improve error messages ([#1218](https://github.com/openai/openai-python/issues/1218)) ([4f5ff29](https://github.com/openai/openai-python/commit/4f5ff298601b5a8bfbf0a9d0c0d1329d1502a205))


### Chores

* **api:** update docs ([#1212](https://github.com/openai/openai-python/issues/1212)) ([71236e0](https://github.com/openai/openai-python/commit/71236e0de4012a249af4c1ffd95973a8ba4fa61f))
* **client:** improve error message for invalid http_client argument ([#1216](https://github.com/openai/openai-python/issues/1216)) ([d0c928a](https://github.com/openai/openai-python/commit/d0c928abbd99020fe828350f3adfd10c638a2eed))
* **docs:** mention install from git repo ([#1203](https://github.com/openai/openai-python/issues/1203)) ([3ab6f44](https://github.com/openai/openai-python/commit/3ab6f447ffd8d2394e58416e401e545a99ec85af))
* export NOT_GIVEN sentinel value ([#1223](https://github.com/openai/openai-python/issues/1223)) ([8a4f76f](https://github.com/openai/openai-python/commit/8a4f76f992c66f20cd6aa070c8dc4839e4cf9f3c))
* **internal:** add core support for deserializing into number response ([#1219](https://github.com/openai/openai-python/issues/1219)) ([004bc92](https://github.com/openai/openai-python/commit/004bc924ea579852b9266ca11aea93463cf75104))
* **internal:** bump pyright ([#1221](https://github.com/openai/openai-python/issues/1221)) ([3c2e815](https://github.com/openai/openai-python/commit/3c2e815311ace4ff81ccd446b23ff50a4e099485))
* **internal:** improve deserialisation of discriminated unions ([#1227](https://github.com/openai/openai-python/issues/1227)) ([4767259](https://github.com/openai/openai-python/commit/4767259d25ac135550b37b15e4c0497e5ff0330d))
* **internal:** minor core client restructuring ([#1199](https://github.com/openai/openai-python/issues/1199)) ([4314cdc](https://github.com/openai/openai-python/commit/4314cdcd522537e6cbbd87206d5bb236f672ce05))
* **internal:** split up transforms into sync / async ([#1210](https://github.com/openai/openai-python/issues/1210)) ([7853a83](https://github.com/openai/openai-python/commit/7853a8358864957cc183581bdf7c03810a7b2756))
* **internal:** support more input types ([#1211](https://github.com/openai/openai-python/issues/1211)) ([d0e4baa](https://github.com/openai/openai-python/commit/d0e4baa40d32c2da0ce5ceef8e0c7193b98f2b5a))
* **internal:** support parsing Annotated types ([#1222](https://github.com/openai/openai-python/issues/1222)) ([8598f81](https://github.com/openai/openai-python/commit/8598f81841eeab0ab00eb21fdec7e8756ffde909))
* **types:** include discriminators in unions ([#1228](https://github.com/openai/openai-python/issues/1228)) ([3ba0dcc](https://github.com/openai/openai-python/commit/3ba0dcc19a2af0ef869c77da2805278f71ee96c2))


### Documentation

* **contributing:** improve wording ([#1201](https://github.com/openai/openai-python/issues/1201)) ([95a1e0e](https://github.com/openai/openai-python/commit/95a1e0ea8e5446c413606847ebf9e35afbc62bf9))

## 1.13.3 (2024-02-28)

Full Changelog: [v1.13.2...v1.13.3](https://github.com/openai/openai-python/compare/v1.13.2...v1.13.3)

### Features

* **api:** add wav and pcm to response_format ([#1189](https://github.com/openai/openai-python/issues/1189)) ([dbd20fc](https://github.com/openai/openai-python/commit/dbd20fc42e93358261f71b9aa0e5f955053c3825))


### Chores

* **client:** use anyio.sleep instead of asyncio.sleep ([#1198](https://github.com/openai/openai-python/issues/1198)) ([b6d025b](https://github.com/openai/openai-python/commit/b6d025b54f091e79f5d4a0a8923f29574fd66027))
* **internal:** bump pyright ([#1193](https://github.com/openai/openai-python/issues/1193)) ([9202e04](https://github.com/openai/openai-python/commit/9202e04d07a7c47232f39196346c734869b8f55a))
* **types:** extract run status to a named type ([#1178](https://github.com/openai/openai-python/issues/1178)) ([249ecbd](https://github.com/openai/openai-python/commit/249ecbdeb6566a385ec46dfd5000b4eaa03965f0))


### Documentation

* add note in azure_deployment docstring ([#1188](https://github.com/openai/openai-python/issues/1188)) ([96fa995](https://github.com/openai/openai-python/commit/96fa99572dd76ee708f2bae04d11b659cdd698b2))
* **examples:** add pyaudio streaming example ([#1194](https://github.com/openai/openai-python/issues/1194)) ([3683c5e](https://github.com/openai/openai-python/commit/3683c5e3c7f07e4b789a0c4cc417b2c59539cae2))

## 1.13.2 (2024-02-20)

Full Changelog: [v1.13.1...v1.13.2](https://github.com/openai/openai-python/compare/v1.13.1...v1.13.2)

### Bug Fixes

* **ci:** revert "move github release logic to github app" ([#1170](https://github.com/openai/openai-python/issues/1170)) ([f1adc2e](https://github.com/openai/openai-python/commit/f1adc2e6f2f29acb4404e84137a9d3109714c585))

## 1.13.1 (2024-02-20)

Full Changelog: [v1.13.0...v1.13.1](https://github.com/openai/openai-python/compare/v1.13.0...v1.13.1)

### Chores

* **internal:** bump rye to v0.24.0 ([#1168](https://github.com/openai/openai-python/issues/1168)) ([84c4256](https://github.com/openai/openai-python/commit/84c4256316f2a79068ecadb852e5e69b6b104a1f))

## 1.13.0 (2024-02-19)

Full Changelog: [v1.12.0...v1.13.0](https://github.com/openai/openai-python/compare/v1.12.0...v1.13.0)

### Features

* **api:** updates ([#1146](https://github.com/openai/openai-python/issues/1146)) ([79b7675](https://github.com/openai/openai-python/commit/79b7675e51fb7d269a6ea281a568bc7812ba2ace))


### Bug Fixes

* **api:** remove non-GA instance_id param ([#1164](https://github.com/openai/openai-python/issues/1164)) ([1abe139](https://github.com/openai/openai-python/commit/1abe139b1a5f5cc41263738fc12856056dce5697))


### Chores

* **ci:** move github release logic to github app ([#1155](https://github.com/openai/openai-python/issues/1155)) ([67cfac2](https://github.com/openai/openai-python/commit/67cfac2564dfb718da0465e34b90ac6928fa962a))
* **client:** use correct accept headers for binary data ([#1161](https://github.com/openai/openai-python/issues/1161)) ([e536437](https://github.com/openai/openai-python/commit/e536437ae0b2cb0ddf2d74618722005d37403f32))
* **internal:** refactor release environment script ([#1158](https://github.com/openai/openai-python/issues/1158)) ([7fe8ec3](https://github.com/openai/openai-python/commit/7fe8ec3bf04ecf85e3bd5adf0d9992c051f87b81))

## 1.12.0 (2024-02-08)

Full Changelog: [v1.11.1...v1.12.0](https://github.com/openai/openai-python/compare/v1.11.1...v1.12.0)

### Features

* **api:** add `timestamp_granularities`, add `gpt-3.5-turbo-0125` model ([#1125](https://github.com/openai/openai-python/issues/1125)) ([1ecf8f6](https://github.com/openai/openai-python/commit/1ecf8f6b12323ed09fb6a2815c85b9533ee52a50))
* **cli/images:** add support for `--model` arg ([#1132](https://github.com/openai/openai-python/issues/1132)) ([0d53866](https://github.com/openai/openai-python/commit/0d5386615cda7cd50d5db90de2119b84dba29519))


### Bug Fixes

* remove double brackets from timestamp_granularities param ([#1140](https://github.com/openai/openai-python/issues/1140)) ([3db0222](https://github.com/openai/openai-python/commit/3db022216a81fa86470b53ec1246669bc7b17897))
* **types:** loosen most List params types to Iterable ([#1129](https://github.com/openai/openai-python/issues/1129)) ([bdb31a3](https://github.com/openai/openai-python/commit/bdb31a3b1db6ede4e02b3c951c4fd23f70260038))


### Chores

* **internal:** add lint command ([#1128](https://github.com/openai/openai-python/issues/1128)) ([4c021c0](https://github.com/openai/openai-python/commit/4c021c0ab0151c2ec092d860c9b60e22e658cd03))
* **internal:** support serialising iterable types ([#1127](https://github.com/openai/openai-python/issues/1127)) ([98d4e59](https://github.com/openai/openai-python/commit/98d4e59afcf2d65d4e660d91eb9462240ef5cd63))


### Documentation

* add CONTRIBUTING.md ([#1138](https://github.com/openai/openai-python/issues/1138)) ([79c8f0e](https://github.com/openai/openai-python/commit/79c8f0e8bf5470e2e31e781e8d279331e89ddfbe))

## 1.11.1 (2024-02-04)

Full Changelog: [v1.11.0...v1.11.1](https://github.com/openai/openai-python/compare/v1.11.0...v1.11.1)

### Bug Fixes

* prevent crash when platform.architecture() is not allowed ([#1120](https://github.com/openai/openai-python/issues/1120)) ([9490554](https://github.com/openai/openai-python/commit/949055488488e93597cbc6c2cdd81f14f203e53b))

## 1.11.0 (2024-02-03)

Full Changelog: [v1.10.0...v1.11.0](https://github.com/openai/openai-python/compare/v1.10.0...v1.11.0)

### Features

* **client:** support parsing custom response types ([#1111](https://github.com/openai/openai-python/issues/1111)) ([da00fc3](https://github.com/openai/openai-python/commit/da00fc3f8e0ff13c6c3ca970e4bb86846304bd06))


### Chores

* **interal:** make link to api.md relative ([#1117](https://github.com/openai/openai-python/issues/1117)) ([4a10879](https://github.com/openai/openai-python/commit/4a108797e46293357601ce933e21b557a5dc6954))
* **internal:** cast type in mocked test ([#1112](https://github.com/openai/openai-python/issues/1112)) ([99b21e1](https://github.com/openai/openai-python/commit/99b21e1fc681eb10e01d479cc043ad3c89272b1c))
* **internal:** enable ruff type checking misuse lint rule ([#1106](https://github.com/openai/openai-python/issues/1106)) ([fa63e60](https://github.com/openai/openai-python/commit/fa63e605c82ec78f4fc27469c434b421a08fb909))
* **internal:** support multipart data with overlapping keys ([#1104](https://github.com/openai/openai-python/issues/1104)) ([455bc9f](https://github.com/openai/openai-python/commit/455bc9f1fd018a32cd604eb4b400e05aa8d71822))
* **internal:** support pre-release versioning ([#1113](https://github.com/openai/openai-python/issues/1113)) ([dea5b08](https://github.com/openai/openai-python/commit/dea5b08c28d47b331fd44f6920cf9fe322b68e51))

## 1.10.0 (2024-01-25)

Full Changelog: [v1.9.0...v1.10.0](https://github.com/openai/openai-python/compare/v1.9.0...v1.10.0)

### Features

* **api:** add text embeddings dimensions param ([#1103](https://github.com/openai/openai-python/issues/1103)) ([94abfa0](https://github.com/openai/openai-python/commit/94abfa0f988c199ea95a9c870c4ae9808823186d))
* **azure:** proactively add audio/speech to deployment endpoints ([#1099](https://github.com/openai/openai-python/issues/1099)) ([fdf8742](https://github.com/openai/openai-python/commit/fdf87429b45ceb47ae6fd068ab70cc07bcb8da44))
* **client:** enable follow redirects by default ([#1100](https://github.com/openai/openai-python/issues/1100)) ([d325b7c](https://github.com/openai/openai-python/commit/d325b7ca594c2abaada536249b5633b106943333))


### Chores

* **internal:** add internal helpers ([#1092](https://github.com/openai/openai-python/issues/1092)) ([629bde5](https://github.com/openai/openai-python/commit/629bde5800d84735e22d924db23109a141f48644))


### Refactors

* remove unnecessary builtin import ([#1094](https://github.com/openai/openai-python/issues/1094)) ([504b7d4](https://github.com/openai/openai-python/commit/504b7d4a0b4715bd49a1a076a8d4868e51fb3351))

## 1.9.0 (2024-01-21)

Full Changelog: [v1.8.0...v1.9.0](https://github.com/openai/openai-python/compare/v1.8.0...v1.9.0)

### Features

* **api:** add usage to runs and run steps ([#1090](https://github.com/openai/openai-python/issues/1090)) ([6c116df](https://github.com/openai/openai-python/commit/6c116dfbb0065d15050450df70e0e98fc8c80349))


### Chores

* **internal:** fix typing util function ([#1083](https://github.com/openai/openai-python/issues/1083)) ([3e60db6](https://github.com/openai/openai-python/commit/3e60db69f5d9187c4eb38451967259f534a36a82))
* **internal:** remove redundant client test ([#1085](https://github.com/openai/openai-python/issues/1085)) ([947974f](https://github.com/openai/openai-python/commit/947974f5af726e252b7b12c863743e50f41b79d3))
* **internal:** share client instances between all tests ([#1088](https://github.com/openai/openai-python/issues/1088)) ([05cd753](https://github.com/openai/openai-python/commit/05cd7531d40774d05c52b14dee54d137ac1452a3))
* **internal:** speculative retry-after-ms support ([#1086](https://github.com/openai/openai-python/issues/1086)) ([36a7576](https://github.com/openai/openai-python/commit/36a7576a913be8509a3cf6f262543083b485136e))
* lazy load raw resource class properties ([#1087](https://github.com/openai/openai-python/issues/1087)) ([d307127](https://github.com/openai/openai-python/commit/d30712744be07461e86763705c03c3495eadfc35))

## 1.8.0 (2024-01-16)

Full Changelog: [v1.7.2...v1.8.0](https://github.com/openai/openai-python/compare/v1.7.2...v1.8.0)

### Features

* **client:** add support for streaming raw responses ([#1072](https://github.com/openai/openai-python/issues/1072)) ([0e93c3b](https://github.com/openai/openai-python/commit/0e93c3b5bc9cfa041e91962fd82c0d9358125024))


### Bug Fixes

* **client:** ensure path params are non-empty ([#1075](https://github.com/openai/openai-python/issues/1075)) ([9a25149](https://github.com/openai/openai-python/commit/9a2514997c2ddccbec9df8be3773e83271f1dab8))
* **proxy:** prevent recursion errors when debugging pycharm ([#1076](https://github.com/openai/openai-python/issues/1076)) ([3d78798](https://github.com/openai/openai-python/commit/3d787987cf7625b5b502cb0b63a37d55956eaf1d))


### Chores

* add write_to_file binary helper method ([#1077](https://github.com/openai/openai-python/issues/1077)) ([c622c6a](https://github.com/openai/openai-python/commit/c622c6aaf2ae7dc62bd6cdfc053204c5dc3293ac))

## 1.7.2 (2024-01-12)

Full Changelog: [v1.7.1...v1.7.2](https://github.com/openai/openai-python/compare/v1.7.1...v1.7.2)

### Documentation

* **readme:** improve api reference ([#1065](https://github.com/openai/openai-python/issues/1065)) ([745b9e0](https://github.com/openai/openai-python/commit/745b9e08ae0abb8bf4cd87ed40fa450d9ad81ede))


### Refactors

* **api:** remove deprecated endpoints ([#1067](https://github.com/openai/openai-python/issues/1067)) ([199ddcd](https://github.com/openai/openai-python/commit/199ddcdca00c136e4e0c3ff16521eff22acf2a1a))

## 1.7.1 (2024-01-10)

Full Changelog: [v1.7.0...v1.7.1](https://github.com/openai/openai-python/compare/v1.7.0...v1.7.1)

### Chores

* **client:** improve debug logging for failed requests ([#1060](https://github.com/openai/openai-python/issues/1060)) ([cf9a651](https://github.com/openai/openai-python/commit/cf9a6517b4aa0f24bcbe143c54ea908d43dfda92))

## 1.7.0 (2024-01-08)

Full Changelog: [v1.6.1...v1.7.0](https://github.com/openai/openai-python/compare/v1.6.1...v1.7.0)

### Features

* add `None` default value to nullable response properties ([#1043](https://github.com/openai/openai-python/issues/1043)) ([d94b4d3](https://github.com/openai/openai-python/commit/d94b4d3d0adcd1a49a1c25cc9730cef013a3e9c9))


### Bug Fixes

* **client:** correctly use custom http client auth ([#1028](https://github.com/openai/openai-python/issues/1028)) ([3d7d93e](https://github.com/openai/openai-python/commit/3d7d93e951eb7fe09cd9d94d10a62a020398c7f9))


### Chores

* add .keep files for examples and custom code directories ([#1057](https://github.com/openai/openai-python/issues/1057)) ([7524097](https://github.com/openai/openai-python/commit/7524097a47af0fdc8b560186ef3b111b59430741))
* **internal:** bump license ([#1037](https://github.com/openai/openai-python/issues/1037)) ([d828527](https://github.com/openai/openai-python/commit/d828527540ebd97679075f48744818f06311b0cb))
* **internal:** loosen type var restrictions ([#1049](https://github.com/openai/openai-python/issues/1049)) ([e00876b](https://github.com/openai/openai-python/commit/e00876b20b93038450eb317899d8775c7661b8eb))
* **internal:** replace isort with ruff ([#1042](https://github.com/openai/openai-python/issues/1042)) ([f1fbc9c](https://github.com/openai/openai-python/commit/f1fbc9c0d62e7d89ab32c8bdfa39cd94b560690b))
* **internal:** update formatting ([#1041](https://github.com/openai/openai-python/issues/1041)) ([2e9ecee](https://github.com/openai/openai-python/commit/2e9ecee9bdfa8ec33b1b1527d5187483b700fad3))
* **src:** fix typos ([#988](https://github.com/openai/openai-python/issues/988)) ([6a8b806](https://github.com/openai/openai-python/commit/6a8b80624636f9a0e5ada151b2509710a6f74808))
* use property declarations for resource members ([#1047](https://github.com/openai/openai-python/issues/1047)) ([131f6bc](https://github.com/openai/openai-python/commit/131f6bc6b0ccf79119096057079e10906b3d4678))


### Documentation

* fix docstring typos ([#1022](https://github.com/openai/openai-python/issues/1022)) ([ad3fd2c](https://github.com/openai/openai-python/commit/ad3fd2cd19bf91f94473e368554dff39a8f9ad16))
* improve audio example to show how to stream to a file ([#1017](https://github.com/openai/openai-python/issues/1017)) ([d45ed7f](https://github.com/openai/openai-python/commit/d45ed7f0513b167555ae875f1877fa205c5790d2))

## 1.6.1 (2023-12-22)

Full Changelog: [v1.6.0...v1.6.1](https://github.com/openai/openai-python/compare/v1.6.0...v1.6.1)

### Chores

* **internal:** add bin script ([#1001](https://github.com/openai/openai-python/issues/1001)) ([99ffbda](https://github.com/openai/openai-python/commit/99ffbda279bf4c159511fb96b1d5bb688af25437))
* **internal:** use ruff instead of black for formatting ([#1008](https://github.com/openai/openai-python/issues/1008)) ([ceaf9a0](https://github.com/openai/openai-python/commit/ceaf9a06fbd1a846756bb72cce50a69c8cc20bd3))

## 1.6.0 (2023-12-19)

Full Changelog: [v1.5.0...v1.6.0](https://github.com/openai/openai-python/compare/v1.5.0...v1.6.0)

### Features

* **api:** add additional instructions for runs ([#995](https://github.com/openai/openai-python/issues/995)) ([7bf9b75](https://github.com/openai/openai-python/commit/7bf9b75067905449e83e828c12eb384022cff6ca))


### Chores

* **cli:** fix typo in completions ([#985](https://github.com/openai/openai-python/issues/985)) ([d1e9e8f](https://github.com/openai/openai-python/commit/d1e9e8f24df366bb7b796c55a98247c025d229f5))
* **cli:** fix typo in completions ([#986](https://github.com/openai/openai-python/issues/986)) ([626bc34](https://github.com/openai/openai-python/commit/626bc34d82a7057bac99f8b556f9e5f60c261ee7))
* **internal:** fix binary response tests ([#983](https://github.com/openai/openai-python/issues/983)) ([cfb7e30](https://github.com/openai/openai-python/commit/cfb7e308393f2e912e959dd10d68096dd5b3ab9c))
* **internal:** fix typos ([#993](https://github.com/openai/openai-python/issues/993)) ([3b338a4](https://github.com/openai/openai-python/commit/3b338a401b206618774291ff8137deb0cc5f6b4c))
* **internal:** minor utils restructuring ([#992](https://github.com/openai/openai-python/issues/992)) ([5ba576a](https://github.com/openai/openai-python/commit/5ba576ae38d2c4c4d32a21933e0d68e0bc2f0d49))
* **package:** bump minimum typing-extensions to 4.7 ([#994](https://github.com/openai/openai-python/issues/994)) ([0c2da84](https://github.com/openai/openai-python/commit/0c2da84badf416f8b2213983f68bd2b6f9e52f2b))
* **streaming:** update constructor to use direct client names ([#991](https://github.com/openai/openai-python/issues/991)) ([6c3427d](https://github.com/openai/openai-python/commit/6c3427dac8c414658516aeb4caf5d5fd8b11097b))


### Documentation

* upgrade models in examples to latest version ([#989](https://github.com/openai/openai-python/issues/989)) ([cedd574](https://github.com/openai/openai-python/commit/cedd574e5611f3e71e92b523a72ba87bcfe546f1))

## 1.5.0 (2023-12-17)

Full Changelog: [v1.4.0...v1.5.0](https://github.com/openai/openai-python/compare/v1.4.0...v1.5.0)

### Features

* **api:** add token logprobs to chat completions ([#980](https://github.com/openai/openai-python/issues/980)) ([f50e962](https://github.com/openai/openai-python/commit/f50e962b930bd682a4299143b2995337e8571273))


### Chores

* **ci:** run release workflow once per day ([#978](https://github.com/openai/openai-python/issues/978)) ([215476a](https://github.com/openai/openai-python/commit/215476a0b99e0c92ab3e44ddd25de207af32d160))

## 1.4.0 (2023-12-15)

Full Changelog: [v1.3.9...v1.4.0](https://github.com/openai/openai-python/compare/v1.3.9...v1.4.0)

### Features

* **api:** add optional `name` argument + improve docs ([#972](https://github.com/openai/openai-python/issues/972)) ([7972010](https://github.com/openai/openai-python/commit/7972010615820099f662c02821cfbd59e7d6ea44))

## 1.3.9 (2023-12-12)

Full Changelog: [v1.3.8...v1.3.9](https://github.com/openai/openai-python/compare/v1.3.8...v1.3.9)

### Documentation

* improve README timeout comment ([#964](https://github.com/openai/openai-python/issues/964)) ([3c3ed5e](https://github.com/openai/openai-python/commit/3c3ed5edd938a9333e8d2fa47cb4b44178eef89a))
* small Improvement in the async chat response code ([#959](https://github.com/openai/openai-python/issues/959)) ([fb9d0a3](https://github.com/openai/openai-python/commit/fb9d0a358fa232043d9d5c149b6a888d50127c7b))
* small streaming readme improvements ([#962](https://github.com/openai/openai-python/issues/962)) ([f3be2e5](https://github.com/openai/openai-python/commit/f3be2e5cc24988471e6cedb3e34bdfd3123edc63))


### Refactors

* **client:** simplify cleanup ([#966](https://github.com/openai/openai-python/issues/966)) ([5c138f4](https://github.com/openai/openai-python/commit/5c138f4a7947e5b4aae8779fae78ca51269b355a))
* simplify internal error handling ([#968](https://github.com/openai/openai-python/issues/968)) ([d187f6b](https://github.com/openai/openai-python/commit/d187f6b6e4e646cca39c6ca35c618aa5c1bfbd61))

## 1.3.8 (2023-12-08)

Full Changelog: [v1.3.7...v1.3.8](https://github.com/openai/openai-python/compare/v1.3.7...v1.3.8)

### Bug Fixes

* avoid leaking memory when Client.with_options is used ([#956](https://github.com/openai/openai-python/issues/956)) ([e37ecca](https://github.com/openai/openai-python/commit/e37ecca04040ce946822a7e40f5604532a59ee85))
* **errors:** properly assign APIError.body ([#949](https://github.com/openai/openai-python/issues/949)) ([c70e194](https://github.com/openai/openai-python/commit/c70e194f0a253409ec851607ae5219e3b5a8c442))
* **pagination:** use correct type hint for .object ([#943](https://github.com/openai/openai-python/issues/943)) ([23fe7ee](https://github.com/openai/openai-python/commit/23fe7ee48a71539b0d1e95ceff349264aae4090e))


### Chores

* **internal:** enable more lint rules ([#945](https://github.com/openai/openai-python/issues/945)) ([2c8add6](https://github.com/openai/openai-python/commit/2c8add64a261dea731bd162bb0cca222518d5440))
* **internal:** reformat imports ([#939](https://github.com/openai/openai-python/issues/939)) ([ec65124](https://github.com/openai/openai-python/commit/ec651249de2f4e4cf959f816e1b52f03d3b1017a))
* **internal:** reformat imports ([#944](https://github.com/openai/openai-python/issues/944)) ([5290639](https://github.com/openai/openai-python/commit/52906391c9b6633656ec7934e6bbac553ec667cd))
* **internal:** update formatting ([#941](https://github.com/openai/openai-python/issues/941)) ([8e5a156](https://github.com/openai/openai-python/commit/8e5a156d555fe68731ba0604a7455cc03cb451ce))
* **package:** lift anyio v4 restriction ([#927](https://github.com/openai/openai-python/issues/927)) ([be0438a](https://github.com/openai/openai-python/commit/be0438a2e399bb0e0a94907229d02fc61ab479c0))


### Documentation

* fix typo in example ([#950](https://github.com/openai/openai-python/issues/950)) ([54f0ce0](https://github.com/openai/openai-python/commit/54f0ce0000abe32e97ae400f2975c028b8a84273))

## 1.3.7 (2023-12-01)

Full Changelog: [v1.3.6...v1.3.7](https://github.com/openai/openai-python/compare/v1.3.6...v1.3.7)

### Bug Fixes

* **client:** correct base_url setter implementation ([#919](https://github.com/openai/openai-python/issues/919)) ([135d9cf](https://github.com/openai/openai-python/commit/135d9cf2820f1524764bf536a9322830bdcd5875))
* **client:** don't cause crashes when inspecting the module ([#897](https://github.com/openai/openai-python/issues/897)) ([db029a5](https://github.com/openai/openai-python/commit/db029a596c90b1af4ef0bfb1cdf31f54b2f5755d))
* **client:** ensure retried requests are closed ([#902](https://github.com/openai/openai-python/issues/902)) ([e025e6b](https://github.com/openai/openai-python/commit/e025e6bee44ea145d948869ef0c79bac0c376b9f))


### Chores

* **internal:** add tests for proxy change ([#899](https://github.com/openai/openai-python/issues/899)) ([71a13d0](https://github.com/openai/openai-python/commit/71a13d0c70d105b2b97720c72a1003b942cda2ae))
* **internal:** remove unused type var ([#915](https://github.com/openai/openai-python/issues/915)) ([4233bcd](https://github.com/openai/openai-python/commit/4233bcdae5f467f10454fcc008a6e728fa846830))
* **internal:** replace string concatenation with f-strings ([#908](https://github.com/openai/openai-python/issues/908)) ([663a8f6](https://github.com/openai/openai-python/commit/663a8f6dead5aa523d1e8779e75af1dabb1690c4))
* **internal:** replace string concatenation with f-strings ([#909](https://github.com/openai/openai-python/issues/909)) ([caab767](https://github.com/openai/openai-python/commit/caab767156375114078cf8d85031863361326b5f))


### Documentation

* fix typo in readme ([#904](https://github.com/openai/openai-python/issues/904)) ([472cd44](https://github.com/openai/openai-python/commit/472cd44e45a45b0b4f12583a5402e8aeb121d7a2))
* **readme:** update example snippets ([#907](https://github.com/openai/openai-python/issues/907)) ([bbb648e](https://github.com/openai/openai-python/commit/bbb648ef81eb11f81b457e2cbf33a832f4d29a76))

## 1.3.6 (2023-11-28)

Full Changelog: [v1.3.5...v1.3.6](https://github.com/openai/openai-python/compare/v1.3.5...v1.3.6)

### Bug Fixes

* **client:** add support for streaming binary responses ([#866](https://github.com/openai/openai-python/issues/866)) ([2470d25](https://github.com/openai/openai-python/commit/2470d251b751e92e8950bc9e3026965e9925ac1c))


### Chores

* **deps:** bump mypy to v1.7.1 ([#891](https://github.com/openai/openai-python/issues/891)) ([11fcb2a](https://github.com/openai/openai-python/commit/11fcb2a3cd4205b307c13c65ad47d9e315b0084d))
* **internal:** send more detailed x-stainless headers ([#877](https://github.com/openai/openai-python/issues/877)) ([69e0549](https://github.com/openai/openai-python/commit/69e054947d587ff2548b101ece690d21d3c38f74))
* revert binary streaming change ([#875](https://github.com/openai/openai-python/issues/875)) ([0a06d6a](https://github.com/openai/openai-python/commit/0a06d6a078c5ee898dae75bab4988e1a1936bfbf))


### Documentation

* **readme:** minor updates ([#894](https://github.com/openai/openai-python/issues/894)) ([5458457](https://github.com/openai/openai-python/commit/54584572df4c2a086172d812c6acb84e3405328b))
* **readme:** update examples ([#893](https://github.com/openai/openai-python/issues/893)) ([124da87](https://github.com/openai/openai-python/commit/124da8720c44d40c083d29179f46a265761c1f4f))
* update readme code snippet ([#890](https://github.com/openai/openai-python/issues/890)) ([c522f21](https://github.com/openai/openai-python/commit/c522f21e2a685454185d57e462e74a28499460f9))

## 1.3.5 (2023-11-21)

Full Changelog: [v1.3.4...v1.3.5](https://github.com/openai/openai-python/compare/v1.3.4...v1.3.5)

### Bug Fixes

* **azure:** ensure custom options can be passed to copy ([#858](https://github.com/openai/openai-python/issues/858)) ([05ca0d6](https://github.com/openai/openai-python/commit/05ca0d68e84d40f975614d27cb52c0f382104377))


### Chores

* **package:** add license classifier ([#826](https://github.com/openai/openai-python/issues/826)) ([bec004d](https://github.com/openai/openai-python/commit/bec004d030b277e05bdd51f66fae1e881291c30b))
* **package:** add license classifier metadata ([#860](https://github.com/openai/openai-python/issues/860)) ([80dffb1](https://github.com/openai/openai-python/commit/80dffb17ff0a10b0b9ea704c4247521e48b68408))

## 1.3.4 (2023-11-21)

Full Changelog: [v1.3.3...v1.3.4](https://github.com/openai/openai-python/compare/v1.3.3...v1.3.4)

### Bug Fixes

* **client:** attempt to parse unknown json content types ([#854](https://github.com/openai/openai-python/issues/854)) ([ba50466](https://github.com/openai/openai-python/commit/ba5046611029a67714d5120b9cc6a3c7fecce10c))


### Chores

* **examples:** fix static types in assistants example ([#852](https://github.com/openai/openai-python/issues/852)) ([5b47b2c](https://github.com/openai/openai-python/commit/5b47b2c542b9b4fb143af121022e2d5ad0890ef4))

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
