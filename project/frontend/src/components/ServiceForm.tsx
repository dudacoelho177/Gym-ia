import { useState } from "react";
import { api } from "../api/client";
import { useGymStore } from "../store/useGymStore";

/** Formulário fixo de serviço + briefing (specs/phase-01/004 e 005) — obrigatório para iniciar o motor. */
export function ServiceForm() {
  const portfolio = useGymStore((s) => s.portfolio);
  const conversations = useGymStore((s) => s.conversations);
  const setConversations = useGymStore((s) => s.setConversations);
  const setCurrentConversation = useGymStore((s) => s.setCurrentConversation);
  const setCoverage = useGymStore((s) => s.setCoverage);

  const [serviceType, setServiceType] = useState("");
  const [title, setTitle] = useState("");
  const [briefing, setBriefing] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const categories = Array.from(new Set(portfolio.map((item) => item.category)));

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!serviceType) {
      setError("Selecione um serviço do portfólio para iniciar.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const conversation = await api.createConversation({ service_type: serviceType, briefing, title });
      setConversations([conversation, ...conversations]);
      setCurrentConversation(conversation);
      const state = await api.getDiscoveryState(conversation.id);
      setCoverage(state.coverage_by_category, state.overall_coverage);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao criar conversa");
    } finally {
      setSubmitting(false);
    }
  }

  const fieldStyle: React.CSSProperties = {
    display: "block",
    width: "100%",
    marginTop: 8,
    padding: "12px 20px",
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        maxWidth: 520,
        margin: "var(--space-6) auto",
        display: "flex",
        flexDirection: "column",
        gap: "var(--space-3)",
      }}
    >
      <div className="eyebrow">Nova oportunidade</div>
      <h2>Iniciar discovery de pré-vendas</h2>
      <p style={{ marginTop: -8 }}>
        Selecione o serviço do portfólio e cole o briefing — o motor conduz a conversa dali em diante.
      </p>

      <label>
        <span style={{ fontSize: 14, fontWeight: 500 }}>Tipo de serviço (portfólio Clear IT) *</span>
        <select
          value={serviceType}
          onChange={(e) => setServiceType(e.target.value)}
          className="pill"
          style={fieldStyle}
        >
          <option value="">Selecione...</option>
          {categories.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
      </label>

      <label>
        <span style={{ fontSize: 14, fontWeight: 500 }}>Título da oportunidade</span>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Ex.: Migração cloud — Cliente X"
          className="pill"
          style={fieldStyle}
        />
      </label>

      <label>
        <span style={{ fontSize: 14, fontWeight: 500 }}>Briefing inicial</span>
        <textarea
          value={briefing}
          onChange={(e) => setBriefing(e.target.value)}
          rows={4}
          placeholder="Cole aqui o briefing recebido do time comercial..."
          style={{ ...fieldStyle, borderRadius: "var(--radius-consent)", resize: "vertical" }}
        />
      </label>

      {error && (
        <div style={{ color: "var(--color-clay-brown)", fontSize: 14, fontWeight: 500 }}>{error}</div>
      )}

      <button type="submit" className="btn-primary pill" disabled={submitting} style={{ alignSelf: "flex-start" }}>
        {submitting ? "Iniciando..." : "Iniciar discovery"}
      </button>
    </form>
  );
}
