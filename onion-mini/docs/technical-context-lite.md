# Technical Context

> Este arquivo é a **SSOT (fonte única de verdade) de Engenharia** — outros artefatos CITAM este arquivo, nunca duplicam seu conteúdo. O agente `@engineer` o atualiza a cada mudança de arquitetura. Ao preencher, **substitua (e remova) os `[colchetes]`**.

## 1. Stack Tecnológica
- **Linguagem:** [Sua linguagem primária]
- **Framework:** [Seu framework principal]
- **Banco de Dados:** [Seu banco de dados]
- **Infraestrutura:** [Onde será hospedado]

## 2. Padrões de Código & Gotchas
- [Regra de lint, ex: "Usar aspas simples no JS"]
- [Padrão de nomenclatura, ex: "Arquivos em kebab-case"]
- [Regras de testes]
- **Gotchas** (armadilhas conhecidas deste projeto): [ex: "a lib X quebra com Node 22"]

## 3. Arquitetura & Mapa do Código
[Diagrama em ASCII, Mermaid ou texto simples explicando como os componentes se comunicam.]

| Diretório/Arquivo-chave | O que vive ali |
|---|---|
| [ex: `src/api/`] | [ex: rotas e controllers] |

## 4. Decisões Técnicas (ADR-lite)
> Toda decisão de arquitetura/tecnologia com trade-off entra aqui — é o que evita rediscutir o mesmo tema.

| Data | Decisão | Alternativa rejeitada | Porquê |
|---|---|---|---|
| | [ex: WebSocket p/ tempo real] | [ex: polling] | [ex: latência + custo] |

## 5. Planos de Implementação Ativos
> O checklist de cada plano é o **quadro de tasks** de Engenharia (`A Fazer → Em Dev → Feito`).

[Quando uma feature for aprovada para dev, o @engineer detalha aqui: arquivos a criar/modificar + checklist passo a passo.]

## 6. Débitos & Riscos Conhecidos
- [ex: "sem testes no módulo Y — risco médio"]

## 7. 🔁 Redesenhos
> A casa do redesenho de Engenharia: todo checkpoint de fechamento do Ciclo de Engenharia registra aqui **o que muda no processo**.

| Data | Ciclo/Feature | O que muda no próximo ciclo |
|---|---|---|
| | | |

---
> **Graduação:** ao adotar o [Sistema Onion completo](https://onionevolve.com), cada seção expande para sua camada em `docs/technical-context/` — §1 → `01-core/project-charter` · §2/§3 → `02-ai-context/` · §4 → `01-core/adr/` (um arquivo por decisão) · §5/§6 → `04-workflow/`. Zero retrabalho.
