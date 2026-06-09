# Instagram AI Actions Starter

Starter kit separato per generare e pubblicare post Instagram con GitHub Actions, OpenAI Images API, Meta Instagram Graph API e notifica Telegram.

## Architettura pratica

Flusso consigliato, a costo minimo:

1. GitHub Actions parte a orario fisso o manualmente.
2. `src/generate_instagram_post.py` prende il prossimo prompt da `content/queue.yml`, genera immagine e caption, salva gli asset in `public/generated/`.
3. Il workflow committa gli asset sul repository, così l'immagine diventa raggiungibile via GitHub Pages o raw URL pubblico.
4. Il workflow invia preview su Telegram, nello stesso stile del flusso X/Telegram.
5. Se `AUTO_PUBLISH=true`, `src/publish_instagram.py` pubblica su Instagram. Se `AUTO_PUBLISH=false`, usi il workflow manuale `Publish approved Instagram post`.

## Servizi necessari

- GitHub Actions: orchestrazione gratuita per volumi bassi.
- OpenAI API: generazione immagine. Il costo scala solo quando generi.
- Meta for Developers: Instagram Graph API per pubblicare su un account Instagram Business o Creator collegato a una pagina Facebook.
- Hosting immagine pubblico: GitHub Pages se il repo e gli asset possono essere pubblici; altrimenti Cloudinary/R2/S3.
- Telegram Bot: preview e log operativo.

## Segreti GitHub

Imposta questi repository secrets:

- `OPENAI_API_KEY`
- `IG_USER_ID`
- `IG_ACCESS_TOKEN`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `PUBLIC_ASSET_BASE_URL`

Esempio `PUBLIC_ASSET_BASE_URL`:

```text
https://<utente>.github.io/<repo>/generated
```

Se non usi GitHub Pages ma raw GitHub in repo pubblico:

```text
https://raw.githubusercontent.com/<utente>/<repo>/main/public/generated
```

## Variabili GitHub

Imposta queste repository variables, o lascia i default nel workflow:

- `AUTO_PUBLISH`: `false` consigliato all'inizio, `true` quando ti fidi del flusso.
- `OPENAI_IMAGE_MODEL`: modello immagini da usare.
- `BRAND_STYLE`: breve descrizione dello stile visivo.

## Setup Meta

1. Crea una app su Meta for Developers.
2. Collega una pagina Facebook all'account Instagram Business/Creator.
3. Ottieni un access token long-lived con permessi di pubblicazione Instagram.
4. Ricava `IG_USER_ID` dell'account Instagram.
5. Verifica che l'URL immagine sia pubblico e scaricabile senza login.

## Uso

Generazione schedulata:

```yaml
on:
  schedule:
    - cron: "15 8 * * 1,3,5"
```

Generazione manuale:

Actions -> Generate Instagram post -> Run workflow.

Pubblicazione manuale:

Actions -> Publish approved Instagram post -> Run workflow -> inserisci `post_id` generato.

## Note operative

- Tieni `AUTO_PUBLISH=false` per i primi 7-10 post.
- Ogni prompt deve avere un `id` stabile.
- Evita testo piccolo nell'immagine: Instagram comprime e i generatori AI possono renderlo male.
- Usa caption generate da template per ridurre costi; fai generare solo l'immagine.
- Non mettere prompt o caption da input pubblici non fidati dentro workflow con privilegi di scrittura.

