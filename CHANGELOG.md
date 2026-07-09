# Changelog

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
