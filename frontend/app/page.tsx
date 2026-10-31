"use client";

import { useEffect, useState } from "react";
import type { FormEvent } from "react";

type ServiceState = "checking" | "online" | "offline";
type Citation = {
  n: number;
  source: string;
  page: number;
  score: number;
  text: string;
};
type AssistantAnswer = {
  question: string;
  answer: string;
  citations: Citation[];
  trace: string[];
  latency_ms: number;
  engine: string;
};
type RAGStatus = {
  embedding_model: string;
  answer_model: string;
  retrieval: string;
  upload_persistence: string;
  indexed_documents: number;
  indexed_chunks: number;
};
type RetrievalDebug = {
  question: string;
  embedding_model: string;
  answer_model: string;
  results: Array<{rank:number;source:string;page:number;score:number;text:string}>;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function Home() {
  const [apiState, setApiState] = useState<ServiceState>("checking");
  const [databaseState, setDatabaseState] = useState("Checking");
  const [ragState, setRagState] = useState<ServiceState>("checking");
  const [ragDetails, setRagDetails] = useState<RAGStatus | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<AssistantAnswer | null>(null);
  const [retrievalDebug, setRetrievalDebug] = useState<RetrievalDebug | null>(null);
  const [askLoading, setAskLoading] = useState(false);
  const [askError, setAskError] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");

  async function checkBackend() {
    setApiState("checking");
    setDatabaseState("Checking");
    try {
      const response = await fetch(`${API_BASE}/ready`, { cache: "no-store" });
      if (!response.ok) throw new Error("Backend is not ready");
      const body = await response.json();
      setApiState("online");
      setDatabaseState(body.database ?? "Connected");
    } catch {
      setApiState("offline");
      setDatabaseState("Unavailable");
    }

    try {
      const response = await fetch(`${API_BASE}/api/v1/assistant/status`, { cache: "no-store" });
      if (!response.ok) throw new Error("RAG service unavailable");
      const status = await response.json() as RAGStatus;
      setRagDetails(status);
      setRagState("online");
    } catch {
      setRagDetails(null);
      setRagState("offline");
    }
  }

  async function submitQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!question.trim()) return;
    setAskLoading(true);
    setAskError("");
    setAnswer(null);
    setRetrievalDebug(null);
    try {
      const response = await fetch(`${API_BASE}/api/v1/assistant/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question.trim() })
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail ?? "The assistant could not answer.");
      setAnswer(body as AssistantAnswer);
      try {
        const debugResponse = await fetch(`${API_BASE}/api/v1/assistant/retrieve`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: question.trim(), limit: 6 })
        });
        if (debugResponse.ok) setRetrievalDebug(await debugResponse.json() as RetrievalDebug);
      } catch {
        // Answer is still useful if the optional diagnostics request fails.
      }
    } catch (error) {
      setAskError(error instanceof Error ? error.message : "Unexpected request error.");
    } finally {
      setAskLoading(false);
    }
  }

  async function uploadDocument(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFile) return;
    setUploadLoading(true);
    setUploadMessage("");
    const form = new FormData();
    form.append("file", selectedFile);
    try {
      const response = await fetch(`${API_BASE}/api/v1/assistant/documents`, {
        method: "POST",
        body: form
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail ?? "Upload failed.");
      setUploadMessage(`Indexed ${body.filename}: ${body.chunks} chunk(s) across ${body.pages} page(s).`);
      setSelectedFile(null);
      const input = document.getElementById("document-upload") as HTMLInputElement | null;
      if (input) input.value = "";
      await checkBackend();
    } catch (error) {
      setUploadMessage(error instanceof Error ? error.message : "Unexpected upload error.");
    } finally {
      setUploadLoading(false);
    }
  }

  useEffect(() => {
    void checkBackend();
  }, []);

  return (
    <main className="shell">
      <aside className="sidebar">
        <a className="brand" href="/" aria-label="Nexus AI home">
          <span className="brand-mark">N</span>
          <span>Nexus<span className="brand-light">AI</span></span>
        </a>
        <div className="workspace-label">WORKSPACE</div>
        <a className="nav-item active" href="#overview"><span>⌂</span> Overview</a>
        <a className="nav-item" href="#knowledge"><span>▤</span> Knowledge base</a>
        <a className="nav-item" href="#assistant"><span>✳</span> AI assistant</a>
        <a className="nav-item" href="#integrations"><span>⌘</span> Governance</a>
        <div className="sidebar-bottom">
          <span className="avatar">CV</span>
          <span><strong>Developer workspace</strong><small>Local environment</small></span>
        </div>
      </aside>

      <section className="main-panel" id="overview">
        <header className="topbar">
          <span className="crumb">Workspace <span>/</span> Overview</span>
          <span className="env-pill">DEVELOPMENT BUILD</span>
        </header>

        <div className="content">
          <div className="eyebrow">ENTERPRISE AI INTELLIGENCE & GOVERNANCE</div>
          <h1>Knowledge into<br /><em>action, safely.</em></h1>
          <p className="intro">Nexus combines the existing Agentic RAG knowledge engine with an enterprise workspace and a controlled integration layer. Answers include source citations; sensitive actions will require explicit authorization and approval.</p>

          <div className="status-row">
            <div className="status-card">
              <span className="status-dot" data-state={apiState} />
              <span><small>NEXUS API</small><strong>{apiState === "online" ? "Connected" : apiState === "offline" ? "Offline" : "Checking…"}</strong></span>
            </div>
            <div className="status-card">
              <span className="status-dot" data-state={databaseState === "connected" ? "online" : apiState === "offline" ? "offline" : "checking"} />
              <span><small>DATABASE</small><strong>{databaseState}</strong></span>
            </div>
            <div className="status-card">
              <span className="status-dot" data-state={ragState} />
              <span><small>RAG ENGINE</small><strong>{ragState === "online" ? "Connected" : ragState === "offline" ? "Unavailable" : "Checking…"}</strong></span>
            </div>
            <button className="refresh-button" onClick={() => void checkBackend()}>↻ Check services</button>
          </div>
          {ragDetails && (
            <div className={`engine-info ${ragDetails.embedding_model.startsWith("hash") ? "engine-info-warning" : ""}`}>
              <strong>Retrieval configuration</strong>
              <span>Embeddings: {ragDetails.embedding_model}</span>
              <span>Answer engine: local {ragDetails.answer_model}</span>
              <span>Uploads: {ragDetails.upload_persistence}</span>
              <span>Indexed: {ragDetails.indexed_documents} documents · {ragDetails.indexed_chunks} chunks</span>
              {ragDetails.embedding_model.startsWith("hash") && (
                <p>Hash embeddings are intended for smoke tests. Use MiniLM embeddings for semantic search.</p>
              )}
              {ragDetails.answer_model === "extractive" && (
                <p>Answers are built locally from relevant document sentences with source citations. No hosted language model or external inference API is called.</p>
              )}
            </div>
          )}

          <div className="section-heading" id="assistant">
            <div><span className="section-kicker">KNOWLEDGE ENGINE</span><h2>Ask your documents</h2></div>
            <span className="coming-badge">RAG INTEGRATION</span>
          </div>

          <div className="assistant-card">
            <div className="assistant-icon">✳</div>
            <div className="assistant-copy">
              <h3>Grounded answers, not guesses.</h3>
              <p>Nexus delegates retrieval, relevance grading, query rewriting, local extractive answering, and citation validation to the shared Agentic RAG engine. No hosted LLM API is required.</p>
              <div className="capability-list"><span>01&nbsp; Existing RAG engine</span><span>02&nbsp; Page-level citations</span><span>03&nbsp; Server-side integration</span></div>
            </div>
          </div>

          <div className="workspace-grid">
            <section className="tool-card" id="knowledge">
              <span className="section-kicker">KNOWLEDGE BASE</span>
              <h3>Add a document</h3>
              <p>Upload a PDF, DOCX, Markdown, or TXT file to the local RAG engine. Source files persist in a Docker volume and are re-indexed after a service restart. This development workspace is not tenant-isolated.</p>
              <form onSubmit={uploadDocument} className="upload-form">
                <input
                  id="document-upload"
                  type="file"
                  accept=".pdf,.docx,.txt,.md"
                  onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
                />
                <button type="submit" disabled={!selectedFile || uploadLoading}>
                  {uploadLoading ? "Indexing…" : "Upload and index"}
                </button>
              </form>
              {uploadMessage && <p className="inline-message" role="status">{uploadMessage}</p>}
              <span className="card-state">PDF · DOCX · TXT · MD · MAX 10 MiB</span>
            </section>

            <section className="tool-card" id="integrations">
              <span className="section-kicker">CONTROL PLANE</span>
              <h3>Enterprise governance</h3>
              <p>The next layer will enforce identity, tool permissions, human approvals, and an audit trail before any state-changing integration is allowed.</p>
              <span className="card-state">NEXT IMPLEMENTATION MILESTONE</span>
            </section>
          </div>

          <section className="chat-panel">
            <div className="panel-title">
              <div><span className="section-kicker">AI ASSISTANT</span><h2>Ask a question</h2></div>
              <span className="small-muted">Agentic RAG · grounded responses</span>
            </div>
            <form onSubmit={submitQuestion} className="question-form">
              <input
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                maxLength={2000}
                placeholder="When does the locker code expire?"
                aria-label="Ask a question about your documents"
              />
              <button type="submit" disabled={!question.trim() || askLoading || ragState === "offline"}>
                {askLoading ? "Thinking…" : "Ask Nexus"}
              </button>
            </form>
            {askError && <p className="error-message" role="alert">{askError}</p>}
            {answer && (
              <div className="answer-panel">
                <div className="answer-meta"><span>ANSWER</span><span>{answer.latency_ms} ms · {answer.engine}</span></div>
                <p className="answer-text">{answer.answer}</p>
                <div className="citation-list">
                  <strong>Sources</strong>
                  {answer.citations.length === 0 ? (
                    <p className="small-muted">The engine abstained or returned no citations.</p>
                  ) : answer.citations.map((citation) => (
                    <article className="citation" key={`${citation.n}-${citation.source}-${citation.page}`}>
                      <div><strong>[{citation.n}] {citation.source}</strong><span>Page {citation.page} · relevance {citation.score.toFixed(3)}</span></div>
                      <p>{citation.text}</p>
                    </article>
                  ))}
                </div>
                {retrievalDebug && (
                  <details className="trace-details retrieval-debug">
                    <summary>Retrieved passages · {retrievalDebug.results.length} result(s)</summary>
                    {retrievalDebug.results.map((result) => (
                      <article className="citation" key={`${result.rank}-${result.source}-${result.page}`}>
                        <div><strong>#{result.rank} {result.source}</strong><span>Page {result.page} · score {result.score.toFixed(4)}</span></div>
                        <p>{result.text}</p>
                      </article>
                    ))}
                  </details>
                )}
                <details className="trace-details">
                  <summary>Agent execution trace</summary>
                  <ol>{answer.trace.map((step, index) => <li key={index}>{step}</li>)}</ol>
                </details>
              </div>
            )}
            {!answer && !askError && <p className="empty-chat">Try the sample question above. The RAG API indexes the included incident, Kafka, and pantry sample documents on first start.</p>}
          </section>
          <footer className="footer"><span>Nexus AI · local MVP</span><span>Local-only answers · enterprise governance in progress</span></footer>
        </div>
      </section>
    </main>
  );
}
