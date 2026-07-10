import type { ReactNode } from "react";
import { useTheme } from "../store/useTheme";

/** Ícones em traço (spec §4 Icon-Only Circle Button) — sem emoji, só linhas na cor do texto. */
function SunIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <circle cx="12" cy="12" r="4" />
      <line x1="12" y1="2" x2="12" y2="5" />
      <line x1="12" y1="19" x2="12" y2="22" />
      <line x1="2" y1="12" x2="5" y2="12" />
      <line x1="19" y1="12" x2="22" y2="12" />
      <line x1="4.6" y1="4.6" x2="6.7" y2="6.7" />
      <line x1="17.3" y1="17.3" x2="19.4" y2="19.4" />
      <line x1="4.6" y1="19.4" x2="6.7" y2="17.3" />
      <line x1="17.3" y1="6.7" x2="19.4" y2="4.6" />
    </svg>
  );
}

function MoonIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5Z" />
    </svg>
  );
}

/** Shell da Home (specs/phase-01/001) no design system Mastercard-inspired: canvas cream,
 * sidebar como painel "lifted cream" com raio grande, nav flutuante em pill branca (spec §4/§5). */
export function Shell({ sidebar, main }: { sidebar: ReactNode; main: ReactNode }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        background: "var(--surface-canvas)",
        padding: "var(--space-3)",
        gap: "var(--space-3)",
      }}
    >
      <aside
        className="surface-lifted card-lg"
        style={{
          width: 288,
          flexShrink: 0,
          padding: "var(--space-3)",
          overflowY: "auto",
        }}
      >
        {sidebar}
      </aside>

      <main style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0, gap: "var(--space-2)" }}>
        <header
          className="pill"
          style={{
            background: "var(--surface-nav)",
            boxShadow: "var(--shadow-1)",
            padding: "10px 16px 10px 32px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <span style={{ fontWeight: 500, fontSize: 16, letterSpacing: "-0.02em" }}>Gym.AI</span>
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
            <span className="eyebrow">Discovery de Pré-Vendas · Clear IT</span>
            <button
              type="button"
              className="theme-toggle"
              onClick={toggleTheme}
              title={theme === "light" ? "Ativar tema escuro" : "Ativar tema claro"}
              aria-label="Alternar tema claro/escuro"
            >
              {theme === "light" ? <MoonIcon /> : <SunIcon />}
            </button>
          </div>
        </header>
        <div className="surface-card" style={{ flex: 1, overflow: "auto", padding: "var(--space-4)" }}>
          {main}
        </div>
      </main>
    </div>
  );
}
