# Previsões e resultados

> As previsões estão em `00-hipoteses.md`, commitadas antes do download dos dados (commit `d899d17`).
> Cada resultado aponta para o arquivo que o produziu. Atualizado a cada fase.

## Previsões numéricas

| # | Previsão | Resultado | Acertou? | Fonte |
|---|---|---|---|---|
| P1 | 8.469 tickets no Dataset 1 (influenciada pelos PRs) | 8.469 registros; 0 duplicados; 0 IDs repetidos. As 29.808 linhas físicas vêm de 6.150 descrições com quebra de linha | Sim | `solution/outputs/audit/audit_d1.json` → `counts` |
| P2 | Spearman entre resolução e CSAT entre −0,10 e +0,10 (influenciada pelos PRs) | ρ = 0,022 (p = 0,25, n = 2.769); só durações não negativas: ρ = 0,003 (p = 0,92, n = 1.404) | Sim | `audit_d1.json` → `csat` |
| P3 | Acurácia de TF-IDF + regressão logística ≈ 86% | Pendente (fase do classificador) | | |
| P4 | ~20% dos erros auditados ligados a ruído de rótulo | Pendente (X1). Não há duplicatas exatas no Dataset 2, então nenhum conflito de rótulo aparece por esse caminho | | `audit_d2.json` → `counts` |
| P5 | ~50% dos tickets roteáveis com precisão ≥ 95% | Pendente | | |
| P6 | Queda de ~40 p.p. em português | Pendente | | |
| P7 | Construir fica mais barato a partir de ~20 mil tickets/mês | Pendente (X3) | | |
| P8 | ~65% dos rascunhos aprovados sem edição | Pendente (X2) | | |

## Hipóteses qualitativas

| Hipótese | Resultado | Fonte |
|---|---|---|
| 1.1 Sinais de dado sintético: descrição padronizada demais | Confirmado: duas frases fixas aparecem em cerca de 6.000 das 8.469 descrições, e `{product_purchased}` em 100% | `audit_d1.json` → `description_text` |
| 1.1 Combinação que não faz sentido | Confirmado: assunto e tipo não se relacionam (V de Cramér 0,03; p = 0,98) | `audit_d1.json` → `associations` |
| 1.1 Distribuição muito regular | Confirmado: tipo, prioridade, canal, status, produto, CSAT e idade indistinguíveis de partes iguais | `audit_d1.json` → `categoricals`, `csat`, `age` |
| 1.1 Diferença clara entre canal e tipo de problema | Não confirmado: canal e tipo não se relacionam (V de Cramér 0,02; p = 0,46) | `audit_d1.json` → `associations.channel_vs_type` |
| 1.1 Correlação perto de zero sozinha não prova que é sintético | Mantido: o veredito de dado sintético se apoia em oito sinais, não na correlação | `docs/auditoria-dados.md` |
| 2.2 Access é a categoria mais difícil | Pendente (fase do classificador) | |
