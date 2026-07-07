# Onion Mini — Instruções para Agentes de IA

> Config universal (padrão AGENTS.md) do **Onion Mini** — a versão mini e portátil do Sistema
> Onion: desenvolvimento **Spec-as-Code** (especificação antes do código).

## Especificação operacional

**Leia e adote [`ONION-MASTER-PROMPT.md`](./ONION-MASTER-PROMPT.md) por inteiro** — ele é a SSOT
do seu comportamento (personas, Fase Zero, fluxos). Os ciclos detalhados vivem em
[`docs/onion-cycles.md`](./docs/onion-cycles.md).

## Invariantes (valem mesmo sem ler o resto)

1. **Regra de Ouro:** nunca gere código antes da especificação — `@product` especifica o negócio,
   `@engineer` planeja a técnica, SÓ ENTÃO codifique (o usuário pode dizer "forçar" — obedeça registrando que o código nasce sem spec).
2. **Ciclo de trabalho:** todo trabalho roda Planejar → Executar → Avaliar, e a avaliação fecha
   **sempre com redesenho** ("o que faremos diferente?").
3. **Dogfood Mini:** nada está "pronto" sem rodar/verificar de verdade; conclusão sem evidência
   é hipótese e deve ser declarada como tal.
4. **Task Manager Lite:** o quadro de tasks é agnóstico de ferramenta — default é a tabela de
   backlog do `business-context-lite.md` + checklist do plano (`A Fazer → Em Dev → Feito`).
5. **Idioma:** chat/documentação em pt-BR; código, identificadores e commits em inglês.

## Mapa de arquivos

| Arquivo | Papel |
|---|---|
| `docs/business-context-lite.md` | **SSOT de Produto** (visão, personas, dores, métricas, backlog, specs, redesenhos) — seções mapeiam as camadas do Onion completo |
| `docs/technical-context-lite.md` | **SSOT de Engenharia** (stack, padrões, arquitetura, ADR-lite, planos, débitos, redesenhos) — idem |
| `docs/onion-cycles.md` | Os 5 ciclos (Produto · Engenharia · KB · Sync · Sessões) |
| `docs/sessions/` | Registro de sessões (`/session "topico"`) |
| `docs/knowledge-base/` | KBs geradas pelo `@meta` (pasta criada sob demanda) |
