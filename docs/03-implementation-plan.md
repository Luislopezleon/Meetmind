# 3. Plan de Implementación

## 📋 Overview del Plan

**Duración estimada:** 1-2 meses (a tiempo parcial)  
**Metodología:** Incremental - cada task es funcional y demostrable  
**Enfoque:** Desarrollo + Testing + Demo en cada iteración

## 🎯 Criterios de Éxito Generales

Cada task debe cumplir:
- ✅ **Funcionalidad completa** - Feature trabajando end-to-end
- ✅ **Tests automatizados** - Cobertura mínima 80%  
- ✅ **Demo funcionando** - Se puede mostrar el progreso
- ✅ **Documentación actualizada** - README y docs reflejan cambios
- ✅ **Docker funcionando** - `docker-compose up` levanta todo

---

## Task 1: Proyecto Base con FastAPI + PostgreSQL + Docker

### 🎯 Objetivo
Scaffolding completo del proyecto con estructura de microservicio, modelos de BD, y CI básico.

### 📝 Implementación Detallada

#### 1.1 Estructura del Proyecto
```
meetmind/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── agents/
│   │   └── utils/
│   ├── tests/
│   ├── alembic/
│   ├── Dockerfile
│   └── requirements.txt
├── dashboard/
├── docs/
├── scripts/
├── docker-compose.yml
├── .env.example
└── README.md
```

#### 1.2 Modelos SQLAlchemy
- **Meeting**: Info básica, estado, participantes
- **TranscriptChunk**: Texto + speaker + timing
- **ActionItem**: Tarea + asignado + deadline + estado
- **Decision**: Decisión + contexto + impacto
- **Risk**: Descripción + severidad + mitigación
- **OpenQuestion**: Pregunta + contexto + estado
- **MeetingSummary**: Resumen ejecutivo + metadata

#### 1.3 Configuración Docker
- PostgreSQL 15 con healthcheck
- Redis 7 para pub/sub y cache
- FastAPI con auto-reload en desarrollo
- Volúmenes para persistencia
- Red interna para servicios

### ✅ Criterios de Éxito Específicos
1. **`docker-compose up` funciona sin errores**
2. **Base de datos se inicializa con schema correcto**
3. **Health check endpoint responde en `/health`**
4. **Tests básicos pasan** (models, config, database connection)
5. **Documentación API disponible** en `/docs`

### 🧪 Tests Requeridos
```python
# test_models.py
def test_meeting_model_creation()
def test_transcript_chunk_relationship()
def test_action_item_model_validation()

# test_database.py  
def test_database_connection()
def test_table_creation()
def test_session_management()

# test_health.py
def test_health_endpoint_returns_200()
def test_health_endpoint_includes_services()
```

### 📊 Demo Task 1
Al completar Task 1, debes poder:
1. Ejecutar `docker-compose up -d`
2. Visitar `http://localhost:8000/docs` y ver la documentación de FastAPI
3. Hacer GET a `http://localhost:8000/health` y recibir status 200
4. Verificar que PostgreSQL acepta conexiones
5. Ejecutar `pytest backend/tests/` y ver tests pasando

---

## Task 2: Integración con Recall.ai

### 🎯 Objetivo  
Dado un link de Google Meet o Teams, el sistema envía un bot que se une a la reunión.

### 📝 Implementación Detallada

#### 2.1 Recall.ai SDK Integration
```python
# services/recall_service.py
class RecallService:
    async def create_bot(self, meeting_url: str, meeting_id: int)
    async def get_bot_status(self, bot_id: str)
    async def handle_webhook(self, payload: dict)
```

#### 2.2 API Endpoints
```python
# POST /api/v1/meetings
# - Recibe meeting_url, title, scheduled_at
# - Crea registro en DB
# - Envía bot via Recall.ai
# - Retorna meeting_id + bot_id

# POST /api/v1/webhooks/recall  
# - Recibe eventos de Recall.ai
# - Actualiza estado del meeting
# - Procesa transcript chunks
```

#### 2.3 Webhook Events Handling
- `bot.status_change`: Bot conectado/desconectado
- `meeting.transcript_ready`: Chunk de transcripción disponible
- `meeting.ended`: Reunión finalizada

### ✅ Criterios de Éxito Específicos
1. **Crear meeting** vía API funciona
2. **Bot aparece en Google Meet** de prueba
3. **Webhooks se reciben** y procesan correctamente
4. **Estado del meeting se actualiza** en tiempo real
5. **Manejo de errores robusto** (URL inválida, bot fails, etc.)

---

## Task 3: Pipeline de Transcripción con Deepgram

### 🎯 Objetivo
Cada chunk de audio de Recall.ai se transcribe con Deepgram y se almacena con speaker ID.

### 📝 Implementación Detallada

#### 3.1 Deepgram Streaming Integration  
```python
# services/transcription_service.py
class TranscriptionService:
    async def process_audio_chunk(self, audio_data: bytes)
    async def handle_transcript_response(self, response: dict)
    async def identify_speakers(self, transcript: dict)
```

#### 3.2 Real-time Pipeline
```
Audio Chunk (Recall) → Deepgram API → Parse Response → Store DB → Publish Redis
```

#### 3.3 Redis Pub/Sub Channels
- `transcript:{meeting_id}`: Nuevos chunks de transcripción
- `meeting:{meeting_id}:status`: Cambios de estado
- `insights:{meeting_id}`: Action items y decisiones detectadas

### ✅ Criterios de Éxito Específicos
1. **Audio se transcribe** en < 2 segundos
2. **Speaker diarization funciona** (identifica quién habla)
3. **Chunks se persisten** en PostgreSQL correctamente
4. **Redis pub/sub** distribuye transcript en tiempo real
5. **Manejo de errores** en API calls y audio corrupto

---

*Continúa en siguiente archivo...*