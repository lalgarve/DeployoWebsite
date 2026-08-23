# Analytics com Matomo — contexto

**Status:** decidido (self-host), integração no site ainda não implementada.

## Decisão

Usar Matomo em vez de Google Analytics, principalmente por privacidade — Matomo permite
modo sem cookies, o que tipicamente dispensa banner de consentimento. Self-hosted (não
Matomo Cloud), rodando em Docker na mesma VPS onde a aplicação e o banco de dados já rodam
em containers (ver `docs/roadmap.md` do jogo-acoes, Iteração 5 — VPS + Docker Compose).

A config Docker do Matomo (docker-compose, volumes, backup do banco do Matomo) fica num
**repositório de infra separado**, não neste repositório nem no jogo-acoes. O repositório
existe agora: [`lalgarve/DeployoInfra`](https://github.com/lalgarve/DeployoInfra) — passou a
ser responsável pela infra completa (site, Matomo e os projetos do portfólio, não só o
Matomo). Mapa de domínios/URLs e estratégia de deploy por projeto em
`docs/mapa-site-e-deploy.md` nesse repositório (branch `docs/mapa-site-e-deploy`, ainda não
mesclada — domínio proposto para o Matomo lá: `analytics.deployo.io`).

## O que cabe no DeployoWebsite

Só a integração do lado do site: o snippet de tracking do Matomo. Diferente do Google
Analytics — que o Hugo já suporta nativamente (`services.googleAnalytics` no `hugo.toml`) —
o Docsy não tem suporte embutido a Matomo. A integração é via um partial customizado que
sobrescreve/estende o `<head>` do tema com o script assíncrono do Matomo.

## Pendências

1. ~~Repositório de infra~~ — feito, ver acima.
2. **Domínio/URL da instância Matomo** — proposta `analytics.deployo.io` registrada no mapa
   do DeployoInfra, ainda não confirmada/implementada. Necessário antes de escrever o
   snippet, já que ele aponta pra URL do tracker.
3. **Site ID do Matomo** — gerado ao criar o site dentro do próprio Matomo; necessário pro
   snippet.
4. **Implementar o partial no Docsy** — depende dos dois itens acima.
5. Decidir se o modo sem cookies do Matomo é suficiente para dispensar banner de
   consentimento neste caso, ou se ainda assim vale ter um (ex. por outras integrações do
   site que usem cookies).
