# BioGuard 🦎

Plataforma **Full Stack** para la gestión de fauna silvestre urbana (Barranquilla, Colombia). Permite a los ciudadanos reportar avistamientos e incidentes, a las autoridades gestionarlos, y a cualquier usuario consultar información de biodiversidad mediante un asistente inteligente (RAG) o un bot de Telegram.

## Arquitectura

```
┌─────────────────────────┐   HTTP    ┌──────────────────────────┐
│  Frontend Angular 22    │ ────────► │  API Backend (FastAPI)   │
│  http://localhost:4200  │           │  http://localhost:8000   │
│  - Auth0 / Firebase     │           │  - CRUD usuarios,        │
│  - Leaflet (mapas)      │           │    especies, incidentes  │
│  - jsPDF (reportes)     │           │    y tickets de soporte  │
└─────────────────────────┘           │  - Auth bcrypt + PyJWT   │
          │                           └──────────────────────────┘
          │                                     │
          │                           ┌───────────▼──────────────┐
          │                           │  Base de datos           │
          │                           │  PostgreSQL / NeonDB     │
          │                           └──────────────────────────┘
          │
          │  HTTP    ┌──────────────────────────┐        ┌──────────────────┐
          └────────► │  Asistente RAG (FastAPI) │ ─────► │  ChromaDB        │
                     │  http://localhost:8001  │        │  (vector store)  │
                     │  - LangChain            │        └──────────────────┘
                     │  - Embeddings HF        │                 ▲
                     │  - LLM vía Groq         │                 │ ingesta
                     └──────────────────────────┘        docs/ (PDF/TXT)
          │
          │  ┌──────────────────────────┐
          └► │  Bot de Telegram         │
             │  - Reportes conversacionales
             │  - Preguntas al RAG      │
             └──────────────────────────┘
```

## Estructura del repositorio

```
BioGuard/
├── proyecto_final/      # Frontend Angular 22 (TypeScript, Vitest)
├── mi_api_neon/         # API REST (FastAPI + SQLAlchemy + NeonDB)
└── RAG/                 # Asistente RAG (LangChain + ChromaDB + Groq) y bot de Telegram
```

## Requisitos previos

| Herramienta     | Versión mínima          |
|-----------------|-------------------------|
| Node.js / npm   | 20 LTS / 9 (o npm 11) |
| Python          | 3.11+                   |
| PostgreSQL      | (se recomienda NeonDB)  |

Claves de API necesarias:
- **GROQ_API_KEY** — [console.groq.com](https://console.groq.com) (LLM)
- **HUGGINGFACEHUB_API_TOKEN** — [huggingface.co](https://huggingface.co) (embeddings)
- **TELEGRAM_TOKEN** — opcional, vía [@BotFather](https://t.me/BotFather)

---

## 1. Base de datos (NeonDB / PostgreSQL)

1. Crea un proyecto en [Neon](https://neon.tech) (o usa PostgreSQL local).
2. Crea las tablas definidas en `mi_api_neon/app/models.py`: `usuarios`, `especies`, `incidentes`, `tickets_soporte`.
3. Configura la cadena de conexión en `mi_api_neon/.env`:

```env
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/bd?sslmode=require
```

> NeonDB exige SSL (`sslmode=require`), ver `mi_api_neon/app/database.py`.

## 2. API Backend (puerto 8000)

```powershell
cd mi_api_neon
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Documentación interactiva (Swagger): <http://localhost:8000/docs>
- Endpoints base: `/api/v1/usuarios`, `/api/v1/especies`, `/api/v1/incidentes`, `/api/v1/tickets`

## 3. Asistente RAG (puerto 8001)

```powershell
cd RAG
python -m venv myvenv
myvenv\Scripts\activate          # Windows
# source myvenv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

Configura `RAG/.env`:

```env
GROQ_API_KEY=sk_...
HUGGINGFACEHUB_API_TOKEN=hf_...
# Opcionales (valores por defecto mostrados):
# EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
# LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
# CHROMA_DB_PATH=./chroma_db
# CHROMA_COLLECTION_NAME=rag_documents
# CHUNK_SIZE=500
# CHUNK_OVERLAP=50
# RETRIEVER_K=4
```

**Indexa los documentos** (obligatorio antes de usar `/ask`):

```powershell
python -m app.ingest
```

Levanta el servidor:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

> El frontend consume el RAG en el puerto **8001** (ver `proyecto_final/src/app/core/services/rag.service.ts`).

## 4. Bot de Telegram (opcional)

```powershell
cd RAG
# Asegúrate de tener TELEGRAM_TOKEN, RAG_API_URL e INCIDENTES_API_URL en .env
python -m app.telegram_bot
```

El bot guía al usuario (especie → ubicación → nivel → foto → descripción), responde preguntas de biodiversidad vía RAG y registra reportes en la API de incidentes.

## 5. Frontend Angular (puerto 4200)

```powershell
cd proyecto_final
npm install
npm start          # ng serve → http://localhost:4200
```

> La configuración de Firebase y la URL de la API están en `proyecto_final/src/environments/environment.ts`.

---

## Probar el proyecto

**Frontend (pruebas unitarias con Vitest):**

```powershell
cd proyecto_final
npm test           # ejecuta los *.spec.ts
npm run build      # build de producción en dist/
```

**API Backend:** abre <http://localhost:8000/docs> y prueba los endpoints desde Swagger.

**RAG:**

```powershell
# Estado del sistema
curl http://localhost:8001/status

# Hacer una pregunta
curl -X POST http://localhost:8001/ask -H "Content-Type: application/json" -d "{\"question\": \"¿Qué debo hacer si encuentro una iguana herida?\"}"
```

Respuesta esperada: `answer` + `sources` (fragmentos de los documentos consultados) + `processing_time_seconds`.

## Orden de arranque recomendado

1. Base de datos (NeonDB) con tablas creadas
2. API Backend → `:8000`
3. RAG: `python -m app.ingest` → `uvicorn ... :8001`
4. Frontend → `:4200`
5. (Opcional) Bot de Telegram

## Solución de problemas

| Problema                                  | Solución                                        |
|-------------------------------------------|-------------------------------------------------|
| Error SSL al conectar a NeonDB            | Verifica `sslmode=require` en `DATABASE_URL`    |
| `/ask` responde 503                       | Ejecuta `python -m app.ingest` primero          |
| Error de CORS                             | El API permite `localhost:4200`; RAG permite `*` |
| `pip install -r requirements.txt` falla   | Usa la versión corregida del archivo            |
| Puerto ocupado                            | Cambia el puerto con `--port` y ajusta las URLs en el frontend |

## Notas de seguridad

- No versiones archivos `.env` (contienen credenciales). Agrega `.env` al `.gitignore`.
- La clave JWT (`SECRET_KEY`) en `mi_api_neon/app/auth.py` está hardcodeada para desarrollo; en producción usa una variable de entorno.
