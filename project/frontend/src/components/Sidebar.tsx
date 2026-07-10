import { api } from "../api/client";
import { useGymStore } from "../store/useGymStore";

/** Sidebar: navegação e histórico (specs/phase-01/002). Itens em pill, raio 999px (spec §5).
 * Inclui link fixo para "Prompts" (prompt editável do tenant, specs/phase-03/002). */
export function Sidebar({ onNewChat }: { onNewChat: () => void }) {
  const conversations = useGymStore((s) => s.conversations);
  const currentConversation = useGymStore((s) => s.currentConversation);
  const setCurrentConversation = useGymStore((s) => s.setCurrentConversation);
  const setCoverage = useGymStore((s) => s.setCoverage);
  const view = useGymStore((s) => s.view);
  const setView = useGymStore((s) => s.setView);

  async function handleSelect(conversation: (typeof conversations)[number]) {
    setCurrentConversation(conversation);
    try {
      const state = await api.getDiscoveryState(conversation.id);
      setCoverage(state.coverage_by_category, state.overall_coverage);
    } catch {
      // Conversa recém-criada pode ainda não ter DiscoveryState — mantém cobertura zerada.
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <button
        className="btn-primary pill"
        style={{ width: "100%", marginBottom: "var(--space-3)" }}
        onClick={onNewChat}
      >
        + Nova conversa
      </button>

      <button
        onClick={() => setView("prompts")}
        className="btn-primary pill"
        style={{ width: "100%", marginBottom: "var(--space-3)" }}
      >
        Prompts
      </button>

      <div className="eyebrow" style={{ marginBottom: "var(--space-2)" }}>
        Histórico
      </div>
      {conversations.length === 0 && (
        <div style={{ color: "var(--text-faint)", fontSize: 14, padding: "4px 12px" }}>
          Nenhuma conversa ainda.
        </div>
      )}
      <div style={{ display: "flex", flexDirection: "column", gap: 4, overflowY: "auto" }}>
        {conversations.map((conversation) => {
          const active = view === "workspace" && currentConversation?.id === conversation.id;
          return (
            <button
              key={conversation.id}
              onClick={() => handleSelect(conversation)}
              className="pill"
              style={{
                display: "block",
                width: "100%",
                textAlign: "left",
                background: active ? "var(--btn-primary-bg)" : "transparent",
                color: active ? "var(--btn-primary-text)" : "var(--text-primary)",
                border: "none",
                padding: "10px 16px",
                fontSize: 14,
                fontWeight: active ? 500 : 450,
              }}
            >
              {conversation.title || conversation.service_type}
            </button>
          );
        })}
      </div>
    </div>
  );
}
