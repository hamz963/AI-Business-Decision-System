# AI-Powered Business Decision Support System (AI-BDSS)

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%200.141-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20TypeScript-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![DuckDB](https://img.shields.io/badge/Analytics-DuckDB%20Columnar-FFF000?logo=duckdb&logoColor=black)](https://duckdb.org/)
[![Vite](https://img.shields.io/badge/Bundler-Vite%205-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade Decision Intelligence and Financial Analytics Platform combining embedded columnar analytics, econometric forecasting, and what-if scenario simulations with **100% free-tier and local AI models** (OpenCode Zen `big-pickle`, `mimo-v2.5-free`, Google Gemini Free-Tier, and local offline Ollama).

---

## Key Highlights

- **Columnar Analytical Engine**: Embedded DuckDB processes multi-million row financial datasets with sub-second execution, zero server overhead, and concurrency protection.
- **Multi-Model AI Business Analyst**: Zero lock-in architecture allowing instant switching between OpenCode deep reasoning (`big-pickle`), high-speed general intelligence (`mimo-v2.5-free`), Google Gemini Free-Tier, and offline private Ollama (`qwen3`).
- **Strict Grounding & Evidence Chain**: Transparent separation of **Facts** (derived from dataset metrics), **Inferences**, **Predictions**, and **Assumptions**—eliminating hallucinations and fabricated demo numbers.
- **What-If Scenario Simulator**: Real-time sensitivity modeling for price changes, marketing budget reallocations, cost reductions, volume shocks, and break-even elasticity.
- **Automated Data Quality & Ingestion**: Auto-schema inference, column mapping (Revenue, COGS, Order ID, Date), anomaly detection (Z-Score + IQR), and null-value auditing.
- **Enterprise Security & Reliability**: Role-based access control (RBAC), JWT authentication, IP rate limiting via SlowAPI, upload file validation (100 MB cap), and origin-whitelisted CORS.

---

## System Architecture

```
                               ┌──────────────────────────────────────────────┐
                               │             React 18 + TypeScript            │
                               │      (Tailwind CSS, Lucide Icons, Vite)      │
                               └──────────────────────┬───────────────────────┘
                                                      │ HTTP / JWT Bearer
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │               FastAPI Backend                │
                               │         (SlowAPI Rate Limiter, CORS)         │
                               └──────┬────────────────┬───────────────┬──────┘
                                      │                │               │
                     ┌────────────────┴────┐           │               └─────────────┐
                     ▼                     ▼           ▼                             ▼
       ┌────────────────────────┐  ┌───────────────┐ ┌───────────────┐  ┌───────────────────────┐
       │   SQLite Metadata DB   │  │ Embedded OLAP │ │ Econometric   │  │   AI Model Gateway    │
       │ Users, Orgs, Datasets, │  │ DuckDB Engine │ │  Forecasting  │  │ • OpenCode big-pickle │
       │ Audit Logs, Scenarios  │  │ (Columnar)    │ │ (Holt-Winters)│  │ • OpenCode mimo-free  │
       └────────────────────────┘  └───────────────┘ └───────────────┘  │ • Google Gemini Free  │
                                                                        │ • Ollama (Local/Free) │
                                                                        └───────────────────────┘
```

---

## Supported Free-Tier & Local AI Models

| Model ID | Provider | Type | Primary Use Case |
|---|---|---|---|
| `big-pickle` | **OpenCode Zen** | Deep Reasoning | Complex financial trade-offs, variance analysis, multi-period strategy |
| `mimo-v2.5-free` | **OpenCode Zen** | High-Speed LLM | Real-time interactive queries, summaries, quick metrics extraction |
| `gemini-2.5-flash` | **Google Cloud** | Multimodal Free | Fast business synthesis, scenario summaries |
| `gemini-2.5-flash-lite` | **Google Cloud** | Lightweight Free | High-throughput data transformation and classification |
| `gemini-3.1-flash-lite` | **Google Cloud** | Next-Gen Free | Rapid responses with low latency |
| `qwen3:0.6b` | **Ollama** | 100% Local / Offline | Fully private, zero-token air-gapped deployments |
| `rule_based` | **Internal** | Deterministic Engine | Zero external dependencies; instant rule-based calculations |

---

## Directory Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST endpoints (auth, datasets, kpis, forecasting, ai)
│   │   ├── core/            # Database engine, JWT security, RBAC dependencies
│   │   ├── models/          # SQLAlchemy ORM models (User, Org, Dataset, Audit)
│   │   ├── schemas/         # Pydantic v2 schemas and validation contracts
│   │   ├── services/        # Analytics, forecasting, DuckDB engine, AI analyst
│   │   ├── config.py        # Environment configuration
│   │   └── main.py          # FastAPI application factory
│   ├── tests/               # Pytest automated test suite (17 comprehensive tests)
│   ├── seed_data.py         # Initial database seeding script
│   └── requirements.txt     # Python backend dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # Views: Dashboard, Datasets, AI Analyst, Scenarios
│   │   ├── services/        # Axios API client with dynamic base URL
│   │   └── types/           # TypeScript interfaces and contracts
│   ├── package.json         # Node.js dependencies
│   ├── vite.config.ts       # Vite configuration with API reverse proxy
│   └── vercel.json          # Frontend SPA routing configuration for Vercel
├── demo_data/               # Pre-generated sample enterprise sales datasets
├── vercel.json              # Monorepo Vercel deployment pipeline configuration
├── docker-compose.yml       # Containerized multi-service deployment
└── README.md
```

---

## Getting Started

### Prerequisites

- **Python**: 3.10 to 3.13
- **Node.js**: 18.x or higher
- **npm** or **yarn**

---

### Backend Setup

1. **Navigate to the backend directory and create a virtual environment:**
   ```bash
   cd backend
   python -m venv ../venv
   ..\venv\Scripts\activate      # On Windows
   # source ../venv/bin/activate # On Linux/macOS
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Copy `.env.example` to `.env` in the root directory:
   ```bash
   cp ../.env.example ../.env
   ```
   Provide your secrets and keys:
   ```env
   SECRET_KEY=your_secure_random_key
   ACTIVE_AI_MODEL=big-pickle
   OPENCODE_API_KEY=your_opencode_zen_key_if_available
   GOOGLE_API_KEY=your_google_free_api_key
   OLLAMA_BASE_URL=http://localhost:11434
   ```

4. **Run the Backend Server:**
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   Interactive Swagger documentation will be available at: `http://127.0.0.1:8000/docs`.

---

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the Development Server:**
   ```bash
   npm run dev
   ```
   Access the dashboard at: `http://localhost:5173`.

---

## Running Automated Tests

Run the test suite to verify data quality calculations, forecasting routines, scenario simulations, and AI model routing:

```bash
$env:PYTHONPATH = "backend"
pytest backend/tests/ -v
```

All 17 tests validate schema compliance, zero-division boundaries, and deterministic analytical guarantees.

---

## Deployment to Vercel

The frontend is ready for 1-click deployment on [Vercel](https://vercel.com):

1. Import the repository `hamz963/AI-Business-Decision-System` on Vercel.
2. In project settings:
   - **Root Directory**: `frontend` (or leave default using root `vercel.json`)
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. Under **Environment Variables**, set:
   - `VITE_API_BASE_URL`: `https://your-backend-api-url.com/api/v1`
4. Click **Deploy**.

---

## License

This project is open-source software licensed under the [MIT License](LICENSE).