# CLAUDE.md

Convenções deste repositório para qualquer sessão (humana ou de IA) que for commitar aqui.

## Commits semânticos

Baseado na convenção usada no jogo-acoes (`docs/context/desenvolvimento.md` lá) — adotada
aqui para manter um histórico de commits navegável e consistente.

Formato da primeira linha:

```
<tipo>: <resumo curto, no imperativo>
```

| Tipo | Quando usar |
|---|---|
| `feat` | Nova funcionalidade ou comportamento observável |
| `fix` | Correção de bug |
| `refactor` | Mudança estrutural que não altera comportamento (renomear, mover, reorganizar) |
| `test` | Adição/alteração de testes |
| `docs` | Mudança só de documentação |
| `chore` | Manutenção sem impacto em código de produção (dependências, config de build) |
| `decision` | Registra uma decisão de arquitetura/design tomada, mesmo que não altere código sozinha |

`tipo` sempre em minúsculo. Sem exceção por o commit ser pequeno, de documentação, ou feito
por uma sessão de IA — todo commit segue o formato.

### Idioma

Mensagens de commit (título e corpo) são em **inglês** — mesma regra do jogo-acoes
(`docs/context/desenvolvimento.md` lá, tabela "Idioma"): código e commits em inglês,
documentação de projeto (`docs/*.md`, este arquivo) em português. Título de PR e mensagem de
merge seguem a mesma regra, por serem essencialmente uma mensagem de commit.

### Corpo da mensagem

Para uma mudança não trivial:

1. **Título**: `<tipo>: <resumo>`.
2. **Por quê** (parágrafo): o raciocínio/problema que motivou a mudança — não repetir o que
   o diff já mostra.
3. **O quê** (lista, opcional): mudanças concretas relevantes, quando o "por quê" sozinho não
   basta para orientar quem revisa.
4. **Validação** (parágrafo, opcional): o que foi de fato testado/rodado nesta sessão de
   trabalho para confirmar que a mudança funciona.
5. **Referência cruzada** (linha final, opcional): se a mudança resolve algo registrado em
   `docs/context/`, apontar para o arquivo.

Commits pequenos e focados numa mudança revisável de cada vez.

### Enforcement

Um hook `commit-msg` versionado em `.githooks/commit-msg` valida o formato da primeira
linha. Ativar uma vez por clone/sessão:

```
git config core.hooksPath .githooks
```

### Nota histórica

Commits anteriores a esta convenção (`Feat:` maiúsculo, ou sem tipo algum, ex. commit
`bbaae3b`) não foram reescritos — histórico existente não é alterado, a convenção vale a
partir daqui. O mesmo vale para a regra de idioma: commits já pushed com corpo em português
(ex. `f84f3a5`, `3563dac`) não são reescritos; commits a partir de agora vão em inglês.

## Branches e Pull Requests

- Um branch por linha de trabalho revisável — nome descritivo do que está sendo feito, não
  um identificador genérico.
- Nunca commitar direto no branch principal (`main`/`master`); toda mudança entra por PR.
- Uma PR corresponde a um branch — não empilhar trabalhos sem relação na mesma PR só porque
  foram feitos na mesma sessão.
- Título e descrição de PR seguem a mesma convenção de idioma das mensagens de commit —
  inglês (ver seção "Idioma" acima) — porque o GitHub usa o título da PR como corpo do merge
  commit em `main`/`master` quando a PR é mesclada.
- Quando o trabalho de uma PR já mesclada precisa continuar, reaproveitar o mesmo branch
  (recriado a partir do estado atual da branch principal) em vez de acumular branches novos
  a cada retomada.
- Este repositório publica um site estático com deploy: abrir um branch novo após cada
  deploy com sucesso em produção, em vez de continuar acumulando commits no mesmo branch já
  publicado.

## Testes: preferir real a fake sempre que der

Sempre que uma dependência externa tiver como rodar localmente/de verdade em teste
automatizado, preferir isso a um mock/stub — um teste que passa contra uma simulação que
não bate com o comportamento real dá falsa confiança ("passou no teste, quebrou em
produção").

**Exemplo usado neste projeto**: os testes do pipeline de import
(`src/tests/test_file_handler.py`) exercitam `FileHandler` contra repositórios temporários
reais no filesystem (fixture `tmp_path`), não contra um filesystem mockado — o
comportamento de percorrer diretórios e decidir o que copiar é testado de ponta a ponta.

## Diagramas Mermaid: validar a renderização de verdade

Um diagrama Mermaid com sintaxe que "parece certa" pode ainda assim falhar ao renderizar —
a gramática tem armadilhas que só aparecem no parser de verdade. Como este repositório
publica `.md` vindos de outros projetos (que podem conter diagramas Mermaid), antes de
considerar pronta uma mudança que adiciona ou altera um diagrama, renderizar de verdade
contra um motor Mermaid real (ex.: `npx @mermaid-js/mermaid-cli`) — não só validar
visualmente/mentalmente a sintaxe.

## Pastas de contexto de IA

Notas de continuidade entre sessões (decisões, pendências) ficam em `docs/context/` — não é
documentação de produto, é o equivalente deste repositório aos arquivos `iteracao-N.md` do
jogo-acoes. O pipeline de import (`src/documentation/file_handler.py`) já pula diretórios
chamados `context` pelo mesmo motivo em repositórios de origem.
