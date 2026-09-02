# Changelog

## [2.4.1](https://github.com/roquerodrigo/ha-metro-sp/compare/v2.4.0...v2.4.1) (2026-09-02)


### Documentation

* add GitHub Sponsors button and support section ([d64464f](https://github.com/roquerodrigo/ha-metro-sp/commit/d64464f4b51762bc6743be4a7c1c29efbccad25b))

## [2.4.0](https://github.com/roquerodrigo/ha-metro-sp/compare/v2.3.0...v2.4.0) (2026-08-24)


### Features

* **hacs:** ship the install zip with every release ([e6c8665](https://github.com/roquerodrigo/ha-metro-sp/commit/e6c866528cbb91aa96fd9b99873e92eee4a16f3e))


### Development Dependencies

* **deps-dev:** bump the python-development group across 1 directory with 3 updates ([09830e0](https://github.com/roquerodrigo/ha-metro-sp/commit/09830e02efaa77d092b0aa40a6c33bb6adf5f905))

## [2.3.0](https://github.com/roquerodrigo/ha-metro-sp/compare/v2.2.3...v2.3.0) (2026-08-10)


### Features

* **coordinator:** poll upstream data every minute ([1dce613](https://github.com/roquerodrigo/ha-metro-sp/commit/1dce6132a88b287429ccc962de9ddf90494aca1f))


### Documentation

* normalize the README header layout ([10c3436](https://github.com/roquerodrigo/ha-metro-sp/commit/10c3436f9943cce1f7716fd7373a7b016466264b))

## [2.2.3](https://github.com/roquerodrigo/ha-metro-sp/compare/v2.2.2...v2.2.3) (2026-08-07)


### Bug Fixes

* render the untranslatable user-facing strings in pt-BR ([972c233](https://github.com/roquerodrigo/ha-metro-sp/commit/972c2339b1eb394ee1a1183776e12d893fab9f89))
* **sensor:** track upstream line list changes safely ([c4aa6b9](https://github.com/roquerodrigo/ha-metro-sp/commit/c4aa6b96455ee594ad267cfbee9e116e7b28159d))


### Code Refactoring

* anglicize code-level strings and drop the unused repairs scaffold ([062fcc3](https://github.com/roquerodrigo/ha-metro-sp/commit/062fcc358d785a8acd9dee70d0121c74a92f25e0))


### Dependencies

* bump Home Assistant to 2026.8.0 ([5ddf077](https://github.com/roquerodrigo/ha-metro-sp/commit/5ddf077fa78314b34be9a9fd8be3644962e81688))


### Documentation

* describe the code as it actually is ([f6c3690](https://github.com/roquerodrigo/ha-metro-sp/commit/f6c3690bad672ddce7bb4db8f162a8a1614208fe))


### Continuous Integration

* run checks on pull requests targeting any branch ([51b2fcb](https://github.com/roquerodrigo/ha-metro-sp/commit/51b2fcb9cc0a345f927b5545bb2a9d84b00cd9ab))
* run code scanning on pull requests targeting any branch ([1e79495](https://github.com/roquerodrigo/ha-metro-sp/commit/1e794952efc10a9fff92e297e09cbdc059e79f11))


### Miscellaneous Chores

* repair dev tooling drift ([259e56a](https://github.com/roquerodrigo/ha-metro-sp/commit/259e56a61d8c35f4ad9331fda1ad19d5c3797020))

## [2.2.2](https://github.com/roquerodrigo/ha-metro-sp/compare/v2.2.1...v2.2.2) (2026-08-05)


### Bug Fixes

* register the bundled card as a Lovelace dashboard resource ([f16e82c](https://github.com/roquerodrigo/ha-metro-sp/commit/f16e82c8328ec458e1f9e0cafed47daadd627398))


### Development Dependencies

* **deps-dev:** bump pre-commit ([2704b52](https://github.com/roquerodrigo/ha-metro-sp/commit/2704b527a7f8f09cc8bc7b7a4e333b4aeeaa8af3))
* **deps-dev:** bump ruff ([a918d24](https://github.com/roquerodrigo/ha-metro-sp/commit/a918d24c0316e9f737c2c1800f8e1a03a1ad958f))
* **deps-dev:** bump ruff in the python-development group ([0b2225f](https://github.com/roquerodrigo/ha-metro-sp/commit/0b2225f7827e0a68c7b2a3e5970ec4e95ce9db02))


### Documentation

* update CLAUDE.md ([2515d6a](https://github.com/roquerodrigo/ha-metro-sp/commit/2515d6aca33fc451f3f597f4247119666bc4887a))


### Continuous Integration

* assign open issues and pull requests to the repository owner ([513608f](https://github.com/roquerodrigo/ha-metro-sp/commit/513608fa97599d684a19f268149b5cc0ac5476f5))
* call the shared auto-assign workflow instead of duplicating it ([210789d](https://github.com/roquerodrigo/ha-metro-sp/commit/210789dbb545edf8918260db4dfe1973e343003b))
* drop the auto-assign job now handled by its own workflow ([ae6f942](https://github.com/roquerodrigo/ha-metro-sp/commit/ae6f942f3d865b63d19a76cf942e07e64e77dc89))
* drop the blank line left by the removed job ([c2be03d](https://github.com/roquerodrigo/ha-metro-sp/commit/c2be03dc5fd24d33155ca69d2c46495743af8d6e))
* split the CI workflow into one file per concern ([9326ea0](https://github.com/roquerodrigo/ha-metro-sp/commit/9326ea0f157468f6ed5b95c9b54ab65e52513c54))


### Miscellaneous Chores

* **deps-dev:** bump ruff to 0.16.0 ([2d6b821](https://github.com/roquerodrigo/ha-metro-sp/commit/2d6b8212457980e279be780d6d59936845456e2e))
* move CI to the shared workflows repository ([351a336](https://github.com/roquerodrigo/ha-metro-sp/commit/351a336a083214cb6b9fcde1f6d5d8c71b75b69b))
* release on every conventional commit type ([77f0036](https://github.com/roquerodrigo/ha-metro-sp/commit/77f0036c0da9509f7ac22c0983366b3604a80e33))

## [2.2.1](https://github.com/roquerodrigo/ha-metro-sp/compare/v2.2.0...v2.2.1) (2026-07-15)


### Bug Fixes

* guard against duplicate custom element registration ([44d96d9](https://github.com/roquerodrigo/ha-metro-sp/commit/44d96d92a31d8fc7139e62f07b3357a5b6a277c7))


### Dependencies

* **deps:** bump pip from 26.1.1 to 26.1.2 ([f91a3df](https://github.com/roquerodrigo/ha-metro-sp/commit/f91a3df075083ad97861e1bb3e4fb25288795ee8))

## [2.2.0](https://github.com/roquerodrigo/ha-metro-sp/compare/v2.1.0...v2.2.0) (2026-07-11)


### Features

* add a built-in Lovelace card for the Metrô SP lines ([c47fb47](https://github.com/roquerodrigo/ha-metro-sp/commit/c47fb4791191a95ece951b791a3d4b8f876d5e11))


### Bug Fixes

* title-case CPTM line color names ([114a53c](https://github.com/roquerodrigo/ha-metro-sp/commit/114a53c6b2cb6acb07c0e4e2040628cb6869fcdf))

## [2.1.0](https://github.com/roquerodrigo/ha-metro-sp/compare/v2.0.2...v2.1.0) (2026-07-09)


### Features

* add Line 6-Laranja support ahead of API rollout ([2395abc](https://github.com/roquerodrigo/ha-metro-sp/commit/2395abce5cebe7cdf896afc5b91cb510c38b6d12))
* add Line 6-Laranja support ahead of API rollout ([0be3bec](https://github.com/roquerodrigo/ha-metro-sp/commit/0be3beceba87495f424a4333692a12c9b64ebd7a))


### Bug Fixes

* correct operators for recently conceded CPTM lines ([45a6da4](https://github.com/roquerodrigo/ha-metro-sp/commit/45a6da4a7d5f2e3256b5d6e4632a4125c65569b3))
* correct operators for recently conceded CPTM lines ([045106c](https://github.com/roquerodrigo/ha-metro-sp/commit/045106cd79f4348a67a74e4be4943495dc5efb0b))

## [2.0.2](https://github.com/roquerodrigo/ha-metro-sp/compare/v2.0.1...v2.0.2) (2026-05-25)


### Documentation

* add CI and HACS badges ([d70abe3](https://github.com/roquerodrigo/ha-metro-sp/commit/d70abe3eba6bd1f3e94d4a46fe767ab77abc07f3))
* add CI and HACS badges ([98c4048](https://github.com/roquerodrigo/ha-metro-sp/commit/98c40488fd5c75b20ed305bd462f3994ef949f69))

## [2.0.1](https://github.com/roquerodrigo/ha-metro-sp/compare/v2.0.0...v2.0.1) (2026-05-22)


### Dependencies

* **deps:** bump the python-production group across 1 directory with 2 updates ([1734ba0](https://github.com/roquerodrigo/ha-metro-sp/commit/1734ba09c77004d69c3396fad3288d2edc513cb6))
* **deps:** bump the python-production group with 2 updates ([b534d74](https://github.com/roquerodrigo/ha-metro-sp/commit/b534d745d24ffd877ed761af0131383d129cbcd8))

## [2.0.0](https://github.com/roquerodrigo/ha-metro-sp/compare/v1.1.3...v2.0.0) (2026-05-10)


### ⚠ BREAKING CHANGES

* **sensor:** `sensor.metro_sp_linha_*_detalhes` entities are removed; consumers should read the `description` attribute on the matching `sensor.metro_sp_linha_*_operacao` entity.

### Bug Fixes

* **sensor:** drop detalhes sensor and expose description as attribute ([79633aa](https://github.com/roquerodrigo/ha-metro-sp/commit/79633aa4205ee2f16e0dd0a46bfc4c1b431611f7))


### Documentation

* standardize CODE_STYLE.md template ([b92ffde](https://github.com/roquerodrigo/ha-metro-sp/commit/b92ffde766b4a08bf66446bdb8d96da55bdf21da))
* standardize CODE_STYLE.md template ([60585ff](https://github.com/roquerodrigo/ha-metro-sp/commit/60585ff5f5ffd9262f92f6199e280adef09110a8))

## [1.1.3](https://github.com/roquerodrigo/ha-metro-sp/compare/v1.1.2...v1.1.3) (2026-05-09)


### Bug Fixes

* fall back detalhes to operacao when description is empty ([37d0825](https://github.com/roquerodrigo/ha-metro-sp/commit/37d0825438b71a36e806cca4a0137cd73f30cf0e))


### Dependencies

* bump mypy to 2.0.0 ([e66596d](https://github.com/roquerodrigo/ha-metro-sp/commit/e66596d43b90ccf7c75d368bc5c76eda5c3a7718))
* **deps:** bump pre-commit in the python-production group ([69d3ecc](https://github.com/roquerodrigo/ha-metro-sp/commit/69d3eccb18b4a2dd368118bc90d3139988bfdfbf))

## [1.1.2](https://github.com/roquerodrigo/ha-metro-sp/compare/v1.1.1...v1.1.2) (2026-05-07)


### Dependencies

* **deps:** bump googleapis/release-please-action from 4 to 5 ([5ad674f](https://github.com/roquerodrigo/ha-metro-sp/commit/5ad674fa6df010ca6ddd1c13f98ded322c64fb3a))
