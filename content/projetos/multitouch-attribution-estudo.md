---
titulo: Atribuição multitoque: sobrevivência, GAM e cadeias de Markov
subtitulo: Tentativa de atribuir conversões a canais de marketing com modelos de sobrevivência, GAM e cadeias de Markov. Estudo sem conclusão efetivada: os dados não distinguiram os canais.
descricao: Estudo de caso em andamento: atribuição multitoque com modelos de sobrevivência para eventos recorrentes (Andersen–Gill, Prentice–Williams–Peterson e Cox), GAM e cadeias de Markov em R e Python. Os modelos não distinguiram os canais e o estudo não chegou a uma conclusão.
linguagens: R, Python
tags: Atribuição multitoque, Análise de sobrevivência, Eventos recorrentes, Andersen–Gill, GAM, Cadeias de Markov, Marketing analytics
repo: multitouch-attribution-estudo
autores: Ana Rosa Nascimento
---

## Resumo

> **Status: sem conclusão efetivada.** Este estudo não produziu um modelo de atribuição que possa ser recomendado. Registramos aqui o que foi tentado, o que deu errado e o que os resultados permitem, e não permitem, afirmar.

Neste estudo, usamos um conjunto público de jornadas de marketing (10.000 interações de 2.847 usuários, em 48 horas) para estimar quanto cada canal contribui para a conversão. Como o conjunto traz várias conversões por usuário, a ideia foi modelar eventos recorrentes. Foram feitos diversos testes com modelos de sobrevivência (entre eles Andersen–Gill, Prentice–Williams–Peterson e Cox com variância robusta por usuário, com e sem fragilidade, e modelos paramétricos no GAMLSS), modelos aditivos generalizados (GAM) e a atribuição por cadeias de Markov de ordem 1 a 5.

Em todos os casos, os canais não se distinguiram. As taxas de conversão são quase idênticas (de 48% a 50% por canal), os modelos de sobrevivência e os GAM não encontraram diferença entre canais, e a atribuição por Markov distribui o crédito de forma próxima da uniforme. Esse resultado descreve este conjunto de dados, não os canais de marketing em geral. O estudo parou nesse ponto, e o próximo passo é refazer a análise com outros dados.

## Dados

- **Fonte:** conjunto *Multi-Touch Attribution*, do Kaggle.
- **Registros:** 10.000 interações (toques) de 2.847 usuários, em 10 e 11/02/2025 (48 horas), com média de 3,5 interações por usuário.
- **Variáveis:** usuário, horário, canal (6 canais), campanha e um indicador de conversão (sim ou não) **em cada interação**.
- **Censura:** 16,4% dos usuários não tiveram nenhuma conversão até o fim das 48 horas (zero conversões até então). Nos modelos de sobrevivência, eles entram como censura à direita.

| Canal | Interações | Taxa de conversão |
|---|---|---|
| Direct Traffic | 1.721 | 49,6% |
| Referral | 1.685 | 49,9% |
| Display Ads | 1.669 | 49,6% |
| Social Media | 1.662 | 49,3% |
| Email | 1.654 | 50,2% |
| Search Ads | 1.609 | 48,0% |

Os canais têm tamanhos parecidos (entre 16% e 17% das interações cada) e taxas de conversão quase iguais. A taxa global é de 49,4% por interação.

![Proporção de usuários por canal](assets/multitouch-attribution-estudo/usuarios_canal.png "Proporção de usuários por canal: os seis canais têm participações próximas.")

![Distribuição de usuários por canal e conversão](assets/multitouch-attribution-estudo/usuarios_canal_conversao.png "Usuários por canal (anel interno) e por conversão (anel externo): em cada canal, convertidos e não convertidos ficam em proporções semelhantes.")

![Total de conversões por hora e canal](assets/multitouch-attribution-estudo/conversoes_hora.png "Total de conversões por hora e por canal, nas 48 horas de observação: as séries oscilam em torno da mesma faixa, sem canal dominante.")

![Distribuição das taxas de conversão por canal e hora](assets/multitouch-attribution-estudo/hist_conversao.png "Histograma das taxas de conversão por canal e por hora: concentração em torno de 50%.")

![Distribuição das taxas de conversão por canal](assets/multitouch-attribution-estudo/conversao_canal.png "Distribuição das taxas de conversão por hora, separada por canal: as curvas praticamente se sobrepõem.")

## A pergunta e os percalços

A ideia inicial era um modelo dinâmico de atribuição. Para um usuário no meio de uma jornada, em uma hora $T$, queríamos estimar a probabilidade de conversão a partir da proporção de usuários que converteram até $T-1$, do número de interações e da última etapa. A probabilidade de conversão seria a função de risco de um modelo de sobrevivência, atualizada a cada hora, como uma inferência sequencial.

Os dados trouxeram três problemas:

1. **Não existe uma conversão única por usuário.** A conversão é registrada em cada interação, por canal e campanha, e muitos usuários convertem em mais de um canal. Por isso não dá para perguntar qual canal causou "a" conversão final. A unidade passa a ser a conversão em um canal.
2. **Jornadas demais, com pouca repetição.** São 1.464 jornadas distintas para 2.847 usuários, e 1.160 delas (79%) aparecem uma única vez. Modelar a jornada completa gera estimativas instáveis.
3. **Repetição de canal na jornada.** O mesmo usuário pode interagir várias vezes com um canal. O modelo de Cox tradicional supõe um evento por usuário e não se aplica diretamente.

Para contornar isso, a pergunta mudou de "qual a probabilidade de um usuário converter?" para "qual a probabilidade de converter em um certo canal, dada a jornada até ali?". Em vez da sequência completa, usamos a contagem de interações por canal. Como o conjunto traz vários eventos por usuário, a ideia foi modelar eventos recorrentes: testamos diversos modelos, entre eles Andersen–Gill, Prentice–Williams–Peterson (PWP) e um modelo de Cox com variância robusta agrupada por usuário. A incrementalidade de cada canal seria avaliada comparando jornadas com e sem ele.

Primeiro, ajustamos os modelos de sobrevivência com o canal como covariável, e as curvas ficaram muito parecidas entre os canais. Por isso, em seguida, decidimos ajustar um modelo separado para cada canal, para estimar a probabilidade de conversão a partir das variáveis construídas na base. Não houve vazamento do desfecho: as variáveis de histórico (canal anterior, conversões anteriores, proporção de conversões anteriores e contagens por canal) usam apenas interações anteriores à atual, e o treino e a validação são separados no tempo (até a hora 30 e depois dela). Os tempos (desde a última interação e desde o início da campanha) usam o horário da própria interação, que é conhecido quando ela ocorre.

Chegou a ser planejada também uma abordagem bayesiana, com a conversão de cada canal modelada por uma beta e o número de interações até a conversão por uma binomial negativa. Ela não foi implementada.

## Metodologia

### Construção da base

A base foi construída em Python (`analise_marketing.ipynb`). Para cada usuário, as interações são ordenadas no tempo, e cada linha recebe:

- o tempo desde a interação anterior (ou desde o início da campanha, na primeira) e o tempo desde o início da campanha;
- a ordem do evento, o canal da etapa anterior e o canal da primeira etapa;
- o indicador de conversão, o número de conversões anteriores e a proporção de conversões anteriores;
- a contagem de interações anteriores em cada um dos seis canais (a interação atual não entra na contagem);
- o indicador de censura (usuário sem nenhuma conversão até o fim da observação).

### Modelos de sobrevivência

- **Kaplan–Meier:** probabilidade acumulada de conversão desde o início da campanha, por canal de entrada, e tempo entre interações, por canal do toque anterior. A função média acumulada (MCF) descreve o número médio de conversões por usuário.
- **Eventos recorrentes:** o conjunto registra várias conversões por usuário, então a ideia era modelar eventos recorrentes. Foram feitos diversos testes, entre eles:
  - **Andersen–Gill:** um risco-base comum a todos os eventos do usuário, com os eventos tratados como independentes dado o histórico (as covariáveis);
  - **Prentice–Williams–Peterson (PWP):** considera a ordem dos eventos e condiciona a ocorrência de cada evento ao anterior;
  - **Cox no relógio da campanha**, descrito a seguir, que é a especificação usada nos resultados abaixo.
- **Cox no relógio da campanha:** modelo de riscos proporcionais de Cox em que cada interação é uma observação, com função de risco
  $$\lambda_i(t) = \lambda_0(t)\,\exp\{\mathbf{x}_i^\top \boldsymbol{\beta}\}$$
  e variância robusta agrupada por usuário. O tempo $t$ é medido em horas desde o início da campanha (`tempo_interacao_horas_campanha`), e o evento é a conversão naquela interação. Como cada interação entra em risco desde a hora 0, um usuário com várias interações conta mais de uma vez no mesmo instante. Por isso os resultados são lidos como comparação entre interações, e não como taxa por usuário. A primeira versão do Andersen–Gill usava o tempo desde a última interação com início zero e, na prática, não usava intervalos entre interações. Ela foi substituída por esta. Foram ajustadas cinco especificações, combinando canal, canal anterior, contagens de interações por canal, proporção de conversões anteriores e primeira etapa, comparadas por AIC e BIC.
- **Fragilidade:** efeito aleatório por usuário (fragilidade gama), para capturar usuários com jornadas parecidas e propensões diferentes.
- **Riscos proporcionais:** testados com os resíduos de Schoenfeld (`cox.zph`), além dos resíduos de martingale e de desvio.
- **GAMLSS:** modelos paramétricos com censura à direita (Weibull e gama), em que o tempo é o intervalo desde a última interação do usuário (`tempo_interacao_horas`), com seleção de covariáveis por AIC (`stepGAIC`) para os parâmetros de posição e de escala.

### GAM

Como o canal, usado como covariável nos modelos de sobrevivência, não separou as curvas, o GAM é ajustado separadamente para cada canal, com ligação logit:

$$\operatorname{logit}\Pr(\text{converteu}=1) = \beta_0 + \sum_{j} f_j(x_j) + \text{termos categóricos}$$

As funções suaves $f_j$ (base com $k=3$, ou seja, no máximo 2 graus de liberdade por termo e curvas simples, estimadas por REML, com penalização que permite zerar termos) foram aplicadas ao tempo desde a última interação, ao tempo desde o início da campanha, à ordem do evento, à proporção de conversões anteriores e às contagens de interações por canal. O canal anterior e a primeira etapa entram como categorias. As primeiras interações de cada usuário não têm canal anterior e ficam fora do ajuste (cerca de 42% das linhas do treino). O treino usa as interações até a hora 30, e a validação, as posteriores.

### Atribuição por cadeias de Markov

Cada jornada é a sequência de canais do usuário. Nesta etapa, a conversão foi reduzida a uma por usuário: a jornada converte se houver qualquer conversão nela. Ajustamos cadeias de ordem 1 a 5 com o pacote `ChannelAttribution`. O efeito de remoção de um canal $c$ é a queda relativa da probabilidade de conversão quando $c$ é retirado do grafo:

$$RE_c = 1 - \frac{P(\text{conversão} \mid \text{sem } c)}{P(\text{conversão})}$$

As conversões atribuídas a cada canal são proporcionais a $RE_c / \sum_k RE_k$.

## Resultados

### Modelos de sobrevivência

- **Canais:** com o canal como covariável, as curvas de sobrevivência ficaram muito parecidas. No modelo de Cox com canal e canal anterior (7.153 interações e 3.541 conversões), o teste robusto global para o canal deu p = 0,68, com razões de risco entre 0,96 e 1,00 em relação ao Direct Traffic.
- **Riscos proporcionais:** nesse modelo, o teste de Schoenfeld rejeitou a proporcionalidade para o canal (p = 0,011). Por isso ajustamos também modelos paramétricos no GAMLSS.
- **Ajustes iniciais:** na versão anterior dos modelos (com o tempo desde a última interação como escala de tempo), a variância estimada da fragilidade foi da ordem de $5 \times 10^{-7}$, o que indica pouca heterogeneidade individual. Termos de contagem de interações apareceram como significativos em alguns ajustes, mas deixaram de ser com a fragilidade, e os coeficientes dos modelos no GAMLSS não foram significativos. Esses ajustes serão refeitos com a especificação atual.

### GAM

Na divisão de treino e validação, a capacidade de discriminar conversões foi medida pela área sob a curva ROC (AUC) nas interações da validação. Os AUC ficaram em torno de 0,5, que é o valor de um modelo sem capacidade preditiva. Poucos termos foram significativos a 5%, sem padrão consistente entre os canais (e sem correção para múltiplos testes).

| Canal | Interações usadas no ajuste | Termos com p < 0,05 | AUC na validação |
|---|---|---|---|
| Search Ads | 567 | 3 de 20 | 0,524 |
| Display Ads | 595 | 1 de 20 | 0,503 |
| Social Media | 599 | 2 de 20 | 0,465 |
| Direct Traffic | 651 | 2 de 20 | 0,503 |
| Email | 591 | 2 de 20 | 0,537 |
| Referral | 607 | 0 de 20 | 0,519 |

### Atribuição por Markov

Os efeitos de remoção ficam entre 37% e 49% conforme a ordem, e as diferenças entre canais dentro de cada ordem são de no máximo 4 pontos percentuais. A tabela mostra o AUC usado para escolher a ordem e a faixa dos efeitos de remoção (valores de uma execução com semente fixa, e as simulações variam ligeiramente entre execuções).

| Ordem | AUC | AUC penalizado | Efeito de remoção (mínimo a máximo) |
|---|---|---|---|
| 1 | 0,523 | 0,522 | 37,1% a 40,4% |
| 2 | 0,707 | 0,705 | 43,5% a 44,7% |
| 3 | 0,828 | 0,824 | 44,0% a 47,2% |
| 4 | 0,892 | 0,887 | 46,5% a 49,4% |
| 5 | 0,904 | 0,895 | 44,9% a 48,9% |

Para a ordem 5, que teve o maior AUC e foi adotada, o crédito fica próximo de um sexto para cada canal (de 378 a 411 das cerca de 2.381 conversões):

| Canal | Efeito de remoção | Conversões atribuídas |
|---|---|---|
| Display Ads | 48,9% | 410,9 |
| Social Media | 48,7% | 409,7 |
| Referral | 48,0% | 403,7 |
| Direct Traffic | 47,0% | 395,6 |
| Email | 45,6% | 383,2 |
| Search Ads | 44,9% | 378,0 |

A função `choose_order` não sugeriu uma ordem até 5, e o AUC cresce a cada ordem. Como 79% das jornadas aparecem uma única vez, esse crescimento é compatível com sobreajuste, e não há validação em dados separados neste estudo. O ranking dos canais também muda de uma ordem para outra, então ele não sustenta uma recomendação.

## Conclusão e status

**Não houve conclusão efetivada.**

- Nenhum modelo apontou diferença entre os canais, e o GAM não mostrou capacidade preditiva (AUC de validação entre 0,47 e 0,54).
- A atribuição por Markov reparte o crédito de forma quase uniforme, e o ranking varia entre as ordens. Ela não serve de base para decidir a alocação de um orçamento.
- As taxas de conversão são quase iguais entre canais, campanhas e horas. Uma leitura possível, **não testada**, é que neste conjunto a conversão não dependa do canal, caso em que uma alocação uniforme seria coerente. Isso é uma hipótese sobre os dados, não um resultado.

Limitações do estudo: só 48 horas de observação, conversão registrada por interação (e não por usuário), nenhuma informação de custo por canal e nenhum desenho experimental. A validação do GAM separa as interações no tempo, mas não os usuários, porque cada usuário tem várias linhas e a conversão é registrada por linha: 1.889 dos 2.585 usuários do treino também aparecem na validação. Por isso o estudo não permite estimar o efeito causal de um canal.

Próximos passos: refazer a análise exploratória com outros dados e retomar a abordagem bayesiana planejada.

## Reprodução

O notebook `analise_marketing.ipynb` (Python, com `pandas`, `numpy`, `matplotlib`, `seaborn` e `kagglehub`) baixa os dados e gera a base `df_atrib_sobrev.csv`. Os scripts em R leem essa base:

- `modelo_sobrevivencia.R`: Kaplan–Meier, Andersen–Gill, Cox, fragilidade e GAMLSS (pacotes `survival`, `survminer`, `coxme`, `gamlss`, `gamlss.cens`, `reda`);
- `modelo_gam.R`: GAM e cadeias de Markov (pacotes `mgcv`, `ChannelAttribution` e `dplyr`).

Cada script define o diretório de trabalho com `setwd()` no início, que precisa ser ajustado.
