"use client";

import { useEffect, useState } from "react";

type ServiceState = "checking" | "online" | "offline";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function Home() {
  const [apiState, setApiState] = useState<ServiceState>("checking");
  const [databaseState, setDatabaseState] = useState("Checking");

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
        <a className="nav-item" href="#integrations"><span>⌘</span> Integrations</a>
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
          <div className="eyebrow">ENTERPRISE INTELLIGENCE WORKSPACE</div>
          <h1>Make knowledge<br /><em>work for you.</em></h1>
          <p className="intro">A grounded AI workspace for searching organizational knowledge and connecting approved business tools. The application foundation is online; core AI workflows are being built next.</p>

          <div className="status-row">
            <div className="status-card">
              <span className="status-dot" data-state={apiState} />
              <span><small>API SERVICE</small><strong>{apiState === "online" ? "Connected" : apiState === "offline" ? "Offline" : "Checking…"}</strong></span>
            </div>
            <div className="status-card">
              <span className="status-dot" data-state={databaseState === "connected" ? "online" : apiState === "offline" ? "offline" : "checking"} />
              <span><small>DATABASE</small><strong>{databaseState}</strong></span>
            </div>
            <button className="refresh-button" onClick={() => void checkBackend()}>↻ Check services</button>
          </div>

          <div className="section-heading" id="assistant">
            <div><span className="section-kicker">START HERE</span><h2>AI assistant</h2></div>
            <span className="coming-badge">COMING IN NEXT MILESTONE</span>
          </div>

          <div className="assistant-card">
            <div className="assistant-icon">✳</div>
            <div className="assistant-copy">
              <h3>Your enterprise copilot is taking shape.</h3>
              <p>Next: upload a knowledge document, index its contents, and ask questions with source citations. Tool integrations will be added behind explicit permissions and approval controls.</p>
              <div className="capability-list"><span>01&nbsp; Document retrieval</span><span>02&nbsp; Source citations</span><span>03&nbsp; Controlled tools</span></div>
            </div>
          </div>

          <div className="grid-two">
            <article className="small-card" id="knowledge">
              <div className="card-icon">▤</div><span className="section-kicker">KNOWLEDGE</span>
              <h3>Knowledge base</h3><p>Document ingestion and semantic retrieval are the next implementation milestone.</p>
              <span className="card-state">NOT IMPLEMENTED YET</span>
            </article>
            <article className="small-card" id="integrations">
              <div className="card-icon">⌘</div><span className="section-kicker">CONNECTIVITY</span>
              <h3>Business integrations</h3><p>Allowlisted read-only tools first, followed by human-approved actions and audit history.</p>
              <span className="card-state">NOT IMPLEMENTED YET</span>
            </article>
          </div>
          <footer className="footer"><span>Nexus AI · v0.1.0</span><span>Built with a security-first approach</span></footer>
        </div>
      </section>
    </main>
  );
}
