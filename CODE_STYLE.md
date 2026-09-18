# Guia de estilo de código

Convenções de estilo do projeto `ha-metro-sp`. Antes de commitar, execute
`uv run ruff format .`, `uv run ruff check . --fix` e
`uv run mypy custom_components/metro_sp`; todos devem terminar sem erros.
Em seguida vem `uv run pytest` (com o gate de 90 % de cobertura).

**Sempre leia este arquivo antes de adicionar ou reestruturar código.**

## Idioma

O `hacs.json` declara `"country": ["BR"]`: o Metrô SP e a CPTM só existem no
Brasil, então o idioma do repositório é o **português do Brasil**.

- **Toda prosa lida por pessoas é escrita em pt-BR:**
  - Documentação: `README.md`, `CONTRIBUTING.md`, este guia, `CLAUDE.md`,
    qualquer outro Markdown, docstrings e comentários de código.
  - Histórico do Git: assunto e corpo dos commits, títulos e descrições de PR.
  - Releases: notas de release e `CHANGELOG.md`, inclusive os títulos de seção
    (`changelog-sections` em `release-please-config.json`).
  - Comunicação pública: issues, comentários em issues e PRs, reviews,
    discussions e os templates em `.github/`.
  - Metadados: a descrição do repositório no GitHub e `description` em
    `pyproject.toml`.
- **O código é escrito em inglês**, independentemente do `country`: nomes de
  arquivo, de classe, de função, de variável e de branch, chaves de dicionário,
  strings identificadoras e mensagens de log. Tudo o que uma ferramenta
  interpreta também é código: tipo e escopo do Conventional Commit
  (`fix(sensor): usa o status quando a descrição vem vazia`), o rodapé
  `BREAKING CHANGE:`, ids de workflow e de job, labels.
- **Termos nativos do domínio nunca são traduzidos, nem no código nem na
  prosa.** Eles são a linguagem ubíqua compartilhada com os usuários e com o
  serviço de origem: `linha`, `operacao`, os nomes das cores das linhas
  (`Azul`, `Lilás`, `Esmeralda`). O que envolve o termo continua em inglês.
  Identificadores perdem os diacríticos (`operacao`); a prosa e as strings
  traduzidas os mantêm (`operação`).
- **Identificadores anteriores a esta regra permanecem como estão:** `Line`
  (`MetroSPLine`, `MetroSPLineSensor`, `line_code`) e `operation` (translation
  key e sufixo do unique id) traduzem `linha` e `operação`, mas o atributo de
  estado `line_code`, a translation key e o unique id são contrato público ou
  estado de registry nas instalações dos usuários. Não os renomeie; aplique a
  regra apenas a identificadores novos.
- A própria API do Metrô SP define as chaves do payload (`Code`, `ColorName`,
  `StatusLabel`, …). Elas são encapsuladas no `TypedDict` `MetroSPLine`, em
  `data.py`, para que o restante do código se refira a uma forma tipada, e não
  a strings cruas.
- O idioma da conversa com o usuário nunca decide o que é gravado em disco.
- Strings voltadas ao usuário ficam em
  `custom_components/metro_sp/translations/{en,pt-BR}.json` sempre que o Home
  Assistant consegue traduzi-las; por isso `_attr_translation_key` permanece em
  inglês (`operation`) enquanto o nome exibido varia por idioma. O `en.json`
  continua obrigatório ao lado do `pt-BR.json`.
- **As poucas strings voltadas ao usuário que o Home Assistant não consegue
  traduzir ficam em pt-BR**: `ATTRIBUTION` e o nome do device de cada linha
  (`Linha 1 - Azul`). Não existe mecanismo de tradução para nenhuma das duas,
  então elas são exibidas literalmente a todos os usuários — e todo usuário
  desta integração está olhando para a rede de São Paulo. Os nomes das cores
  das linhas vêm literalmente do payload da API.
- Os entity ids mantêm os slugs históricos em pt-BR
  (`sensor.metro_sp_linha_{N}_{cor}_operacao`) — são estado de registry nas
  instalações dos usuários, não código, e renomeá-los quebraria dashboards
  existentes.

## Organização de arquivos

- **Uma classe de nível superior por arquivo.** Várias classes semanticamente
  relacionadas (por exemplo, famílias de exceções ou as entidades de sensor de
  uma plataforma) são agrupadas em um diretório de pacote, com uma classe por
  submódulo e um `__init__.py` reexportando os símbolos públicos.
  - Exemplo: `exceptions/` contém `api_client_error.py`,
    `api_client_communication_error.py` e o `__init__.py`.
- **TypedDicts e aliases `type` não contam como "classes"** para esta regra —
  eles ficam junto do código relacionado (normalmente em `data.py`) e não
  precisam de arquivo próprio.
- **Funções auxiliares** podem ficar no mesmo arquivo da única classe que as
  utiliza (por exemplo, `_verify_response_or_raise` em `api.py`).
- **O `__init__.py` do pacote da integração** conecta `async_setup_entry`,
  `async_unload_entry` e `async_reload_entry` (delegando o registro do card e
  dos arquivos estáticos a `MetroSPCardRegistration`) e nada mais.

## Entidades: uma classe por entidade

- **Uma classe por entidade.** Toda entidade tem a sua própria classe dedicada —
  nunca compartilhe uma classe genérica parametrizada por uma subclasse de
  `EntityDescription` com campos chamáveis como `value_fn` ou `action_fn`.
  Codifique o comportamento da entidade diretamente na classe, por meio de
  `@property` e de constantes `_attr_*` no nível da classe (ou de uma instância
  simples de `EntityDescription` atribuída no nível da classe).
  - Não escreva uma subclasse `MetroSPSensorDescription` com um campo
    `value_fn`.
  - Escreva uma classe por entidade — a `MetroSPLineSensor` existente codifica
    o comportamento de operacao diretamente, por meio de `@property` e de
    constantes `_attr_*` no nível da classe, sem a indireção de uma description
    com chamáveis.
- O motivo: cada entidade é um contrato distinto; misturá-las em uma classe
  genérica esconde o contrato atrás de indireção e desestimula o refinamento por
  entidade (ícones, atributos de estado, lógica própria).

## Nomenclatura

- Classes públicas recebem o prefixo `MetroSP`.
- Entidades concretas de plataforma terminam com o tipo da entidade:
  `MetroSPLineSensor`.
- Classes de exceção terminam com `Error`: `MetroSPApiClientError`,
  `MetroSPApiClientCommunicationError`.
- Atributos e funções privados recebem o prefixo `_`.

## Tipagem

**Tipagem estrita. Sem genéricos, sem `Any`.** O Mypy (`uv run mypy custom_components/metro_sp`) garante isso.

Proibidos: `typing.Any`, `object` como tipo de valor, `dict` / `list` / `tuple` /
`set` sem parâmetros, `dict[str, Any]`, `Mapping[str, Any]`.

Obrigatórios:

- `TypedDict` para formas conhecidas de dict / JSON (veja `data.py`:
  `MetroSPLine`, `MetroSPDiagnosticsEntry`, `MetroSPDiagnosticsPayload`,
  `MetroSPSensorAttributes`).
- `@dataclass` para registros estruturados (`MetroSPData`).
- Aliases `type` nomeados para formas recursivas ou compartilhadas —
  `JsonPrimitive`, `JsonValue`, `JsonObject` em `data.py`.
- `frozenset[str]` / `tuple[str, ...]` para coleções fixas de strings.
- `cast("TypedDictName", value)` nas fronteiras com o framework do HA que
  entregam um tipo permissivo (por exemplo, `entry.data` é
  `MappingProxyType[str, Any]`).

Ao estreitar a assinatura de um callback fornecido pelo HA, o mypy reporta
`[override]` (violação de Liskov). Adicione `# type: ignore[override]` com um
comentário de uma linha explicando o estreitamento deliberado.

## Properties e `__init__`

- **Sempre prefira `@property`** a atribuir valores `_attr_*` no `__init__`.
  Properties são calculadas sob demanda a partir dos campos guardados na classe
  pai (por exemplo, `self.coordinator`, `self.entity_description`).
- Quando o corpo do `__init__` apenas chamaria `super().__init__(...)`, omita o
  `__init__` por completo e deixe o Python herdar o da classe pai.
- Constantes no nível da classe, como `_attr_attribution = ATTRIBUTION` e
  `_attr_has_entity_name = True`, são aceitas — não dependem do estado da
  instância.

## Imports

- Sempre comece todo módulo com `from __future__ import annotations`, para que
  as anotações de tipo virem strings avaliadas sob demanda e o custo em tempo
  de execução dos imports sob `if TYPE_CHECKING` seja zero.
- Imports relativos dentro do mesmo pacote (`from .module import …`) são o
  padrão.
- Mova imports usados apenas para tipagem para um bloco `TYPE_CHECKING` (Ruff
  `TC001`/`TC003`):

  ```python
  from __future__ import annotations
  from typing import TYPE_CHECKING

  if TYPE_CHECKING:
      from collections.abc import Mapping
      from .data import MetroSPLine
  ```

- Comentários `noqa` são reservados a restrições inevitáveis do framework (por
  exemplo, `# noqa: ARG001` para parâmetros de callback do HA que precisam
  existir mas não são usados). Documente o motivo na própria linha quando não
  for óbvio. Nunca silencie uma regra para "agradar o ruff" — corrija o código.

## Docstrings

- Toda classe, função e método públicos (inclusive `@property`) e todo
  `__init__` têm docstring. O Ruff garante isso com `D102`/`D107`.
- As docstrings são escritas em pt-BR (veja [Idioma](#idioma)).
- Uma única frase costuma bastar. Descreva o *contrato* ou o *porquê*, não a
  implementação óbvia.
- Docstring de módulo no topo de todo arquivo `.py`.
- Evite repetir o tipo — a assinatura já faz isso.

## Comentários

- O padrão é **não comentar**. Adicione um comentário apenas quando o *porquê*
  não for óbvio a partir do código: uma restrição oculta, um contorno, uma
  invariante sutil ou uma sobreposição deliberada do sistema de tipos.
- Nunca descreva *o que* o código faz — identificadores bem nomeados cuidam
  disso.
- **Sem divisores de seção** como `# --- API payloads ---` para agrupar
  declarações relacionadas. Se um arquivo tem tantas seções que você sente falta
  de separadores visuais, divida-o em vários arquivos.

## Logging

- Cada módulo usa o `LOGGER` do pacote, definido em `const.py`
  (`LOGGER: Logger = getLogger(__package__)`); nunca chame
  `logging.getLogger(...)` de forma avulsa.
- As mensagens de log são código e permanecem em inglês.
- Use **formatação `%` tardia**, nunca f-strings — elas forçam a interpolação
  mesmo quando o nível está filtrado:

  ```python
  LOGGER.warning("Metrô SP API error; keeping last known data: %s", exception)   # ✓
  LOGGER.warning(f"Metrô SP API error: {exception}")                              # ✗
  ```

- Níveis:
  - `debug` — resumos de buscas bem-sucedidas, diagnósticos de cada ciclo.
  - `info` — eventos únicos do ciclo de vida (setup concluído).
  - `warning` — falhas recuperáveis (erro transitório da API, uso de fallback).
  - `error` / `exception` — falhas irrecuperáveis no ciclo atual; use
    `exception` com exceções capturadas dentro de blocos `except` para obter o
    traceback completo.

## Mensagens de erro

- Formato: `"Failed to <verb> <object>: <cause>"`, em que `<cause>` é a exceção
  ou um motivo curto. Mantenha-as curtas e fáceis de localizar com grep.
- As exceções próprias seguem a mesma hierarquia:
  `MetroSPApiClientError` (base) → `MetroSPApiClientCommunicationError`
  (timeout, conexão, DNS). A API do Metrô SP não exige autenticação, então não
  existe `AuthenticationError`. Encapsule os erros crus de origem na fronteira
  do cliente da API; tudo o que fica acima captura apenas a hierarquia própria.

## Coordinator e runtime data

- Todo o estado da API passa por `entry.runtime_data: MetroSPData`
  (`data.py`). Nunca guarde estado da integração em `hass.data` (as únicas
  exceções neste repositório são as sentinelas de registro em
  `card_registration.py` — `_STATIC_PATH_REGISTERED_KEY` e
  `_EXTRA_MODULE_REGISTERED_KEY` —, que valem por `hass`, não por entry).
- O coordinator é tipado como `DataUpdateCoordinator[dict[int, MetroSPLine]]`,
  indexado pelo `Code` da linha. `_async_update_data` devolve o payload tipado;
  erros do cliente viram `UpdateFailed`.
- A API do Metrô SP não exige autenticação, então não existe
  `ConfigEntryAuthFailed` nem fluxo de reauth. Não adicione um, a menos que a
  API de origem passe a exigir autenticação.

## Config / diagnostics

- O `config_flow.py` tem um único passo, `async_step_user`, apoiado em um
  auxiliar `_validate`. A API não tem credenciais, então não há fluxo de
  reauth, de reconfigure nem de options. Mantenha assim até o contrato da API
  mudar.
- Não existe `repairs.py` — a integração hoje não tem nenhuma condição
  recuperável a expor. Introduza a plataforma junto com a primeira issue real
  que ela levantar, nunca como um esqueleto sem uso.
- O `diagnostics.py` devolve `MetroSPDiagnosticsPayload`. Não há segredos em
  `entry.data`, então `TO_REDACT` está vazio — mantenha a chamada a
  `async_redact_data` no lugar, para que adicionar uma chave a ocultar no
  futuro seja uma mudança de uma linha.

## Traduções

- Dois locales: `en.json` e `pt-BR.json`. O `tests/test_translations.py`
  parametriza sobre todos os locales e falha se os conjuntos de chaves
  aninhadas divergirem.
- As strings do fluxo ficam em `config.step.<step_id>`; os nomes de entidade,
  em `entity.sensor.<key>.name` (a translation key do sensor é `operation`).

## Hooks de pre-commit

O `pre-commit` é uma dependência de desenvolvimento (declarada em
`pyproject.toml`), e o `.pre-commit-config.yaml` executa os comandos de lint
como **hooks locais via `uv run`** (ruff format, ruff check, mypy); assim o hook
sempre usa exatamente as versões fixadas em `pyproject.toml` — sem um pin
separado que possa divergir. Instale uma vez por clone:

```bash
pre-commit install
```

O hook executa os mesmos gates do CI a cada commit. Ignore-o apenas em um
`git commit --no-verify` de emergência e, em seguida, execute de novo os
comandos de lint (`uv run ruff format .`, `uv run ruff check . --fix`,
`uv run mypy custom_components/metro_sp`).

## Conventional commits

Todos os commits seguem o
[Conventional Commits](https://www.conventionalcommits.org/), que o
`release-please` interpreta para incrementar a versão e gerar o `CHANGELOG.md`:

| Tipo | Significado | Incremento |
|---|---|---|
| `feat` | Nova funcionalidade | minor |
| `fix` | Correção de bug | patch |
| `perf` | Melhoria de desempenho | patch |
| `deps` | Atualização de dependência | patch |
| `docs` | Apenas documentação | nenhum |
| `refactor` | Refatoração sem mudança de comportamento | nenhum |
| `test` | Mudança apenas em testes | nenhum |
| `ci` | Mudança de CI / ferramentas | nenhum |
| `chore` | Qualquer outra coisa (raramente) | nenhum |

- Assunto: em pt-BR, no imperativo, em minúsculas, sem ponto final. O tipo e o
  escopo ficam sempre em inglês.
- Use escopos quando forem úteis:
  `fix(sensor): usa o status quando a descrição vem vazia`.
- Um rodapé `BREAKING CHANGE:` (ou `!` depois do tipo) incrementa a versão
  major.

## Lint e verificação

- A configuração do Ruff fica em `pyproject.toml` (`[tool.ruff]`), com `select = ["ALL"]`.
- A configuração do Mypy fica em `pyproject.toml` (`[tool.mypy]`). Execute ambos
  diretamente com `uv run ruff check .` e `uv run mypy custom_components/metro_sp`.
- Depois de cada mudança, execute `uv run ruff format . && uv run ruff check . --fix && uv run mypy custom_components/metro_sp && uv run pytest`.
  Os dois gates espelham o CI.
- Os testes ficam em `tests/`, espelhando a estrutura do código de produção. O
  gate de 90 % de cobertura (`[tool.pytest.ini_options]` em `pyproject.toml`)
  impede que código sem teste passe despercebido. Quando um teste exercita um
  estado impossível sob os novos tipos, atualize-o ou remova-o — nunca
  enfraqueça o tipo para satisfazer o teste.
