import { useEffect, useState } from "react";
import { api, type PromptDTO } from "../api/client";

/** Prompt Editável (specs/phase-03/002): CRUD do usuário sobre o prompt do tenant.
 * Cada "Salvar" cria uma NOVA versão imutável (ADR-0012) — nunca sobrescreve a anterior.
 * O Pré-Prompt (soberano, não editável) não aparece aqui — vive em `prompt_engine.py` no backend. */
export function PromptsPage() {
  const [prompt, setPrompt] = useState<PromptDTO | null>(null);
  const [name, setName] = useState("Prompt padrão de pré-vendas");
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activatingId, setActivatingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [previewVersionId, setPreviewVersionId] = useState<string | null>(null);

  useEffect(() => {
    api
      .getActivePrompt()
      .then((result) => {
        setPrompt(result);
        if (result) {
          setName(result.name);
          const active = result.versions.find((v) => v.id === result.active_version_id);
          setDraft(active?.content ?? "");
        }
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Erro ao carregar prompt"))
      .finally(() => setLoading(false));
  }, []);

  async function handleSave() {
    if (!draft.trim()) {
      setError("O conteúdo do prompt não pode ficar vazio.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const result = await api.savePrompt({ name, content: draft });
      setPrompt(result);
      setPreviewVersionId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao salvar prompt");
    } finally {
      setSaving(false);
    }
  }

  async function handleActivate(versionId: string) {
    setActivatingId(versionId);
    setError(null);
    try {
      const result = await api.activatePromptVersion(versionId);
      setPrompt(result);
      const active = result.versions.find((v) => v.id === result.active_version_id);
      setDraft(active?.content ?? "");
      setPreviewVersionId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao ativar versão");
    } finally {
      setActivatingId(null);
    }
  }

  if (loading) {
    return <p style={{ color: "var(--text-muted)" }}>Carregando prompt...</p>;
  }

  const versions = prompt ? [...prompt.versions].sort((a, b) => b.version_number - a.version_number) : [];

  return (
    <div style={{ maxWidth: 720, margin: "0 auto", display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
      <div>
        <div className="eyebrow">Prompt Engine</div>
        <h2>Prompt editável</h2>
        <p>
          Este prompt é injetado depois do Pré-Prompt interno (soberano, não editável) e antes do briefing —
          use para ajustar tom, foco ou prioridades do discovery para este tenant. Toda alteração cria uma
          nova versão; versões anteriores continuam disponíveis para reativação.
        </p>
      </div>

      <label>
        <span style={{ fontSize: 14, fontWeight: 500 }}>Nome do prompt</span>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="pill"
          style={{ display: "block", width: "100%", marginTop: 8, padding: "12px 20px" }}
        />
      </label>

      <label>
        <span style={{ fontSize: 14, fontWeight: 500 }}>Conteúdo</span>
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          rows={10}
          placeholder="Ex.: Priorize perguntas de escopo técnico e trate o cliente com tom consultivo..."
          style={{
            display: "block",
            width: "100%",
            marginTop: 8,
            padding: "12px 20px",
            borderRadius: "var(--radius-consent)",
            resize: "vertical",
            fontFamily: "monospace",
            fontSize: 13,
          }}
        />
      </label>

      {error && <div style={{ color: "var(--color-clay-brown)", fontSize: 14, fontWeight: 500 }}>{error}</div>}

      <button className="btn-primary pill" onClick={handleSave} disabled={saving} style={{ alignSelf: "flex-start" }}>
        {saving ? "Salvando..." : "Salvar nova versão"}
      </button>

      <div style={{ marginTop: "var(--space-2)" }}>
        <div className="eyebrow" style={{ marginBottom: "var(--space-2)" }}>
          Histórico de versões
        </div>
        {versions.length === 0 && (
          <p style={{ color: "var(--text-faint)" }}>Nenhuma versão salva ainda — salve a primeira acima.</p>
        )}
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-1)" }}>
          {versions.map((version) => {
            const isActive = version.id === prompt?.active_version_id;
            return (
              <div
                key={version.id}
                className="surface-card"
                style={{
                  boxShadow: "none",
                  border: isActive ? "1.5px solid var(--border-strong)" : "1px solid var(--border-subtle)",
                  padding: "var(--space-2)",
                  display: "flex",
                  flexDirection: "column",
                  gap: 8,
                }}
              >
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <span style={{ fontWeight: 500, fontSize: 14 }}>
                    v{version.version_number} {isActive && "· ativa"}
                  </span>
                  <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                    <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
                      {new Date(version.created_at).toLocaleString("pt-BR")}
                    </span>
                    <button
                      className="btn-secondary pill"
                      style={{ padding: "4px 14px", fontSize: 12 }}
                      onClick={() => setPreviewVersionId(previewVersionId === version.id ? null : version.id)}
                    >
                      {previewVersionId === version.id ? "Ocultar" : "Ver"}
                    </button>
                    {!isActive && (
                      <button
                        className="btn-secondary pill"
                        style={{ padding: "4px 14px", fontSize: 12 }}
                        onClick={() => handleActivate(version.id)}
                        disabled={activatingId === version.id}
                      >
                        {activatingId === version.id ? "Ativando..." : "Ativar"}
                      </button>
                    )}
                  </div>
                </div>
                {previewVersionId === version.id && (
                  <pre
                    style={{
                      whiteSpace: "pre-wrap",
                      fontSize: 12,
                      background: "var(--surface-bubble-assistant)",
                      borderRadius: "var(--radius-tiny)",
                      padding: "var(--space-2)",
                      margin: 0,
                    }}
                  >
                    {version.content}
                  </pre>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
