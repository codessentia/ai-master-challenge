# Classificador de tickets

> Gerado por `solution/scripts/write_classifier_report.py` a partir de `solution/outputs/classifier/`.
> Não editar à mão: rode `uv run python scripts/train_classifier.py` e depois este script.

Um classificador TF-IDF + SVM linear acerta 86,7% dos tickets de TI do Dataset 2 (macro-F1 86,5%). Com um limiar por classe, ele roteia sozinho 64,9% dos tickets com 97,0% de precisão, e o resto vai para a triagem humana. Nos tickets do Dataset 1 ele não serve, e um guarda de vocabulário barra 99,99% deles antes de qualquer roteamento.

## Dados e divisão

- 47.837 tickets em 8 classes.
- Quase-duplicatas (similaridade de cosseno TF-IDF de pelo menos 0,9): 1.286 grupos com 5.630 tickets. Cada grupo fica inteiro de um lado da divisão, para o teste não ver textos quase iguais aos do treino.
- 105 desses grupos (617 tickets) têm rótulos diferentes para textos quase iguais. É a primeira evidência de ruído de rótulo (X1); a lista está em `solution/outputs/classifier/near_duplicate_conflicts.csv`.
- Divisão estratificada: treino 33.185, calibração 4.740, escolha de limiar 4.741 e teste 5.171. O teste foi usado uma única vez, no fim.

## Escolha do modelo

| Modelo | Macro-F1 na validação |
| --- | --- |
| TF-IDF + SVM linear (C = 1,0) (escolhido) | 86,5% |
| TF-IDF + regressão logística (C = 16) | 85,9% |
| TF-IDF + regressão logística (C = 4) | 85,6% |
| TF-IDF + SVM linear (C = 0,25) | 85,3% |
| TF-IDF + regressão logística (C = 1) | 83,6% |
| TF-IDF + Naive Bayes complementar (alfa 0,5) | 80,7% |
| TF-IDF + Naive Bayes complementar (alfa 0,1) | 79,6% |

## Resultado no teste

Acurácia 86,7% (IC 95% 85,8% a 87,6%); macro-F1 86,5% (IC 95% 85,5% a 87,6%). A classe mais difícil é Administrative rights, com F1 de 78,9%.

| Classe | Precisão | Recall | F1 | Tickets no teste |
| --- | --- | --- | --- | --- |
| Administrative rights | 88,7% | 71,0% | 78,9% | 176 |
| Miscellaneous | 87,4% | 77,8% | 82,3% | 706 |
| Hardware | 79,5% | 89,2% | 84,0% | 1.361 |
| HR Support | 86,3% | 84,6% | 85,5% | 1.091 |
| Internal Project | 87,4% | 85,3% | 86,3% | 211 |
| Storage | 89,5% | 86,3% | 87,9% | 277 |
| Access | 91,0% | 86,7% | 88,8% | 712 |
| Purchase | 97,4% | 100,0% | 98,7% | 637 |

Matriz de confusão do teste (linhas: classe real; colunas: classe prevista). Hardware é o destino mais comum dos erros.

| Real \ Previsto | Access | Administrative rights | HR Support | Hardware | Internal Project | Miscellaneous | Purchase | Storage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Access** | **617** | 3 | 28 | 46 | 0 | 11 | 0 | 7 |
| **Administrative rights** | 1 | **125** | 5 | 37 | 1 | 6 | 0 | 1 |
| **HR Support** | 16 | 2 | **923** | 110 | 6 | 22 | 1 | 11 |
| **Hardware** | 24 | 8 | 61 | **1.214** | 8 | 27 | 13 | 6 |
| **Internal Project** | 3 | 0 | 8 | 14 | **180** | 4 | 1 | 1 |
| **Miscellaneous** | 16 | 2 | 36 | 88 | 11 | **549** | 2 | 2 |
| **Purchase** | 0 | 0 | 0 | 0 | 0 | 0 | **637** | 0 |
| **Storage** | 1 | 1 | 8 | 19 | 0 | 9 | 0 | **239** |

## Calibração

Probabilidades calibradas pelo método sigmoide, ajustado só na parte de calibração. Erro de calibração esperado no teste: 3,6%.

## Regras de roteamento

O alvo é o da hipótese 3.2 do Diogo: pelo menos 95% de precisão nos tickets que a IA roteia sozinha, olhando por categoria. Cada limiar foi escolhido na parte de validação de modo que o limite inferior do intervalo de 95% da precisão fique acima do alvo.

| Regra | Limiar | Cobertura | Precisão (IC 95%) | Ponto fraco |
| --- | --- | --- | --- | --- |
| Limiar único escolhido para 95% de precisão | 0,735 | 74,2% | 95,9% (95,2% a 96,4%) | Hardware com 92,9% |
| **Limiares por classe** (adotado) | um por classe | **64,9%** | **97,0%** (96,4% a 97,5%) | Administrative rights nunca é roteado |
| Limiar pelo custo do erro (4 min de triagem contra 10 min de retrabalho) | 0,60 | 85,8% | 92,4% (91,6% a 93,2%) | Abaixo dos 95% exigidos |

Limiares por classe, medidos no teste:

| Classe | Limiar | Previstos | Roteados | Precisão (IC 95%) |
| --- | --- | --- | --- | --- |
| Access | 0,65 | 678 | 571 | 97,0% (95,3% a 98,1%) |
| Administrative rights | — | 141 | 0 | não roteado |
| HR Support | 0,75 | 1.069 | 752 | 95,6% (93,9% a 96,9%) |
| Hardware | 0,86 | 1.528 | 760 | 96,8% (95,3% a 97,9%) |
| Internal Project | 0,84 | 206 | 106 | 99,1% (94,8% a 99,8%) |
| Miscellaneous | 0,86 | 628 | 298 | 99,3% (97,6% a 99,8%) |
| Purchase | 0,63 | 654 | 648 | 98,3% (97,0% a 99,0%) |
| Storage | 0,68 | 267 | 219 | 94,5% (90,7% a 96,8%) |

Storage ficou em 94,5% no teste, abaixo do alvo, embora a validação garantisse 95%: é variação de amostra, e o intervalo vai de 90,7% a 96,8%. No piloto, a precisão de cada classe é acompanhada e o limiar sobe se ela ficar abaixo do alvo.

## Desvio de domínio: o modelo nos tickets do Dataset 1

O modelo aprendeu com tickets de TI e não com suporte ao cliente. Aplicado às 8.469 descrições do Dataset 1, ele prevê Hardware 83,5%, Access 7,7%, Miscellaneous 5,8%, com confiança mediana de 73,8%. Sem proteção, 50,6% passariam do limiar único e 20,8% dos limiares por classe: confiança alta não garante que o ticket seja do domínio.

O guarda mede quanto do vocabulário do ticket o modelo viu no treino. Na validação, a mediana é 100%; no Dataset 1, 78,0%. Com o corte em 92,3% (o 1º percentil da validação), o guarda manda para humanos 99,99% dos tickets do Dataset 1 e só 0,95% dos tickets de teste do Dataset 2.
