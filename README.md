# Site público — GitHub + Railway

Este diretório é uma versão separada somente do site público. Ele não contém o painel administrativo e não possui credenciais reais.

## Conteúdo incluído

- Página pública;
- Carrossel e imagens;
- Lista de presentes;
- Checkout Pro do Mercado Pago;
- Retorno de pagamentos;
- Webhook;
- Registro mínimo de pagamentos;
- Banco inicial sem convidados e sem pagamentos antigos.

## Conteúdo não incluído

- `admin_main.py`;
- `admin_static/`;
- Lista de convidados;
- Dados de RSVP;
- Access Token ou qualquer credencial real.

## Publicar em um repositório novo

Crie um repositório privado no GitHub, por exemplo:

```text
casamento-bovi-public
```

Envie para esse repositório somente o conteúdo desta pasta, e não a pasta administrativa do projeto original.

O Railway poderá ser conectado diretamente a esse repositório. Ele detectará o `railway.toml`, instalará `requirements.txt` e executará:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Variáveis do Railway

Configure no serviço:

```env
MERCADO_PAGO_ACCESS_TOKEN=seu_token_de_producao
MERCADO_PAGO_PUBLIC_KEY=sua_public_key
BACKEND_URL=https://seudominio.com.br
FRONTEND_URL=https://seudominio.com.br
DATABASE_URL=sqlite:////app/data/wedding.db
UPLOADS_DIR=/app/data/uploads
UPLOADS_SEED_DIR=uploads_seed
SEED_DATABASE_PATH=seed_wedding.db
USE_SANDBOX_CHECKOUT=false
```

Não envie `.env` para o GitHub. Cadastre os valores secretos diretamente nas variáveis do Railway.

## Persistência no Railway

Adicione um volume ao serviço e monte em:

```text
/app/data
```

O banco e os uploads serão preservados em:

```text
/app/data/wedding.db
/app/data/uploads/
```

Na primeira execução, o site copia `seed_wedding.db` e as imagens de `uploads_seed/` para o volume, caso ainda não existam.

## Mercado Pago

Configure o webhook para:

```text
https://seudominio.com.br/api/payments/webhook
```

Retornos:

```text
https://seudominio.com.br/pagamento/sucesso
https://seudominio.com.br/pagamento/falha
https://seudominio.com.br/pagamento/pendente
```

## Verificação

Depois do deploy, teste:

```text
https://seudominio.com.br/api/health
```

Também teste imagens, presentes, pagamento fixo, pagamento livre de R$ 1,00 e webhook.
