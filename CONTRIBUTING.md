# Diretrizes de contribuição

Contribuir com este projeto deve ser o mais simples e transparente possível, seja para:

- Reportar um bug
- Discutir o estado atual do código
- Enviar uma correção
- Propor novas funcionalidades

## Idioma

Este repositório atende a um serviço que só existe no Brasil, então tudo é escrito em **português do Brasil**: issues, comentários, títulos e descrições de pull request, mensagens de commit, documentação, docstrings e comentários de código. O código permanece em inglês — identificadores, nomes de arquivo e de branch, mensagens de log e o tipo e o escopo do Conventional Commit (`fix(sensor): usa o status quando a descrição vem vazia`). Os termos do domínio (`linha`, `operacao`, os nomes das cores das linhas) nunca são traduzidos. Os detalhes estão na seção "Idioma" do [`CODE_STYLE.md`](./CODE_STYLE.md).

## O GitHub é usado para tudo

O GitHub hospeda o código, acompanha issues e pedidos de funcionalidade e recebe os pull requests.

Pull requests são a melhor forma de propor mudanças no código.

1. Faça um fork do repositório e crie a sua branch a partir da `main`.
2. Se você alterou algo, atualize a documentação.
3. Garanta que o código passa no lint (execute `uv run ruff format .`, `uv run ruff check . --fix` e `uv run mypy custom_components/metro_sp`).
4. Teste a sua contribuição (`uv run pytest`).
5. Abra o pull request!

## Toda contribuição fica sob a licença MIT

Em resumo: ao enviar mudanças de código, entende-se que elas ficam sob a mesma [licença MIT](http://choosealicense.com/licenses/mit/) que cobre o projeto. Entre em contato com os mantenedores se isso for um problema.

## Reporte bugs pelas [issues](../../issues) do GitHub

As issues do GitHub são usadas para acompanhar os bugs públicos.
Reporte um bug [abrindo uma nova issue](../../issues/new/choose).

## Escreva relatos de bug com detalhes, contexto e exemplos

**Bons relatos de bug** costumam ter:

- Um resumo rápido e/ou o contexto
- Passos para reproduzir
  - Seja específico!
  - Inclua exemplos de código ou de configuração, se puder.
- O que você esperava que acontecesse
- O que acontece de fato
- Observações (incluindo, possivelmente, por que você acha que isso acontece ou o que você tentou e não funcionou)

## Siga o estilo de código do projeto

As convenções estão no [`CODE_STYLE.md`](./CODE_STYLE.md). A formatação e o lint são feitos com o [Ruff](https://docs.astral.sh/ruff/), e a tipagem é verificada com o Mypy.

## Teste a sua modificação

Esta integração foi baseada no [template integration_blueprint](https://github.com/ludeeus/integration_blueprint).

Ela traz um ambiente de desenvolvimento em container, fácil de iniciar no
Visual Studio Code. Com esse container você tem uma instância independente do
Home Assistant em execução, já configurada com o
[`configuration.yaml`](./config/configuration.yaml) incluído.

## Licença

Ao contribuir, você concorda que as suas contribuições serão licenciadas sob a licença MIT do projeto.
