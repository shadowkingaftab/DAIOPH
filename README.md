# Edge AI Intent Classifier & Orchestration Ecosystem
### Production-Grade Hybrid Inference & Prompt Bifurcation Suite

A comprehensive suite of intelligence-routing frameworks and task compilers designed to orchestrate complex prompt workflows across local **Edge AI (Qwen2-0.5B / Qwen-1.8B GGUF)** and **Cloud AI (xAI Grok API)**. Features multi-stage task decomposition, dynamic DAG parallel execution, real-time visual telemetry, and offline self-refining dual-role agent compilers.

---

## 🚀 Key Features

*   **Four Orchestration Architectures**: Explore the evolution from baseline zero-shot intent routing to a highly sophisticated offline-first self-refining task compiler.
*   **Dual-Role LLMCompiler & Self-Refine**: 100% offline planner-executor-refiner pipelines that decompose, execute, and self-correct complex workflows.
*   **Graphviz-Powered DAG Visualization**: View generated Task Bifurcation Directed Acyclic Graphs (DAGs) in real-time as tasks execute.
*   **Multi-Stage Task Decomposition**: Automated sentence tokenization, coreference resolution, and clustering to parallelize multi-step prompts.
*   **Seamless Cloud-to-Local Fallback**: Primary cloud pipelines degrade gracefully to local offline engines if APIs fail or credentials are missing.
*   **Production Telemetry Dashboard**: Track success rates, execution latencies, prompt logs, and routing distributions using Plotly and Pandas.
*   **Agent & Protocol Ready**: Built-in Model Context Protocol (MCP) server support for external agent discovery.

---

## 📁 Ecosystem Structure

The repository is structured into four progressive orchestration frameworks:

```
├── core/                     # Shared core logic (Grok clients, Task Executors, Prompts)
├── utils/                    # PDF parsers, thread loggers, and visualizers
├── models/                   # Local GGUF models and HuggingFace download target
│
├── streamlit_app.py          # Framework 1: Real-time Intent Classifier & Dashboard (Production)
├── unified_orchestrator/     # Framework 2: Hierarchical Parallel DAG Orchestrator
├── smart_orchestrator/       # Framework 3: Bartender-Decomposition & Telemetry Router
└── revolutionary_orchestrator/ # Framework 4: 100% Offline LLMCompiler + Self-Refining Pipeline
```

---

## 🛠 Quick Setup

### 1. Prerequisite Packages
Install the required Python dependencies:
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy the `.env.example` file to `.env` and fill in your keys:
```bash
GROK_API_KEY=your_xai_grok_api_key
CLASSIFIER_MODEL_PATH=models/fine_tuned_classifier  # Optional fine-tuned target
```

---

## 🚀 Running the Orchestrator Frameworks

Choose the orchestrator architecture you want to launch using Streamlit:

### 1. Framework 1: Intent Classifier & Dashboard (Baseline)
Deterministic zero-shot classifier routing single prompts between edge and cloud based on intent classification.
```bash
streamlit run streamlit_app.py
```

### 2. Framework 2: Unified Hybrid Orchestrator
Extracts tasks using NLTK sentence parsing, maps coreferences, parallelizes executions, and displays Graphviz DAGs.
```bash
streamlit run unified_orchestrator/app.py
```

### 3. Framework 3: Smart LLM Orchestrator
Decomposes complex flows using template-based Bartender logic and tracks live task metrics.
```bash
streamlit run smart_orchestrator/app.py
```

### 4. Framework 4: Revolutionary Prompt Bifurcation (LLMCompiler)
Runs entirely offline. Planning, Execution, and Self-Refining correction nodes run locally on CPU, sharing a single model context to optimize RAM usage.
```bash
streamlit run revolutionary_orchestrator/app.py
```

---

## 🐳 Docker Deployment

To build and run the entire suite in a unified container:
```bash
docker-compose up --build
```
Access the primary dashboard at `http://localhost:8501`.

---

## 🎯 Classifier Fine-Tuning Pipeline

To fine-tune the intent classifier model (`typeform/distilbert-base-uncased-mnli`) on custom enterprise data to achieve classification confidences above 95%:
1. Add custom intent training samples in `training/domain_dataset.json`.
2. Launch the trainer script:
   ```bash
   python training/train_classifier.py --epochs 5 --eval
   ```
3. Update `.env` to point `CLASSIFIER_MODEL_PATH` to the generated `models/fine_tuned_classifier` directory.

---

## ☁️ Streamlit Cloud Deployment Notes

The entire workspace is optimized for seamless zero-config deployment on **Streamlit Community Cloud**:
*   **Lazy Loading**: Local GGUF models and DistilBERT are dynamically downloaded on first load if missing.
*   **Fallback Protections**: If C++ compilers are restricted, the system catches import errors and routes traffic gracefully to Grok without disrupting server uptime.
*   **Thread Safety**: Local inference requests are sequentially locked (`threading.Lock`) to prevent memory corruption under high multi-tenant traffic.
