---
titulo: Modelagem do absenteísmo escolar com modelos lineares generalizados
subtitulo: Dias de ausência de alunos modelados como contagem, com Poisson, quase-Poisson e binomial negativa, seleção por AIC e teste da razão de verossimilhanças.
descricao: Estudo de caso: modelagem de dias de ausência escolar com GLMs Poisson, quase-Poisson e binomial negativa, com seleção por AIC e LRT, em R.
linguagens: R
tags: Modelos lineares generalizados, Dados de contagem, Superdispersão, Binomial negativa, Seleção por AIC, Teste da razão de verossimilhanças
repo: modelos-lineares-generalizados
autores: Ana Rosa Nascimento
rascunho: sim
---

## Resumo

Neste estudo, modelamos o **número de dias de ausência** de alunos de uma escola australiana em função de origem étnica, sexo, faixa etária e grupo de aprendizagem. Como a variável é uma contagem com muita variabilidade, o modelo de Poisson, que é o ponto de partida natural, mostra **superdispersão** forte: a variância observada é cerca de 16 vezes a média. Por isso, o modelo final usa a **binomial negativa**, que reduz o AIC de cerca de 2151 para 1105 e corrige os erros-padrão. O efeito da idade depende da origem étnica, e a interação entre os dois é o principal achado.

## Dados

- **Fonte:** conjunto `quine`, do pacote `MASS` do R.
- **Observações:** 146 alunos.
- **Resposta:** `Days`, número de dias de ausência no ano letivo. Média de 16,5 dias e variância de 264. Cerca de 6% dos alunos não faltaram nenhum dia.
- **Covariáveis:**
  - `Eth`: origem étnica (aborígene ou não aborígene);
  - `Sex`: sexo (masculino ou feminino);
  - `Age`: faixa de idade escolar (F0 a F3, com F0 como referência);
  - `Lrn`: grupo de aprendizagem (aprendizagem normal ou lenta).

![Distribuição do número de dias de ausência](assets/modelos-lineares-generalizados/dias_ausencia.png "Distribuição do número de dias de ausência: forte assimetria à direita e muitos valores baixos.")

## Metodologia

### 1. Modelo de Poisson como referência

Supomos que o número de dias de ausência $Y_i$ segue uma distribuição de Poisson com média $\mu_i$, e que o logaritmo da média é uma combinação linear das covariáveis:

$$\log \mu_i = \log \mathbb{E}[Y_i \mid x_i] = x_i^\top \beta$$

Na Poisson, a variância é igual à média. Os dados não respeitam isso, então o modelo serve de referência e não de conclusão.

### 2. Seleção de modelos

Comparamos cinco especificações, do modelo nulo ao modelo com todas as interações de interesse:

- **M0:** só o intercepto;
- **M1:** efeitos principais de `Eth`, `Sex`, `Age` e `Lrn`;
- **M2:** M1 mais a interação `Eth × Sex`;
- **M3:** M1 mais a interação `Age × Lrn`;
- **M4:** M1 mais as interações `Eth × Age` e `Age × Lrn`.

O critério principal é o AIC, dado por $AIC = -2\,\ell(\hat\beta) + 2p$, em que $p$ é o número de parâmetros. Para comparar modelos aninhados, usamos o teste da razão de verossimilhanças (LRT).

### 3. Superdispersão e modelos alternativos

A dispersão de Pearson estima o quanto a variância excede a da Poisson:

$$\hat\phi = \frac{\sum_i r_{P,i}^2}{n - p}$$

Quando $\hat\phi \gg 1$, há superdispersão. Usamos dois modelos para corrigir isso:

- **Quase-Poisson:** mantém a média da Poisson e assume variância $\phi\,\mu$. Corrige só os erros-padrão.
- **Binomial negativa:** assume variância $\mu + \mu^2/\theta$, com $\theta$ estimado. Modela a superdispersão na própria distribuição.

### 4. Diagnóstico

Verificamos os resíduos de desvio contra os valores ajustados, o QQ-plot com envelope de 95% e a distância de Cook para identificar observações influentes.

## Resultados

### Seleção entre as especificações de Poisson

| Modelo | Termos | AIC |
|---|---|---|
| M0 | intercepto | 2664,0 |
| M1 | Eth + Sex + Age + Lrn | 2299,2 |
| M2 | M1 + Eth × Sex | 2279,4 |
| M3 | M1 + Age × Lrn | 2294,4 |
| M4 original | M1 + Eth × Age + Age × Lrn | 2147,7 |
| M4 corrigido | M1 + Eth × Age | 2151,3 |

O M4 original tem o menor AIC entre os modelos de Poisson, mas a combinação de idade F3 com aprendizagem lenta não tem observações, e a matriz de informação fica singular. Por isso removemos a interação `Age × Lrn` e usamos o **M4 corrigido**, que é o modelo base da comparação com a binomial negativa.

A dispersão de Pearson do M4 corrigido é $\hat\phi \approx 11{,}7$, o que confirma a superdispersão. Com o ajuste quase-Poisson, os erros-padrão ficam cerca de $\sqrt{11{,}7} \approx 3{,}4$ vezes maiores.

### Binomial negativa (modelo final)

O parâmetro estimado é $\hat\theta \approx 1{,}38$, e o AIC cai de 2151,3 (Poisson) para **1104,7**. A tabela mostra as razões de médias, $\exp(\hat\beta)$, com a referência sendo não aborígene, do sexo masculino, na faixa F0 e com aprendizagem normal.

| Efeito | Razão de médias | Valor-p |
|---|---|---|
| Intercepto (referência) | 14,94 | — |
| Origem aborígene (na faixa F0) | 0,95 | 0,868 |
| Sexo feminino | 0,89 | 0,467 |
| Faixa F1 (não aborígene) | 0,44 | 0,009 |
| Faixa F2 (não aborígene) | 0,62 | 0,136 |
| Faixa F3 (não aborígene) | 1,35 | 0,360 |
| Aprendizagem lenta | 1,26 | 0,207 |
| Aborígene × F1 | 2,46 | 0,040 |
| Aborígene × F2 | 3,26 | 0,008 |
| Aborígene × F3 | 1,11 | 0,826 |

Como a origem étnica entra na interação, o efeito da idade é diferente para cada grupo. Para alunos não aborígenes, a faixa F1 tem cerca de 56% menos dias de ausência que a F0. Para alunos aborígenes, a diferença entre F0 e F1 desaparece (razão de cerca de 1,09) e a F2 passa a ter cerca de o dobro da F0 (razão de cerca de 2,03).

Sexo e grupo de aprendizagem não são significativos isoladamente neste ajuste.

![Resíduos de desvio e distância de Cook para os modelos de Poisson e binomial negativa](assets/modelos-lineares-generalizados/residuos_poisson_vs_nb.png "Resíduos de desvio contra valores ajustados (acima) e distância de Cook (abaixo), para Poisson (esquerda) e binomial negativa (direita).")

Os resíduos de desvio da Poisson chegam a cerca de 7 em módulo, enquanto os da binomial negativa ficam aproximadamente entre -2,5 e 2,5. A distância de Cook da binomial negativa tem poucos pontos acima do limiar, sem observações que dominem o ajuste.

![QQ-plot com envelope de 95% para o modelo binomial negativo](assets/modelos-lineares-generalizados/qqplot_envelope_nb.png "QQ-plot dos resíduos quantílicos com envelope de 95% para o modelo binomial negativo. A maioria dos pontos fica dentro do envelope; os extremos inferiores ficam levemente fora.")

## Limitações e cuidados

- **Amostra pequena:** 146 alunos de uma única escola limitam a generalização.
- **Células esparsas:** algumas combinações de origem étnica, idade e grupo de aprendizagem têm poucas observações, então os intervalos das interações são largos.
- **Testes aproximados:** o R avisou que os testes LRT da binomial negativa foram feitos sem reestimar $\theta$, o que os torna aproximados.
- **Alternativas não exploradas:** modelos de excesso de zeros (como zero-inflated) não foram comparados, embora a proporção de zeros seja baixa.
- **Validação:** a avaliação dos modelos é por AIC, LRT e diagnósticos. Não há validação cruzada no código.

## Reprodução

```r
# na raiz do repositório
Rscript "quine/trabalho_ana_dados_contagem.R"
```

Pacotes: `MASS` (modelo binomial negativo e dados `quine`), `ggplot2`, `dplyr` e `emmeans`.
