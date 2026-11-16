# Bruno Moreira — Portfólio

Site estático de portfólio para Bruno Moreira, diretor de arte e designer gráfico.

## Sincronização com o Behance

O GitHub Actions consulta o feed público do Bruno a cada hora e espelha os projetos listados no perfil em `behance-projects.json`. Cada projeto aparece uma vez, com a capa e o link direto para seu case no Behance. Projetos novos, mudanças de título/capa e remoções da lista pública são refletidos na próxima sincronização.

O workflow está em `.github/workflows/sync-behance.yml`. Ele pode ser iniciado manualmente pela aba **Actions** do GitHub. Quando o arquivo de dados muda, o workflow envia um commit para `main`; o Cloudflare Pages precisa estar conectado a este repositório e configurado para publicar a pasta `dist` para que essa alteração chegue ao domínio.

O feed público do Behance fornece títulos, links, descrições e capas. As capas são carregadas na versão WebP de maior resolução disponível no CDN público do Behance.

## Arquivos

- `index.html`: página e interações do site.
- `assets/`: imagens locais do portfólio anterior.
- `behance-projects.json`: dados sincronizados do feed público do Behance.
- `scripts/sync_behance.py`: rotina que atualiza o arquivo de dados.
- `.github/workflows/sync-behance.yml`: atualização horária pelo GitHub Actions.

## Publicação no Cloudflare Pages

Crie um projeto Pages conectado a este repositório e configure:

- Framework preset: `None`
- Build command: vazio
- Build output directory: `.` (raiz do repositório)

Depois que o projeto estiver publicado em `*.pages.dev`, conecte `brunomoreira.com.br` e `www.brunomoreira.com.br` no painel Cloudflare. Confira os registros DNS existentes antes de alterar nameservers ou remover registros do domínio.
