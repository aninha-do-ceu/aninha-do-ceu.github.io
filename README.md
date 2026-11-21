# aninha-do-ceu.github.io

Portfólio e estudos de caso de Ana Rosa Nascimento. Site estático gerado a partir de Markdown.

## Estrutura

```
content/projetos/*.md   ← você escreve aqui (um arquivo por estudo de caso)
static/                 ← copiado como está para o site
  index.html            ← portfólio
  assets/<projeto>/     ← figuras (PNG, SVG…)
  embed/<projeto>/      ← gráficos interativos (HTML do Plotly/Folium)
tools/                  ← build.py, page.css, requirements.txt
externos/               ← arquivos que pertencem a OUTROS repositórios (não são publicados)
dist/                   ← saída gerada (ignorada pelo git)
```

## Novo estudo de caso

1. Copie `content/projetos/_template.md` para `content/projetos/<nome>.md` (use o nome do repositório do projeto).
2. Coloque as figuras em `static/assets/<nome>/` e os interativos em `static/embed/<nome>/`.
3. Pré-visualize:
   ```
   pip install -r tools/requirements.txt   # só na primeira vez
   python tools/build.py
   python -m http.server 8000 -d dist      # http://localhost:8000
   ```
4. Dê push na branch `main`: o GitHub Actions roda o build e publica.

O build avisa sobre figuras ausentes e trechos `[preencher]` / `PREENCHA` que ainda restam no texto.

## Publicação (configuração única)

No GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
Depois de publicar, cadastre o site no Google Search Console e envie `https://aninha-do-ceu.github.io/sitemap.xml`.

## Galeria de mapas

`externos/mapas-disque100-HT/index_galeria_mapas.html` é o `index.html` do repositório
`mapas-disque100-HT` (usa caminhos relativos para os mapas daquele repo). Não é publicado por este site.
