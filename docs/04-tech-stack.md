# 4. Stack Tecnológico Detallado

## 🛠️ Backend Stack

### FastAPI + Python 3.11
**Versión:** FastAPI 0.104.1 + Python 3.11.8

**Justificación técnica:**
- **Performance:** 3x más rápido que Flask, comparable con Node.js
- **Type Safety:** Type hints nativos + Pydantic validation automática
- **Documentation:** OpenAPI/Swagger generado automáticamente
- **Async Native:** Soporte nativo para async/await desde el core
- **Ecosystem:** Integración perfecta con SQLAlchemy, Alembic, Redis

**Dependencias core:**
```python
fastapi==0.104.1           # Web framework
uvicorn[standard]==0.24.0  # ASGI server
pydantic==2.5.0           # Data validation
pydantic-settings==2.1.0  # Settings management
```

### PostgreSQL + SQLAlchemy
**Versión:** PostgreSQL 15 + SQLAlchemy 2.0.23

**Justificación técnica:**
- **ACID Compliance:** Crítico para consistency de meeting data
- **Relational Model:** Meeting ↔ Transcripts ↔ ActionItems relationships
- **JSON Support:** Nativo para metadata flexible (participants, settings)
- **Performance:** Query optimization + connection pooling
- **Migrations:** Alembic para schema evolution controlada

**Configuración optimizada:**
```python
# database.py optimizations
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # 10 conexiones base
    max_overflow=20,       # Hasta 30 total
    pool_pre_ping=True,    # Health check connections
    pool_recycle=300,      # Recycle cada 5 min
    echo=False             # No SQL logging en prod
)
```

### Redis for Caching & Pub/Sub
**Versión:** Redis 7.2 + redis-py 5.0.1

**Justificación técnica:**
- **Real-time Messaging:** Pub/Sub para WebSocket distribution
- **Session Cache:** User sessions + temporary data
- **Rate Limiting:** Request throttling implementation
- **Performance:** Sub-millisecond latency para live updates

**Canales Redis:**
```yaml
Channels:
  transcript:{meeting_id}: Transcript chunks en tiempo real
  insights:{meeting_id}: Action items + decisions detectadas  
  meeting:{meeting_id}:status: Estado del meeting (bot_joined, ended, etc)
  
Cache Keys:
  session:{user_id}: User session data
  meeting:{meeting_id}:metadata: Meeting info cache
  ratelimit:{ip}: Request rate limiting
```

## 🤖 AI & Processing Stack

### LangGraph + OpenAI
**Versiones:** LangGraph 0.0.38 + OpenAI 1.3.5

**Justificación técnica:**
- **State Management:** LangGraph maneja estado complejo entre nodos
- **Multi-step Processing:** Pipeline de análisis con dependencias
- **Error Recovery:** Retry logic y fallbacks automáticos
- **Observability:** Tracing completo del flujo del agente

**Modelos utilizados:**
```python
Models:
  gpt-4o-mini: 
    - Uso: Detección de action items, decisiones, riesgos
    - Costo: ~$0.15/1M tokens input
    - Latencia: ~800ms average
    - Accuracy: 85%+ en classification tasks
    
  gpt-4o:
    - Uso: Generación de resumen ejecutivo final
    - Costo: ~$5/1M tokens input  
    - Latencia: ~1.2s average
    - Quality: Premium para summaries
```

### Deepgram for Speech-to-Text
**Versión:** Deepgram SDK 3.2.7

**Justificación técnica:**
- **Streaming STT:** Real-time transcription con latencia < 300ms
- **Speaker Diarization:** Identifica quién habla automáticamente
- **Custom Models:** Nova-3 optimizado para meetings
- **Cost Efficiency:** $0.0043/minuto vs $0.006/min AssemblyAI

**Configuración optimizada:**
```python
# Deepgram config for meetings
config = {
    "model": "nova-2",
    "language": "es-ES",           # Spanish optimized  
    "smart_format": True,          # Punctuation + formatting
    "diarize": True,              # Speaker identification
    "multichannel": False,        # Single channel audio
    "interim_results": True,      # Partial results for low latency
}
```

### Recall.ai Meeting Bot SDK
**Versión:** recall-ai 0.1.0

**Justificación técnica:**
- **Platform Agnostic:** Google Meet, Teams, Zoom unified API
- **No WebRTC Complexity:** Evita meses de desarrollo custom
- **Audio Quality:** High-quality audio capture automático
- **Meeting Management:** Join/leave logic handled by service

**Integration pattern:**
```python
# Recall.ai workflow
1. create_bot(meeting_url) → bot_id
2. webhook: bot_joined → start transcription pipeline  
3. webhook: transcript_chunk → process with Deepgram
4. webhook: meeting_ended → trigger summary generation
```

## 🎨 Frontend Stack

### Next.js 15 + TypeScript
**Versión:** Next.js 15.0.1 + TypeScript 5.3

**Justificación técnica:**
- **App Router:** Nueva arquitectura más performante
- **Server Components:** SSR híbrido para mejor SEO
- **Type Safety:** End-to-end typing con backend
- **Real-time Ready:** Excelente WebSocket support

**Configuración optimizada:**
```javascript
// next.config.js
module.exports = {
  experimental: {
    appDir: true,           # App Router enabled
    serverActions: true,    # Server Actions para forms
  },
  typescript: {
    ignoreBuildErrors: false  # Strict type checking
  }
}
```

### Tailwind CSS + Headless UI
**Versión:** Tailwind CSS 3.4 + Headless UI 2.0

**Justificación técnica:**
- **Rapid Prototyping:** Faster than custom CSS
- **Consistent Design:** Design system built-in
- **Performance:** Purged CSS, smaller bundles
- **Accessibility:** Headless UI components son accesibles by default

**Design System:**
```css
/* Color palette */
Primary: #3B82F6 (blue-500)
Secondary: #10B981 (emerald-500)  
Accent: #F59E0B (amber-500)
Neutral: #6B7280 (gray-500)

/* Typography scale */
Text-xs: 0.75rem    /* Timestamps, metadata */
Text-sm: 0.875rem   /* Body text, transcripts */
Text-base: 1rem     /* Default */  
Text-lg: 1.125rem   /* Headings */
```

### React Query + Zustand
**Versión:** React Query 5.8 + Zustand 4.4

**Justificación técnica:**
- **Server State:** React Query para API calls + caching
- **Client State:** Zustand para UI state (sidebar, modals)
- **Real-time Sync:** Optimistic updates + background sync
- **DevX:** Excellent debugging tools

## 🚀 DevOps & Infrastructure

### Docker + Docker Compose
**Versión:** Docker 24.0 + Compose 2.23

**Justificación técnica:**
- **Environment Consistency:** Dev/staging/prod identical
- **Service Isolation:** Cada servicio en su container
- **Scaling Ready:** Preparado para Kubernetes migration
- **Developer Experience:** `docker-compose up` y funciona todo

**Multi-stage builds:**
```dockerfile
# Backend Dockerfile optimizado
FROM python:3.11-slim as base
FROM base as deps
FROM base as runtime
# Resultado: 150MB vs 800MB image
```

### AWS EC2 + NGINX
**Configuración:** t3.small (2 vCPU, 2GB RAM) + Ubuntu 22.04

**Justificación técnica:**
- **Cost Control:** $15/mes vs $50/mes serverless equivalente
- **Full Control:** Acceso root para debugging y optimización
- **Scaling Path:** Upgrade path hacia load balancer + multiple instances
- **SSL Termination:** NGINX handles SSL + reverse proxy

**NGINX config optimizada:**
```nginx
# Optimized for real-time apps
upstream backend {
    server backend:8000;
    keepalive 32;
}

server {
    # WebSocket upgrade headers
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    
    # Performance optimizations
    gzip on;
    gzip_types application/json text/css application/javascript;
}
```

### GitHub Actions CI/CD
**Justificación técnica:**
- **Native Integration:** GitHub repo + Actions seamless
- **Cost:** Free para public repos
- **Docker Support:** Excellent container build/push support
- **Matrix Testing:** Test multiple Python versions

**Pipeline stages:**
```yaml
1. Lint & Format: black, flake8, mypy
2. Test: pytest con coverage > 80%
3. Build: Docker images para backend/frontend  
4. Deploy: SSH a EC2, docker-compose pull + restart
5. Health Check: Verify deployment success
```

## 📊 Performance Targets & Monitoring

### SLA Objectives
```yaml
Availability: 99.5% uptime (3.65 hours downtime/month)
Latency:
  - API Response: p95 < 200ms
  - WebSocket Message: < 100ms
  - Transcript Processing: < 2s end-to-end
  
Throughput:
  - 10 concurrent meetings
  - 100 transcript chunks/second
  - 1000 WebSocket messages/second
```

### Monitoring Stack
```yaml
Logging:
  - Loguru structured logging
  - Log levels: DEBUG, INFO, WARNING, ERROR
  - Centralized logging a stdout (Docker captures)

Metrics:
  - Application metrics custom (Prometheus compatible)
  - System metrics: htop, df, free
  - Database metrics: connection pool, query time

Health Checks:
  - /health endpoint con service status
  - Docker container health checks
  - External monitoring: UptimeRobot
```

---

*Documento actualizado: 12 Agosto 2026*