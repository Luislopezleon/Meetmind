# 12. Contexto de Decisiones del Proyecto

## 🤔 Por Qué Este Proyecto Específico

### El Problema Original
Luis estaba perdido sobre qué proyecto hacer para su portfolio, sin saber en qué especializarse ni qué dirección tomar. Necesitaba:

1. **Proyecto técnicamente impresionante** para recruiters y LinkedIn
2. **Aprender tecnologías modernas** (especialmente agentes de IA)
3. **Algo con potencial real** de monetización/producto
4. **Que conecte con su experiencia** (FastAPI, Docker, sistemas backend)

### El Proceso de Decisión

#### Criterios de Evaluación Usados:
```yaml
Impacto en Portfolio:
  - Técnicamente avanzado pero demostrable
  - Problema reconocible por cualquier recruiter
  - Stack moderno y demandado en el mercado
  - URL pública deployada para mostrar

Aprendizaje:
  - Profundizar en LangGraph/agentes (de cero a experto)
  - Mantener stack conocido (FastAPI) como base
  - Integrar múltiples APIs complejas
  - Arquitectura de sistemas en tiempo real

Viabilidad:
  - Completable en 1-2 meses a tiempo parcial
  - Free tiers suficientes para desarrollo
  - No requiere equipos o recursos externos
  - Deploy barato (<$15/mes)
```

#### Alternativas Consideradas:
1. **Email Agent** - Problema real pero mercado saturado
2. **Second Brain Agent** - Técnicamente interesante pero menos diferencial
3. **Code Review Agent** - Muy técnico pero nicho específico
4. **Job Application Autopilot** - Mercado existente (Teal, Kickresume)
5. **Meeting Intelligence Agent** - ✅ **ELEGIDO**

### Por Qué Meeting Intelligence Ganó

1. **Problema Universal**: Cualquier empresa/recruiter reconoce el problema inmediatamente
2. **Complejidad Técnica Visible**: Agentes + tiempo real + múltiples integraciones
3. **Menos Saturado**: Fireflies.ai existe pero como SaaS cerrado, no open source
4. **Stack Perfecto**: Combina lo conocido (FastAPI) con lo nuevo (LangGraph)
5. **Demostrable**: Se puede hacer demo live en entrevistas

---

## ⚖️ Decisiones de Stack Tecnológico

### Backend: FastAPI vs Django vs Flask

| Factor | FastAPI | Django | Flask | Decisión |
|--------|---------|---------|--------|----------|
| **Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | FastAPI |
| **Type Safety** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | FastAPI |  
| **API Docs** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ | FastAPI |
| **Real-time** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | FastAPI |
| **Experiencia Luis** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | FastAPI |

**Decisión:** FastAPI - Balance perfecto de performance, developer experience, y funcionalidades modernas.

### Database: PostgreSQL vs MongoDB vs SQLite

| Factor | PostgreSQL | MongoDB | SQLite | Decisión |
|--------|------------|---------|--------|----------|
| **Relational Data** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | PostgreSQL |
| **JSON Support** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | PostgreSQL |
| **Scalability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | PostgreSQL |
| **ACID Compliance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | PostgreSQL |
| **Ecosystem** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | PostgreSQL |

**Decisión:** PostgreSQL - Datos relacionados (meetings ↔ transcripts ↔ action_items) con soporte JSON para flexibilidad.

### AI Framework: LangGraph vs LangChain vs Custom

| Factor | LangGraph | LangChain | Custom | Decisión |
|--------|-----------|-----------|---------|----------|
| **State Management** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | LangGraph |
| **Multi-Agent** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | LangGraph |
| **Learning Value** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | LangGraph |
| **Community** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | LangGraph |
| **Portfolio Impact** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | LangGraph |

**Decisión:** LangGraph - Framework especializado para agentes con estado, mejor para el caso de uso específico.

### Frontend: Next.js vs React vs Vue

| Factor | Next.js | React | Vue | Decisión |
|--------|---------|--------|-----|----------|
| **SSR/SEO** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | Next.js |
| **Real-time** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Next.js |
| **Ecosystem** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Next.js |
| **Learning Curve** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Next.js |
| **Job Market** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Next.js |

**Decisión:** Next.js - Framework full-stack, mejor para landing pages profesionales y SEO.

---

## 🔌 Decisiones de APIs e Integraciones

### Meeting Bot: Recall.ai vs Custom WebRTC

**Evaluación:**
```yaml
Custom WebRTC:
  Pros: 
    - Control total del audio/video
    - No dependencia externa
    - Customización completa
  Contras:
    - 2-3 meses de desarrollo solo para esto
    - Complejidad extrema (protocols, cross-browser, auth)  
    - Mantenimiento constante por cambios de plataformas
    - No es el core value del proyecto

Recall.ai:
  Pros:
    - API unificada para Meet/Teams/Zoom
    - 100 minutos gratis/mes para desarrollo
    - Mantienen compatibilidad con cambios de plataformas
    - Nos enfocamos en el agente de IA (core value)
  Contras:
    - Dependencia externa
    - Costo en producción
    - Menos control sobre el audio quality
```

**Decisión:** Recall.ai - El tiempo ahorrado se invierte en el agente inteligente (diferenciador real).

### STT: Deepgram vs AssemblyAI vs Whisper

**Evaluación:**
```yaml
Whisper (OpenAI):
  Pros: Gratis, muy preciso, control total
  Contras: No streaming, no speaker diarization, latencia alta
  
AssemblyAI:
  Pros: Excelente accuracy, buenas features
  Contras: Más caro, latencia ligeramente mayor
  
Deepgram:  
  Pros: Latencia más baja, precio competitivo, streaming nativo
  Contras: Accuracy ligeramente menor que AssemblyAI
```

**Decisión:** Deepgram - Para tiempo real, la latencia es más crítica que accuracy perfecta.

---

## 🏗️ Decisiones de Arquitectura

### Monolith vs Microservices

**Evaluación:**
```yaml
Monolith (FastAPI único):
  Pros: 
    - Simplicidad de desarrollo y deploy
    - Menos overhead de comunicación
    - Debugging más fácil
    - Perfecto para team de 1 persona
  Contras:
    - Menos impressive para arquitectura
    - Escalabilidad limitada
    
Microservices:
  Pros:
    - Más impressive en portfolio
    - Escalabilidad independiente
    - Tecnologías mixtas posibles
  Contras:
    - Complejidad de networking
    - Overhead de development
    - Overkill para el scope actual
```

**Decisión:** Monolith modular - Arquitectura de microservicio dentro de una app FastAPI. Escalable pero simple.

### Real-time: WebSockets vs Server-Sent Events vs Polling

**Evaluación:**
```yaml
Polling:
  Pros: Simple, compatible universalmente
  Contras: Ineficiente, latencia alta, load innecesario
  
Server-Sent Events:
  Pros: Unidireccional eficiente, reconnect automático
  Contras: Solo server→client, limitaciones de browsers
  
WebSockets:
  Pros: Bidireccional, latencia mínima, full-duplex
  Contras: Más complejo, manejo de reconnection manual
```

**Decisión:** WebSockets - Necesario para true real-time experience del dashboard.

### State Management: Redis vs In-Memory vs Database

**Evaluación:**
```yaml
In-Memory (dict/cache):
  Pros: Latencia cero, simplicidad
  Contras: Se pierde al restart, no escala
  
Database (PostgreSQL):
  Pros: Persistencia garantizada, ACID
  Contras: Latencia para queries frecuentes
  
Redis:
  Pros: Persistencia + performance, pub/sub nativo
  Contras: Infraestructura adicional
```

**Decisión:** Híbrido - Redis para real-time + cache, PostgreSQL para persistencia.

---

## 📚 Lecciones Aprendidas (Actualizándose)

### Del Proceso de Planificación

1. **Documentación exhaustiva upfront ahorra tiempo después**
   - Tener todo el contexto documentado permite continuar sin perderse
   - Decisiones justificadas evitan "analysis paralysis" después

2. **Elegir problemas universales amplifica el impacto del portfolio**  
   - "Meeting intelligence" vs "CLI for developers" - el primero resuena con más gente

3. **Balance entre tecnologías conocidas vs nuevas**
   - FastAPI (conocido) + LangGraph (nuevo) = learning sin overwhelming

### De Decisiones Técnicas

1. **Free tiers permiten validar ideas sin costo**
   - Recall.ai, Deepgram, OpenAI - todo gratis para desarrollo
   
2. **Stack coherente > stack "cool"**  
   - Python end-to-end mejor que Python + Node + Go mixed

3. **Optimizar para demo-ability**
   - Dashboard visual > CLI tool para impresionar en entrevistas

### Próximas Lecciones (se actualizará con implementación)

- [ ] Performance real vs estimado de LangGraph
- [ ] Calidad de transcripción Deepgram en práctica  
- [ ] Precisión del agente en detección de insights
- [ ] UX real del dashboard en tiempo real
- [ ] Costo real vs estimado en producción

---

## 🔄 Evolución de Decisiones

### Cambios Durante la Planificación

1. **Scope creep controlado**: Inicialmente era "simple meeting bot", evolucionó a "meeting intelligence platform"
2. **Stack refinement**: Consideramos Django inicialmente, FastAPI ganó por performance + type safety
3. **Frontend approach**: Casi elegimos Vue por simplicidad, Next.js ganó por SEO + job market

### Decisiones Pendientes (para implementación)

- [ ] **Prompt engineering strategy**: Few-shot vs zero-shot para detección de insights
- [ ] **Caching strategy**: Qué cachear en Redis vs qué persiste en PostgreSQL  
- [ ] **Error handling**: Retry policies para APIs externas
- [ ] **Testing approach**: Unit vs integration vs e2e ratios
- [ ] **Monitoring strategy**: Qué métricas son críticas vs nice-to-have

---

*Este documento se actualizará conforme avance la implementación y aprendamos de decisiones reales vs teóricas.*

*Documento creado: 12 Agosto 2026*