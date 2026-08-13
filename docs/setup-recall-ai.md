# Configuración de Recall.ai API

## 📋 Información General

**Recall.ai** es el servicio que usamos para que nuestro bot se una automáticamente a reuniones de Google Meet, Teams y Zoom.

### Pricing (2026)
- **Free Tier**: 5 horas de grabación gratuitas al registrarse
- **Pay As You Go**: $0.50 por hora de grabación
- **Para desarrollo**: 5 horas gratuitas son suficientes para múltiples demos

## 🚀 Setup Paso a Paso

### Paso 1: Crear Cuenta
1. Ve a [recall.ai](https://recall.ai)
2. Click en "Sign Up" 
3. Elige **"Pay As You Go Plan"** (incluye 5 horas gratuitas)
4. Completa el registro con email/password

### Paso 2: Obtener API Key
1. Una vez registrado, ve al [Dashboard de Recall](https://app.recall.ai)
2. Navega a **"API Keys"** en el sidebar
3. Click en **"Create API Key"**
4. Copia la API key generada

### Paso 3: Configurar en MeetMind
1. Abre el archivo `.env` en el proyecto
2. Actualiza la variable:
   ```bash
   RECALL_AI_API_KEY=tu_api_key_aqui
   ```

### Paso 4: Configurar Webhook URL
Para recibir eventos de Recall.ai cuando el bot se una/salga de reuniones:

1. En el Dashboard de Recall.ai, ve a **"Webhooks"**
2. Configura webhook URL: `https://tu-dominio.com/api/v1/webhooks/recall`
3. Para desarrollo local: usa [ngrok](https://ngrok.com) para exponer localhost

## 🔧 Variables de Entorno Requeridas

```bash
# Recall.ai Configuration
RECALL_AI_API_KEY=rk_xxxxxxxxxxxxxxxxxxxxxxxx
RECALL_WEBHOOK_SECRET=webhook_secret_opcional
RECALL_REGION=us-west-2  # Default region
```

## 📡 Regiones Disponibles

Recall.ai opera en múltiples regiones. Para mejor performance:
- **US West**: `us-west-2` (default)
- **US East**: `us-east-1` 
- **Europe**: `eu-west-1`

## 🧪 Testing API Connection

Una vez configurado, puedes probar la conexión:

```bash
curl -X GET "https://api.recall.ai/api/v1/bots" \
  -H "Authorization: Token YOUR_API_KEY" \
  -H "Accept: application/json"
```

Respuesta esperada:
```json
{
  "results": [],
  "count": 0
}
```

## 🚨 Limitaciones del Free Tier

- **5 horas de grabación** total
- **API rate limits**: 100 requests/minute
- **Regiones**: Solo US West por defecto
- **Retención**: 30 días de datos

## 🔐 Seguridad

⚠️ **IMPORTANTE**: 
- Nunca commits la API key al código
- Úsala solo en variables de entorno
- Rota las keys regularmente en producción

## 📚 Recursos Útiles

- **Documentación Oficial**: [docs.recall.ai](https://docs.recall.ai)
- **API Reference**: [docs.recall.ai/api](https://docs.recall.ai/api)
- **Soporte**: Via dashboard o email

---

**Siguiente**: Una vez configurado, procedemos a implementar el `RecallService` en Python.