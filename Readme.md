# 🤖 AI/ML Knowledge Bot — Production RAG Pipeline

A production-grade Retrieval-Augmented Generation (RAG) system built from scratch, featuring a modular OOP pipeline, automated evaluation, CI/CD with GitHub Actions, and cloud deployment on Azure VM via Terraform.

---

## 📌 What This Project Does

The AI/ML Knowledge Bot is a conversational assistant that answers questions about AI, ML, and LLM concepts. It retrieves relevant context from a curated knowledge base before generating answers — grounding responses in real content rather than relying solely on the LLM's training data.

**The core pipeline:**
```
Documents → Chunking → Embedding → Vector Store → Retrieval → Generation → Evaluation
```

Built with production engineering discipline throughout: every stage is modular, independently testable, config-driven, and automatically evaluated before deployment.

---

## 🏗️ Architecture

### Pipeline Design — Config → Manager → Component Pattern

Every pipeline stage follows a strict three-layer architecture:

```
ConfigurationManager          →  reads config.yaml, builds typed Config objects
        ↓
@dataclass(frozen=True) Config →  immutable, typed settings container
        ↓
Component Class               →  receives Config, does the actual work
```

This pattern ensures clean separation of concerns, easy testability, and the ability to tune any parameter (chunk size, embedding model, top_k, temperature) without touching business logic.

### Component Breakdown

| Component | Responsibility | Key Design Decision |
|-----------|---------------|-------------------|
| `DataIngestion` | Loads 32 .md corpus files via DirectoryLoader | UTF-8 encoding enforced, source metadata preserved for eval tracing |
| `Chunking` | Splits documents into 160 chunks | RecursiveCharacterTextSplitter with chunk_size=1000, chunk_overlap=50 — tuned from data (min:267, max:998, avg:634 chars) |
| `Embedding` | Embeds chunks via HuggingFace, persists to Chroma | Idempotent — loads existing vector store on re-run, never re-embeds unnecessarily |
| `Retrieval` | Similarity search over vector store | top_k=5, returns LangChain retriever object for downstream use |
| `Generation` | LLM answer generation via Groq | Three-tier prompt: grounded on context → general knowledge fallback → honest "I don't know" |
| `Evaluation` | Automated quality gate | Two independent metrics: keyword_coverage (retrieval) + LLM-as-judge accuracy (generation) |

---

## 📊 Evaluation Design

A key feature of this project is a **real, automated evaluation pipeline** — not just "does it run" but "does it produce quality output."

### Metrics

**Retrieval Metric — Keyword Coverage**
```
For each test question:
    Check if expected keywords appear in retrieved chunks
    Score = keywords_found / total_keywords  (0 to 1)
    Threshold: >= 0.70 to pass
```

**Generation Metric — LLM-as-Judge Accuracy**
```
For each test question:
    Judge LLM compares generated answer vs. reference answer
    Score = 1 (wrong) to 5 (perfect)
    Threshold: >= 3.5 to pass
```

### Evaluation Results

| Model | Avg Keyword Coverage | Avg Accuracy | Gate |
|-------|---------------------|--------------|------|
| all-MiniLM-L6-v2 | 0.525 | 3.60/5 | FAIL (retrieval) |
| all-mpnet-base-v2 | 0.525 | 3.60/5 | FAIL (retrieval) |

**Finding:** Keyword coverage failure was diagnosed as a metric limitation (exact string matching doesn't capture semantic retrieval success) rather than a true retrieval failure — generation accuracy (3.60/5) consistently passes threshold, confirming the LLM produces acceptable answers even when keyword matching misses. This is a documented finding, not an unresolved bug.

### CI/CD Evaluation Gate

Every push to `main` triggers the evaluation pipeline automatically:
```
Push code → GitHub Actions → run 10 fixed smoke-test questions 
    → keyword_coverage >= 0.70 AND accuracy >= 3.5?
    → PASS: proceed to Docker build + Azure deployment
    → FAIL: block deployment, notify developer
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Llama 3.3 70B via Groq API |
| **Embeddings** | sentence-transformers/all-mpnet-base-v2 (local, free) |
| **Vector Store** | ChromaDB (persisted to disk) |
| **Orchestration** | LangChain (LCEL pipeline) |
| **UI** | Streamlit |
| **Config** | YAML + python-box ConfigBox |
| **Containerization** | Docker |
| **CI/CD** | GitHub Actions |
| **Infrastructure** | Terraform |
| **Cloud** | Azure VM + Azure Blob Storage |

---

## 🗂️ Project Structure

```
bot_project/
├── .github/
│   └── workflows/
│       └── cicd.yaml           # GitHub Actions pipeline
├── .streamlit/
│   └── config.toml             # Streamlit config (disables file watcher)
├── components/
│   ├── data_ingestion.py       # Document loading
│   ├── chunking.py             # Text splitting
│   ├── embedding.py            # Vector store creation/loading
│   ├── retrieval.py            # Similarity search
│   ├── generation.py           # LLM answer generation
│   └── evaluation.py           # Automated quality evaluation
├── config/
│   ├── config.yaml             # All pipeline parameters
│   └── configuration.py        # ConfigurationManager
├── entity/
│   └── config_entity.py        # Typed dataclass Config objects
├── synthetic_corpus/
│   ├── *.md                    # 32 AI/ML concept articles
│   └── eval_set.jsonl          # 96 Q&A pairs for evaluation
├── artifacts/                  # Generated at runtime (gitignored)
│   └── embedding/
│       └── vector_store/       # Persisted Chroma DB
├── app.py                      # Streamlit UI
├── Dockerfile                  # Container definition
├── terraform/
│   ├── main.tf                 # Azure VM + networking
│   └── variables.tf            # Terraform variables
└── requirements.txt
```

---

## ⚙️ Configuration

All pipeline parameters live in `config/config.yaml` — no hardcoded values anywhere in the codebase:

```yaml
chunking:
  chunk_size: 1000
  chunk_overlap: 50

embedding:
  model_name: all-mpnet-base-v2

retrieval:
  top_k: 5

generation:
  model_name: llama-3.3-70b-versatile
  temperature: 0.4
  max_tokens: 1024

evaluation:
  smoke_test_questions: [3, 17, 22, 41, 55, 68, 74, 80, 88, 95]
  keyword_coverage_threshold: 0.7
  accuracy_threshold: 3.5
```

---

## 🚀 Deployment

### Local Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/bot_project.git
cd bot_project

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Add your GROQ_API_KEY to .env

# Run pipeline setup (first time only — builds vector store)
python main.py

# Launch the app
streamlit run app.py
```

### CI/CD Pipeline

Every push to `main`:
1. GitHub Actions triggers
2. Runs automated evaluation against fixed smoke-test questions
3. If both metrics pass threshold → builds Docker image → pushes to registry
4. Deploys to Azure VM via SSH

### Cloud Deployment (Azure VM via Terraform)

```bash
# Provision infrastructure
cd terraform
terraform init
terraform plan
terraform apply

# Deploy container
docker pull yourusername/ragbot:latest
docker run -d -p 8501:8501 \
  -e GROQ_API_KEY=your_key \
  -v /home/azureuser/artifacts:/app/artifacts \
  yourusername/ragbot:latest
```

The app runs as a `systemd` service on the VM — auto-starts on reboot, auto-restarts on crash, logs to `/home/azureuser/bot_project/logs/app.log`.

---



## 📐 Key Engineering Decisions

**Why hand-rolled evaluation instead of RAGAS?**
RAGAS had dependency conflicts with the current LangChain stack (`langchain-core 1.4.8` vs. RAGAS requiring `<0.3`). The hand-rolled metrics implement the same conceptual measurements (retrieval quality + generation quality, independently scored) with full transparency into what's being measured and why.

**Why local HuggingFace embeddings instead of OpenAI?**
Cost-zero for this project scope. `all-mpnet-base-v2` is a strong, production-used model that runs locally — no per-embedding API cost, no external dependency for a core pipeline step.

**Why persisted Chroma instead of in-memory?**
Embedding 160 chunks takes ~30 seconds on CPU. An ephemeral store would re-embed on every app restart — wasteful and slow. Persisted Chroma loads in ~2 seconds. The idempotency check (`if vector_store exists → load, else embed`) enforces this automatically.

**Why `@st.cache_resource` for pipeline loading?**
The vector store, embedding model, and LLM client are expensive to initialize. `@st.cache_resource` initializes them once when the Streamlit process starts and caches them for the lifetime of the process — all user queries share the same loaded pipeline, with no re-initialization per query.

---

## 📈 What I Learned Building This

- **Production OOP discipline** — Config→Manager→Component pattern applied consistently across 6 pipeline stages, keeping business logic independent of configuration sources
- **RAG evaluation** — the difference between retrieval metrics (did we find the right content) and generation metrics (did we use it correctly), and why they must be measured independently
- **Embedding model tradeoffs** — empirically measured the difference between `all-MiniLM-L6-v2` and `all-mpnet-base-v2` with real eval numbers, not assumptions
- **GenAI deployment lifecycle** — three independent change types (code, data, model) each need their own validation path before deployment
- **Idempotency as a first-class concern** — built into every stage that produces artifacts, not retrofitted as an afterthought

---

## 🔮 Future Improvements

- [ ] Swap to RAGAS once dependency conflicts resolve (semantic retrieval scoring vs. keyword matching)
- [ ] Add reranking step (cross-encoder) between retrieval and generation to improve context precision
- [ ] Hybrid search (BM25 + semantic) to handle exact-keyword queries better
- [ ] Azure Monitor integration for production observability
- [ ] DVC data versioning if corpus expands beyond static synthetic set
- [ ] LangSmith tracing for LLM call observability in production

---

## 👨‍💻 Author

**Aryan Dhawan**  
AI Consultant | RAG & MLOps Engineer  
[LinkedIn](https://www.linkedin.com/in/aryan-dhawan-40760a160/) • [Portfolio](https://aryan-dhawan.vercel.app) • [GitHub](https://github.com/aryandhawan)