---
titulo: Título do projeto
subtitulo: Uma linha resumindo o projeto (aceita **negrito** e *itálico*).
descricao: Frase curta para buscadores e prévia de link (opcional).
linguagens: R, Python
tags: Tema 1, Tema 2, 2025–2026
repo: nome-do-repositorio
autores: Ana Rosa Nascimento
rodape: Evento ou publicação (opcional)
data: 2026-01-31
imagem: assets/nome-do-projeto/capa.png
imagem_alt: Descrição da imagem de capa
rascunho: sim
---

<!-- ================================================================
  COMO USAR ESTE TEMPLATE
  1. Copie este arquivo para  content/projetos/nome-do-projeto.md
     (use o nome do repositório; vira a URL /projetos/nome-do-projeto/)
  2. Figuras em static/assets/nome-do-projeto/ · interativos em static/embed/nome-do-projeto/
  3. Pré-visualizar (na raiz do repositório):
       python tools/build.py
       python -m http.server 8000 -d dist     →  http://localhost:8000/projetos/nome-do-projeto/
  4. git push na main: o GitHub Actions refaz o build e publica.
     (Edite sempre o .md; dist/ é gerada e não vai para o git.)

  Cabeçalho (entre os ---): campos opcionais, exceto titulo.
    data = AAAA-MM-DD (aparece no Google) · imagem = capa para prévia de link
    (LinkedIn/WhatsApp), ideal 1200x630 · rascunho: sim = não indexa nem lista.
    Remova as linhas data/imagem/rascunho se não for usar.
    linguagens = chips verdes · tags = chips cinza · repo = nome do repo
    (ou URL completa) · autores/rodape = linha final da página.

  Texto: Markdown comum.  Cada "## Título" vira um cartão na página.
  Fórmulas (LaTeX):  $x^2$ no meio do texto,  $$ ... $$  destacada,
    ou ambientes \begin{align} ... \end{align}.  Use \$ para um cifrão literal.
  Figuras:  ![descrição](assets/projeto/figura.png "Legenda")
    — numeração automática ("Figura 1.") e aviso visual se o arquivo não existir.
    Caminhos de imagem e embed são relativos à raiz do site (static/ vira a raiz):
    assets/projeto/figura.png  =  static/assets/projeto/figura.png
  Interativos (Plotly/Folium):  [[embed: embed/projeto/mapa.html | 480 | Legenda]]
    (altura e legenda são opcionais; deve ficar sozinho na linha).
  Dica SEO: o título e o subtítulo viram o que aparece no Google; escreva
    com as palavras que alguém buscaria (ex.: "análise de sobrevivência").
  Código:  ```r ... ```  (destaque de sintaxe automático).
  Comentários HTML como este não aparecem na página.
================================================================= -->

## Resumo

2–4 frases: o problema, o que você fez e o resultado principal.

## Dados

Fonte, período, tamanho da base, variáveis principais, limpeza feita.

- variável / fonte
- outra variável

## Metodologia

### Passo 1 — ...

Explique a abordagem em linguagem clara. Fórmula destacada:

$$S(t) = P(T > t)$$

E no meio do texto: o estimador $\hat{\beta}$ maximiza a verossimilhança.

### Passo 2 — ...

Alinhando várias equações:

$$
\begin{aligned}
h(t \mid x) &= h_0(t)\,e^{x^\top\beta} \\
S(t \mid x) &= S_0(t)^{e^{x^\top\beta}}
\end{aligned}
$$

## Resultados

![Descreva o gráfico aqui](assets/nome-do-projeto/figura1.png "Legenda explicando o que o gráfico mostra.")

Interpretação do gráfico em linguagem de negócio/técnica.

[[embed: embed/nome-do-projeto/grafico-interativo.html | 480 | Gráfico interativo — arraste, dê zoom e passe o mouse.]]

| Modelo | AIC | Observação |
|---|---|---|
| A | 100,2 | referência |
| B | 95,7 | melhor ajuste |

## Limitações e cuidados

Vieses, qualidade dos dados, premissas fortes. Recrutador adora essa seção.

> Destaque importante: blocos de citação viram caixas de destaque.

## Reprodução

```r
# comandos para reproduzir a análise
source("analysis/main.R")
```
