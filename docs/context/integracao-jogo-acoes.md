# Integração do jogo-acoes ao portfólio — contexto

**Status:** em andamento.

Este documento registra o estado da integração do primeiro projeto do portfólio
(jogo-acoes) a este site, para que uma nova sessão de chat possa retomar sem precisar
reconstruir o raciocínio a partir do zero. Convenção: arquivos desta pasta (`docs/context/`)
são notas de continuidade entre sessões, não documentação do produto — o próprio pipeline
de import deste repositório pula diretórios chamados `context` pelo mesmo motivo (ver
`src/documentation/file_handler.py::should_traverse_directory`).

## Decisões já tomadas e aplicadas

- **Mermaid habilitado** (`hugo.toml`, `[params.mermaid] enable = true`) — o Docsy renderiza
  nativamente os blocos ` ```mermaid ` que o jogo-acoes já usa em `docs/diagrams/der.md` e
  `docs/roadmap.md`, sem shortcode custom. (commit `bbaae3b`)
- **Convenção `docs/context/`** — diretórios chamados `context` são pulados pelo pipeline de
  import (`should_traverse_directory` em `src/documentation/file_handler.py`, e o equivalente
  em `scripts/addDocumentation.py`), do mesmo jeito que já acontecia com `uml`/`backlog`.
  Motivo: arquivos como `desenvolvimento.md` e `iteracao-N.md` do jogo-acoes são contexto de
  retomada entre sessões de chat, não documentação para publicar. (commit `bbaae3b`)
- Pedido feito ao chat que cuida do jogo-acoes: mover `desenvolvimento.md`, `iteracao-2.md`,
  `iteracao-3.md`, `iteracao-4.md` para `docs/context/` lá.
  **Ainda não confirmado que foi feito** — checar antes de rodar o import de verdade.

## Pendências (ainda não implementadas)

1. **Generalizar o pipeline para docs sem subpasta de idioma** — `docs/` do jogo-acoes é
   plano (sem `en`/`pt-br`); `build_destination_path` hoje só organiza quando existe subpasta
   de idioma reconhecida, senão cai no fallback (`content/` sem estrutura nenhuma). Decisão
   proposta e ainda não implementada: tratar ausência de subpasta de idioma como pt-br por
   default.
2. **`docs/openapi.yaml` do jogo-acoes** — não é `.md` nem `.png`; hoje seria ignorado pelo
   pipeline (`determine_file_actions` só reconhece essas duas extensões). Decisão adiada.
3. **Terminar a orquestração do pipeline novo** — `src/documentation/file_handler.py` tem as
   peças (`should_traverse_directory`, `determine_file_actions`, `handle_png`,
   `Markdown.merge_files`) mas nenhum `main`/orquestrador as liga; só o script antigo
   (`scripts/addDocumentation.py`) roda ponta a ponta hoje. Proposta: usar esta integração
   para terminar o pipeline novo e aposentar o antigo, em vez de manter os dois.
4. **Página de apresentação do projeto no portfólio** — decidir estrutura de conteúdo (ex.
   `content/pt-br/portfolio/jogo-acoes/_index.md`) com descrição, link do repositório,
   screenshots, e como ela referencia os docs técnicos importados. Rascunho inicial de URLs
   em `docs/mapa-site-e-deploy.md` do [`lalgarve/DeployoInfra`](https://github.com/lalgarve/DeployoInfra)
   (branch `docs/mapa-site-e-deploy`): a página linkaria `.../docs/jogo-acoes/` (documentação)
   e `jogo-acoes.deployo.io` (a aplicação rodando de verdade — depende da VPS/Docker Compose
   descrita na Iteração 5 do roadmap do jogo-acoes, ainda não implementada).

## Outras práticas do jogo-acoes avaliadas para este repositório

O jogo-acoes tem um `docs/desenvolvimento.md` com convenções de processo (idioma,
commits semânticos com tipo `decision`, branches/PRs, docs vivas por iteração, CI com piso
de cobertura obrigatório) explicitamente desenhado para ser copiável entre projetos.
Avaliação rápida do que se aplica aqui:

- **Commits semânticos + tipo `decision`**: **implementado** (commit `79817b1`) — convenção
  documentada em `CLAUDE.md` e validada por `.githooks/commit-msg`
  (`git config core.hooksPath .githooks` para ativar por clone/sessão).
- **CI com suíte de testes e piso de cobertura**: aplicável e é um gap real — não existe
  `.github/` neste repositório, nada roda automaticamente (nem os testes Python já
  existentes em `src/tests/`).
- **Specs Gherkin/OpenAPI antes do código, DER antes das entidades**: não se aplica — este
  repositório é site estático + scripts de importação, não uma API com modelo de dados.
- **Nomenclatura de ambientes** (`sandbox`/`docker`/`staging`/`production`): não se aplica
  ainda — não há múltiplos ambientes configurados.
- **Testes preferindo dependência real a mock**: aplicável parcialmente —
  `src/tests/test_markdown.py` mocka `GitClient` inteiro; um fixture com `git init` real
  seria mais robusto (e teria ajudado a expor o bug do mock com path errado
  `scr.documentation...` em vez de `src.documentation...`).

As demais seguem não implementadas — registradas aqui para não se perder caso a decisão de
adotá-las seja tomada numa sessão futura.
