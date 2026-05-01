# 🛡️ Sentinel AI - Enterprise Compliance & Risk Engine

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangGraph](https://img.shields.io/badge/Architecture-LangGraph-orange)
![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-purple)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)

Sentinel AI is a fully autonomous, multi-agent AI pipeline designed to automate merchant onboarding and compliance audits for Fintech companies. It scrapes live merchant websites, retrieves corporate Acceptable Use Policies (AUP) via a local Vector Database, and utilizes LLMs to generate instant risk assessments and executive summaries.

## 🚀 System Architecture

Sentinel replaces static, rigid code with a dynamic **Zero-Shot Multi-Agent Workflow**:

1. **Scraper Agent:** Bypasses basic bot-protection to extract clean, live text from the target URL. Auto-handles invalid URLs and connection failures.
2. **Policy Retriever Agent (RAG):** Queries a local `ChromaDB` instance to dynamically fetch the specific corporate rules relevant to the scraped text.
3. **Compliance Agent:** Evaluates the website text against the retrieved policy, extracting structured JSON data (Business Category, Risk Flags, High-Risk Boolean) strictly adhering to the corporate rulebook.
4. **Risk Agent:** Applies deterministic logic to the AI's compliance score to render a final `Approve` or `Reject` decision.
5. **Synthesizer Agent:** Drafts a concise, human-readable executive summary for the final underwriter.

### 🛡️ Enterprise Resilience (Fault Tolerance)
API limits happen. To prevent pipeline crashes during high-traffic periods, Sentinel utilizes the `Tenacity` library to implement **Exponential Backoff and Retry** mechanisms across all LLM network calls, ensuring bulletproof execution.

---

## 🏢 How to Adapt Sentinel for Your Company

Sentinel is designed as a **Multi-Tenant System**. The AI engine is completely decoupled from the compliance rules. It does not possess hardcoded logic about what is "good" or "bad"—it only enforces the policy it is given.

To deploy Sentinel for your specific organization:

1. **Update the Rulebook:** Open `policy.txt` (or create a new text file) and paste your company's specific Acceptable Usage Policy (AUP), underwriting guidelines, or prohibited business categories.
2. **Rebuild the Brain:** Run the database ingestion script. This will chunk your company's policy, convert the text into mathematical vectors, and save them to the local `chroma_db` folder.
   ```bash
   python build_db.py
   ```
3. **Run the Auditor:** The AI will now instantly enforce your specific ruleset for all future audits. If you upload a Bank's loan policy, Sentinel becomes a bank underwriter. If you upload Stripe's AUP, it becomes a Stripe auditor.

---

## 🛠️ Installation & Quick Start

1. **Clone the Repository**

   ```bash
   git clone https://www.github.com/ayush11223366/Sentinel-ai
   
   ```
2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```
  

3. **Configure API Keys**
   Open sentinel.py and replace the placeholder API key with your active Google Gemini API Key.

   ```python
   os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY_HERE"
   ```
4. **Initialize the Vector Database**

   ```bash
   python build_db.py
   ```
5. **Launch the Dashboard**

   ```bash
   streamlit run app.py
   ```

---

## 🔮 Future Roadmap

- **Dynamic PDF Ingestion:** Upgrade the Streamlit UI to allow compliance officers to drag-and-drop 50-page legal PDFs directly into the dashboard to overwrite system rules in real-time.
- **Audit History:** Integrate SQLite/PostgreSQL to log all historical audits, flagged keywords, and decisions for internal reporting.
- **Model Fallback Routing:** Implement LangChain fallback chains to route requests to secondary LLMs (e.g., Llama 3 via Groq) if the primary provider experiences prolonged outages.

***

### The Final Step
Create a quick repository on GitHub, upload your files (`sentinel.py`, `app.py`, etc.), and share your AI-powered compliance engine with the world!
