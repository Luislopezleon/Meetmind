# 2. Arquitectura Técnica

## 🏗️ Diagrama de Arquitectura General

```mermaid
graph TB
    %% User Interface Layer
    U[👨‍💼 Usuario] --> D[📱 Dashboard Next.js]
    
    %% API Gateway Layer  
    D --> F[🚀 FastAPI Backend]
    
    %% Meeting Bot Layer
    F --> R[🤖 Recall.ai Bot]
    R --> M[🎬 Google Meet/Teams]
    
    %% Audio Processing Pipeline
    M --> A[🎵 Audio Stream]
    A --> DG[🎤 Deepgram STT]
    DG --> T[📝 Transcripción + Speaker ID]
    
    %% Real-time Distribution
    T --> RD[🔄 Redis Pub/Sub]
    RD --> W[🌐 WebSocket]
    W --> D
    
    %% AI Agent Processing
    RD --> L[🧠 LangGraph Agent]
    L --> AI1[🎯 Action Items Detector]
    L --> AI2[⚖️ Decision Detector] 
    L --> AI3[⚠️ Risk Detector]
    L --> AI4[❓ Questions Detector]
    
    %% Data Persistence
    AI1 --> P[🗄️ PostgreSQL]
    AI2 --> P
    AI3 --> P
    AI4 --> P
    T --> P
    
    %% External Integration
    P --> J[🔗 Jira API]
    P --> N[📄 Notion API]
    
    %% Summary Generation
    P --> S[📊 Summary Generator]
    S --> P
    
    %% Styling
    classDef userLayer fill:#e1f5fe
    classDef apiLayer fill:#f3e5f5
    classDef aiLayer fill:#fff3e0
    classDef dataLayer fill:#e8f5e8
    classDef extLayer fill:#fce4ec
    
    class U,D userLayer
    class F,W apiLayer
    class R,DG,L,AI1,AI2,AI3,AI4,S aiLayer
    class P,RD dataLayer
    class J,N extLayer
```

## 🛠️ Stack Tecnológico Detallado

### Backend Core
```yaml
Framework: FastAPI 0.104.1
Language: Python 3.11
ASGI Server: Uvicorn + Gunicorn (producción)
```

**Justificación:**
- **FastAPI**: Mejor performance que Flask/Django para APIs, documentación automática, type hints nativos
- **Python 3.11**: Soporte nativo para async/await, mejor performance que 3.10
- **Uvicorn**: ASGI server con mejor handling de WebSockets que WSGI

### Base de Datos
```yaml
Primary DB: PostgreSQL 15
ORM: SQLAlchemy 2.0 + Alembic
Cache/Pub-Sub: Redis 7
Connection Pool: Configurado para 20 conexiones concurrentes
```

**Justificación:**
- **PostgreSQL**: ACID compliance, mejor para datos relacionados (meetings ↔ transcripts ↔ action_items)
- **SQLAlchemy 2.0**: Query syntax moderna, mejor type safety
- **Redis**: Pub/Sub para tiempo real + cache para sessiones/temporales

### AI & Processing
```yaml
Agent Framework: LangGraph 0.0.38
LLM: OpenAI GPT-4o-mini (detección) + GPT-4o (resúmenes)
STT: Deepgram Nova-3 Streaming
Meeting Bot: Recall.ai SDK
```

**Justificación:**
- **LangGraph**: Mejor que LangChain vanilla para agentes con estado complejo
- **GPT-4o-mini**: 10x más barato, suficiente para extracción estructurada
- **Deepgram**: Latencia más baja que AssemblyAI, mejor diarización
- **Recall.ai**: Evita complejidad de WebRTC custom, API unificada para todas las plataformas

### Frontend & Real-time
```yaml
Framework: Next.js 15 + TypeScript
Styling: Tailwind CSS 3.4
Real-time: WebSockets + Server-Sent Events
State Management: React Query + Zustand
```

**Justificación:**
- **Next.js 15**: SSR + CSR híbrido, mejor SEO, App Router estable
- **TypeScript**: Type safety end-to-end con backend
- **Tailwind**: Rapid prototyping, consistent design system
- **WebSockets**: Bidireccional para comandos + real-time updates

### DevOps & Deploy
```yaml
Containerización: Docker + Docker Compose
CI/CD: GitHub Actions
Deploy: AWS EC2 + NGINX
SSL: Let's Encrypt (Certbot)
Monitoring: Loguru + Prometheus (opcional)
```

**Justificación:**
- **Docker**: Consistent environments dev/prod
- **GitHub Actions**: Free para repos públicos, integración nativa
- **AWS EC2**: Balance costo/control, evita vendor lock-in de serverless
- **NGINX**: Reverse proxy + load balancing + SSL termination

## 🔄 Flujo de Datos Completo

### 1. Creación de Reunión
```mermaid
sequenceDiagram
    participant U as Usuario
    participant D as Dashboard  
    participant F as FastAPI
    participant R as Recall.ai
    participant DB as PostgreSQL

    U->>D: Crea reunión (título, URL, fecha)
    D->>F: POST /api/v1/meetings
    F->>DB: Guarda meeting record
    F->>R: Crea bot con meeting URL
    R-->>F: Bot ID + Status
    F->>DB: Actualiza meeting con bot_id
    F-->>D: Meeting creado + bot_id
    D-->>U: Confirmación + link de dashboard
```

### 2. Bot Entra a Reunión
```mermaid
sequenceDiagram
    participant R as Recall.ai Bot
    participant M as Google Meet
    participant W as Webhook
    participant F as FastAPI
    participant Redis as Redis
    participant D as Dashboard

    R->>M: Bot entra a reunión
    M-->>R: Audio stream begins
    R->>W: Webhook: bot_joined
    W->>F: POST /webhooks/recall
    F->>Redis: PUBLISH meeting:123:status "bot_joined"
    Redis->>D: WebSocket message
    D-->>U: "Bot conectado ✅"
```

### 3. Transcripción en Tiempo Real
```mermaid
sequenceDiagram
    participant R as Recall.ai
    participant D as Deepgram
    participant F as FastAPI
    participant Redis as Redis
    participant DB as PostgreSQL
    participant WS as WebSocket
    participant Agent as LangGraph

    loop Cada chunk de audio
        R->>D: Audio chunk
        D-->>F: Transcript + Speaker ID
        F->>DB: Guarda TranscriptChunk
        F->>Redis: PUBLISH transcript:123 {text, speaker, timestamp}
        Redis->>WS: Broadcast a dashboard
        Redis->>Agent: Trigger análisis
        Agent->>DB: Guarda insights detectados
        Agent->>Redis: PUBLISH insights:123 {action_items, decisions}
        Redis->>WS: Broadcast insights al dashboard
    end
```

### 4. Finalización y Resumen
```mermaid
sequenceDiagram
    participant R as Recall.ai
    participant F as FastAPI
    participant Agent as LangGraph
    participant DB as PostgreSQL
    participant J as Jira API
    participant N as Notion API

    R->>F: Webhook: meeting_ended
    F->>Agent: Trigger summary_generator
    Agent->>DB: Consulta todos los insights
    Agent->>Agent: Genera resumen ejecutivo
    Agent->>DB: Guarda MeetingSummary
    
    par Sync con Jira
        F->>J: Crea issues para action_items
        J-->>F: Issue IDs
        F->>DB: Actualiza action_items con jira_ids
    and Sync con Notion  
        F->>N: Crea página con resumen
        N-->>F: Page ID
        F->>DB: Actualiza summary con notion_id
    end
    
    F->>Redis: PUBLISH meeting:123:summary {summary, jira_links, notion_link}
```

## 🧠 Arquitectura del Agente LangGraph

### Grafo de Estados
```python
# Nodos del grafo
nodes = {
    "transcription_buffer": accumulate_transcripts,
    "content_analyzer": analyze_content,  
    "action_item_extractor": detect_action_items,
    "decision_extractor": detect_decisions,
    "risk_detector": detect_risks,
    "question_tracker": track_open_questions,
    "confidence_filter": filter_low_confidence,
    "summary_generator": generate_summary
}

# Estado compartido entre nodos
state = {
    "meeting_id": int,
    "transcript_chunks": List[str],
    "raw_insights": Dict,
    "filtered_insights": Dict,
    "confidence_threshold": float,
    "context_window": int
}
```

### Flujo de Decisiones
```mermaid
graph TD
    T[📝 Nuevo Transcript Chunk] --> B[📚 Buffer de Contexto]
    B --> A{Suficiente contexto?}
    A -->|No| B
    A -->|Sí| C[🔍 Content Analyzer]
    
    C --> AI[🎯 Action Item Detector]
    C --> D[⚖️ Decision Detector]  
    C --> R[⚠️ Risk Detector]
    C --> Q[❓ Question Detector]
    
    AI --> CF[🎚️ Confidence Filter]
    D --> CF
    R --> CF
    Q --> CF
    
    CF --> DB[(💾 PostgreSQL)]
    CF --> WS[🌐 WebSocket Broadcast]
    
    E[🏁 Meeting Ends] --> S[📊 Summary Generator]
    S --> EXT[🔗 External Sync]
```

## 📊 Escalabilidad y Performance

### Métricas Target
- **Latencia de transcripción**: < 2 segundos from speech to dashboard
- **Detección de insights**: < 5 segundos from transcript to classified insight  
- **Concurrencia**: 10 reuniones simultáneas en single instance
- **Throughput**: 100 transcript chunks/segundo
- **Availability**: 99.5% uptime

### Estrategias de Optimización
1. **Connection Pooling**: PostgreSQL pool optimizado para read/write ratio
2. **Redis Pub/Sub**: Evita polling, reduce latencia de real-time updates
3. **Async Processing**: Todo el pipeline es asíncrono desde audio hasta insights
4. **Batch Inference**: LangGraph procesa múltiples chunks en single call
5. **Caching Strategy**: Insights temporales en Redis, persistencia en PostgreSQL

### Puntos de Monitoreo
```yaml
Application Metrics:
  - transcript_processing_latency_seconds
  - insight_detection_accuracy_ratio
  - websocket_connection_count
  - meeting_concurrent_active_count

Infrastructure Metrics:  
  - postgresql_connection_pool_usage
  - redis_memory_usage_bytes
  - cpu_usage_percent
  - memory_usage_percent
```

## 🔒 Consideraciones de Seguridad

### API Security
- **Rate Limiting**: 100 requests/minute per IP
- **CORS**: Configurado solo para dominios autorizados
- **Input Validation**: Pydantic schemas en todas las endpoints
- **SQL Injection**: SQLAlchemy ORM + parameterized queries

### Data Security  
- **Encryption in Transit**: HTTPS/WSS en todas las comunicaciones
- **API Keys**: Almacenadas como variables de entorno, nunca en código
- **Webhook Validation**: HMAC signature validation para Recall.ai webhooks
- **Data Retention**: Auto-delete transcripts > 30 días (GDPR compliance)

### Infrastructure Security
- **Container Security**: Non-root users, minimal base images
- **Network Security**: Internal Docker network, expose solo puertos necesarios
- **SSL/TLS**: Let's Encrypt certificates con auto-renewal
- **Backup Strategy**: Daily PostgreSQL backups a S3

---

*Documento actualizado: 12 Agosto 2026*