# Versionamento de docs no Docsy — pendência

**Status:** decisão adiada, sem necessidade imediata.

## O que existe

O Docsy tem um seletor de versões pronto no navbar via `[[params.versions]]` no
`hugo.toml` — cada entrada é `version` + `url`. O tema só desenha o dropdown; ele **não**
builda nem hospeda as versões — isso é responsabilidade nossa (builds separados por
tag/branch, publicados em subdomínios ou paths diferentes, ex. `v1.example.com`/`v2.example.com`
ou `/v1/`/`/v2/`). Com `version_menu_pagelinks = true`, o link do dropdown aponta pra mesma
página na outra versão em vez de sempre ir pra home daquela versão. Rótulo padrão do menu é
"Releases", customizável via `version_menu`.

Referência: https://www.docsy.dev/docs/content/versioning/

## Quando revisitar

Configurar isso quando **algum projeto do portfólio tiver 2 ou mais releases** cujos docs
valha a pena manter navegáveis separadamente (não só o mais recente). Nenhum projeto está
nessa situação ainda (jogo-acoes é o primeiro projeto integrado e ainda não tem release).

## Ao implementar, decidir

- Estratégia de hospedagem por versão (subdomínio vs. path).
- Se `version_menu_pagelinks` compensa (depende de quão estável é a estrutura de páginas
  entre versões).
- Como isso se encaixa com a estrutura de import por projeto já usada aqui (`content/<idioma>/docs/<projeto>/...`) —
  provavelmente um nível a mais por versão dentro dessa estrutura.
