# Business Context

> Este arquivo é a **SSOT (fonte única de verdade) de Produto** — outros artefatos CITAM este arquivo, nunca duplicam seu conteúdo. O agente `@product` o atualiza a cada descoberta. Ao preencher, **substitua (e remova) os `[colchetes]`**.

## 1. Visão do Produto
Agente de IA para apoiar a pré-vendas da Clear IT na geração de roteiros de levantamento técnico, comercial e operacional a partir de uma descrição de oportunidade e de um portfólio de referência. O diferencial é transformar briefings iniciais em perguntas categorizadas, priorizadas e aderentes ao portfólio, reduzindo dependência da experiência individual e retrabalho na qualificação.
- **Fora do escopo (não-objetivos):** integrar o MVP a sistemas internos; substituir a revisão de um profissional de pré-vendas; inventar capacidades fora do portfólio informado; usar dados reais de clientes sem anonimização ou autorização.

## 2. Público & Personas
| Persona | Quem é | Contexto de uso |
|---|---|---|
| Pré-vendas | Profissional responsável por qualificar oportunidades e preparar reuniões de descoberta. | Recebe um briefing inicial do comercial e precisa montar rapidamente um roteiro de perguntas técnico, comercial e operacional. |
| Comercial | Vendedor ou account manager que recebe a demanda inicial do cliente. | Usa o roteiro para complementar informações, alinhar expectativas e preparar a passagem para pré-vendas. |
| Especialista técnico | Arquiteto, engenheiro ou especialista de infraestrutura, cloud, cybersegurança, observabilidade, backup, redes, COPS ou SOC. | Revisa perguntas, premissas e riscos quando a oportunidade exige validação técnica mais profunda. |
| Gestor de pré-vendas | Liderança responsável por qualidade, produtividade e padronização do processo. | Avalia indicadores de tempo, completude, retrabalho, aderência ao portfólio e reutilização de conhecimento. |
| Cliente | Cliente final impactado indiretamente pela qualidade da reunião e da proposta. | Responde perguntas mais claras e contextualizadas, reduzindo idas e vindas e desalinhamentos de escopo. |

## 3. Dores do Cliente (Problemas que resolvemos)
| Dor | Impacto (o que custa hoje) |
|---|---|
| Preparação manual de perguntas de levantamento. | Aumenta o tempo para montar o primeiro roteiro e atrasa a resposta ao cliente. |
| Qualidade variável conforme experiência individual. | Profissionais menos experientes podem esquecer perguntas importantes ou gerar roteiros genéricos. |
| Baixa padronização entre oportunidades semelhantes. | Dificulta alinhamento entre comercial, pré-vendas, operação, pós-venda e cliente. |
| Dependência de múltiplas fontes e especialistas. | Consome tempo com consultas a propostas antigas, portfólio, anotações e validações pontuais. |
| Briefings incompletos ou pouco contextualizados. | Gera novas rodadas com o cliente, ajustes de escopo e reabertura de discussões técnicas. |
| Risco de desalinhamento com o portfólio. | Pode levar a perguntas, premissas ou recomendações desconectadas das ofertas disponíveis. |

## 4. Objetivos & Métricas de Sucesso
- **Objetivo:** reduzir o tempo e aumentar a qualidade da etapa de levantamento em pré-vendas por meio de um agente de IA que gere perguntas contextualizadas ao tipo de oportunidade e ao portfólio de produtos e serviços.
- **Como medimos:** tempo para montar o primeiro roteiro; completude do briefing na primeira rodada; redução de retrabalho técnico; aderência das perguntas ao portfólio; qualidade percebida pelos usuários internos; reutilização de blocos de perguntas em oportunidades semelhantes.

## 5. Backlog de Épicos e Features
> Este é o **quadro de tasks** de Produto (Task Manager Lite). Status: `A Fazer → Pronto para Dev → Em Dev → Feito`.

| ID | Título | Status | Notas |
|---|---|---|---|
| F-01 | Gerador de Roteiro de Levantamento por Oportunidade | Feito | MVP implementado com CLI, UI local, exemplos ficticios, portfolio mockado, classificador, planejador, validador e testes automatizados. |
| F-02 | Base Reutilizável de Blocos de Perguntas por Solução | A Fazer | Categorias previstas: infraestrutura, cloud, cybersegurança, backup, observabilidade, redes, COPS, SOC e serviços de sustentação. |
| F-03 | Avaliação de Aderência ao Portfólio | A Fazer | Deve evitar capacidades inexistentes e sinalizar lacunas para validação com especialista. |
| F-04 | Adaptação de Profundidade por Público-alvo | A Fazer | Ajustar linguagem e profundidade para comercial, técnico, operação, gestão, compras ou cliente final. |

## 6. Especificações Ativas (Em Detalhe)
### F-01 — Gerador de Roteiro de Levantamento por Oportunidade
**História:** Como profissional de pré-vendas, quero informar uma descrição de oportunidade e um portfólio de referência para receber um roteiro inicial de levantamento organizado por categorias, de modo que eu consiga preparar reuniões de descoberta com mais rapidez, consistência e aderência ao escopo.

**Critérios de Aceite:**
1. Dada uma descrição de oportunidade com tipo de solução, cliente/segmento, objetivo da demanda, escopo inicial e portfólio de referência, quando o agente processar a entrada, então deve classificar o tipo de oportunidade ou sinalizar que a classificação precisa de validação.
2. Dado um briefing inicial, quando o roteiro for gerado, então a saída deve organizar perguntas por categorias como contexto de negócio, ambiente atual, escopo técnico, operação e sustentação, segurança e conformidade, volumetria e capacidade, criticidade, governança, premissas e exclusões, riscos e validações.
3. Dado o roteiro gerado, quando houver informações insuficientes no briefing, então o agente deve listar informações faltantes e separar perguntas prioritárias de perguntas complementares.
4. Dado um portfólio de referência, quando o agente sugerir perguntas, premissas ou pontos de atenção, então o conteúdo deve estar aderente às ofertas disponíveis e deve sinalizar lacunas quando a informação não existir no portfólio.
5. Dadas pelo menos três oportunidades fictícias ou autorizadas por produto e serviço, quando comparadas com perguntas elaboradas por especialistas, então o roteiro deve ser considerado coerente, claro e útil para preparação de reunião ou solicitação de informações complementares.

**Regras de Negócio:**
- O agente deve tratar a saída como apoio à decisão; o uso com clientes exige revisão de um profissional de pré-vendas.
- O agente não deve inventar capacidades, ofertas, integrações, SLAs ou responsabilidades que não estejam no portfólio informado.
- Quando a informação não estiver disponível, o agente deve sinalizar a lacuna e sugerir validação com especialista.
- Dados usados em exemplos ou testes devem ser fictícios, anonimizados ou previamente autorizados.
- O MVP pode funcionar com documentos, planilhas, formulários ou textos inseridos manualmente, sem integração obrigatória com sistemas internos.
- As perguntas devem ser claras, objetivas, categorizadas e adequadas ao contexto de pré-vendas, evitando linguagem excessivamente genérica.
- A profundidade das perguntas deve variar conforme o público-alvo: comercial, técnico, operação, gestão, compras ou cliente final.

## 7. Pendências de Validação
- Confirmar o formato preferido de entrada do MVP: texto livre, formulário, planilha, upload de documento ou combinação desses formatos.
- Confirmar quais materiais de portfólio estarão disponíveis para o protótipo e em qual formato.
- Definir quais três oportunidades por produto/serviço serão usadas na validação inicial.
- Confirmar escala e método de avaliação de qualidade percebida pelos usuários internos.
- [INFERIDO] Considerar pré-vendas como usuário principal do primeiro MVP antes de expandir para comercial e gestão.
- [INFERIDO] Considerar infraestrutura, COPS, SOC, segurança, backup, cloud, redes e observabilidade como categorias iniciais de cobertura.

## 8. 🔁 Redesenhos
> A casa do redesenho de Produto: todo checkpoint de fechamento do Ciclo de Produto registra aqui **o que faremos diferente**.

| Data | Ciclo/Feature | O que muda no próximo ciclo |
|---|---|---|
| 2026-07-07 | Product/F-01 | No próximo ciclo, separar explicitamente hipóteses confirmadas pelo briefing de decisões que dependem de validação com o time Clear IT/Pulse Mais antes de planejar engenharia. |

---
> **Graduação:** ao adotar o [Sistema Onion completo](https://onionevolve.com), cada seção expande para sua camada em `docs/business-context/` — §1/§4/§5/§6 → `02-product/` · §2/§3 → `01-customer/` · §7 → convenção `[INFERIDO]` do core. Zero retrabalho.
