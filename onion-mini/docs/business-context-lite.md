# Business Context

> Este arquivo é a **SSOT (fonte única de verdade) de Produto** — outros artefatos CITAM este arquivo, nunca duplicam seu conteúdo. O agente `@product` o atualiza a cada descoberta. Ao preencher, **substitua (e remova) os `[colchetes]`**.

## 1. Visão do Produto
[O que é o projeto, em 2-3 frases: o que faz, para quem, e qual o diferencial.]
- **Fora do escopo (não-objetivos):** [ex: pagamento in-app — o guard-rail anti-scope-creep]

## 2. Público & Personas
| Persona | Quem é | Contexto de uso |
|---|---|---|
| [Nome] | [ex: mãe organizadora da casa] | [ex: usa no celular, no mercado] |

## 3. Dores do Cliente (Problemas que resolvemos)
| Dor | Impacto (o que custa hoje) |
|---|---|
| [Problema 1] | [ex: compras duplicadas toda semana] |

## 4. Objetivos & Métricas de Sucesso
- **Objetivo:** [ex: famílias pararem de comprar em duplicidade]
- **Como medimos:** [ex: % de listas com item marcado por 2+ pessoas]

## 5. Backlog de Épicos e Features
> Este é o **quadro de tasks** de Produto (Task Manager Lite). Status: `A Fazer → Pronto para Dev → Em Dev → Feito`.

| ID | Título | Status | Notas |
|---|---|---|---|
| F-01 | [Nome da Primeira Feature] | A Fazer | [Notas adicionais] |

## 6. Especificações Ativas (Em Detalhe)
### F-XX — [Nome da Feature]
**História:** Como [persona], quero [ação], para [benefício].
**Critérios de Aceite:** [3-5, testáveis — "dado X, quando Y, então Z"]
**Regras de Negócio:** [limites, permissões, exceções]

## 7. Pendências de Validação
[Tudo que foi assumido sem confirmação do usuário entra aqui marcado com `[INFERIDO]` — e sai quando validado.]

## 8. 🔁 Redesenhos
> A casa do redesenho de Produto: todo checkpoint de fechamento do Ciclo de Produto registra aqui **o que faremos diferente**.

| Data | Ciclo/Feature | O que muda no próximo ciclo |
|---|---|---|
| | | |

---
> **Graduação:** ao adotar o [Sistema Onion completo](https://onionevolve.com), cada seção expande para sua camada em `docs/business-context/` — §1/§4/§5/§6 → `02-product/` · §2/§3 → `01-customer/` · §7 → convenção `[INFERIDO]` do core. Zero retrabalho.
