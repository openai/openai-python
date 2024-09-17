# Changelog

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
