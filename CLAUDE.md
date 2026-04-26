# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos úteis

```bash
scripts/setup      # instala dependências (requirements.txt)
scripts/develop    # sobe o Home Assistant em modo debug com a integração carregada
scripts/lint       # formata e corrige o código com ruff
```

O HA sobe com config em `config/` e `PYTHONPATH` apontando para `custom_components/` — não são necessários symlinks.

Ao reiniciar o HA durante desenvolvimento, limpe o registry para que entity/device IDs sejam recriados com os valores atuais:
```bash
rm config/.storage/core.entity_registry config/.storage/core.device_registry
```

O Bluetooth do macOS causa crash intermitente (PyObjC/CoreBluetooth race condition, exit 134). Não é relacionado à integração. `config/configuration.yaml` já tem `bluetooth: passive_scanning: false` como mitigação.

## Arquitetura

A integração segue o padrão `DataUpdateCoordinator` do HA. O fluxo é:

```
config_flow.py   → cria a ConfigEntry (sem credenciais, só testa conectividade)
__init__.py      → instancia MetroSPApiClient + MetroSPDataUpdateCoordinator, faz o primeiro refresh
coordinator.py   → polling a cada 5 min; retorna dict[int, dict] indexado por Code da linha
sensor.py        → lê coordinator.data e cria 2 entidades por linha (operacao + detalhes)
```

### Dados da API

`GET https://apim-proximotrem-prd-brazilsouth-001.azure-api.net/api/v1/lines` — pública, sem auth.

Campos relevantes por linha: `Code`, `ColorName`, `ColorHex`, `Line`, `StatusCode`, `StatusLabel`, `StatusColor`, `Description`.

### Entidades por linha

Cada linha vira um **device** independente com `manufacturer` mapeado por operador (`_LINE_OPERATORS` em `sensor.py`). Cada device tem dois sensores:

- **Operação** (`sensor.metro_sp_linha_{N}_{cor}_operacao`): `native_value = StatusLabel`, atributos de status e cor, `entity_picture` gerada via ui-avatars.com com número e cor da linha.
- **Detalhes da Operação** (`sensor.metro_sp_linha_{N}_{cor}_detalhes`): `native_value = Description`.

O `entity_id` é sugerido explicitamente no construtor via `self.entity_id = "sensor.{base_id}_{key}"`, que o HA usa como `suggested_object_id` no registry na primeira criação.

## CI

- `lint.yml`: ruff check + format (Python 3.14)
- `validate.yml`: hassfest (validação de manifesto HA) + HACS validation — roda em push/PR para main e diariamente
