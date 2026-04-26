# Metrô SP para Home Assistant

Integração custom para o [Home Assistant](https://www.home-assistant.io/) que exibe o status operacional em tempo real
das linhas do Metrô SP e CPTM.

## Linhas suportadas

| Linha | Nome      | Operador      |
|-------|-----------|---------------|
| 1     | Azul      | Metrô SP      |
| 2     | Verde     | Metrô SP      |
| 3     | Vermelha  | Metrô SP      |
| 4     | Amarela   | ViaQuatro     |
| 5     | Lilás     | ViaMobilidade |
| 7     | Rubi      | CPTM          |
| 8     | Diamante  | ViaMobilidade |
| 9     | Esmeralda | ViaMobilidade |
| 10    | Turquesa  | CPTM          |
| 11    | Coral     | CPTM          |
| 12    | Safira    | CPTM          |
| 13    | Jade      | CPTM          |
| 15    | Prata     | Metrô SP      |
| 17    | Ouro      | ViaMobilidade |

## Sensores criados

Cada linha gera um **device** independente com dois sensores:

| Sensor               | Entity ID                              | Descrição                                     |
|----------------------|----------------------------------------|-----------------------------------------------|
| Operação             | `sensor.metro_sp_linha_X_cor_operacao` | Status atual da linha (ex: "Operação Normal") |
| Detalhes da Operação | `sensor.metro_sp_linha_X_cor_detalhes` | Descrição detalhada de ocorrências            |

### Atributos do sensor de Operação

| Atributo       | Descrição                                   |
|----------------|---------------------------------------------|
| `status_code`  | Código do status (ex: `OperacaoNormal`)     |
| `status_color` | Cor do status (`verde`, `amarelo`, `cinza`) |
| `color_name`   | Nome da cor da linha                        |
| `color_hex`    | Código hexadecimal da cor da linha          |
| `line_code`    | Número da linha                             |

## Instalação

### Manual

1. Copie a pasta `custom_components/metro_sp` para o diretório `custom_components` da sua instalação do Home Assistant.
2. Reinicie o Home Assistant.
3. Acesse **Configurações → Dispositivos e Serviços → Adicionar Integração** e pesquise por **Metrô SP**.
4. Confirme a instalação. Os sensores serão criados automaticamente.

### HACS

Em breve.

## Atualização dos dados

Os dados são atualizados a cada **5 minutos** via polling na API pública do Metrô SP. Nenhuma credencial é necessária.

## Licença

[MIT](LICENSE)
