# Contribuindo

Relatos de bug, ideias e pull requests são bem-vindos.

## Idioma

O Metrô SP e a CPTM só existem no Brasil, então issues, pull requests,
mensagens de commit, documentação, docstrings e comentários são escritos em
português do Brasil. O código continua em inglês: identificadores, nomes de
arquivo e de branch, mensagens de log e o tipo e o escopo do Conventional
Commit (`fix(sensor): usa o status quando a descrição vem vazia`). Os termos
do domínio, como `linha`, `operacao` e os nomes das cores das linhas, não são
traduzidos. A regra completa está na seção "Idioma" do
[CODE_STYLE.md](CODE_STYLE.md).

## Relatando um bug

Abra uma [issue](https://github.com/roquerodrigo/ha-metro-sp/issues/new/choose)
com:

- a versão do Home Assistant e a da integração;
- o que você fez, o que esperava e o que aconteceu;
- os diagnósticos baixados no menu da integração e as linhas relevantes do
  log.

## Ambiente de desenvolvimento

O projeto usa o [uv](https://docs.astral.sh/uv/). Também há um dev container
(`.devcontainer.json`) com tudo instalado.

```bash
scripts/setup      # instala as dependências no .venv
scripts/develop    # roda o Home Assistant em http://localhost:8123 com esta integração carregada
```

O `scripts/develop` usa a configuração em [`config/`](config/). Para que os IDs
de entidade e de dispositivo sejam recriados do zero, apague o registro antes
de reiniciar:

```bash
rm config/.storage/core.entity_registry config/.storage/core.device_registry
```

O card de dashboard é JavaScript puro, sem etapa de build, e fica em
`custom_components/metro_sp/www/metro-card.js`. Recarregue o navegador depois
de alterá-lo.

## Verificações

Rode estes comandos antes de abrir um pull request. O CI roda os mesmos, e o
`pre-commit install` faz os três primeiros rodarem a cada commit, junto com
verificações de espaços, fim de linha e sintaxe de YAML, JSON e TOML.

```bash
uv run ruff format .                      # formatação
uv run ruff check . --fix                 # lint
uv run mypy custom_components/metro_sp    # verificação de tipos
uv run pytest                             # testes, a cobertura precisa ficar em 90 % ou mais
```

Leia o [CODE_STYLE.md](CODE_STYLE.md) antes de adicionar ou reestruturar
código.

## Pull requests

1. Faça um fork do repositório e crie a sua branch a partir da `main`.
2. Escreva as mensagens de commit no padrão
   [Conventional Commits](https://www.conventionalcommits.org/). As releases e
   as notas de release são geradas a partir desses commits. Marque mudanças
   incompatíveis com `!` ou com o rodapé `BREAKING CHANGE:`.
3. Atualize `translations/en.json` e `translations/pt-BR.json` juntos quando
   mudar textos exibidos ao usuário. Os textos do card ficam no próprio
   `metro-card.js`, também nos dois idiomas.
4. Atualize o README quando o comportamento, a configuração ou as entidades
   mudarem.
5. Preencha o template do pull request.

## Licença

As contribuições são publicadas sob a [licença MIT](LICENSE) do projeto.
