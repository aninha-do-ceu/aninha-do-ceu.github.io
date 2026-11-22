---
titulo: Modelos de dose–resposta com regressão binária para mortalidade de larvas
subtitulo: Mortalidade por sexo ajustada com modelos binomiais e funções de ligação logit, probit e cloglog, com estimação de doses letais e bandas simultâneas.
descricao: Estudo de caso: modelos de dose–resposta com GLM binomial (logit, probit e cloglog) para mortalidade de larvas por sexo, com doses letais e bandas simultâneas, em R.
linguagens: R
tags: Dose–resposta, Regressão binária, Modelos lineares generalizados, Dose letal, Função de ligação, Bandas simultâneas
repo: modelos-lineares-generalizados
autores: Ana Rosa Nascimento
---

## Dose–resposta

### Variáveis

| Variável | Descrição |
|---|---|
| `dose` | Variável que explicita a dose aplicada |
| `x` | Log da dose aplicada |
| `mortos` | Número de larvas mortas |
| `sexo` | Sexo da larva |
| `expostos` | Número de larvas expostas por sexo e dose |

### Conclusão

Em conclusão, a análise do modelo ajustado permitiu caracterizar a relação entre a log-dose e a probabilidade de mortalidade, bem como comparar o comportamento dos dois sexos. Os resultados indicam que as fêmeas apresentam, em geral, menor índice de mortalidade do que os machos para doses comparáveis, sugerindo menor suscetibilidade ao efeito letal do agente em estudo.

A análise dos resíduos revelou uma distribuição aleatória e uma concordância satisfatória com a distribuição teórica no gráfico Q-Q. Já os diagnósticos baseados na distância de Cook e na alavancagem (leverage) não identificaram observações que ultrapassassem os limites de referência considerados.

A estimação intervalar, feita com intervalos de confiança pontuais de 95% e com bandas de confiança simultâneas construídas pelo método delta, permitiu avaliar a incerteza associada às curvas estimadas. Verificou-se, porém, que a observação correspondente a 100% de mortalidade nos machos e a observação correspondente a 0% de mortalidade nas fêmeas ficam fora das respectivas bandas simultâneas. Isso evidencia discrepâncias pontuais entre os dados observados e o comportamento previsto pelo modelo.

Para avaliar a discrepância dessas observações, foram utilizadas a distância de Cook e a alavancagem, além do reajuste do modelo selecionado removendo observações, uma a uma. Apesar de estarem fora das bandas, essas observações não foram as que mais aumentaram ou diminuíram as estimativas da dose letal de 50% por sexo.

## Reprodução

```r
# na pasta do repositório modelos-lineares-generalizados
Rscript "modelo dose resposta/codigo_dose_resposta.R"
```

Pacotes: `ggplot2`, `dplyr`, `tidyr` e `patchwork`. Os dados (`budworm`) estão no arquivo `budworm.rda`, na mesma pasta.
