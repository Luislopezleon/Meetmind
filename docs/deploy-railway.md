# Deploy en Railway

## Pasos

### 1. Crear cuenta
Ve a [railway.app](https://railway.app) y haz login con tu cuenta de GitHub.

### 2. Crear proyecto
- Click "New Project"
- Selecciona "Deploy from GitHub repo"
- Conecta tu repo `Luislopezleon/Meetmind`

### 3. Añadir PostgreSQL
- En el proyecto, click "New" → "Database" → "PostgreSQL"
- Railway crea la DB automáticamente y te da una `DATABASE_URL`

### 4. Añadir Redis
- Click "New" → "Database" → "Redis"
- Railway crea Redis y te da una `REDIS_URL`

### 5. Configurar el Backend
- Click en el servicio del repo → Settings
- **Root Directory:** `backend`
- **Dockerfile Path:** `Dockerfile.prod`
- En **Variables**, añadir:
  ```
  DATABASE_URL=<la que te dio Railway para PostgreSQL>
  REDIS_URL=<la que te dio Railway para Redis>
  GEMINI_API_KEY=<tu key>
  RECALL_AI_API_KEY=<tu key>
  RECALL_REGION=eu-central-1
  ENVIRONMENT=production
  LOG_LEVEL=INFO
  SECRET_KEY=<genera una clave random larga>
  FRONTEND_URL=<URL del dashboard cuando lo tengas>
  ```
- El puerto se detecta automáticamente (8000)

### 6. Configurar el Dashboard
- Click "New" → "GitHub Repo" → misma repo
- **Root Directory:** `dashboard`
- **Dockerfile Path:** `Dockerfile.prod`
- En **Variables**, añadir:
  ```
  NEXT_PUBLIC_API_URL=<URL del backend que Railway te dio>
  NEXT_PUBLIC_WS_URL=<misma URL pero con wss://>
  ```

### 7. Ejecutar migraciones
Una vez el backend esté deployado:
- Ve al servicio backend → click en "Terminal" (o usa Railway CLI)
- Ejecuta: `alembic upgrade head`

### 8. Configurar webhooks de Recall.ai
- Tu backend ahora tiene URL fija (ej: `https://meetmind-backend-production.up.railway.app`)
- Ve al [Recall Dashboard](https://eu-central-1.recall.ai/dashboard/webhooks/)
- Añade endpoint: `https://TU-URL/api/v1/webhooks/recall`
- Copia el signing secret → añádelo como variable `RECALL_WEBHOOK_SECRET`

### 9. Verificar
```bash
curl https://TU-URL-BACKEND/health/
# {"status": "healthy", ...}
```

## Costes
- Railway Free Tier: 500 horas de ejecución/mes + $5 de crédito
- Con 4 servicios (backend, dashboard, postgres, redis) consume ~$5-10/mes después del free tier
- Para una POC/demo es más que suficiente

## Alternativa: Render.com
Si prefieres Render (también gratis pero los containers se duermen):
- Mismo proceso pero en render.com
- Usa `render.yaml` en vez de Railway config
