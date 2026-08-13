# 3. Plan de Implementación (Continuación)

## Task 4: Agente LangGraph - Detección de Action Items y Decisiones

### 🎯 Objetivo
Un grafo LangGraph que consume la transcripción y detecta action items y decisiones de forma incremental.

### 📝 Implementación Detallada

#### 4.1 Diseño del Grafo LangGraph
```python
# agents/meeting_agent.py
class MeetingIntelligenceAgent:
    nodes = {
        "transcription_buffer": self.accumulate_context,
        "content_analyzer": self.analyze_content,
        "action_item_extractor": self.extract_action_items,
        "decision_extractor": self.extract_decisions,
        "confidence_filter": self.filter_results
    }
```

#### 4.2 Prompts de Detección
```python
ACTION_ITEM_PROMPT = """
Analiza esta transcripción de reunión y detecta action items.

SOLO extrae action items que cumplan TODOS estos criterios:
1. Tarea específica mencionada explícitamente
2. Persona asignada claramente identificada  
3. Deadline o timeframe mencionado

Formato de salida JSON:
{
  "action_items": [
    {
      "task": "descripción específica",
      "assignee": "nombre de la persona",
      "deadline": "deadline mencionado",
      "confidence": 0.85
    }
  ]
}
"""
```

#### 4.3 Estado del Agente
- **Context Window**: Últimos 10 chunks de transcripción
- **Memory**: Action items ya detectados (evitar duplicados)
- **Confidence Threshold**: 0.75 mínimo para persistir

### ✅ Criterios de Éxito Específicos
1. **Detecta action items reales** con precisión > 80%
2. **Falsos positivos < 15%** en transcripciones de test
3. **Se ejecuta en < 5 segundos** por chunk de transcripción
4. **Evita duplicados** efectivamente
5. **Persiste resultados** en PostgreSQL con metadata

---

## Task 5: Dashboard en Tiempo Real con Next.js + WebSockets

### 🎯 Objetivo
Interfaz web donde se ve la transcripción llegando en vivo y los action items/decisiones apareciendo en tiempo real.

### 📝 Implementación Detallada

#### 5.1 Estructura del Dashboard
```
dashboard/
├── src/
│   ├── components/
│   │   ├── MeetingDashboard/
│   │   ├── TranscriptPanel/
│   │   ├── InsightsPanel/
│   │   └── MeetingControls/
│   ├── hooks/
│   │   ├── useWebSocket.ts
│   │   └── useMeetingData.ts
│   ├── types/
│   └── utils/
```

#### 5.2 Layout del Dashboard
```
┌─────────────────┬─────────────────┐
│   Transcript    │    Insights     │
│    Panel        │     Panel       │
│                 │                 │
│ 👤 Luis: Vamos  │ 🎯 Action Items │
│ a necesitar...  │ • Luis: enviar  │
│                 │   informe (vie) │
│ 👤 María: Sí,   │                 │
│ yo me encargo   │ ⚖️ Decisions    │
│ de la base...   │ • Usar React    │
│                 │   para el UI    │
└─────────────────┴─────────────────┘
```

#### 5.3 WebSocket Integration
```typescript
// hooks/useWebSocket.ts
export const useWebSocket = (meetingId: string) => {
  const [transcript, setTranscript] = useState<TranscriptChunk[]>([]);
  const [insights, setInsights] = useState<Insights>({});
  
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${meetingId}`);
    // Handle real-time updates
  }, [meetingId]);
};
```

### ✅ Criterios de Éxito Específicos
1. **URL pública accesible** (http://meetmind.tudominio.com)
2. **Transcripción aparece en < 3 segundos** desde que se habla
3. **Insights aparecen en tiempo real** cuando se detectan
4. **Diseño responsive** y profesional
5. **Manejo de reconexión** si WebSocket se cae

---

## Task 6: Nodos de Riesgos y Preguntas + Resumen Ejecutivo

### 🎯 Objetivo
Ampliar el agente LangGraph con detección de riesgos y un nodo final que genera el resumen ejecutivo.

### 📝 Implementación Detallada

#### 6.1 Nuevos Nodos del Agente
```python
# Detección de riesgos
"risk_detector": self.detect_risks,
# Seguimiento de preguntas abiertas  
"question_tracker": self.track_open_questions,
# Generador de resumen (trigger: meeting_ended)
"summary_generator": self.generate_executive_summary
```

#### 6.2 Prompt para Riesgos
```python
RISK_DETECTION_PROMPT = """
Identifica riesgos, problemas o preocupaciones mencionados en la reunión.

Detecta:
- Obstáculos técnicos mencionados
- Problemas de timeline o recursos
- Dependencias externas riesgosas
- Preocupaciones de stakeholders

NO detectes:
- Riesgos hipotéticos o teóricos
- Preocupaciones ya resueltas en la conversación
"""
```

#### 6.3 Resumen Ejecutivo Estructurado
```markdown
# Resumen Ejecutivo - [Título de Reunión]

## 📊 Resumen
[Párrafo de 2-3 líneas con el core de la reunión]

## ⚖️ Decisiones Tomadas
- Decisión 1 (Responsable: Persona)
- Decisión 2 (Impacto: Alto)

## 🎯 Action Items  
- [ ] Tarea 1 - @Luis - Viernes
- [ ] Tarea 2 - @María - Próxima semana

## ⚠️ Riesgos Identificados
- Riesgo 1 (Severidad: Media)
- Riesgo 2 (Mitigación sugerida: X)

## ❓ Preguntas Abiertas
- Pregunta 1 - Requiere investigación
- Pregunta 2 - Pendiente de decisión

## 🔄 Próximos Pasos
[Resumen de next steps y follow-ups]
```

### ✅ Criterios de Éxito Específicos
1. **Detecta riesgos relevantes** sin falsos positivos excesivos
2. **Rastrea preguntas sin respuesta** efectivamente  
3. **Genera resumen coherente** al finalizar reunión
4. **Resumen es accionable** y bien estructurado
5. **Se ejecuta automáticamente** cuando Recall.ai envía meeting_ended

---

## Task 7: Integración con Jira y Notion

### 🎯 Objetivo
Al terminar la reunión, los action items se sincronizan automáticamente como tareas en Jira y/o el resumen se publica en Notion.

### 📝 Implementación Detallada

#### 7.1 Jira Integration
```python
# services/jira_service.py
class JiraService:
    async def create_issue(self, action_item: ActionItem) -> str
    async def update_issue(self, issue_key: str, updates: dict)
    async def get_projects(self) -> List[JiraProject]
```

#### 7.2 Notion Integration  
```python
# services/notion_service.py
class NotionService:
    async def create_page(self, summary: MeetingSummary) -> str
    async def update_page(self, page_id: str, content: str)
    async def get_databases(self) -> List[NotionDatabase]
```

#### 7.3 UI Configuration
```typescript
// Configuración en dashboard
interface IntegrationSettings {
  jira: {
    enabled: boolean;
    project_key: string;
    issue_type: string;
  };
  notion: {
    enabled: boolean;
    database_id: string;
  };
}
```

### ✅ Criterios de Éxito Específicos
1. **Action items crean issues en Jira** automáticamente
2. **Resumen se publica en Notion** como página
3. **Links bidireccionales** funcionan (Jira ↔ MeetMind)
4. **UI de configuración** permite conectar cuentas
5. **Manejo de errores** si APIs fallan o auth expira

---

## Task 8: Deploy en Producción + Pulido Final

### 🎯 Objetivo
El producto está deployado con URL pública, documentado, y listo para mostrar en LinkedIn.

### 📝 Implementación Detallada

#### 8.1 AWS EC2 Setup
- Ubuntu 22.04 LTS, t3.small (2 vCPU, 2GB RAM)
- Docker + Docker Compose instalado
- NGINX como reverse proxy
- Let's Encrypt SSL certificate
- Dominio: meetmind.luislopezleon.com

#### 8.2 GitHub Actions CI/CD
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to EC2
      - name: Run tests
      - name: Build containers
      - name: Deploy with zero downtime
```

#### 8.3 Observabilidad
- **Logs**: Loguru + centralized logging
- **Metrics**: Basic Prometheus metrics
- **Health checks**: Endpoint + container health
- **Alerts**: Email notifications para downtime

#### 8.4 Documentación Final
- README con GIF/video demo
- Arquitectura diagram actualizado
- API documentation completa
- Setup instructions para desarrollo

### ✅ Criterios de Éxito Específicos
1. **URL pública funciona 24/7** (99.5% uptime target)
2. **CI/CD deploys automáticamente** en cada push a main
3. **README impresionante** con demo visual
4. **Metrics y logs** funcionando
5. **Ready para LinkedIn post** y portfolio

---

## 📊 Timeline Estimado

| Task | Duración | Dependencias | Demostración |
|------|----------|--------------|--------------|
| Task 1 | 3-4 días | Ninguna | Health check + Docker up |
| Task 2 | 5-7 días | Task 1 | Bot entra a Google Meet |
| Task 3 | 4-5 días | Task 2 | Transcripción en tiempo real |
| Task 4 | 7-10 días | Task 3 | Agente detecta action items |
| Task 5 | 5-7 días | Task 4 | Dashboard funcional |
| Task 6 | 4-5 días | Task 5 | Resumen ejecutivo completo |
| Task 7 | 6-8 días | Task 6 | Sync con Jira/Notion |
| Task 8 | 3-4 días | Task 7 | URL pública + CI/CD |

**Total estimado:** 37-50 días calendario (1.5-2 meses a medio tiempo)

---

*Documento actualizado: 12 Agosto 2026*