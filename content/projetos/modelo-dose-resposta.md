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

### Metodologia

#### Ajuste dos Modelos

A diferença entre a resposta Bernoulli e a contagem binomial é que a primeira é um ensaio de Bernoulli, em que o parâmetro é a probabilidade de ocorrer um sucesso. A segunda são $n$ ensaios de Bernoulli, em que os parâmetros são o total de ensaios e a probabilidade de ocorrer sucesso. Aplicando ao contexto da atividade, a resposta Bernoulli se refere à probabilidade de ocorrer a morte quando se aplica uma certa dose a uma larva de sexo estabelecido, e a contagem binomial é o número esperado de larvas mortas após receberem uma certa dose e serem de um sexo estabelecido.

Precisamos, ainda, estabelecer pressupostos de independência e homogeneidade entre os grupos: cada um dos lotes de larvas que recebem as doses deve ser independente, de modo que o resultado de um grupo não afeta o de outro, e cada dose estabelecida por sexo deve ser aplicada por 3 dias para todas as larvas.

Considerando $\pi(d) = P(Y=1 \mid d) = P(T \le d) = F_T(d)$, a probabilidade de morte é a probabilidade acumulada do limiar de tolerância $T$ quando a dose aplicada é $d$. Seja $T$ a variável aleatória que determina a tolerância individual à dose do inseticida, $d$ a dose aplicada e $\pi(d)$ a probabilidade de morte para essa dose. Temos:

- Se $T \le d$, a dose aplicada é igual ou maior que o limiar de tolerância da larva e, assim, a morte ocorre.
- Se $T > d$, a dose aplicada é menor que o limiar e, portanto, a larva sobrevive.

Logo, a probabilidade de morte é $\pi(d) = P(T \le d)$. É necessário assumir que a distribuição é monotônica em relação à dose e que as condições experimentais são comparáveis. Isso se relaciona com as figuras de proporção de mortalidade, que mostram a mortalidade por dose aplicada.

Para $d > 0$ e supondo $X = \log_2(T)$, com $\log_2(T) = \mu + \sigma Z$, onde $Z$ é uma variável aleatória com distribuição de probabilidade conhecida, temos

$$
\begin{aligned}
\pi(d) &= F_T(d) = P(T \le d) = P(\log_2(T) \le \log_2(d)) = P(\mu + \sigma Z \le \log_2(d)) \\
&= P\left(Z \le \frac{\log_2(d) - \mu}{\sigma}\right) = F_Z(\beta_0 + \beta_1 \log_2(d))
\end{aligned}
$$

em que $\beta_0 = -\mu/\sigma$ e $\beta_1 = 1/\sigma > 0$.

Se considerarmos $Z$ como normal padrão, temos

$$
\begin{aligned}
\pi(d) &= F_Z(\beta_0 + \beta_1 \log_2(d)) = \Phi(\beta_0 + \beta_1 \log_2(d)) \\
\Phi^{-1}(\pi(d)) &= \beta_0 + \beta_1 \log_2(d)
\end{aligned}
$$

sendo a função de ligação correspondente a ligação **probit**.

Se $Z$ tiver densidade logística, temos $F_Z(z) = \frac{1}{1 + e^{-z}}$ e

$$
\pi(d) = F_Z(\beta_0 + \beta_1 \log_2(d)) = \frac{1}{1 + e^{-(\beta_0 + \beta_1 \log_2(d))}}
$$

Partindo da equação logística acima, temos

$$
\begin{aligned}
1 - \pi(d) &= \frac{e^{-(\beta_0 + \beta_1 \log_2(d))}}{1 + e^{-(\beta_0 + \beta_1 \log_2(d))}} \\
\frac{\pi(d)}{1 - \pi(d)} &= e^{\beta_0 + \beta_1 \log_2(d)} \\
\log\left(\frac{\pi(d)}{1 - \pi(d)}\right) &= \beta_0 + \beta_1 \log_2(d)
\end{aligned}
$$

Assim, a função de ligação é a **logit**: $\operatorname{logit}(\pi(d)) = \log\left(\frac{\pi(d)}{1 - \pi(d)}\right)$.

Para $Z$ com distribuição de valor extremo, temos $F_Z(z) = 1 - e^{-e^{z}}$ e

$$
\pi(d) = F_Z(\beta_0 + \beta_1 \log_2(d)) = 1 - e^{-e^{\beta_0 + \beta_1 \log_2(d)}}
$$

Partindo dessa expressão, temos

$$
\begin{aligned}
1 - \pi(d) &= e^{-e^{\beta_0 + \beta_1 \log_2(d)}} \\
\log(1 - \pi(d)) &= -e^{\beta_0 + \beta_1 \log_2(d)} \\
\log(-\log(1 - \pi(d))) &= \beta_0 + \beta_1 \log_2(d)
\end{aligned}
$$

Que é a ligação **log-log complementar**: $\operatorname{cloglog}(\pi(d)) = \log(-\log(1 - \pi(d)))$.

Temos $Y_i \mid \mathbf{x}_i \sim \text{Bernoulli}(\pi_i)$ e $g(\pi_i) = \beta_0 + \mathbf{x}_i^\top \boldsymbol{\beta}$. Com independência assumida, $n_j$ indivíduos e probabilidades $\pi_j$, a verossimilhança é

$$
L(\boldsymbol{\beta}) = \prod_{j=1}^{m} \binom{n_j}{r_j} \pi_j^{r_j} (1 - \pi_j)^{n_j - r_j}
$$

e a log-verossimilhança é

$$
\ell(\boldsymbol{\beta}) = \sum_{j=1}^{m} \left[ \log\binom{n_j}{r_j} + r_j \log(\pi_j) + (n_j - r_j) \log(1 - \pi_j) \right]
$$

Os modelos especificados $M_0$, $M_1$ e $M_2$ são:

- $M_0: g(\pi_j) = \beta_0 + \beta_1 x_j$
- $M_1: g(\pi_j) = \beta_0 + \beta_1 x_j + \beta_2 s_j$
- $M_2: g(\pi_j) = \beta_0 + \beta_1 x_j + \beta_2 s_j + \beta_3 x_j s_j$

A variável sexo está codificada como $s = 0$ para "Feminino" e $s = 1$ para "Masculino". Em $M_1$, $\beta_1$ é a inclinação da dose comum aos dois sexos e $\beta_2$ é o deslocamento para machos, com fêmeas como referência. Em $M_2$, $\beta_1$ é a inclinação para fêmeas e a inclinação para machos é $\beta_1 + \beta_3$.

Os modelos foram ajustados com as ligações logit, probit e cloglog, e os gráficos estão na figura de ajustes dos modelos.

##### Estimação pontual das doses letais

Considerando uma função genérica $g$ e uma probabilidade de mortalidade $0 < r < 1$, a dose letal $DL_{100r}$ é tal que $\pi(DL_{100r}) = r$, ou seja, $F_T(DL_{100r}) = r$, de modo que $DL_{100r} = F_T^{-1}(r)$. Assim, com $g(\pi_j) = \beta_0 + \beta_1 \log_2(d_j)$, segue que

$$
x_r = \log_2(DL_{100r}) = \log_2(F_T^{-1}(r)) = \frac{g(r) - \beta_0}{\beta_1}
$$

E, portanto,

$$
DL_{100r} = 2^{\frac{g(r) - \beta_0}{\beta_1}}
$$

Pela invariância da máxima verossimilhança, a estimativa pontual de $x_r$ é

$$
\begin{aligned}
\hat{x}_r &= \frac{g(r) - \hat{\beta}_0}{\hat{\beta}_1} \\
\widehat{DL}_{100r} &= 2^{\hat{x}_r}
\end{aligned}
$$

Para o modelo $M_2$, temos $g(r_j) = \beta_0 + \beta_1 x + \beta_2 s_j + \beta_3 x s_j = \beta_0 + (\beta_1 + \beta_3 s_j) x + \beta_2 s_j$, de modo que $x_r = \frac{g(r_j) - \beta_0 - \beta_2 s_j}{\beta_1 + \beta_3 s_j}$. Assim,

$$
DL_{100r_j} = 2^{\frac{g(r_j) - \hat{\beta}_0 - \hat{\beta}_2 s_j}{\hat{\beta}_1 + \hat{\beta}_3 s_j}}
$$

A tabela de doses letais por sexo e por ligação apresenta esses valores.

Aplicando as funções de ligação logit e probit na probabilidade $r = 0{,}5$ (onde se espera a morte de 50% das larvas), temos $g(0{,}5) = \log\left(\frac{0{,}5}{0{,}5}\right) = \log(1) = 0$ e $g(0{,}5) = \Phi^{-1}(0{,}5) = 0$, respectivamente. Logo, $\hat{x}_{0{,}5} = -\frac{\hat{\beta}_0}{\hat{\beta}_1}$.

Para a cloglog, $g(r_j) = \log(-\log(1 - r_j))$, temos $g(0{,}5) = \log(-\log(0{,}5)) \approx -0{,}3665$ e, portanto, $\hat{x}_{0{,}5} = \frac{-0{,}3665 - \hat{\beta}_0}{\hat{\beta}_1}$, e não $-\frac{\hat{\beta}_0}{\hat{\beta}_1}$. Quando o preditor linear é zero, temos

$$
\begin{aligned}
\log(-\log(1 - r_j)) &= 0 \\
-\log(1 - r_j) &= 1 \\
1 - r_j &= e^{-1} \\
r_j &= 1 - e^{-1} \approx 0{,}6321 \neq 0{,}5
\end{aligned}
$$

Assim, o ponto $x = -\frac{\beta_0}{\beta_1}$ representa uma mortalidade de $63{,}21\%$, e não de $50\%$. O ponto em que se espera 50% de mortalidade é $\hat{x}_{0{,}5} = \frac{-0{,}3665 - \beta_0}{\beta_1}$, pois

$$
\begin{aligned}
\log(-\log(1 - 0{,}5)) &= -0{,}3665 \\
\log(-\log(1 - r_j)) &= \beta_0 + \beta_1 x_{0{,}5}(0) \\
x_{0{,}5}(0) &= \frac{-0{,}3665 - \beta_0}{\beta_1} \\
DL_{50}(0) &= 2^{\frac{-0{,}3665 - \beta_0}{\beta_1}}
\end{aligned}
$$

##### Estimação intervalar

Os intervalos de confiança de $\hat{x}_r$ serão estimados de acordo com o modelo escolhido, pelo critério do AIC. Considerando $g$ a função de ligação do modelo selecionado, temos, para os modelos $M_0$ e $M_1$, respectivamente, os gradientes:

$$
q_s(\boldsymbol{\beta}) = \frac{g(r_j) - \beta_0}{\beta_1} \quad\Rightarrow\quad \nabla q_s(\boldsymbol{\beta}) = \begin{pmatrix} -\dfrac{1}{\beta_1} \\ -\dfrac{g(r_j) - \beta_0}{\beta_1^2} \end{pmatrix}
$$

$$
q_s(\boldsymbol{\beta}) = \frac{g(r_j) - \beta_0 - \beta_2 s_j}{\beta_1} \quad\Rightarrow\quad \nabla q_s(\boldsymbol{\beta}) = \begin{pmatrix} -\dfrac{1}{\beta_1} \\ -\dfrac{g(r_j) - \beta_0 - \beta_2 s_j}{\beta_1^2} \\ -\dfrac{s_j}{\beta_1} \end{pmatrix}
$$

A estimação para a escala original será feita com o método Delta:

$$
\widehat{\operatorname{Var}}(\hat{x}_r) = \nabla q_s(\hat{\boldsymbol{\beta}})^\top \, \hat{V} \, \nabla q_s(\hat{\boldsymbol{\beta}})
$$

em que $\hat{V}$ é a matriz de covariância dos coeficientes.

Na escala $x_r = \log_2(DL_{100r})$, o intervalo de confiança de nível $1-\alpha$ é simétrico em torno de $\hat{x}_r$:

$$
\hat{x}_r \pm z_{1-\alpha/2} \sqrt{\widehat{\operatorname{Var}}(\hat{x}_r)}
$$

Como $DL_{100r} = 2^{x_r}$ é uma transformação exponencial, os intervalos simétricos se tornam assimétricos na escala da dose:

$$
\left[ 2^{\hat{x}_r - z_{1-\alpha/2}\sqrt{\widehat{\operatorname{Var}}(\hat{x}_r)}} \,;\, 2^{\hat{x}_r + z_{1-\alpha/2}\sqrt{\widehat{\operatorname{Var}}(\hat{x}_r)}} \right]
$$

Quando o coeficiente $\beta_1$ é próximo de 0, o termo $q_s(\boldsymbol{\beta})$ cresce e, pelo método Delta, a variância estimada também cresce, com termo quadrático em $\beta_1$. Assim, quando a inclinação está próxima de zero, a incerteza associada é maior e a estimativa fica mais instável.

##### Análise de resíduos

A adequação da dispersão do modelo foi examinada a partir dos resíduos de Pearson e de desvio. A estatística para quantificar a dispersão é

$$
\hat{\phi} = \frac{X^2_P}{m - k}
$$

em que $X^2_P$ é a estatística de Pearson, $m$ é o número de grupos e $k$ é o número de parâmetros do modelo.

Valores de $\hat{\phi}$ próximos de 1 indicam uma variabilidade aderente ao previsto, enquanto valores maiores podem sugerir sobredispersão. Como o número de grupos é pequeno, esses valores devem ser analisados com cautela, pois a estatística pode ficar instável no comportamento assintótico. Além disso, probabilidades ajustadas próximas de 0 ou 1 aumentam a sensibilidade dos resíduos às diferenças entre frequências observadas e esperadas. Por isso, a análise da dispersão deve ser complementada pela avaliação gráfica dos resíduos, considerando também as probabilidades ajustadas e os tamanhos amostrais de cada grupo.

### Resultados

Os gráficos indicam que a mortalidade para machos é maior quando comparada à das fêmeas. O uso da escala acaba sendo mais justificável pelo fato de ela retornar retas, o que é mais propício para aplicar modelos de regressão.

![Mortalidade de larvas por dose e sexo](assets/modelos-lineares-generalizados/mortalidade_sexo.png "Mortalidade de larvas")

#### Ajuste dos Modelos

Lembrando que a variável sexo está codificada como $s = 0$ para "Feminino" e $s = 1$ para "Masculino". Em $M_1$, $\beta_1$ é a inclinação da dose comum aos dois sexos e $\beta_2$ é o deslocamento para machos, com fêmeas como referência. Em $M_2$, $\beta_1$ é a inclinação para fêmeas e a inclinação para machos é $\beta_1 + \beta_3$.

Os modelos foram ajustados com as ligações logit, probit e cloglog, e os gráficos estão a seguir.

![Ajuste do modelo às proporções de mortes: ligação logit](assets/modelos-lineares-generalizados/ajuste_logit.png "Ajuste do modelo às proporções de mortes: ligação logit")

![Ajuste do modelo às proporções de mortes: ligação probit](assets/modelos-lineares-generalizados/ajuste_probit.png "Ajuste do modelo às proporções de mortes: ligação probit")

![Ajuste do modelo às proporções de mortes: ligação cloglog](assets/modelos-lineares-generalizados/ajuste_cloglog.png "Ajuste do modelo às proporções de mortes: ligação cloglog")

As estimativas dos coeficientes de cada modelo, com erro-padrão (EP), log-verossimilhança (LV), desvio residual (DR), graus de liberdade (GL) e AIC, estão na tabela abaixo. A log-verossimilhança aumenta conforme a complexidade do modelo, e os modelos $M_2$ têm as maiores. O modelo com menor AIC é o $M_1$ com ligação probit.

**Estimativas dos coeficientes e medidas de ajuste dos modelos**

<table>
  <thead>
    <tr><th>Modelo</th><th colspan="3">$M_0$</th><th colspan="3">$M_1$</th><th colspan="3">$M_2$</th></tr>
    <tr><th>Ligação</th><th>Logit</th><th>Probit</th><th>Cloglog</th><th>Logit</th><th>Probit</th><th>Cloglog</th><th>Logit</th><th>Probit</th><th>Cloglog</th></tr>
  </thead>
  <tbody>
    <tr><td>$\beta_0$</td><td>-2.766</td><td>-1.643</td><td>-2.339</td><td>-3.473</td><td>-2.060</td><td>-2.935</td><td>-2.994</td><td>-1.801</td><td>-2.633</td></tr>
    <tr><td>$EP(\beta_0)$</td><td>0.370</td><td>0.199</td><td>0.277</td><td>0.469</td><td>0.251</td><td>0.347</td><td>0.553</td><td>0.298</td><td>0.437</td></tr>
    <tr><td>$\beta_1$</td><td>1.007</td><td>0.597</td><td>0.664</td><td>1.064</td><td>0.632</td><td>0.729</td><td>0.906</td><td>0.545</td><td>0.647</td></tr>
    <tr><td>$EP(\beta_1)$</td><td>0.124</td><td>0.066</td><td>0.076</td><td>0.131</td><td>0.070</td><td>0.084</td><td>0.167</td><td>0.091</td><td>0.114</td></tr>
    <tr><td>$\beta_2$</td><td>-</td><td>-</td><td>-</td><td>1.101</td><td>0.654</td><td>0.828</td><td>0.175</td><td>0.155</td><td>0.251</td></tr>
    <tr><td>$EP(\beta_2)$</td><td>-</td><td>-</td><td>-</td><td>0.356</td><td>0.202</td><td>0.230</td><td>0.778</td><td>0.416</td><td>0.600</td></tr>
    <tr><td>$\beta_3$</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>0.175</td><td>0.155</td><td>0.251</td></tr>
    <tr><td>$EP(\beta_3)$</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>0.778</td><td>0.416</td><td>0.600</td></tr>
    <tr><td>LV</td><td>-23.547</td><td>-23.262</td><td>-25.242</td><td>-18.434</td><td>-17.838</td><td>-18.469</td><td>-17.552</td><td>-16.939</td><td>-17.933</td></tr>
    <tr><td>DR</td><td>16.984</td><td>16.414</td><td>20.374</td><td>6.757</td><td>5.566</td><td>6.828</td><td>4.994</td><td>3.768</td><td>5.756</td></tr>
    <tr><td>GL</td><td>10</td><td>10</td><td>10</td><td>9</td><td>9</td><td>9</td><td>8</td><td>8</td><td>8</td></tr>
    <tr><td>AIC</td><td>51.094</td><td>50.524</td><td>54.485</td><td>42.868</td><td>41.676</td><td>42.938</td><td>43.104</td><td>41.878</td><td>43.866</td></tr>
  </tbody>
</table>

A tabela abaixo resume a convergência e o sinal dos coeficientes. Em todos os modelos, os coeficientes são positivos, com exceção do intercepto.

**Convergência e sinal dos coeficientes**

| Modelo | Ligação | Convergência | Sinal $\beta_1$ | Sinal $\beta_2$ | Sinal $\beta_3$ |
|---|---|---|---|---|---|
| $M_0$ | Logit | Sim | Positivo | - | - |
| $M_0$ | Probit | Sim | Positivo | - | - |
| $M_0$ | Cloglog | Sim | Positivo | - | - |
| $M_1$ | Logit | Sim | Positivo | Positivo | - |
| $M_1$ | Probit | Sim | Positivo | Positivo | - |
| $M_1$ | Cloglog | Sim | Positivo | Positivo | - |
| $M_2$ | Logit | Sim | Positivo | Positivo | Positivo |
| $M_2$ | Probit | Sim | Positivo | Positivo | Positivo |
| $M_2$ | Cloglog | Sim | Positivo | Positivo | Positivo |

#### Seleção do Modelo

Com os pesos de Akaike calculados, obtemos a contribuição percentual de cada modelo em relação aos demais. Quando um modelo tem peso muito alto, ele explica melhor a variância presente nos dados do que os demais e é o melhor candidato. Quando os pesos são próximos, não há consenso sobre qual é o melhor, e é preciso recorrer a outras validações para definir o modelo.

Neste caso, o modelo com menor AIC foi definido como melhor, ou seja, o $M_1$ com ligação probit. O peso de Akaike desse modelo é $0,2608$, enquanto o do segundo melhor (o $M_2$ com ligação probit) é $0,2358$. Ou seja, ambos são bons candidatos.

**Pesos de Akaike por modelo**

<table>
  <thead>
    <tr><th>Modelo</th><th colspan="3">$M_0$</th><th colspan="3">$M_1$</th><th colspan="3">$M_2$</th></tr>
    <tr><th>Ligação</th><th>Logit</th><th>Probit</th><th>Cloglog</th><th>Logit</th><th>Probit</th><th>Cloglog</th><th>Logit</th><th>Probit</th><th>Cloglog</th></tr>
  </thead>
  <tbody>
    <tr><td>AIC</td><td>51.094</td><td>50.524</td><td>54.485</td><td>42.868</td><td><strong>41.676</strong></td><td>42.938</td><td>43.104</td><td>41.878</td><td>43.866</td></tr>
    <tr><td>Peso de Akaike</td><td>0.0024</td><td>0.0031</td><td>0.0004</td><td>0.1437</td><td><strong>0.2608</strong></td><td>0.1388</td><td>0.1277</td><td>0.2358</td><td>0.0873</td></tr>
  </tbody>
</table>

Com as log-verossimilhanças da tabela de estimativas e os graus de liberdade, podemos aplicar o teste da razão de verossimilhanças para cada função de ligação, entre os modelos $M_1$ e $M_2$. A hipótese nula é

$$
H_0: \beta_3 = 0 \quad \text{vs} \quad H_1: \beta_3 \neq 0
$$

Fixado o nível de confiança de 95%, se o p-valor for menor que 5%, os dados indicam que o modelo com o coeficiente adicional é mais aderente. Se o p-valor for suficientemente maior que o nível de significância, o modelo mais simples é preferível. A estatística do teste é

$$
T = 2\big[ LV(M_2) - LV(M_1) \big]
$$

que, comparada à distribuição qui-quadrado com graus de liberdade iguais à diferença entre o número de parâmetros de $M_2$ e $M_1$, resulta na tabela abaixo.

**Resultados dos testes de razão de verossimilhanças**

| Ligação | T | GL | p-valor |
|---|---|---|---|
| Logit | 1.764 | 1 | 0.1841264 |
| Probit | 1.798 | 1 | 0.1799545 |
| Cloglog | 1.072 | 1 | 0.3004941 |

Ao comparar os modelos aninhados $M_2$ e $M_1$ para cada ligação, os dados não fornecem evidências para rejeitar a hipótese nula de que o efeito da interação sexo × dose é nulo. Portanto, o modelo $M_1$ é preferível por ser mais simples.

![Modelos ajustados para mortalidade entre larvas fêmeas](assets/modelos-lineares-generalizados/modelos_ajustados_femea.png "Modelos ajustados para mortalidade entre larvas fêmeas")

![Modelos ajustados para mortalidade entre larvas machos](assets/modelos-lineares-generalizados/modelos_ajustados_macho.png "Modelos ajustados para mortalidade entre larvas machos")

#### Estimação das Doses Letais

A tabela abaixo apresenta as doses letais por sexo e por ligação. As larvas fêmeas têm uma dose letal maior que as dos machos, o que indica que são mais resistentes.

**Doses letais por sexo da larva e por função de ligação**

<table>
  <thead>
    <tr><th></th><th colspan="3">Fêmeas ($s=0$)</th><th colspan="3">Machos ($s=1$)</th></tr>
    <tr><th>Ligação</th><th>$DL_{10}$</th><th>$DL_{50}$</th><th>$DL_{90}$</th><th>$DL_{10}$</th><th>$DL_{50}$</th><th>$DL_{90}$</th></tr>
  </thead>
  <tbody>
    <tr><td>Logit</td><td>1.838975</td><td>9.876481</td><td>53.04307</td><td>1.407886</td><td>4.720092</td><td>15.82462</td></tr>
    <tr><td>Probit</td><td>1.934806</td><td>9.867339</td><td>50.32255</td><td>1.408807</td><td>4.703120</td><td>15.70076</td></tr>
    <tr><td>Cloglog</td><td>1.506548</td><td>11.321039</td><td>40.93391</td><td>1.117297</td><td>5.439609</td><td>14.91538</td></tr>
  </tbody>
</table>

A avaliação numérica mostra que as doses de cada curva produzem a probabilidade-alvo.

![Probabilidade-alvo na ligação logit](assets/modelos-lineares-generalizados/prob_alvo1.png "Probabilidade-alvo na ligação logit")

![Probabilidade-alvo na ligação probit](assets/modelos-lineares-generalizados/prob_alvo2.png "Probabilidade-alvo na ligação probit")

![Probabilidade-alvo na ligação complementar log-log](assets/modelos-lineares-generalizados/prob_alvo3.png "Probabilidade-alvo na ligação complementar log-log")

#### Estimação Intervalar

O modelo selecionado pelo critério AIC é o $M_1$ com ligação probit. Na análise das bandas de confiança simultâneas, a observação de 100% de mortalidade dos machos fica fora da banda estimada. De forma análoga, a observação de 0% de mortalidade das fêmeas também fica fora da respectiva banda. Esses resultados indicam que, para essas observações específicas, os valores empíricos não são abrangidos pela banda simultânea do modelo ajustado, o que sugere possíveis discrepâncias entre as proporções observadas e as probabilidades estimadas. Esses desvios devem ser interpretados com cautela, considerando o tamanho reduzido da amostra e a variabilidade associada às observações extremas.

![Bandas simultâneas e IC de 95% da log dose](assets/modelos-lineares-generalizados/bandas.png "Bandas simultâneas e IC de 95% da log dose")

#### Análise de Resíduos

A análise dos resíduos avaliou a adequação do modelo selecionado. O gráfico de resíduos em função dos valores ajustados mostra uma distribuição aleatória, sem padrões sistemáticos ou tendências evidentes, o que sugere ausência de falta de ajuste relevante. O QQ-plot apresenta os resíduos aproximadamente alinhados à reta de referência, indicando concordância satisfatória com a distribuição teórica esperada.

A influência das observações foi avaliada pela distância de Cook e pela alavancagem (leverage). A distância de Cook identifica observações cuja exclusão pode alterar de forma relevante as estimativas dos parâmetros. A alavancagem identifica observações com valores das variáveis explicativas distantes do padrão geral dos dados. Nenhuma observação ultrapassou os limites de referência considerados para essas medidas, e não há evidências gráficas de observações excessivamente influentes ou com alavancagem elevada.

![Análise de resíduos de Pearson](assets/modelos-lineares-generalizados/residuos_pearson.png "Análise de resíduos de Pearson")

![Análise de influência das observações](assets/modelos-lineares-generalizados/influencia.png "Análise de influência das observações")

Reajustando o modelo selecionado removendo uma observação de cada vez, obtemos diferenças entre -6,5% e 9,3% na dose letal de 50%. As observações 9 e 12 são responsáveis pela diminuição e pelo acréscimo na estimativa, respectivamente. As observações referentes às proporções 0 e 1 não foram as que causaram maior impacto na incerteza.

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
