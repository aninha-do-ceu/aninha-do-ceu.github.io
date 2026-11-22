---
titulo: Análise de Sobrevivência Aplicada ao Tráfico Humano no Brasil
subtitulo: Tempo até o resgate de vítimas sob censura intervalar — trabalho aceito no **26º SINAPE** (Simpósio Nacional de Probabilidade e Estatística).
descricao: Estudo de caso: tempo até o resgate de vítimas de tráfico humano com censura intervalar — Turnbull, GAMLSS e riscos proporcionais (icenReg). Publicado no 26º SINAPE.
linguagens: R
tags: Análise de sobrevivência, Censura intervalar, Turnbull, GAMLSS, icenReg
repo: analise-de-sobrevivencia
autores: Ana Rosa Almeida do Nascimento, João Victor Lopes Pereira dos Santos, Oilson Alberto Gonzatto Junior e Mirela Teixeira Cazzolato
rodape: 26º SINAPE
---

## Resumo

O presente projeto visa modelar o tempo até o resgate de vítimas de tráfico no Brasil com características pessoais da vítima e do suspeito, bem como variáveis referentes ao município de origem da vítima. O trabalho usa técnicas de análise de sobrevivência. A censura presente na variável resposta é intervalar pois somente se sabe que o resgate ocorreu entre dois marcos temporais, exigindo métodos próprios para análise como a troca de estimação de curvas de sobrevivência com Kaplan-Meier para Turnbull. O trabalho resultou em publicação no 26º SINAPE, em coautoria com João Victor Lopes Pereira dos Santos, Oilson Alberto Gonzatto Junior e orientação da Profa. Dra. Mirela Teixeira Cazzolato (USP São Carlos).

## Dados



- **Fonte:** Disque100
- **Período:** 2° semestre de 2020 até final de 2025
- **Observações:** 8.006 registros

<table>
  <thead>
    <tr><th colspan="2" style="text-align:center">Variáveis</th></tr>
    <tr><th>Individual</th><th>Municipal</th></tr>
  </thead>
  <tbody>
    <tr><td>Gênero (vítima/suspeito)</td><td>Escolaridade média (anos)</td></tr>
    <tr><td>Faixa etária (vítima/suspeito)</td><td>Urbanização (%)</td></tr>
    <tr><td>Cor (vítima)</td><td>Ocupação feminina (%)</td></tr>
    <tr><td>Relação entre vítima e suspeito</td><td></td></tr>
    <tr><td>Cenário da violação</td><td><strong></strong></td></tr>
  </tbody>
</table>


> Definição central: para cada vítima, não observamos $T_i$ diretamente — observamos apenas que $L_i < T_i < R_i$. A análise inteira gira em torno de extrair informação dessa restrição.

## Introdução

### 1. O que é tráfico humano?

O tráfico humano é definido como o crime de "aliciamento, transporte e recepção de pessoas mediante força e/ou fraude para exploração com o intuito de lucrar".  

## Metodologia

### 1. A estrutura de verossimilhança sob censura intervalar

Considerando a censura intervalar da variável Início\_das\_violacoes, temos, considerando o tempo $x_i$, os limites para os intervalos:

$$
\begin{cases}
X_i \in [L_i, R_i), \\
L_i \geq 0, \\
R_i \in (L_i, \infty].
\end{cases}
$$

Como a função de sobrevivência se caracteriza por $S(x) = 1 - F(x) = P(X > x)$, adapta-se para a censura intervalar com $P(X < R_i) = F(R_i)$ e $P(X < L_i) = F(L_i)$. Assim, a contribuição da i-ésima observação para a função de verossimilhança é dada por

$$
\begin{aligned}
P(L_i \leq X_i < R_i) &= P(X_i \geq L_i) - P(X_i \geq R_i) \\
                      &= S(L_i) - S(R_i) \\
                      &= \big(1 - F(L_i)\big) - \big(1 - F(R_i)\big) \\
                      &= F(R_i) - F(L_i)
\end{aligned}
$$

Particularmente, quando $R_i \rightarrow \infty$, temos $P(L_i \leq X_i < R_i) = P(L_i \leq X_i < \infty) = S(L_i)$, tornando-se o caso de censura à  direita. Por fim, com a aplicação para a Gompertz generalizada temos

$$
    P(L_i \leq X_i < R_i) = \left[1 - e^{-\frac{\lambda}{c}(e^{c r_i}-1)} \right]^{\theta} - \left[1 - e^{-\frac{\lambda}{c}(e^{c l_i}-1)} \right]^{\theta}
$$

Assim, a função de verossimilhança é dada por

$$
    L(\lambda, \theta, c) = \prod_{i=1}^n \big\{ F(R_i) - F(L_i) \big\} = \prod_{i=1}^n \big\{ \left[1 - e^{-\frac{\lambda}{c}(e^{c r_i}-1)} \right]^{\theta} - \left[1 - e^{-\frac{\lambda}{c}(e^{c l_i}-1)} \right]^{\theta} \big\}
$$

Com a função de verossimilhança não-paramétrica, obtém-se o estimador de Turnbull como a solução da equação

$$
    \hat{F}(x) = \underset{(\lambda, \theta, c)}{\text{arg max}} \prod_{i=1}^n \big\{ F(R_i) - F(L_i) \big\}
$$

$$
    \hat{S}(x) = 1 - \hat{F}(x)
$$

A função log-verossimilhança é denotada por

<span id="eq-logvero"></span>

$$
\ell(\lambda, \theta, c) = \log L(\lambda, \theta, c) = \sum_{i=1}^{n} \log \Big( \left[ 1 - e^{-\frac{\lambda}{c}\left(e^{c r_i}-1\right)} \right]^{\theta} - \left[ 1 - e^{-\frac{\lambda}{c}\left(e^{c l_i}-1\right)} \right]^{\theta} \Big) \tag{1}
$$

A otimização da [Equação (1)](#eq-logvero) nos retorna os estimadores de máxima verossimilhança dos parâmetros dos modelos paramétricos utilizados. No caso acima, a Gompertz Generalizada. 



### 2. Estimação não paramétrica: Turnbull

Como a função de sobrevivência de Kaplan-Meier não se aplica a intervalos, usamos o estimador de **Turnbull** (NPMLE), obtido via algoritmo EM: cada observação começa com um peso distribuído dentro do seu intervalo, as estimativas são agregadas e o processo repete até convergir. O resultado é uma curva $S(t)$ consistente sem impor forma paramétrica alguma.

### 3. Riscos proporcionais com censura intervalar (icenReg)

Para quantificar o efeito de covariáveis no tempo até o resgate, ajustamos o modelo de riscos proporcionais estendido a dados intervalares, porém tem como pressuposto riscos proporcionais...

<p style="text-align:center"><img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRp2ArOZsfqtRnctXvivzk53hT-dPCvsjXpXuqI1yZe9Kyu9CbLPPCu92s&s=10" alt="Imagem ilustrativa" width="320"></p>

Com um teste apropriado, poderíamos seguir com a estimação semi-paramétrica para avaliar os impactos das variáveis no tempo até o resgate.

$$h(t \mid x) = h_0(t)\,\exp(x^\top\beta)$$

com verossimilhança de intervalo $S(l_i \mid x) - S(r_i \mid x)$, ajustado pelo pacote `icenReg` (`ic_sp` para a versão semiparamétrica). Os $\exp(\beta)$ são interpretados como razões de hazards por covariável.

### 4. Modelagem paramétrica flexível: GAMLSS

Ao final, ajustamos modelos **GAMLSS**, em que os parâmetros da distribuição do tempo de exposição (posição, escala, forma) podem depender de covariáveis, e a distribuição candidata é escolhida entre várias famílias compatíveis com a censura. Estudamos as distribuições Weibull (lembrando que esta ainda tem pressuposto de riscos proporcionais) com dois parâmetros, Log-Normal com dois parâmetros, Gama generalizada com três e Box-Cox T e Box-Cox Power Exponential com quatro parâmetros. A seleção de variáveis é via StepAIC por parâmetro, inicia-se com o modelo sem covariáveis e usa o passo forward para selecionar as que explicam bem parte da variância. Após a seleção do melhor modelo para o parâmetro, usa este como base para a seleção das covariáveis para outro parâmetro e assim por diante. A comparação entre especificações usa critérios de informação (AIC/GAIC) e diagnóstico de resíduos.

### Ferramentas

Todo o pipeline em **R**: `survival` (infraestrutura de sobrevivência), `icenReg` (regressão com censura intervalar), `GAMLSS` (modelagem paramétrica flexível) e `ggplot2` (visualização).

## Resultados

### Análise exploratória


Temos o número de denúncias feitas por gênero no gráfico abaixo. Vemos que mulheres são a maioria das vítimas.

![Número de denúncias por ano](assets/analise-de-sobrevivencia/denuncias_tempo_por_genero_2011_para_frente.png "Número de denúncias por ano e gênero")

Além disso, o histograma de idades das vítimas por ano mostra que crianças e adolescentes são maioria e que é um comportamento atemporal, com a idade média sendo por volta de 15 anos.

![Idades das vítimas por ano](assets/analise-de-sobrevivencia/denuncias_idade_ridge_2.png "Idades das vítimas por ano")


Em relação à cor da vítima, temos que a maioria são brancas e pardas e tem um bom número de denúncias que não tem essa informação. Além disso, temos presença de denúncias de pessoas indígenas e amarelas, algo já esperado devido à vulnerabilidade social. A maior parte das vítimas demora para ser resgatada: a moda se concentra em até 10 anos. Poucas vítimas são resgatadas em até uma semana.

![Denúncias por Cor da Vítima e Tempo até Resgate](assets/analise-de-sobrevivencia/grafico_vio_e_cor2.png "Denúncias por Cor da Vítima e Tempo até Resgate")





### Estimação Não-Paramétrica por Variável

![Curva de sobrevivência do tempo até o resgate](assets/analise-de-sobrevivencia/curva_sobrev.png "Curva de sobrevivência do tempo até o resgate")

![Cor da vítima e tempo até o resgate](assets/analise-de-sobrevivencia/cv_cor_novo.png "Cor da vítima e tempo até o resgate")

![Faixa etária do suspeito](assets/analise-de-sobrevivencia/cv_faixa_etaria_suspeito.png "Faixa etária do suspeito")

![Faixa etária da vítima](assets/analise-de-sobrevivencia/cv_faixa_etaria_vitima.png "Faixa etária da vítima")

![Gênero](assets/analise-de-sobrevivencia/cv_genero.png "Gênero")

![Relação entre vítima e suspeito](assets/analise-de-sobrevivencia/cv_relacao_vitima_suspeito_novo.png "Relação entre vítima e suspeito")


### Ajuste dos Modelos

![curvas](assets/analise-de-sobrevivencia/grafico_curva_sob_transp2.png "Ajuste dos modelos paramétricos à curva de sobrevivência")

<table>
  <thead>
    <tr><th>Modelo</th><th>Parâmetro</th><th>Variáveis selecionadas</th></tr>
  </thead>
  <tbody>
    <tr><td rowspan="4">Box-Cox Power Exponential</td><td>$\mu$</td><td>Relação V-S; Faixa Etária V/S; Gênero V/S; Cenário de Violação; Ocupação Feminina; Escolaridade Média</td></tr>
    <tr><td>$\sigma$</td><td>Faixa Etária V; Escolaridade Média; Gênero S</td></tr>
    <tr><td>$\nu$</td><td></td></tr>
    <tr><td>$\tau$</td><td>Escolaridade Média; Gênero V</td></tr>
    <tr><td rowspan="3">Box-Cox T</td><td>$\mu$</td><td>Relação V-S; Faixa Etária V/S; Gênero V/S; Cenário de Violação; Ocupação Feminina; Escolaridade Média</td></tr>
    <tr><td>$\sigma$</td><td>Faixa Etária V; Escolaridade Média; Gênero S</td></tr>
    <tr><td>$\nu$</td><td></td></tr>
    <tr><td rowspan="3">Gama Generalizada</td><td>$\mu$</td><td>Relação V-S; Faixa Etária V/S; Gênero V/S; Cenário de Violação; Ocupação Feminina; Escolaridade Média</td></tr>
    <tr><td>$\sigma$</td><td>Faixa Etária V; Escolaridade Média; Gênero S</td></tr>
    <tr><td>$\nu$</td><td></td></tr>
    <tr><td rowspan="2">Log-Normal</td><td>$\mu$</td><td>Relação V-S; Faixa Etária V/S; Gênero V/S; Cenário de Violação; Ocupação Feminina; Escolaridade Média</td></tr>
    <tr><td>$\sigma$</td><td>Faixa Etária V; Escolaridade Média; Gênero S</td></tr>
    <tr><td rowspan="2">Weibull</td><td>$\mu$</td><td>Relação V-S; Faixa Etária V/S; Gênero V/S; Cenário da Violação; Ocupação Feminina; Escolaridade Média</td></tr>
    <tr><td>$\sigma$</td><td>Relação V-S; Faixa Etária V; Gênero V</td></tr>
  </tbody>
</table>

Os Worm plot de cada ajuste estão abaixo. 

![Worm plot do modelo com distribuição Box-Cox Power Exponential (BCPE)](assets/analise-de-sobrevivencia/wp_bcpe.png "Worm plot do modelo com distribuição Box-Cox Power Exponential (BCPE)")

![Worm plot do modelo com distribuição Box-Cox t (BCT)](assets/analise-de-sobrevivencia/wp_bct.png "Worm plot da curva gerada pela distribuição Box-Cox t (BCT)")

![Worm plot do modelo com distribuição gama generalizada (GG)](assets/analise-de-sobrevivencia/wp_gg.png "Worm plot do modelo com distribuição gama generalizada (GG)")

![Worm plot do modelo com distribuição log-normal (LOGNO)](assets/analise-de-sobrevivencia/wp_logno.png "Worm plot do modelo com distribuição log-normal (LOGNO)")

![Worm plot do modelo com distribuição Weibull (WEI3)](assets/analise-de-sobrevivencia/wp_wei3.png "Worm plot do modelo com distribuição Weibull (WEI3)")

| Modelo | AIC | Média | Variância | Assimetria | Curtose |
|---|---|---|---|---|---|
| Box-Cox Power Exponential | 23568.73 | 0.003 | 0.998 | 0.008 | 2.992 |
| Box-Cox-T | 23588.93 | -0.002 | 0.996 | 0.001 | 2.928 |
| Gama Generalizada | 23585.91 | 0.001 | 0.999 | 0.018 | 2.974 |
| Log-normal | 23657.75 | -0.001 | 1.002 | -0.208 | 3.032 |
| Weibull | 23888.97 | 0.004 | 0.958 | 0.362 | 2.97 |

Considerando AIC e Worm plot a Box-Cox Power Exponential teve o melhor ajuste entre os modelos ajustados, seguida da Box-Cox-T e Gama Generalizada também com bons ajustes.
Das 8 variáveis iniciais, somente as variáveis Urbanização e Cor da Vítima não foram selecionadas em nenhuma ordem.


## Limitações e cuidados

- A censura está presente em todo o dataset, o que torna as estimativas instáveis. 
- Falta de generalização: para além da subnotificação, não conseguimos generalizar para a população pois não temos informação de quem ainda não foi resgatado, limitando a análise à apenas a amostra que colhemos.



Pacotes: `survival`, `icenReg`, `GAMLSS`, `ggplot2`.
