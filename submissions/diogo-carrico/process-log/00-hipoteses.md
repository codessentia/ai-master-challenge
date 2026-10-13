# 00 — Hipóteses antes de abrir os dados

> Escrito por mim, antes de abrir qualquer linha dos datasets.
> Commit deste arquivo: ver `git log -- process-log/00-hipoteses.md` (a data do commit é a prova).
> Respostas curtas, nas minhas palavras. Não usar IA para redigir este arquivo.

## 0. O que eu já sei antes de começar

**0.1** O que aprendi lendo os PRs públicos de outros candidatos (Challenge 002) e o que considero já estabelecido — e o que ainda quero verificar por conta própria?

> 

**0.2** Da minha experiência profissional: onde uma operação de suporte real costuma perder tempo? Dê um exemplo concreto que já vivi ou vi.

> 

## 1. Dataset 1 — tickets de suporte (~30K segundo o brief)

**1.1** O que espero encontrar quando abrir os dados? Quais sinais me fariam concluir que é sintético?

> 

**1.2** Se o Dataset 1 for sintético, o que muda na resposta às três perguntas do Diretor? O que ainda dá para responder com honestidade?

> 

**1.3** Se eu não puder medir gargalos nem drivers de CSAT nestes dados, o que eu recomendaria medir primeiro numa operação real — e por quê?

> 

## 2. Dataset 2 — tickets de TI (~48K, 8 categorias)

**2.1** Outros candidatos ficaram em 84–87% de acurácia. Por que eu acho que existe esse teto? Quanto do erro restante eu acho que é ruído de rótulo (rótulos errados ou ambíguos) e não limitação do modelo?

> 

**2.2** Qual categoria espero que seja a mais difícil, e por quê?

> 

## 3. Automação — onde IA entra e onde não entra

**3.1** O que eu nunca automatizaria num suporte ao cliente, mesmo com 99% de acurácia? Por quê (risco, regulação, relação com o cliente)?

> 

**3.2** Qual é o custo de um ticket roteado errado comparado ao custo da triagem manual? Que precisão mínima eu exigiria antes de rotear automaticamente — e o que acontece com o resto?

> 

## 4. Rascunhos de resposta em pt-BR (diferencial 1)

**4.1** O que torna um rascunho de resposta aceitável para um agente enviar? O que o torna inaceitável (promessa indevida, tom, informação inventada)?

> 

**4.2** Como eu saberia se os rascunhos estão bons sem confiar só na opinião de outra IA?

> 

## 5. Construir vs. comprar (diferencial 2)

**5.1** Para 2.500 tickets/mês e ~10 agentes, meu palpite antes de calcular: construir ou comprar (Zendesk, Intercom Fin, Freshdesk...)? Por quê?

> 

**5.2** O que normalmente se esquece no custo de "construir"?

> 

## 6. Previsões numéricas (pré-registradas)

Preencho a coluna "Minha previsão" agora. As colunas "Resultado" e "Errei por quê?" ficam para depois da medição.

| # | Pergunta | Minha previsão | Como vou medir | Resultado | Errei por quê? |
|---|---|---|---|---|---|
| P1 | Nº real de tickets no Dataset 1 | | Contagem após parsing correto do CSV | | |
| P2 | Correlação entre tempo de resolução e CSAT | | Spearman + teste de permutação | | |
| P3 | Acurácia de TF-IDF + regressão logística no Dataset 2 (teste) | | Split estratificado, conjunto de teste intocado | | |
| P4 | % do erro explicado por ruído de rótulo | | Duplicatas conflitantes + reetiquetagem manual de amostra | | |
| P5 | % dos tickets que dá para rotear automaticamente com ≥95% de precisão | | Limiar calibrado na validação, medido no teste | | |
| P6 | Queda de acurácia ao aplicar o modelo em texto em português | | Amostra traduzida + tickets escritos à mão | | |
| P7 | Volume mensal a partir do qual construir sai mais barato que comprar | | Modelo de custo com preços datados e citados | | |
| P8 | % dos rascunhos pt-BR aprovados sem edição pela minha rubrica | | Conjunto de teste de 60–100 mensagens, incluindo casos adversariais | | |

## 7. O que me faria mudar de ideia

**7.1** Que resultado me faria abandonar ou mudar a proposta de automação?

> 

## 8. Divisão de papéis

**8.1** O que eu decido e verifico pessoalmente, e o que delego à IA? Onde não confio na IA sem checar?

> 
