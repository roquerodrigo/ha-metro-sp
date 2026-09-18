# CLAUDE.md

Orientações para agentes do Claude Code (claude.ai/code) que trabalham neste repositório.

## Sempre leia o `CODE_STYLE.md` primeiro

Antes de criar, renomear ou reestruturar qualquer arquivo, classe ou função, **leia o [`CODE_STYLE.md`](./CODE_STYLE.md)** — a única fonte da verdade para as convenções (idioma, organização de arquivos, nomenclatura, tipagem, padrão do coordinator, traduções, fluxo de lint, conventional commits). Para os temas voltados ao usuário (linhas suportadas, instalação, atributos do sensor), veja o [`README.md`](./README.md).

Este arquivo só acrescenta o que nenhum dos dois cobre: o fluxo de verificação, as particularidades do desenvolvimento local e o *porquê* das decisões de arquitetura.

## Idioma do repositório

O `hacs.json` declara `"country": ["BR"]`, então o idioma do repositório é o pt-BR: documentação, docstrings, comentários, commits, PRs, changelog, templates em `.github/` e toda resposta pública. O código permanece em inglês, e os termos nativos do domínio (`linha`, `operacao`, os nomes das cores) nunca são traduzidos. A regra completa está na seção "Idioma" do `CODE_STYLE.md`.

## Fluxo de verificação

**Depois de cada mudança de código, execute o lint e, em seguida, os testes, nessa ordem, antes de dar a tarefa como concluída:**

```bash
uv run ruff format . && uv run ruff check . --fix && uv run mypy custom_components/metro_sp && uv run pytest
```

O `pytest` impõe um **gate de 90 % de cobertura** (configurado em `pyproject.toml`). Os dois gates espelham o CI. Pule esta etapa apenas quando a mudança literalmente não puder afetar lint nem testes (por exemplo, edições só no README).

## Desenvolvimento local

- O `scripts/develop` inicia o Home Assistant em modo debug com a integração carregada (configuração em `config/`, `PYTHONPATH` em `custom_components/`; sem symlinks).
- Ao reiniciar o HA durante o desenvolvimento, limpe o registry para que os IDs de entidade e de device sejam recriados com os valores atuais:

  ```bash
  rm config/.storage/core.entity_registry config/.storage/core.device_registry
  ```

- O Bluetooth do macOS causa crashes intermitentes (condição de corrida entre PyObjC e CoreBluetooth, exit 134), sem relação com esta integração. Contorne com `bluetooth: passive_scanning: false` em `config/configuration.yaml`.

## Justificativa da arquitetura

Estrutura padrão do HA com `DataUpdateCoordinator`; as decisões não óbvias:

- **Período de tolerância do coordinator.** Quando a origem falha, o coordinator devolve os últimos dados conhecidos durante `FAILURE_GRACE_PERIOD` (5 min) em vez de marcar as entidades como indisponíveis, e só levanta `UpdateFailed` depois que esse período termina.
- **API pública, sem autenticação** (`.../api/v1/lines`). Deliberadamente não existe `AuthenticationError`, reauth nem options flow — não adicione nenhum deles, a menos que a API de origem passe a exigir autenticação.
- **`description` é um atributo de estado, não um sensor separado:** o HA trunca para `unknown` valores de estado com mais de 255 caracteres, e o texto de ocorrência da origem ultrapassa esse limite com frequência.
- **Um device por linha.** Cada linha é o seu próprio device, então `device_info` é uma `@property` de `MetroSPLineSensor`, e não da base `MetroSPEntity`. O slug pt-BR do `entity_id` (`sensor.metro_sp_linha_{N}_{cor}_operacao`) é definido via `self.entity_id` no construtor e é estado de registry nas instalações dos usuários — nunca o renomeie.
- **Card Lovelace embutido** (`www/metro-card.js`, um `custom:metro-card` em vanilla JS, sem build): a `MetroSPCardRegistration` o registra como recurso de dashboard do Lovelace, e não apenas via `add_extra_js_url`. Recursos de dashboard persistem em storage e são buscados a cada carregamento do dashboard, o que fecha a janela de inicialização em que um módulo extra adicionado no meio do boot faltava nas páginas já servidas; o `add_extra_js_url` permanece apenas como fallback para o Lovelace em modo YAML. A query `?v={integration.version}` invalida o cache do navegador a cada release. As strings de i18n ficam embutidas no arquivo — um plugin puramente de frontend não tem acesso às traduções de `custom_components`.
- **Sem `repairs.py`:** não há nenhuma condição recuperável a expor. Adicione a plataforma junto com a primeira issue real que ela levantar, nunca como um esqueleto sem uso.
