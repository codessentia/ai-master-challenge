# Decisões — o que a IA propôs, o que eu decidi e por quê

> Uma linha por decisão relevante, na ordem em que aconteceram.
> "Origem" = quem levantou a questão. A coluna "Por quê" é sempre escrita por mim.

| # | Data | Decisão | Origem | O que a IA propôs | O que eu decidi | Por quê (nas minhas palavras) |
|---|---|---|---|---|---|---|
| D01 | 2026-10-13 | Escolha do challenge | IA, a meu pedido | Comparou os 4 desafios; recomendou o 002 como o mais aderente ao perfil AI Master | Challenge 002 | Por que era o mais complexto para propor a solução e o mais alinhado com o perfil da vaga. |
| D02 | 2026-10-13 | Protótipo obrigatório ou opcional | Eu | — | Eu apontei a inconsistência do brief (a introdução pede "algo rodando"; a lista de entregáveis chama o protótipo de diferencial) e decidi tratá-lo como obrigatório | Melhor apresentar a solução mais complete. Cliente decide se adota ou não. |
| D03 | 2026-10-13 | Revisar todos os PRs públicos antes de executar | Eu | — | Analisar os 184 PRs (38 do Challenge 002) e o padrão de avaliação da G4 antes de qualquer análise | Para que reinventar a roda - vou olhar o que já foi feito e trabalhar no que ainda não foi. |
| D04 | 2026-10-13 | Tabelas de custo mensal: construir vs. comprar | Eu | — | Pedir preços verificados de APIs (OpenAI, Anthropic e os modelos do índice da Artificial Analysis), APIs gratuitas e ferramentas de mercado | Básico de qq projeto: o orçamento. |
| D05 | 2026-10-13 | Escopo | IA, após a revisão dos PRs | Cortar de 10 entregáveis para os 4 obrigatórios + 3 diferenciais (rascunhos pt-BR avaliados; construir vs. comprar com ponto de equilíbrio; teto de ruído de rótulo com limiar calibrado) | Aceito | Otimização de recursos |
| D06 | 2026-10-13 | Idioma da submissão | IA | pt-BR com valores em R$ (36 de 38 PRs do 002 estão em português; o avaliador escreve em pt-BR) | Aceito | Padronização. |
| D07 | 2026-10-13 | Ambiente Python | IA ofereceu 3 opções | uv com lockfile (reprodutível para o avaliador) | uv | Sem comentários |
| D08 | 2026-10-13 | Obtenção dos dados | IA ofereceu 3 opções | Script de download com token Kaggle; nenhum CSV no repositório | Token Kaggle + script | Mais eficiente em tempos de IA |
| D09 | 2026-10-13 | Proteção de segredos | Eu | — | Bloquear tokens `KGAT_` no `stage.sh`, ignorar `access_token`, revogar o token antes da submissão | Proteger minha API em um repositorio publico. |
