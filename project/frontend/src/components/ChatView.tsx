import { useState } from "react";
import { api, type ArtifactDTO, type MessageDTO } from "../api/client";
import { useGymStore } from "../store/useGymStore";

/** Chat/conversa (specs/phase-01/003): envio, "Gerar entendimento" a qualquer momento. */
export function ChatView() {
  const conversation = useGymStore((s) => s.currentConversation);
  const appendMessages = useGymStore((s) => s.appendMessages);
  const coverageByCategory = useGymStore((s) => s.coverageByCategory);
  const overallCoverage = useGymStore((s) => s.overallCoverage);
  const setCoverage = useGymStore((s) => s.setCoverage);
  const understanding = useGymStore((s) => s.understanding);
  const setUnderstanding = useGymStore((s) => s.setUnderstanding);

  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [artifacts, setArtifacts] = useState<ArtifactDTO[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [understandingLoading, setUnderstandingLoading] = useState(false);
  const [artifactsLoading, setArtifactsLoading] = useState(false);

  if (!conversation) {
    return <div style={{ color: "var(--text-muted)" }}>Selecione ou crie uma conversa para começar.</div>;
  }

  async function handleSend(event: React.FormEvent) {
    event.preventDefault();
    if (!draft.trim() || !conversation) return;
    setSending(true);
    setError(null);
    const content = draft;
    setDraft("");
    try {
      const userMessage: MessageDTO = {
        id: `local-${Date.now()}`,
        role: "user",
        content,
        created_at: new Date().toISOString(),
      };
      const response = await api.sendMessage(conversation.id, content);
      appendMessages(userMessage, response.assistant_message);
      setCoverage(response.coverage_by_category, response.overall_coverage);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao enviar mensagem");
    } finally {
      setSending(false);
    }
  }

  async function handleGenerateUnderstanding() {
    if (!conversation) return;
    setUnderstandingLoading(true);
    setError(null);
    try {
      const result = await api.generateUnderstanding(conversation.id);
      setUnderstanding(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao gerar entendimento");
    } finally {
      setUnderstandingLoading(false);
    }
  }

  async function handleGenerateArtifacts() {
    if (!conversation) return;
    setArtifactsLoading(true);
    setError(null);
    try {
      const result = await api.generateArtifacts(conversation.id, ["spec", "adr"]);
      setArtifacts(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao gerar artefatos");
    } finally {
      setArtifactsLoading(false);
    }
  }

  return (
    <div style={{ display: "flex", gap: "var(--space-4)", height: "100%" }}>
      <div style={{ flex: 2, display: "flex", flexDirection: "column", minWidth: 0 }}>
        <div className="eyebrow" style={{ marginBottom: "var(--space-2)" }}>
          {conversation.service_type}
        </div>
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            gap: "var(--space-2)",
            paddingRight: 4,
          }}
        >
          {conversation.messages.length === 0 && (
            <p style={{ color: "var(--text-muted)" }}>
              Envie a primeira mensagem para o motor começar o discovery.
            </p>
          )}
          {conversation.messages.map((message) => (
            <div
              key={message.id}
              className="pill"
              style={{
                alignSelf: message.role === "user" ? "flex-end" : "flex-start",
                background: message.role === "user" ? "var(--btn-primary-bg)" : "var(--surface-bubble-assistant)",
                color: message.role === "user" ? "var(--btn-primary-text)" : "var(--text-primary)",
                padding: "12px 20px",
                maxWidth: "70%",
                fontWeight: 450,
                lineHeight: 1.4,
              }}
            >
              {message.content}
            </div>
          ))}
        </div>
        <form onSubmit={handleSend} style={{ display: "flex", gap: "var(--space-1)", marginTop: "var(--space-3)" }}>
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="Responda a pergunta do discovery..."
            className="pill"
            style={{ flex: 1, padding: "12px 20px" }}
          />
          <button className="btn-primary pill" disabled={sending} type="submit">
            {sending ? "Enviando..." : "Enviar"}
          </button>
        </form>
        {error && (
          <div style={{ color: "var(--color-clay-brown)", marginTop: "var(--space-1)", fontSize: 14 }}>{error}</div>
        )}
      </div>

      <aside
        className="surface-lifted card-lg"
        style={{ flex: 1, minWidth: 300, padding: "var(--space-3)", overflowY: "auto" }}
      >
        <div className="eyebrow">Cobertura do discovery</div>
        <div style={{ fontSize: 32, fontWeight: 500, letterSpacing: "-0.02em", margin: "var(--space-1) 0" }}>
          {Math.round(overallCoverage * 100)}%
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-1)", marginTop: "var(--space-2)" }}>
          {Object.entries(coverageByCategory).map(([category, value]) => (
            <div key={category}>
              <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 4 }}>
                {category.replaceAll("_", " ")}
              </div>
              <div className="pill" style={{ background: "var(--surface-track)", height: 6 }}>
                <div
                  className="pill"
                  style={{
                    width: `${value * 100}%`,
                    background: "var(--color-light-signal-orange)",
                    height: 6,
                  }}
                />
              </div>
            </div>
          ))}
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-1)", marginTop: "var(--space-3)" }}>
          <button className="btn-secondary pill" onClick={handleGenerateUnderstanding} disabled={understandingLoading}>
            {understandingLoading ? "Gerando..." : "Gerar entendimento"}
          </button>
          <button className="btn-secondary pill" onClick={handleGenerateArtifacts} disabled={artifactsLoading}>
            {artifactsLoading ? "Gerando..." : "Gerar artefatos"}
          </button>
        </div>

        {understanding && (
          <div className="surface-card" style={{ marginTop: "var(--space-3)", padding: "var(--space-3)" }}>
            <div className="eyebrow">Entendimento executivo · v{understanding.version}</div>
            <p>{understanding.summary}</p>
            <p style={{ fontSize: 13, color: "var(--text-muted)" }}>{understanding.diagnosis}</p>
            <p style={{ fontSize: 12, fontStyle: "italic", color: "var(--text-italic-muted)" }}>
              {understanding.human_review_notice}
            </p>
          </div>
        )}

        {artifacts.length > 0 && (
          <div style={{ marginTop: "var(--space-3)" }}>
            <div className="eyebrow" style={{ marginBottom: "var(--space-1)" }}>
              Artefatos gerados
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-1)" }}>
              {artifacts.map((artifact) => (
                <details
                  key={artifact.id}
                  className="surface-card"
                  style={{ padding: "var(--space-2)", boxShadow: "none", border: "1px solid var(--border-subtle)" }}
                >
                  <summary style={{ fontWeight: 500, cursor: "pointer" }}>{artifact.title}</summary>
                  <pre style={{ whiteSpace: "pre-wrap", fontSize: 12, marginTop: 8 }}>{artifact.content}</pre>
                </details>
              ))}
            </div>
          </div>
        )}
      </aside>
    </div>
  );
}
