---
titulo: Modelos de contagem para dias de ausência escolar (dados quine)
subtitulo: Metodologia para modelar dias de ausência com Poisson, quase-Poisson e binomial negativa, com validação K-fold.
descricao: Estudo de caso: metodologia de modelos de contagem (Poisson, quase-Poisson e binomial negativa) para dias de ausência escolar com o conjunto quine, em R.
linguagens: R
tags: Dados de contagem, Modelos lineares generalizados, Poisson, Quase-Poisson, Binomial negativa, Validação Cruzada, Validação K-fold
repo: modelos-lineares-generalizados
autores: Ana Rosa Nascimento
---

## Metodologia

### Sobre os Dados

O conjunto de dados é o quine, disponível no pacote `MASS` do R. As variáveis contidas no conjunto de dados são:

- **Days:** variável correspondente ao número de dias que o aluno faltou no ano escolar;
- **Eth:** variável binária que indica a origem étnica do aluno: (A) aborígene ou (N) não aborígene;
- **Sex:** variável que indica o gênero do aluno: (F) feminino ou (M) masculino;
- **Age:** grupo escolar: F0, F1, F2 ou F3;
- **Lrn:** situação de aprendizagem: (AL) média ou (SL) lenta.

A variável resposta da modelagem é a variável Days, cujo suporte é discreto positivo. As covariáveis são as demais variáveis Eth, Sex, Age e Lrn. Assim, deseja-se entender se a origem étnica, o gênero, o grupo escolar inserido e a situação de aprendizagem do aluno afetam a sua frequência às aulas.

Os algoritmos serão implementados utilizando a linguagem R.

$$
Y_i = \text{Days}_i, \quad Y_i \in \{0, 1, 2, 3, \dots\}
$$

Seja $\mu_i$ o número médio de dias de ausência para alunos com características $\mathbf{x}_i$, temos

$$
\mu_i = E(Y_i \mid \mathbf{x}_i)
$$

Como Days é discreto positivo, o modelo apropriado é um modelo de contagem. Se utilizássemos o modelo Normal para modelar o número médio de dias de ausência, obteríamos estimativas na escala contínua real, ou seja, poderíamos gerar algo como -33,2 dias de ausência, o que não faria sentido. Um modelo de contagem tem como suporte a escala discreta e positiva (0, 1, 2, 3, ...), sendo mais adequado à modelagem.

A variável Age é categórica, representando os grupos escolares dos alunos. Ela será implementada como uma variável categórica nominal. Apesar de haver uma hierarquia natural, tratá-la como ordinal muda a esquematização do modelo: o modelo gerará um coeficiente para todas as categorias e terá como suposição um efeito associado ao aumento do nível (Ex: o número de faltas aumentar quando o aluno passa de F0 para F1), o que pode não ocorrer. Com a especificação como nominal, cada categoria terá um coeficiente associado, podendo-se testar os efeitos de forma única.

Uma das hipóteses a serem testadas é referente à variável de origem étnica, ao se testar se alunos de origem aborígene acabam faltando mais em comparação aos alunos de origem não aborígene. A outra hipótese a ser testada é se alunos com aprendizagem mais lenta acabam faltando mais em comparação aos que possuem aprendizagem média.

### Formulação Estatística

O modelo proposto é o modelo Poisson. Seja a variável aleatória $Y_i \mid \mathbf{x}_i \sim \text{Poisson}(\mu_i)$, cuja função massa de probabilidade é definida por

$$
P(y_i \mid \mathbf{x}_i) = \frac{e^{-\mu_i} \, \mu_i^{y_i}}{y_i!}, \quad y_i \in \{0, 1, 2, 3, \dots\}
$$

O suporte da variável são os discretos positivos, sua média é $\mu_i$ e sua variância também é $\mu_i$. O índice de dispersão avalia o grau de variabilidade de uma variável aleatória:

$$
I_{Po} = \frac{E(Y_i)}{\operatorname{Var}(Y_i)} = \frac{\mu_i}{\mu_i} = 1
$$

Como o índice de dispersão é 1, temos o caso de equidispersão, ou seja, média igual à variância.

Considerando a função de ligação logarítmica, temos

$$
\begin{aligned}
\log(\mu_i) &= \eta_i = \mathbf{x}_i^\top \boldsymbol{\beta} \\
\mu_i &= e^{\mathbf{x}_i^\top \boldsymbol{\beta}}
\end{aligned}
$$

com $\mathbf{x}_i \in \mathbb{R}^p$ e $\boldsymbol{\beta} \in \mathbb{R}^p$, de modo que o preditor linear também pertence aos reais. Com a aplicação da exponencial na função de ligação logarítmica, $\exp(\mathbf{x}_i^\top \boldsymbol{\beta}) > 0$, e o valor esperado da variável resposta fica estritamente positivo, sendo mais adequado à modelagem de fenômenos de contagem.

Considerando uma variável dicotômica $x_j$, temos que $E(Y \mid x_j = 1) = e^{\beta_0 + \beta_j}$ e $E(Y \mid x_j = 0) = e^{\beta_0}$. Assim, $e^{\beta_j}$ é uma razão de médias, fixadas as demais covariáveis, pois

$$
\frac{E(Y \mid x_j = 1)}{E(Y \mid x_j = 0)} = e^{\beta_j}
$$

De modo que $100 \times (e^{\beta_j} - 1)$ é o acréscimo ou decréscimo percentual do efeito relacionado à variável dicotômica em relação à categoria de referência.

Para além da função de variância da distribuição Poisson, temos também outras especificações que geram distribuições diferentes, a Quase-Poisson e a Binomial Negativa:

$$
\begin{aligned}
\operatorname{Var}(Y_i \mid \mathbf{x}_i) &= \phi \, \mu_i \\
\operatorname{Var}(Y_i \mid \mathbf{x}_i) &= \mu_i + \alpha \, \mu_i^2
\end{aligned}
$$

Na primeira especificação, o parâmetro $\phi$ também segue uma relação linear como o da Poisson, mas o coeficiente associado pode ser diferente de 1, sendo proporcional à média. Para a segunda especificação, a relação média-variância passa a ter também um componente quadrático, sendo mais adequada às situações de sobredispersão.

A Quase-Poisson não gera uma distribuição completa, pois não possui uma função de probabilidade completa, e por isso não é possível obter a verossimilhança. Da mesma forma, o AIC não é obtido diretamente.

As diferentes especificações são os modelos:

**Especificações dos Modelos**

| Modelo | Especificação |
|---|---|
| M0 | $\eta_i = \beta_0$ |
| M1 | $\eta_i = \beta_0 + Eth_i + Sex_i + Age_i + Lrn_i$ |
| M2 | $M_1 + Eth_i : Sex_i$ |
| M3 | $M_1 + Age_i : Lrn_i$ |
| M4 | $M_1 + Eth_i : Age_i + Age_i : Lrn_i$ |

O teste de razão de verossimilhanças será utilizado para avaliar o acréscimo de variáveis nos modelos aninhados. Considerando uma variável com $(n+1)$ níveis, as hipóteses são

$$
H_0: \beta_1 = \beta_2 = \dots = \beta_n = 0 \quad \text{vs.} \quad H_1: \beta_i \neq 0, \; i \in \{1, 2, \dots, n\}
$$

A hipótese nula é rejeitada se, com os modelos $M_0 \subset M_1$, a estatística for maior que o valor da distribuição qui-quadrado com $q$ graus de liberdade (número de variáveis acrescidas) e nível de significância $\alpha$: $LR = 2 \left(\ell(\hat{\theta}_1) - \ell(\hat{\theta}_0)\right) > \chi^2_{q,\,1-\alpha}$.

Adicionalmente, o pacote emmeans do R permite comparar a igualdade de médias entre diferentes contrastes e se baseia no teste de Wald. Ele será utilizado para comparar as ausências dos diferentes perfis dos alunos.

Não se deve interpretar os efeitos das variáveis sobre o número médio esperado de faltas como causalidade. Embora o modelo associe o número de faltas às covariáveis, uma variável não necessariamente vai diminuir ou aumentar faltas por si só. Pode-se afirmar que, a partir dos coeficientes, tal grupo esteve associado a uma razão de médias tal, mas não que um indivíduo pertencente a este grupo necessariamente terá um número de ausências relacionado a essa razão. Além disso, há fatores externos que devem ser levados em conta na interpretação dos resultados.

Para avaliar a adequação dos modelos quanto à análise residual, serão utilizadas as dispersões baseadas nos resíduos de Pearson e de desvio. Valores próximos de 1 indicam que o ajuste pela distribuição Poisson retorna uma equidispersão, sendo aderente. Valores abaixo de 1 indicam subdispersão e valores acima de 1 indicam sobredispersão. Essas medidas não são definitivas de adequação ou inadequação, pois são medidas globais, o que pode mascarar observações influentes e padrões sistemáticos nos resíduos. Desta maneira, os modelos Quase-Poisson e Binomial Negativa também serão avaliados.

Ademais, a validação K-fold (com K = 10, neste caso) será utilizada para avaliar a adequação. Ao particionar a base em K partições, as três distribuições serão ajustadas considerando diferentes conjuntos de treino e um conjunto de validação por fold. Para calcular a performance de cada modelo, serão utilizadas as métricas Desvio Médio de Poisson, o Erro Absoluto Médio (MAE) e a Raiz do Erro Quadrático Médio (RMSE).

Ao final, serão mostradas estas últimas métricas, junto às referentes à dispersão (Pearson e desvio) e ao AIC, como um compilado de resultados.

## Análise Exploratória

Não há valores ausentes, e as categorias presentes nas variáveis são as categorias previamente explicitadas. Para as variáveis Eth, Sex, Age e Lrn, temos as frequências:

**Categorias únicas das variáveis do conjunto de dados**

| Variável | Categoria | Frequência |
|---|---|---|
| Eth | A | 69 |
| | N | 77 |
| Sex | F | 80 |
| | M | 66 |
| Age | F0 | 27 |
| | F1 | 46 |
| | F2 | 40 |
| | F3 | 33 |
| Lrn | AL | 83 |
| | SL | 63 |

As categorias de referência para cada variável estão listadas na tabela abaixo. Busca-se analisar se grupos minoritários têm um número de faltas consideravelmente diferente do de homens não aborígenes no grupo escolar F0 com situação de aprendizagem média. Esta escolha afeta os coeficientes da regressão, uma vez que as variáveis dummy representam as categorias em relação à categoria de referência. Todavia, ela não afeta os valores ajustados, pois o modelo é o mesmo. Um exemplo seria se o vetor de entrada tiver como gênero "Masculino": a variável dummy da categoria "Feminino" teria como entrada o valor "0". Por isso, as comparações globais também não mudam, pois a comparação busca capturar a contribuição da variável considerando o modelo como um todo. Todas as categorias possuem um coeficiente associado, sendo somente uma delas a referência.

**Categorias de referência das variáveis categóricas**

| Variável | Categoria de referência |
|---|---|
| Eth | N |
| Sex | M |
| Age | F0 |
| Lrn | AL |

As estatísticas associadas à variável Days estão apresentadas na tabela abaixo. O valor mínimo é 0 dias de ausência, com o máximo sendo 81 dias. Além disso, 75% dos alunos têm menos de 23 dias de faltas. A média de faltas é 16,46, enquanto a mediana é 11, evidenciando a assimetria à direita, e a variância é 264,17. O fato de a variância ser muito maior em magnitude do que a média contribui para uma evidência de não adequabilidade do modelo Poisson, pois este tem como pressuposto que a variância dos dados é igual à média. Esse pressuposto não é cumprido pelas estatísticas, o que gera um erro maior nos valores ajustados e nas previsões.

**Estatísticas da variável Days**

| Mínimo | 25% | 50% | 75% | Média | Máximo | Variância | Desvio-padrão |
|---|---|---|---|---|---|---|---|
| 0 | 5 | 11 | 22,75 | 16,46 | 81 | 264,17 | 16,25 |

A variável Days tem uma distribuição assimétrica à direita, com a maior parte das ausências sendo menor que 40 dias e uma concentração de valores entre 0 e 10 dias, com a moda sendo 5 dias de faltas. A mediana de dias de falta é 11 dias, ou seja, 50% do número de faltas é igual ou abaixo de 11 dias. A assimetria da distribuição também já pode indicar uma falta de adequabilidade do modelo Poisson, pois os valores são centrados na média $\mu$. Além disso,

![Histograma da variável Days](assets/dados-de-contagem-quine/hist_days.png "Histograma da variável Days")

A proporção de zeros na variável é 6,164%, e isso não implica, por si só, a inflação de zeros, pois, dependendo dos parâmetros do modelo final, pode haver uma proporção associada ao zero.

Comparando as distribuições de faltas por origem étnica, vemos uma maior uniformização para alunos aborígenes, enquanto alunos não aborígenes seguem a distribuição assimétrica original. A média e a mediana de faltas para os grupos são bem diferentes, bem como a variância. O tamanho de cada grupo é relativamente próximo.

![Histograma da variável Days por origem étnica](assets/dados-de-contagem-quine/hist_days_eth.png "Histograma da variável Days por origem étnica")

**Estatísticas por nível de Eth**

| Eth | Mediana | Média | Variância | Tamanho |
|---|---|---|---|---|
| A | 15 | 21,2 | 314 | 69 |
| N | 7 | 12,2 | 184 | 77 |

Para a variável de gênero, vemos, pelas estatísticas e distribuições de faltas, que mulheres faltam menos que homens. A assimetria da distribuição original se mantém. O tamanho de cada grupo também é relativamente próximo, com 55% das observações pertencentes a mulheres e 45% a homens.

![Histograma da variável Days por gênero](assets/dados-de-contagem-quine/hist_days_sex.png "Histograma da variável Days por gênero")

**Estatísticas por nível de gênero**

| Sex | Mediana | Média | Variância | Tamanho |
|---|---|---|---|---|
| F | 10 | 15,2 | 254 | 80 |
| M | 14 | 18 | 277 | 66 |

Para a situação de aprendizagem, ambos os níveis têm estatísticas e distribuições próximas, apesar de alunos com aprendizagem lenta terem um número maior de outliers.

![Histograma da variável Days por aprendizagem](assets/dados-de-contagem-quine/hist_days_lrn.png "Histograma da variável Days por aprendizagem")

**Estatísticas por nível de situação de aprendizagem**

| Lrn | Mediana | Média | Variância | Tamanho |
|---|---|---|---|---|
| AL | 12 | 15,8 | 193 | 83 |
| SL | 10 | 17,3 | 361 | 63 |

As distribuições por grupo escolar também são bem semelhantes entre os grupos, exceto pelo grupo F1, que tem estatísticas menores que os demais grupos e conserva a assimetria original.

![Histograma da variável Days por grupo escolar](assets/dados-de-contagem-quine/hist_days_age.png "Histograma da variável Days por grupo escolar")

**Estatísticas por nível de grupo escolar**

| Age | Mediana | Média | Variância | Tamanho |
|---|---|---|---|---|
| F0 | 11 | 14,9 | 219 | 27 |
| F1 | 6 | 11,2 | 136 | 46 |
| F2 | 14 | 21 | 405 | 40 |
| F3 | 18 | 19,6 | 255 | 33 |

### Ajuste dos Modelos

O modelo $M_1$ foi ajustado inicialmente.

**Estimativas do ajuste do modelo $M_1$**

| Variável/Nível | Coeficiente | Erro-Padrão | 2,5% | 97,5% | Razão de Média | 2,5% | 97,5% | P-valor |
|---|---|---|---|---|---|---|---|---|
| (Intercept) | 2.3434 | 0.0604 | 2.2236 | 2.4603 | 10.4163 | 9.2407 | 11.7086 | 0 |
| EthA | 0.5336 | 0.0419 | 0.4517 | 0.616 | 1.7051 | 1.5711 | 1.8514 | 0 |
| SexF | -0.1616 | 0.0425 | -0.2449 | -0.0782 | 0.8508 | 0.7827 | 0.9248 | 1e-04 |
| AgeF1 | -0.3339 | 0.0701 | -0.471 | -0.1962 | 0.7161 | 0.6244 | 0.8219 | 0 |
| AgeF2 | 0.2578 | 0.0624 | 0.1362 | 0.381 | 1.2941 | 1.1459 | 1.4637 | 0 |
| AgeF3 | 0.4277 | 0.0677 | 0.2957 | 0.5611 | 1.5337 | 1.344 | 1.7526 | 0 |
| LrnSL | 0.3489 | 0.052 | 0.2473 | 0.4513 | 1.4176 | 1.2805 | 1.5703 | 0 |

Com relação à origem étnica do aluno, tendo como referência alunos não aborígenes, a razão de médias entre alunos aborígenes e não aborígenes é de cerca de 1,7051. Isso significa que alunos aborígenes têm uma média de faltas cerca de 70% **maior**, com efeito significativo (p-valor < 0,005).

Olhando pela perspectiva das situações de aprendizagem, tendo alunos com aprendizagem média como referência, a razão de médias para alunos com aprendizagem lenta é de 1,4176, ou seja, uma média de faltas cerca de 41,76% **maior**. Novamente, o p-valor associado é bem baixo, indicando significância.

De acordo com o grupo escolar, sendo F0 a referência, temos as razões de médias 0,7161, 1,2941 e 1,5337 para F1, F2 e F3, respectivamente. Isso indica que o grupo F1 tem média de faltas 28,39% **menor** em relação ao grupo de referência, enquanto os grupos F2 e F3 têm acréscimos de 29,41% e 53,37%, respectivamente. Os p-valores associados indicam que todos os níveis da variável são estatisticamente significantes. No entanto, isso não indica que, ao mudar o grupo de referência, os coeficientes associados se mantenham, com exceção, claro, da comparação entre o grupo de referência anterior e o atual.

Analogamente para o gênero, com homens como grupo de referência, temos uma média de faltas 14,92% **menor** para mulheres.

O modelo indica uma maior frequência esperada de faltas de grupos minoritários em comparação com os grupos de referência.

Pelo teste de razão de verossimilhanças aplicado a cada variável em relação ao modelo completo $M_1$, temos que todas as variáveis são significativas de forma global. Isso, no entanto, não significa que todos os níveis das variáveis são significativos, pois a hipótese do teste é verificar se todos os coeficientes associados aos níveis da variável são iguais a zero.

Com o teste de razão de verossimilhanças tendo como modelo base o $M_1$, verificando as interações adicionadas nos modelos $M_2$, $M_3$ e $M_4$, a tabela abaixo foi construída com os p-valores.

**Resultados dos testes de razão de verossimilhança para as interações**

| Modelos | Hipótese | P-valor |
|---|---|---|
| $M_1$ vs. $M_2$ | $H_0: Eth_i:Sex_i = 0$ vs $H_1: Eth_i:Sex_i \neq 0$ | 2.975e-06 |
| $M_1$ vs. $M_3$ | $H_0: Age_i:Lrn_i = 0$ vs $H_1: Age_i:Lrn_i \neq 0$ | 0.01246 |
| $M_1$ vs. $M_4$ | $H_0: Eth_i:Age_i = Age_i:Lrn_i = 0$ vs $H_1: Eth_i:Age_i \neq 0 \text{ e/ou } Age_i:Lrn_i \neq 0$ | 2.2e-16 |

No primeiro caso, a interação entre a origem étnica e o gênero é testada em relação ao modelo base, e o resultado indica significância da interação. No segundo caso, a interação entre o grupo escolar e a situação de aprendizagem é testada e, novamente, a interação é significativa para o modelo. No terceiro, as interações origem étnica × grupo escolar e grupo escolar × situação de aprendizagem são testadas conjuntamente, com p-valor muito baixo, indicando que ao menos uma delas é significativa. Um teste avaliando o acréscimo de cada variável foi realizado (note que, quando $Eth_i:Age_i = 0$, temos o modelo $M_3$). Em ambos os testes, os coeficientes foram significativos.

O modelo selecionado foi $M_4$. O critério de informação de Akaike foi utilizado em conjunto com os pesos de Akaike, bem como a análise dos resíduos de todos os modelos. As observações 36, 104 e 72 foram destacadas.

![Resíduos do Modelo $M_4$](assets/dados-de-contagem-quine/residuos_ajuste_m4.png "Resíduos do Modelo $M_4$")

Ao tentar obter a distância de Cook, houve um erro: a matriz $X^\top W X$ é singular. Verificando o posto, temos que é 12, enquanto há 13 coeficientes. Assim, a matriz não tem posto completo, indicando que uma das colunas é combinação linear das outras. Ao verificar as frequências das interações, uma combinação entre Age e Lrn retornou zero: F3 e SL. Removendo a interação Age × Lrn, o modelo $M_4$ corrigido continuou com o **menor** AIC e bom ajuste residual. Pelo gráfico de distância de Cook, as observações 36, 104 e 72 foram novamente destacadas.

![Resíduos do Modelo $M_4$](assets/dados-de-contagem-quine/residuos_m4.png "Resíduos do Modelo $M_4$")

![Distância de Cook](assets/dados-de-contagem-quine/distancia_cook.png "Distância de Cook")

Ao fazer a análise de sensibilidade removendo cada uma das observações, e também removendo-as em conjunto, verificou-se que a observação 72 interfere de forma significativa nas estimativas e nos intervalos de confiança. Considerando a origem étnica, a razão de médias estimada para o modelo corrigido $M_4$ é de 0,873, ou seja, a média esperada de faltas dos alunos aborígenes é 12,7% **menor** que a dos não aborígenes. A estimativa se mantém próxima considerando as observações 36 e 104, mas, para a observação 72, a estimativa é 14,4% menor. Para gênero e demais variáveis não há mudança brusca, com exceção da combinação entre alunos não aborígenes e grupo escolar F3, que também muda de direção na interpretação do efeito. Assim, o modelo escolhido foi o modelo $M_4$ corrigido.

**Estimativas do ajuste do modelo selecionado $M_4$ corrigido**

| Variável/Nível | Coeficiente | Erro-Padrão | 2,5% | 97,5% | Razão de Média | 2,5% | 97,5% | P-valor |
|---|---|---|---|---|---|---|---|---|
| (Intercept) | 2.6965 | 0.0705 | 2.5554 | 2.8321 | 14.8274 | 12.8769 | 16.9805 | 0 |
| EthA | -0.1358 | 0.1004 | -0.3334 | 0.0605 | 0.8731 | 0.7165 | 1.0624 | 0.1764 |
| SexF | -0.163 | 0.0427 | -0.2467 | -0.0792 | 0.8496 | 0.7814 | 0.9239 | 1e-04 |
| AgeF1 | -0.9095 | 0.1025 | -1.1112 | -0.709 | 0.4027 | 0.3292 | 0.4921 | 0 |
| AgeF2 | -0.493 | 0.0978 | -0.685 | -0.3014 | 0.6108 | 0.5041 | 0.7398 | 0 |
| AgeF3 | 0.3498 | 0.0902 | 0.1738 | 0.5277 | 1.4188 | 1.1899 | 1.695 | 1e-04 |
| LrnSL | 0.3579 | 0.0521 | 0.2561 | 0.4604 | 1.4304 | 1.2919 | 1.5847 | 0 |
| EthA:AgeF1 | 1.0289 | 0.1365 | 0.7623 | 1.2976 | 2.7979 | 2.1433 | 3.6605 | 0 |
| EthA:AgeF2 | 1.2346 | 0.1283 | 0.9843 | 1.4873 | 3.4371 | 2.6759 | 4.4253 | 0 |
| EthA:AgeF3 | 0.1767 | 0.1275 | -0.073 | 0.4272 | 1.1933 | 0.9296 | 1.5329 | 0.166 |

Nota-se que a variável dummy Eth referente a alunos aborígenes tem p-valor alto, mas será mantida para preservar a hierarquia, visto que a interação Eth × Age é significativa. Além disso, os resíduos mostram-se aleatoriamente dispersos em contraponto aos valores ajustados, enquanto as observações influentes ainda são explicitadas no gráfico de distância de Cook. O gráfico QQ-plot dos resíduos aparenta estar adequado.

![Resíduos do Modelo $M_4$ corrigido](assets/dados-de-contagem-quine/residuos_ajuste_m4_corrig.png "Resíduos do Modelo $M_4$ corrigido")

As estimativas do número médio de dias, com intervalos de confiança de 95%, foram geradas a partir de perfis de estudantes.

O primeiro perfil é de mulheres aborígenes no grupo escolar F3 com situação de aprendizagem média, com estimativa média de 19 faltas e intervalo de confiança [16,57; 20,92].

O segundo perfil é de mulheres não aborígenes no mesmo grupo escolar, com situação de aprendizagem média. O intervalo de confiança é [15,93; 20,05], com média de 16 faltas, aproximadamente.

O terceiro perfil é de homens aborígenes com situação de aprendizagem lenta no grupo escolar F3, e o quarto, de homens não aborígenes. O número médio esperado de faltas para ambos é, respectivamente, 31 e 30 faltas, aproximadamente. Os intervalos de confiança são [26,68; 36,83] e [25,61; 35,36].

Entre mulheres aborígenes e não aborígenes, primeiro e segundo perfis, temos a razão de médias de 0,96 com o contraste N/A (na escala da resposta), com p-valor de 0,6027. Assim, com as hipóteses $H_0: \mu_{A,F} = \mu_{N,F}$ vs. $H_1: \mu_{A,F} \neq \mu_{N,F}$, falha-se em rejeitar a hipótese nula, indicando que não há diferença estatisticamente significante.

Para o terceiro e o quarto perfis, buscamos comparar as faltas entre homens de origem aborígene e não aborígene com aprendizagem lenta no grupo F3. Com as hipóteses $H_0: \mu_{A,M} = \mu_{N,M}$ vs. $H_1: \mu_{A,M} \neq \mu_{N,M}$, falha-se em rejeitar a hipótese nula, indicando que não há diferença estatisticamente significante.

### Adequação do Modelo

A proporção prevista de zeros para o modelo selecionado $M_4$ corrigido é de 0,037%, enquanto a tabela possui uma proporção de zeros de 6,164%, indicando que há um excesso de zeros no conjunto de dados em relação ao modelo.

A dispersão de Pearson retornou 11,73, indicando uma forte sobredispersão. Pela dispersão baseada no desvio residual, o valor obtido foi de 11,35, corroborando a indicação de sobredispersão da estimativa anterior.

Com o ajuste do modelo $M_4$ corrigido com a Quase-Poisson e com a Binomial Negativa, os coeficientes não mudaram com o ajuste da Quase-Poisson, enquanto a Binomial Negativa modificou as estimativas. No entanto, o erro-padrão associado à Quase-Poisson aumentou em comparação ao modelo selecionado. Adicionalmente, além da variável dummy de Eth para alunos aborígenes ter p-valor alto, a variável Sex também tem, sendo dummy para mulheres. Os p-valores associados a outros níveis das outras variáveis também mudam. A direção das razões de médias não mudou.

**Significâncias das covariáveis por distribuição**

| Variável | P-valor M4 corrigido | P-valor QP | P-valor BN |
|---|---|---|---|
| (Intercept) | 0 | 0 | 0 |
| EthA | 0,1764 | 0,6937 | 0,8680 |
| SexF | 1e-04 | 0,2677 | 0,4667 |
| AgeF1 | 0 | 0,0107 | 0,0090 |
| AgeF2 | 0 | 0,1434 | 0,1357 |
| AgeF3 | 1e-04 | 0,2597 | 0,3598 |
| LrnSL | 0 | 0,0469 | 0,2074 |
| EthA:AgeF1 | 0 | 0,0295 | 0,0395 |
| EthA:AgeF2 | 0 | 0,0057 | 0,0078 |
| EthA:AgeF3 | 0,166 | 0,6866 | 0,8258 |

A estimativa da interação se mantém próxima do modelo selecionado, mas o efeito diminui de forma suave. O erro-padrão associado ao ajuste da Quase-Poisson aumenta enquanto mantém as estimativas do modelo selecionado, e a Binomial Negativa mantém coeficientes próximos, mas com erro-padrão também maior. Os resíduos da Quase-Poisson também se mostram aleatoriamente dispersos em relação aos valores ajustados, assim como os da Binomial Negativa. Porém, o gráfico QQ-plot indica uma certa falta de ajuste na cauda superior em relação à Normal. Em contrapartida, a Binomial Negativa se mostra mais aderente. Assim, o modelo selecionado no momento é a Binomial Negativa.

![Resíduos do ajuste da Quase-Poisson](assets/dados-de-contagem-quine/residuos_ajuste_qp.png "Resíduos do ajuste da Quase-Poisson")

![Resíduos do ajuste da Binomial Negativa](assets/dados-de-contagem-quine/residuos_ajuste_nb.png "Resíduos do ajuste da Binomial Negativa")

![Comparação entre Poisson e Binomial Negativa](assets/dados-de-contagem-quine/comparacao_poi_nb.png "Comparação entre Poisson e Binomial Negativa")

### Validação Cruzada

A base foi dividida em 10 partições, com os 3 modelos sendo rodados para a validação cruzada. A tabela abaixo inclui as métricas utilizadas para indicar a performance de cada distribuição, bem como as outras indicadas na seção de metodologia.

**Compilado das métricas de ajuste das distribuições**

| Modelo | Desvio Médio de Poisson | MAE | RMSE | AIC | Dispersão de Pearson | Dispersão de Desvio |
|---|---|---|---|---|---|---|
| Poisson | 19.45 | 13.82 | 18.57 | 2151.31 | 11.73 | 11.35 |
| Quase-Poisson | 19.45 | 13.82 | 18.57 | - | 11.34 | 11.15 |
| Binomial Negativa | 19.16 | 13.82 | 18.47 | 1000.93 | 0.96 | 1.24 |
