# Webhook Setup Guide

## Configurar Webhooks de Recall.ai para desarrollo local

### 1. Instalar ngrok

```bash
# macOS
brew install ngrok

# Linux (snap)
snap install ngrok

# O descarga directa: https://ngrok.com/download
```

Crea una cuenta gratuita en [ngrok.com](https://ngrok.com) y configura tu authtoken:

```bash
ngrok config add-authtoken YOUR_TOKEN
```

### 2. Exponer el backend localmente

El backend corre en el puerto 8001 (mapeado desde Docker):

```bash
ngrok http 8001
```

Esto te da una URL pública como: `https://abc123.ngrok-free.app`

Tu webhook endpoint será: `https://abc123.ngrok-free.app/api/v1/webhooks/recall`

> **Tip:** Para una URL estática (no cambia entre reinicios), usa un dominio ngrok:
> ```bash
> ngrok http --domain=tu-dominio.ngrok-free.app 8001
> ```

### 3. Configurar en Recall.ai Dashboard

1. Ve al [Recall Webhooks Dashboard](https://eu-central-1.recall.ai/dashboard/webhooks/)
2. Click "Add Endpoint"
3. En **Endpoint URL**: `https://TU-URL-NGROK/api/v1/webhooks/recall`
4. Suscríbete a estos eventos:
   - `bot.joining_call`
   - `bot.in_waiting_room`
   - `bot.in_call_not_recording`
   - `bot.in_call_recording`
   - `bot.call_ended`
   - `bot.done`
   - `bot.fatal`
5. Click "Create"
6. **Copia el Signing Secret** (formato: `whsec_...`)

### 4. Configurar el secret en .env

```bash
RECALL_WEBHOOK_SECRET=whsec_tu_signing_secret_aqui
```

Reinicia el backend:

```bash
docker compose up -d --build backend
```

### 5. Probar el flujo completo

1. Asegúrate de que ngrok está corriendo
2. Crea una reunión en [meet.new](https://meet.new)
3. Envía un bot:
   ```bash
   docker compose exec backend python scripts/test_recall_bot.py "https://meet.google.com/TU-URL"
   ```
4. Deberías ver en los logs del backend los webhooks llegando:
   ```bash
   docker compose logs -f backend
   ```

### Notas

- **Sin webhook secret:** En modo development, los webhooks se procesan sin verificar firma (para facilitar testing).
- **Con webhook secret:** En producción, la firma Svix se verifica siempre.
- **Svix retry:** Si tu endpoint no responde 2xx, Recall.ai reintenta durante 24h con backoff.
- **Timeout:** Los webhooks tienen timeout de 15 segundos. Procesar async si necesitas más tiempo.
