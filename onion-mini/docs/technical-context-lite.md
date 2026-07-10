# Technical Context

> Este arquivo é a **SSOT (fonte única de verdade) de Engenharia** — outros artefatos CITAM este arquivo, nunca duplicam seu conteúdo. O agente `@engineer` o atualiza a cada mudança de arquitetura. Ao preencher, **substitua (e remova) os `[colchetes]`**.

## 1. Stack Tecnológica
- **Linguagem:** Python 3.11+ para backend/prototipo do agente; HTML/CSS gerado por servidor local para interface inicial.
- **Framework:** Sem framework externo no MVP. A UI local usa `http.server` da biblioteca padrao; caso o MVP precise virar produto web multiusuario, evoluir para FastAPI + frontend dedicado.
- **Banco de Dados:** Sem banco no MVP. Usar arquivos locais versionados para exemplos fictícios, categorias, blocos de perguntas e portfólio de referência. Persistência estruturada fica como evolução.
- **Infraestrutura:** Execução local durante o desafio. Sem integração obrigatória com sistemas internos; deploy futuro pode ser containerizado quando houver stack alvo definida pela Clear IT/Pulse Mais.
- **IA/LLM:** Adaptador isolado para provedor de LLM, com fallback determinístico/rule-based para testes sem chave de API. O adaptador deve receber oportunidade + portfólio e devolver roteiro estruturado.

## 2. Padrões de Código & Gotchas
- Código em inglês; textos de interface e prompts em português do Brasil.
- Separar regras de negócio e geração de prompt da camada de UI.
- Manter saída do agente em estrutura validável antes de renderizar: categorias, perguntas prioritárias, perguntas complementares, lacunas, premissas e riscos.
- Não commitar dados reais de clientes. Exemplos devem ser fictícios, anonimizados ou autorizados.
- Testes devem cobrir classificação de oportunidade, detecção de lacunas, aderência a categorias e bloqueio contra capacidades não presentes no portfólio.
- **Gotchas:** sem portfólio real o agente deve sinalizar baixa confiança; sem chave de LLM o fallback não representa qualidade final de linguagem; prompts podem gerar conteúdo fora do portfólio se não houver validação de saída.

## 3. Arquitetura & Mapa do Código
Arquitetura proposta para F-01:

```text
User
  -> UI: opportunity form/text input + portfolio reference
  -> Application service: validates input and builds request
  -> Opportunity classifier: identifies solution category or flags uncertainty
  -> Question planner: selects categories and blocks of questions
  -> LLM adapter: generates/refines wording when available
  -> Output validator: checks structure, missing info, assumptions and portfolio adherence
  -> UI: renders structured discovery roteiro
```

O MVP deve manter um nucleo de dominio independente da interface. Assim, a mesma logica pode servir uma UI local agora e uma API depois.

| Diretório/Arquivo-chave | O que vive ali |
|---|---|
| `app/` | Entrada da aplicacao do MVP, interface local e composicao dos servicos. |
| `src/domain/` | Modelos e regras centrais: oportunidade, portfolio, categoria, roteiro, pergunta, lacuna, premissa e risco. |
| `src/services/` | Classificacao, selecao de blocos, geracao de roteiro e validacao de aderencia. |
| `src/adapters/` | Adaptadores para LLM, leitura de arquivos de portfolio e fontes de entrada. |
| `data/examples/` | Oportunidades ficticias/autorizadas usadas em validacao. |
| `data/portfolio/` | Portfolio de referencia usado pelo MVP. |
| `tests/` | Testes automatizados de dominio, servicos e validacao de saida. |

## 4. Decisões Técnicas (ADR-lite)
> Toda decisão de arquitetura/tecnologia com trade-off entra aqui — é o que evita rediscutir o mesmo tema.

| Data | Decisão | Alternativa rejeitada | Porquê |
|---|---|---|---|
| 2026-07-07 | MVP local, sem banco e sem integracao com sistemas internos | Integrar CRM, ferramentas internas ou banco relacional desde o inicio | A spec de Produto define que o MVP pode funcionar com textos/documentos inseridos manualmente; reduzir integracoes diminui risco e acelera validacao. |
| 2026-07-07 | Separar dominio/servicos da UI | Colocar toda a logica diretamente na tela do prototipo | Facilita testes, troca de interface e evolucao futura para API ou copiloto completo. |
| 2026-07-07 | Usar adaptador de LLM com fallback deterministico | Acoplar o codigo a um provedor especifico de IA | Permite demonstrar fluxo sem chave/API e evita dependencia prematura de fornecedor. |
| 2026-07-07 | Usar UI local com biblioteca padrao do Python no MVP | Depender de Streamlit ou outra biblioteca externa | O ambiente nao exigiu instalacao de dependencias e a validacao pode rodar imediatamente. |

## 5. Planos de Implementação Ativos
> O checklist de cada plano é o **quadro de tasks** de Engenharia (`A Fazer → Em Dev → Feito`).

### Plano para F-01 — Gerador de Roteiro de Levantamento por Oportunidade

**Critério de pronto:** dado um briefing de oportunidade e um portfolio de referencia, o MVP gera um roteiro estruturado por categorias, identifica lacunas, separa perguntas prioritarias/complementares, lista premissas e riscos, e passa por testes com pelo menos tres oportunidades ficticias/autorizadas.

**Arquivos a criar/modificar:**
- Criar `app/` para interface local do prototipo.
- Criar `src/domain/` com modelos de oportunidade, portfolio e roteiro.
- Criar `src/services/` com classificacao, planejamento de perguntas e validacao.
- Criar `src/adapters/` com adaptador de LLM e fallback deterministico.
- Criar `data/examples/` com oportunidades ficticias por categoria.
- Criar `data/portfolio/` com portfolio de referencia fornecido ou mockado.
- Criar `tests/` para cobrir dominio e servicos.
- Atualizar `README.md` ou documento de uso quando o codigo existir.

**Checklist de tasks:**
| Task | Status | Evidencia esperada |
|---|---|---|
| Definir formato estruturado de entrada e saida do roteiro | Feito | Modelos em `src/domain/models.py` e saida JSON/Markdown pela CLI. |
| Criar dados ficticios de exemplo para pelo menos tres oportunidades | Feito | Exemplos em `data/examples/backup_opportunity.json`, `cloud_opportunity.json` e `soc_opportunity.json`. |
| Criar portfolio de referencia inicial ou mockado | Feito | Portfolio em `data/portfolio/reference_portfolio.json`. |
| Implementar classificador de tipo de oportunidade | Feito | Testes cobrem backup, SOC e validacao necessaria. |
| Implementar planejador de categorias e blocos de perguntas | Feito | Testes cobrem categorias obrigatorias e pergunta especifica por solucao. |
| Implementar adaptador de LLM com fallback deterministico | Feito | `src/adapters/llm.py` preserva contrato para provedor futuro sem chave de API. |
| Implementar validador de lacunas, premissas, riscos e aderencia ao portfolio | Feito | Testes cobrem informacoes faltantes e ausencia de oferta aderente. |
| Implementar UI local para entrada e visualizacao do roteiro | Feito | `app/web.py` disponibiliza formulario local em `http://127.0.0.1:8501`. |
| Rodar validacao com tres oportunidades ficticias/autorizadas | Feito | `python3 -m unittest discover -s tests` passou com 5 testes. |

## 6. Débitos & Riscos Conhecidos
- Portfolio real ainda nao foi fornecido; o MVP valida contra portfolio mockado.
- Formato preferido de entrada ainda pendente em Produto; a UI atual usa formulario simples e CLI com JSON.
- Qualidade final depende de avaliacao de especialistas de pre-vendas; sem essa validacao, aderencia fica parcial.
- Uso de LLM pode gerar conteudo fora do portfolio; mitigacao obrigatoria via validador e sinalizacao de lacunas.
- Sem definicao de provedor de IA; manter adaptador isolado para evitar lock-in.

## 7. 🔁 Redesenhos
> A casa do redesenho de Engenharia: todo checkpoint de fechamento do Ciclo de Engenharia registra aqui **o que muda no processo**.

| Data | Ciclo/Feature | O que muda no próximo ciclo |
|---|---|---|
| 2026-07-07 | Engineer/F-01 | Antes de codificar, validar stack alvo e formato de entrada com a pessoa usuaria para evitar implementar uma UI incompatível com a apresentação do desafio. |
| 2026-07-07 | Engineer/F-01 Finish | Em proximos ciclos, preferir implementacao sem dependencia externa quando o objetivo for demonstrar rapidamente em ambiente restrito. |

---
> **Graduação:** ao adotar o [Sistema Onion completo](https://onionevolve.com), cada seção expande para sua camada em `docs/technical-context/` — §1 → `01-core/project-charter` · §2/§3 → `02-ai-context/` · §4 → `01-core/adr/` (um arquivo por decisão) · §5/§6 → `04-workflow/`. Zero retrabalho.
