# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

# Changelog

## [2.0.2](https://github.com/laurentmor/CGI-tools/compare/v2.0.1...v2.0.2) (2026-04-27)


### 🧹 Maintenance

* add SPDX-License to test runner ([5b6eddf](https://github.com/laurentmor/CGI-tools/commit/5b6eddfd9fedae410e09b9ed15d812d7cd2e7603))


### ♻️ Refactoring

* arranged module strucure so obeccts and types can be resolved by tests - all passing ([49c127b](https://github.com/laurentmor/CGI-tools/commit/49c127b5145323272cdb049a64d83cb724d4e434))
* **HISTGEN:** clean src layout, 192-test suite, 96% coverage, README ([f3b6afc](https://github.com/laurentmor/CGI-tools/commit/f3b6afc3f5c67e441a0a0c2d8f39c89a9148d0d0))

## [2.0.1](https://github.com/laurentmor/CGI-tools/compare/v2.0.0...v2.0.1) (2026-04-25)


### 🧹 Maintenance

* cleanup ([8924e47](https://github.com/laurentmor/CGI-tools/commit/8924e47e11ad6c4358e3d534bfbf7423b9e11309))
* cleanup ([31b1b4d](https://github.com/laurentmor/CGI-tools/commit/31b1b4d61b26cfc5fd538f52ba45a5e160e00baf))

## [2.0.0](https://github.com/laurentmor/CGI-tools/compare/v1.0.0...v2.0.0) (2026-04-22)


### ⚠ BREAKING CHANGES

* **cli:** sound paths are no longer filesystem-based, so direct file access to sounds is not supported.  Use the xml-extractor CLI or import the package and use the play_sound function to access sounds.

### 🚀 Features

* add header job ([fdf16ac](https://github.com/laurentmor/CGI-tools/commit/fdf16acf46bfd617499cc0ec8fd233b6d02a368f))
* add lint job ([a026da9](https://github.com/laurentmor/CGI-tools/commit/a026da9bbd8a806eee687c599d6f112a6f290589))
* **cli:** add global CLI entrypoint and bundle sound assets ([824876c](https://github.com/laurentmor/CGI-tools/commit/824876c5348b05dc1a0a1cf4d388ce394307c2c0))
* new cool stuff ([8bf12c2](https://github.com/laurentmor/CGI-tools/commit/8bf12c2f975f03db9efb24dd5e7a1b89dad4394d))
* script is now  installable ([ae61c5c](https://github.com/laurentmor/CGI-tools/commit/ae61c5c5805b556a8ad5062c2c73fa207367dd3c))
* script is now  installable ([ebd2ad9](https://github.com/laurentmor/CGI-tools/commit/ebd2ad9b9bcbbcb75a65f573677d7abe0fc17500))


### 🐛 Bug Fixes

* CI base dir ([236fd59](https://github.com/laurentmor/CGI-tools/commit/236fd595b0927a30024f74b0d994159acc8aa85c))
* CI base dir ([1d40427](https://github.com/laurentmor/CGI-tools/commit/1d404273ad6be26260c62d94003b3e27958b6216))
* clean workfow ([455f69d](https://github.com/laurentmor/CGI-tools/commit/455f69de2a3cb5655d11187dca0de7a844ecbad6))
* correcting tests so they pass ([789e6ea](https://github.com/laurentmor/CGI-tools/commit/789e6eab37b2567db48b2a38d30ff68b6040e171))
* Corrections to Release confg ([3907389](https://github.com/laurentmor/CGI-tools/commit/3907389e5c5aa59f369f3961c0392dbd8f61d993))
* Node version freeze ([ab5109a](https://github.com/laurentmor/CGI-tools/commit/ab5109aa1badb0503243e37efc5ee14f49945275))
* Node version freeze ([b67926f](https://github.com/laurentmor/CGI-tools/commit/b67926f12989b29ea080a510aaf656b66bb5f29e))
* proect file ([6ed0e86](https://github.com/laurentmor/CGI-tools/commit/6ed0e868b95ee5a0275d71197248969f569b0625))
* Renamed Release confg ([14a9bb2](https://github.com/laurentmor/CGI-tools/commit/14a9bb2b25ef0faeca1068cd12b78b2ff4de7cc7))
* Renamed Release confg   (added .) ([ca09147](https://github.com/laurentmor/CGI-tools/commit/ca0914764a27128232d3b72130102bb9ce84efbc))
* streamline version look up ([6325be2](https://github.com/laurentmor/CGI-tools/commit/6325be2a432b544712b61d9d45c6a93f868f0245))
* streamline version look up ([700246b](https://github.com/laurentmor/CGI-tools/commit/700246b7bc4bfab0ff13a2be6f75c962b440058b))
* streamline version look up to match current ([c4579d1](https://github.com/laurentmor/CGI-tools/commit/c4579d17be77ef97ee717929e3f39567e59117d0))
* Switch to Release please ([2579b85](https://github.com/laurentmor/CGI-tools/commit/2579b857f77d1fcbe0dc4cbf261a1cb707f11da4))
* test ([190c655](https://github.com/laurentmor/CGI-tools/commit/190c65522e53e8bb9c3f7a2f744b751c9a50b335))
* Test ([b3fd241](https://github.com/laurentmor/CGI-tools/commit/b3fd241b92fada3d7fe899886d37a3672b1e9353))
* test-1 ([81248c4](https://github.com/laurentmor/CGI-tools/commit/81248c46b6c2bd39cf4ae960f4340acd06bd9f41))
* Update version handling and command-line version output ([10432a8](https://github.com/laurentmor/CGI-tools/commit/10432a8d0642db43e320751add5880f8fe3ea628))
* workflow ([179d126](https://github.com/laurentmor/CGI-tools/commit/179d12642dd20e8d1ea3ab85b5dffeb0e89d09c9))
* workflow ([ff1d4b0](https://github.com/laurentmor/CGI-tools/commit/ff1d4b0645450910d2a2995e744622d4c6e87e05))
* workflow ([d82e7d7](https://github.com/laurentmor/CGI-tools/commit/d82e7d7785bcbaa9e6f3aac85db09525dd8bb8dc))
* workflow correction ([e8e25c4](https://github.com/laurentmor/CGI-tools/commit/e8e25c4a5f3eefc7894bf49e1efbc865340dc273))
* workflow correction based on Claude ([c09f6ea](https://github.com/laurentmor/CGI-tools/commit/c09f6ea7bb4ebae350c80ff57498dfb78041d2f5))


### 🧹 Maintenance

* add SPDX license headers ([43d4932](https://github.com/laurentmor/CGI-tools/commit/43d4932fb76404bbe21e73094f97329b644fe291))
* add SPDX license headers ([d62da4c](https://github.com/laurentmor/CGI-tools/commit/d62da4c2c302d3b9281878c8fe7d704651eecb1f))
* auto-fix lint (ruff) ([39b330d](https://github.com/laurentmor/CGI-tools/commit/39b330df33c7f42000eb51277817bcce95b786a7))
* auto-fix lint (ruff) ([d2c218c](https://github.com/laurentmor/CGI-tools/commit/d2c218cd98743ed7ba9cb353e838b84b8daabcd8))
* clean tests ([637fe29](https://github.com/laurentmor/CGI-tools/commit/637fe293765cdb2d9165ac9cbec0e385bf174286))
* configure ruff ([d747f4c](https://github.com/laurentmor/CGI-tools/commit/d747f4c6fe68638eb962dfd8fbf96f38c0804fa3))
* configure ruff version ([527eb7f](https://github.com/laurentmor/CGI-tools/commit/527eb7f5591109e4dbeb165be205f2af681f0117))
* **deps:** bump lxml from 5.3.1 to 6.1.0 in /XMLExtractor ([25d0334](https://github.com/laurentmor/CGI-tools/commit/25d0334258971e58752473a3a63f74005f774e2e))
* **deps:** bump lxml from 5.3.1 to 6.1.0 in /XMLExtractor ([9ed346e](https://github.com/laurentmor/CGI-tools/commit/9ed346e22a0532c81cb494a59d0d520c2c44576a))
* fix workflow name so bage will work ([546069a](https://github.com/laurentmor/CGI-tools/commit/546069a66d2547b119dcbe5b99f23fe058f4c9c8))
* lint ([f2abf11](https://github.com/laurentmor/CGI-tools/commit/f2abf112c3cfae0b5dd52152e57a5b117be31c0c))
* **main:** release 0.1.0 ([00ad162](https://github.com/laurentmor/CGI-tools/commit/00ad162bbce45df54920dbb274bc18d9432cb095))
* **main:** release 0.1.0 ([1328ed3](https://github.com/laurentmor/CGI-tools/commit/1328ed3e493abc4444c9d1b66730af3877d8445f))
* **main:** release 0.1.1 ([23202d9](https://github.com/laurentmor/CGI-tools/commit/23202d96c4733eeb9d1f43769222eeb149d5006c))
* **main:** release 0.1.1 ([640d336](https://github.com/laurentmor/CGI-tools/commit/640d3368f5b46cca41e7980c8e7b270a6e477726))
* **main:** release 0.1.2 ([dc41456](https://github.com/laurentmor/CGI-tools/commit/dc414564db1e4944bc1bf49c76034207e7db6df8))
* **main:** release 0.1.2 ([e7a561e](https://github.com/laurentmor/CGI-tools/commit/e7a561ec91228ced1466099c38316b10e10bc94c))
* **main:** release 0.1.3 ([bd9cfbd](https://github.com/laurentmor/CGI-tools/commit/bd9cfbddf5974a17fa22ed7346b88bda8991dd64))
* **main:** release 0.1.3 ([e71cde0](https://github.com/laurentmor/CGI-tools/commit/e71cde05a5e66d19e729179fdbf25978912c7806))
* **main:** release 0.1.4 ([e0e1faa](https://github.com/laurentmor/CGI-tools/commit/e0e1faa2ce5009d8d61e9bf37be4ee0523f39bb8))
* **main:** release 0.1.4 ([8f40dff](https://github.com/laurentmor/CGI-tools/commit/8f40dffb72989ddda2f1d1384aa32a58546b5931))
* **main:** release 0.2.0 ([be2d959](https://github.com/laurentmor/CGI-tools/commit/be2d95913d4b9e6d581aceabca5999c0672008e0))
* **main:** release 0.2.0 ([7353ab0](https://github.com/laurentmor/CGI-tools/commit/7353ab0f7c93d9b1b612984b97d1f3eecdc9c31d))
* **main:** release 0.3.0 ([50082bd](https://github.com/laurentmor/CGI-tools/commit/50082bdb2813bf584d7f89613f67ab5aefb795a5))
* **main:** release 0.3.0 ([ac3c5c2](https://github.com/laurentmor/CGI-tools/commit/ac3c5c284fb906b70a8b1c50770c926ae70f70df))
* **main:** release 0.3.1 ([0446104](https://github.com/laurentmor/CGI-tools/commit/0446104ce0f99db20e9236f370b8887beb3abfbb))
* **main:** release 0.3.1 ([90da037](https://github.com/laurentmor/CGI-tools/commit/90da03776c2e88d1f926ea856f65f328ca7c13dd))
* **main:** release 0.3.2 ([111049c](https://github.com/laurentmor/CGI-tools/commit/111049c9372aa81bb9df0158332ef5c26bee9f50))
* **main:** release 0.3.2 ([74c35bd](https://github.com/laurentmor/CGI-tools/commit/74c35bd2db7dfc1d733975339e209ba2ca8b16c8))
* **main:** release 0.3.3 ([f780261](https://github.com/laurentmor/CGI-tools/commit/f780261e2667ca80a19bc62d2be8281beb320c09))
* **main:** release 0.4.0 ([07aa494](https://github.com/laurentmor/CGI-tools/commit/07aa494fa8bad5c58ac0b81124d8523b7123e98f))
* **main:** release 0.4.0 ([3fd2589](https://github.com/laurentmor/CGI-tools/commit/3fd25892dc9b78d81a924db106f7349f132173c3))
* **main:** release 0.4.1 ([7a04445](https://github.com/laurentmor/CGI-tools/commit/7a04445bc43cec49214b732a6408419051cc9668))
* **main:** release 0.4.1 ([964ac39](https://github.com/laurentmor/CGI-tools/commit/964ac39cd76e46d23f8908fbe80f80b54d40f924))
* **main:** release 0.4.2 ([6655c8c](https://github.com/laurentmor/CGI-tools/commit/6655c8c1ad29dc71aa2f024b0b13bfa1d8065807))
* **main:** release 0.4.2 ([b218b30](https://github.com/laurentmor/CGI-tools/commit/b218b30b1010d9c52b440f521c504f537a899033))
* **main:** release 1.0.0 ([c3673c1](https://github.com/laurentmor/CGI-tools/commit/c3673c19a92fe7d3e403d6e9bdc7e80b8f47bac8))
* **main:** release 1.0.0 ([d4a5caa](https://github.com/laurentmor/CGI-tools/commit/d4a5caa9444e385abf96a0768ecb054961c8bb3d))
* proper copyright/licensing ([182ac5a](https://github.com/laurentmor/CGI-tools/commit/182ac5ad60f6e0eab973c570d1a0ed1ac0c9f2ce))
* proper workflow name for badge display ([48c830c](https://github.com/laurentmor/CGI-tools/commit/48c830ce4fc67e498c56db3bb823cc7a3c444e41))
* remove unused tool ([7d27540](https://github.com/laurentmor/CGI-tools/commit/7d27540402c2939a767cb85b39d2b3a0125793ab))
* retry ([f102b39](https://github.com/laurentmor/CGI-tools/commit/f102b3953d26df9aacd904e275e5d4feb8ba66f9))
* update checkout version ([fbb416b](https://github.com/laurentmor/CGI-tools/commit/fbb416b3e6af3e897334ad6a60c2b80c972ce48d))


### ♻️ Refactoring

* rename XMLExtractor-1.2 to XMLExtractor ([4a46dfc](https://github.com/laurentmor/CGI-tools/commit/4a46dfc5ce615387095951c7701f7db9981453fd))
* rewritw config and CI ([d1071c3](https://github.com/laurentmor/CGI-tools/commit/d1071c3b202165d0f7089bb1174cbf90d797639a))

## [1.0.0](https://github.com/laurentmor/CGI-tools/compare/v0.4.2...v1.0.0) (2026-04-22)


### ⚠ BREAKING CHANGES

* **cli:** sound paths are no longer filesystem-based, so direct file access to sounds is not supported.  Use the xml-extractor CLI or import the package and use the play_sound function to access sounds.

### 🚀 Features

* **cli:** add global CLI entrypoint and bundle sound assets ([824876c](https://github.com/laurentmor/CGI-tools/commit/824876c5348b05dc1a0a1cf4d388ce394307c2c0))
* script is now  installable ([ae61c5c](https://github.com/laurentmor/CGI-tools/commit/ae61c5c5805b556a8ad5062c2c73fa207367dd3c))
* script is now  installable ([ebd2ad9](https://github.com/laurentmor/CGI-tools/commit/ebd2ad9b9bcbbcb75a65f573677d7abe0fc17500))


### 🐛 Bug Fixes

* proect file ([6ed0e86](https://github.com/laurentmor/CGI-tools/commit/6ed0e868b95ee5a0275d71197248969f569b0625))


### 🧹 Maintenance

* **deps:** bump lxml from 5.3.1 to 6.1.0 in /XMLExtractor ([25d0334](https://github.com/laurentmor/CGI-tools/commit/25d0334258971e58752473a3a63f74005f774e2e))
* lint ([f2abf11](https://github.com/laurentmor/CGI-tools/commit/f2abf112c3cfae0b5dd52152e57a5b117be31c0c))

## [0.4.2](https://github.com/laurentmor/CGI-tools/compare/v0.4.1...v0.4.2) (2026-04-21)


### 🧹 Maintenance

* proper workflow name for badge display ([48c830c](https://github.com/laurentmor/CGI-tools/commit/48c830ce4fc67e498c56db3bb823cc7a3c444e41))

## [0.4.1](https://github.com/laurentmor/CGI-tools/compare/v0.4.0...v0.4.1) (2026-04-21)


### 🐛 Bug Fixes

* CI base dir ([236fd59](https://github.com/laurentmor/CGI-tools/commit/236fd595b0927a30024f74b0d994159acc8aa85c))
* CI base dir ([1d40427](https://github.com/laurentmor/CGI-tools/commit/1d404273ad6be26260c62d94003b3e27958b6216))
* correcting tests so they pass ([789e6ea](https://github.com/laurentmor/CGI-tools/commit/789e6eab37b2567db48b2a38d30ff68b6040e171))
* workflow ([179d126](https://github.com/laurentmor/CGI-tools/commit/179d12642dd20e8d1ea3ab85b5dffeb0e89d09c9))
* workflow ([ff1d4b0](https://github.com/laurentmor/CGI-tools/commit/ff1d4b0645450910d2a2995e744622d4c6e87e05))
* workflow ([d82e7d7](https://github.com/laurentmor/CGI-tools/commit/d82e7d7785bcbaa9e6f3aac85db09525dd8bb8dc))


### 🧹 Maintenance

* clean tests ([637fe29](https://github.com/laurentmor/CGI-tools/commit/637fe293765cdb2d9165ac9cbec0e385bf174286))
* proper copyright/licensing ([182ac5a](https://github.com/laurentmor/CGI-tools/commit/182ac5ad60f6e0eab973c570d1a0ed1ac0c9f2ce))


### ♻️ Refactoring

* rename XMLExtractor-1.2 to XMLExtractor ([4a46dfc](https://github.com/laurentmor/CGI-tools/commit/4a46dfc5ce615387095951c7701f7db9981453fd))
* rewritw config and CI ([d1071c3](https://github.com/laurentmor/CGI-tools/commit/d1071c3b202165d0f7089bb1174cbf90d797639a))

## [0.4.0](https://github.com/laurentmor/CGI-tools/compare/v0.3.3...v0.4.0) (2026-04-19)


### 🚀 Features

* add header job ([fdf16ac](https://github.com/laurentmor/CGI-tools/commit/fdf16acf46bfd617499cc0ec8fd233b6d02a368f))
* add lint job ([a026da9](https://github.com/laurentmor/CGI-tools/commit/a026da9bbd8a806eee687c599d6f112a6f290589))
* new cool stuff ([8bf12c2](https://github.com/laurentmor/CGI-tools/commit/8bf12c2f975f03db9efb24dd5e7a1b89dad4394d))


### 🐛 Bug Fixes

* clean workfow ([455f69d](https://github.com/laurentmor/CGI-tools/commit/455f69de2a3cb5655d11187dca0de7a844ecbad6))
* Corrections to Release confg ([3907389](https://github.com/laurentmor/CGI-tools/commit/3907389e5c5aa59f369f3961c0392dbd8f61d993))
* Node version freeze ([ab5109a](https://github.com/laurentmor/CGI-tools/commit/ab5109aa1badb0503243e37efc5ee14f49945275))
* Node version freeze ([b67926f](https://github.com/laurentmor/CGI-tools/commit/b67926f12989b29ea080a510aaf656b66bb5f29e))
* Renamed Release confg ([14a9bb2](https://github.com/laurentmor/CGI-tools/commit/14a9bb2b25ef0faeca1068cd12b78b2ff4de7cc7))
* Renamed Release confg   (added .) ([ca09147](https://github.com/laurentmor/CGI-tools/commit/ca0914764a27128232d3b72130102bb9ce84efbc))
* stabilize decorator, test infrastructure, and validation error handling ([aa38010](https://github.com/laurentmor/CGI-tools/commit/aa380109ffaf0ea173af59f9168fc4c28f21fba3))
* streamline version look up ([6325be2](https://github.com/laurentmor/CGI-tools/commit/6325be2a432b544712b61d9d45c6a93f868f0245))
* streamline version look up ([700246b](https://github.com/laurentmor/CGI-tools/commit/700246b7bc4bfab0ff13a2be6f75c962b440058b))
* streamline version look up to match current ([c4579d1](https://github.com/laurentmor/CGI-tools/commit/c4579d17be77ef97ee717929e3f39567e59117d0))
* Switch to Release please ([2579b85](https://github.com/laurentmor/CGI-tools/commit/2579b857f77d1fcbe0dc4cbf261a1cb707f11da4))
* test ([190c655](https://github.com/laurentmor/CGI-tools/commit/190c65522e53e8bb9c3f7a2f744b751c9a50b335))
* Test ([b3fd241](https://github.com/laurentmor/CGI-tools/commit/b3fd241b92fada3d7fe899886d37a3672b1e9353))
* test-1 ([81248c4](https://github.com/laurentmor/CGI-tools/commit/81248c46b6c2bd39cf4ae960f4340acd06bd9f41))
* Update version handling and command-line version output ([10432a8](https://github.com/laurentmor/CGI-tools/commit/10432a8d0642db43e320751add5880f8fe3ea628))
* workflow correction ([e8e25c4](https://github.com/laurentmor/CGI-tools/commit/e8e25c4a5f3eefc7894bf49e1efbc865340dc273))
* workflow correction based on Claude ([c09f6ea](https://github.com/laurentmor/CGI-tools/commit/c09f6ea7bb4ebae350c80ff57498dfb78041d2f5))


### 🧹 Maintenance

* add SPDX license headers ([43d4932](https://github.com/laurentmor/CGI-tools/commit/43d4932fb76404bbe21e73094f97329b644fe291))
* add SPDX license headers ([d62da4c](https://github.com/laurentmor/CGI-tools/commit/d62da4c2c302d3b9281878c8fe7d704651eecb1f))
* auto-fix lint (ruff) ([39b330d](https://github.com/laurentmor/CGI-tools/commit/39b330df33c7f42000eb51277817bcce95b786a7))
* auto-fix lint (ruff) ([d2c218c](https://github.com/laurentmor/CGI-tools/commit/d2c218cd98743ed7ba9cb353e838b84b8daabcd8))
* configure ruff ([d747f4c](https://github.com/laurentmor/CGI-tools/commit/d747f4c6fe68638eb962dfd8fbf96f38c0804fa3))
* configure ruff version ([527eb7f](https://github.com/laurentmor/CGI-tools/commit/527eb7f5591109e4dbeb165be205f2af681f0117))
* fix workflow name so bage will work ([546069a](https://github.com/laurentmor/CGI-tools/commit/546069a66d2547b119dcbe5b99f23fe058f4c9c8))
* **main:** release 0.1.0 ([00ad162](https://github.com/laurentmor/CGI-tools/commit/00ad162bbce45df54920dbb274bc18d9432cb095))
* **main:** release 0.1.0 ([1328ed3](https://github.com/laurentmor/CGI-tools/commit/1328ed3e493abc4444c9d1b66730af3877d8445f))
* **main:** release 0.1.1 ([23202d9](https://github.com/laurentmor/CGI-tools/commit/23202d96c4733eeb9d1f43769222eeb149d5006c))
* **main:** release 0.1.1 ([640d336](https://github.com/laurentmor/CGI-tools/commit/640d3368f5b46cca41e7980c8e7b270a6e477726))
* **main:** release 0.1.2 ([dc41456](https://github.com/laurentmor/CGI-tools/commit/dc414564db1e4944bc1bf49c76034207e7db6df8))
* **main:** release 0.1.2 ([e7a561e](https://github.com/laurentmor/CGI-tools/commit/e7a561ec91228ced1466099c38316b10e10bc94c))
* **main:** release 0.1.3 ([bd9cfbd](https://github.com/laurentmor/CGI-tools/commit/bd9cfbddf5974a17fa22ed7346b88bda8991dd64))
* **main:** release 0.1.3 ([e71cde0](https://github.com/laurentmor/CGI-tools/commit/e71cde05a5e66d19e729179fdbf25978912c7806))
* **main:** release 0.1.4 ([e0e1faa](https://github.com/laurentmor/CGI-tools/commit/e0e1faa2ce5009d8d61e9bf37be4ee0523f39bb8))
* **main:** release 0.1.4 ([8f40dff](https://github.com/laurentmor/CGI-tools/commit/8f40dffb72989ddda2f1d1384aa32a58546b5931))
* **main:** release 0.2.0 ([be2d959](https://github.com/laurentmor/CGI-tools/commit/be2d95913d4b9e6d581aceabca5999c0672008e0))
* **main:** release 0.2.0 ([7353ab0](https://github.com/laurentmor/CGI-tools/commit/7353ab0f7c93d9b1b612984b97d1f3eecdc9c31d))
* **main:** release 0.3.0 ([50082bd](https://github.com/laurentmor/CGI-tools/commit/50082bdb2813bf584d7f89613f67ab5aefb795a5))
* **main:** release 0.3.0 ([ac3c5c2](https://github.com/laurentmor/CGI-tools/commit/ac3c5c284fb906b70a8b1c50770c926ae70f70df))
* **main:** release 0.3.1 ([0446104](https://github.com/laurentmor/CGI-tools/commit/0446104ce0f99db20e9236f370b8887beb3abfbb))
* **main:** release 0.3.1 ([90da037](https://github.com/laurentmor/CGI-tools/commit/90da03776c2e88d1f926ea856f65f328ca7c13dd))
* **main:** release 0.3.2 ([111049c](https://github.com/laurentmor/CGI-tools/commit/111049c9372aa81bb9df0158332ef5c26bee9f50))
* **main:** release 0.3.2 ([74c35bd](https://github.com/laurentmor/CGI-tools/commit/74c35bd2db7dfc1d733975339e209ba2ca8b16c8))
* **main:** release 0.3.3 ([f780261](https://github.com/laurentmor/CGI-tools/commit/f780261e2667ca80a19bc62d2be8281beb320c09))
* remove unused tool ([7d27540](https://github.com/laurentmor/CGI-tools/commit/7d27540402c2939a767cb85b39d2b3a0125793ab))
* retry ([f102b39](https://github.com/laurentmor/CGI-tools/commit/f102b3953d26df9aacd904e275e5d4feb8ba66f9))
* update checkout version ([fbb416b](https://github.com/laurentmor/CGI-tools/commit/fbb416b3e6af3e897334ad6a60c2b80c972ce48d))

## [0.3.3](https://github.com/laurentmor/CGI-tools/compare/v0.3.2...v0.3.3) (2026-04-18)


### 🧹 Maintenance

* fix workflow name so bage will work ([546069a](https://github.com/laurentmor/CGI-tools/commit/546069a66d2547b119dcbe5b99f23fe058f4c9c8))

## [0.3.2](https://github.com/laurentmor/CGI-tools/compare/v0.3.1...v0.3.2) (2026-04-18)


### 🐛 Bug Fixes

* streamline version look up ([6325be2](https://github.com/laurentmor/CGI-tools/commit/6325be2a432b544712b61d9d45c6a93f868f0245))
* streamline version look up ([700246b](https://github.com/laurentmor/CGI-tools/commit/700246b7bc4bfab0ff13a2be6f75c962b440058b))
* streamline version look up to match current ([c4579d1](https://github.com/laurentmor/CGI-tools/commit/c4579d17be77ef97ee717929e3f39567e59117d0))
* Update version handling and command-line version output ([10432a8](https://github.com/laurentmor/CGI-tools/commit/10432a8d0642db43e320751add5880f8fe3ea628))


### 🧹 Maintenance

* add SPDX license headers ([43d4932](https://github.com/laurentmor/CGI-tools/commit/43d4932fb76404bbe21e73094f97329b644fe291))
* auto-fix lint (ruff) ([39b330d](https://github.com/laurentmor/CGI-tools/commit/39b330df33c7f42000eb51277817bcce95b786a7))

## [0.3.1](https://github.com/laurentmor/CGI-tools/compare/v0.3.0...v0.3.1) (2026-04-18)


### 🧹 Maintenance

* configure ruff version ([527eb7f](https://github.com/laurentmor/CGI-tools/commit/527eb7f5591109e4dbeb165be205f2af681f0117))

## [0.3.0](https://github.com/laurentmor/CGI-tools/compare/v0.2.0...v0.3.0) (2026-04-18)


### 🚀 Features

* add lint job ([a026da9](https://github.com/laurentmor/CGI-tools/commit/a026da9bbd8a806eee687c599d6f112a6f290589))


### 🧹 Maintenance

* auto-fix lint (ruff) ([d2c218c](https://github.com/laurentmor/CGI-tools/commit/d2c218cd98743ed7ba9cb353e838b84b8daabcd8))
* configure ruff ([d747f4c](https://github.com/laurentmor/CGI-tools/commit/d747f4c6fe68638eb962dfd8fbf96f38c0804fa3))

## [0.2.0](https://github.com/laurentmor/CGI-tools/compare/v0.1.4...v0.2.0) (2026-04-17)


### 🚀 Features

* add header job ([fdf16ac](https://github.com/laurentmor/CGI-tools/commit/fdf16acf46bfd617499cc0ec8fd233b6d02a368f))


### 🧹 Maintenance

* add SPDX license headers ([d62da4c](https://github.com/laurentmor/CGI-tools/commit/d62da4c2c302d3b9281878c8fe7d704651eecb1f))

## [0.1.4](https://github.com/laurentmor/CGI-tools/compare/v0.1.3...v0.1.4) (2026-04-17)


### 🧹 Maintenance

* update checkout version ([fbb416b](https://github.com/laurentmor/CGI-tools/commit/fbb416b3e6af3e897334ad6a60c2b80c972ce48d))

## [0.1.3](https://github.com/laurentmor/CGI-tools/compare/v0.1.2...v0.1.3) (2026-04-17)


### 🐛 Bug Fixes

* Node version freeze ([ab5109a](https://github.com/laurentmor/CGI-tools/commit/ab5109aa1badb0503243e37efc5ee14f49945275))
* Node version freeze ([b67926f](https://github.com/laurentmor/CGI-tools/commit/b67926f12989b29ea080a510aaf656b66bb5f29e))

## [0.1.2](https://github.com/laurentmor/CGI-tools/compare/v0.1.1...v0.1.2) (2026-04-17)


### 🐛 Bug Fixes

* clean workfow ([455f69d](https://github.com/laurentmor/CGI-tools/commit/455f69de2a3cb5655d11187dca0de7a844ecbad6))

## [0.1.1](https://github.com/laurentmor/CGI-tools/compare/v0.1.0...v0.1.1) (2026-04-17)


### 🧹 Maintenance

* remove unused tool ([7d27540](https://github.com/laurentmor/CGI-tools/commit/7d27540402c2939a767cb85b39d2b3a0125793ab))

## 0.1.0 (2026-04-16)


### 🚀 Features

* new cool stuff ([8bf12c2](https://github.com/laurentmor/CGI-tools/commit/8bf12c2f975f03db9efb24dd5e7a1b89dad4394d))


### 🐛 Bug Fixes

* Corrections to Release confg ([3907389](https://github.com/laurentmor/CGI-tools/commit/3907389e5c5aa59f369f3961c0392dbd8f61d993))
* Renamed Release confg ([14a9bb2](https://github.com/laurentmor/CGI-tools/commit/14a9bb2b25ef0faeca1068cd12b78b2ff4de7cc7))
* Renamed Release confg   (added .) ([ca09147](https://github.com/laurentmor/CGI-tools/commit/ca0914764a27128232d3b72130102bb9ce84efbc))
* stabilize decorator, test infrastructure, and validation error handling ([aa38010](https://github.com/laurentmor/CGI-tools/commit/aa380109ffaf0ea173af59f9168fc4c28f21fba3))
* Switch to Release please ([2579b85](https://github.com/laurentmor/CGI-tools/commit/2579b857f77d1fcbe0dc4cbf261a1cb707f11da4))
* test ([190c655](https://github.com/laurentmor/CGI-tools/commit/190c65522e53e8bb9c3f7a2f744b751c9a50b335))
* Test ([b3fd241](https://github.com/laurentmor/CGI-tools/commit/b3fd241b92fada3d7fe899886d37a3672b1e9353))
* test-1 ([81248c4](https://github.com/laurentmor/CGI-tools/commit/81248c46b6c2bd39cf4ae960f4340acd06bd9f41))
* workflow correction ([e8e25c4](https://github.com/laurentmor/CGI-tools/commit/e8e25c4a5f3eefc7894bf49e1efbc865340dc273))
* workflow correction based on Claude ([c09f6ea](https://github.com/laurentmor/CGI-tools/commit/c09f6ea7bb4ebae350c80ff57498dfb78041d2f5))


### 🧹 Maintenance

* retry ([f102b39](https://github.com/laurentmor/CGI-tools/commit/f102b3953d26df9aacd904e275e5d4feb8ba66f9))
