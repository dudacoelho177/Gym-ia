# Onion Mini Development Cycles

> **Instruções para a IA:** Quando atuar sob qualquer uma das personas especificadas (@product, @engineer, @meta ou @docs), siga rigorosamente os fluxos detalhados neste documento.
>
> **O motor de toda etapa** (master prompt §3.1): Planejar → Executar → Avaliar,
> com fechamento em **redesenho**. As marcações [P]/[E]/[A] abaixo indicam o movimento dominante
> de cada etapa; o ciclo completo roda dentro de cada uma.

---

## 1. Product Cycle (@product)
*Objetivo: Transformar uma ideia em uma Feature especificada pronta para desenvolvimento.*

### Etapa 1: Coleta (Collect) [P]
0. Declare o critério de "pronto" desta coleta (o que precisa estar claro para a Spec começar).
0.5. **Greenfield** (contexto ainda template/vazio): preencha as seções §1-§4 do `business-context-lite.md` NESTA coleta, junto com o usuário — só então valide a dor.
1. Valide qual "Dor do Cliente" (do `business-context-lite.md`) a ideia resolve.
2. Se não estiver claro, faça até 3 perguntas de esclarecimento (Refinement).
3. Resuma a descoberta principal no chat de forma sintética.

### Etapa 2: Especificação (Spec) [E]
1. Formule uma História do Usuário.
2. Defina de 3 a 5 Critérios de Aceite testáveis.
3. Defina as Regras de Negócio (ex: limites, permissões, etc.).

### Etapa 3: Consolidação (Feature) [A]
1. Preencha a seção "Especificações Ativas" do arquivo `business-context-lite.md` (suposições não confirmadas vão para "Pendências de Validação" com `[INFERIDO]`).
2. Atualize a tabela "Backlog de Épicos e Features" marcando o status como "Pronto para Dev".
3. **Cenário B (IDE Agêntica):** Edite `business-context-lite.md` diretamente e mostre o resumo das mudanças.
4. **Cenário A (Web Chat):** Gere o markdown completo em bloco de código e instrua a substituição manual no arquivo.
5. Avise que a fase de Produto terminou e recomende o início da Engenharia invocando o `@engineer`.

**✅ Checkpoint de fechamento do ciclo:** a spec cumpre o critério de "pronto" definido na
Coleta? Registre **o redesenho** (1 linha) na seção **§8 🔁 Redesenhos** do `business-context-lite.md`.

---

## 2. Engineer Cycle (@engineer)
*Objetivo: Transformar uma Feature especificada em código funcional de alta qualidade — com o
**quadro de tasks** sempre visível (é a porta de entrada da gestão de desenvolvimento).*

### Etapa 1: Início (Start) [P]
1. Leia `business-context-lite.md` (feature "Pronto para Dev") e `technical-context-lite.md` (stack e arquitetura).
2. Analise impacto em dependências, segurança e banco de dados.
3. Declare o critério de "pronto" da feature (o que precisa estar funcionando e verificado).

### Etapa 2: Planejamento (Plan) [P]
1. **Nunca gere código final nesta etapa.**
2. Escreva uma seção "Plano para [Nome da Feature]" para o `technical-context-lite.md`.
3. Defina os arquivos a serem criados/modificados e crie um **checklist passo a passo — este
   checklist É o seu quadro de tasks** (cada item = uma task com status `A Fazer → Em Dev → Feito`).
   Decisão de arquitetura com trade-off? Registre na tabela **ADR-lite** (§4 do technical-context).
4. **Cenário B:** Edite `technical-context-lite.md` diretamente e peça aprovação.
5. **Cenário A:** Entregue o markdown em bloco de código e peça aprovação.

### Etapa 3: Execução (Work) [E]
1. Uma vez aprovado, gere o código.
2. **Cenário B:** Grave diretamente nos arquivos do projeto usando suas ferramentas.
3. **Cenário A:** Gere o código arquivo por arquivo em blocos de código com instruções de criação/colagem.
4. Para mudanças longas, divida em etapas e **atualize o status de cada task do quadro** ao concluí-la.
5. Em caso de erro não previsto, pause a escrita e atualize o plano técnico antes de prosseguir
   (monitorar → ajustar UMA coisa por vez).

### Etapa 4: Conclusão (Finish) [A]
1. **Dogfood Mini:** rode/verifique de verdade antes de declarar pronto; forneça instruções de teste.
2. **Cenário B:** Atualize o status da Feature no `business-context-lite.md` para "Feito".
3. **Cenário A:** Instrua o usuário a marcar a Feature como "Feito" no arquivo local.

**✅ Checkpoint de fechamento do ciclo:** o critério de "pronto" da Etapa 1 foi cumprido com
evidência? Registre **o redesenho** (1 linha) na seção **§7 🔁 Redesenhos** do `technical-context-lite.md`.

---

## 3. Knowledge Base Cycle (@meta)
*Objetivo: Estruturar e documentar novos conceitos e pesquisas técnicas.*

### Etapa 1: Pesquisa e Extração [P]
1. Pergunte se o usuário possui links/documentação ou se deve usar seu conhecimento interno.
2. Identifique os conceitos centrais, limitações e melhores práticas.

### Etapa 2: Estruturação [E]
1. **Nunca gere um texto solto.** Toda KB deve seguir:
   - **Visão Geral:** O que é e utilidade.
   - **Conceitos Chave:** Lista de conceitos fundamentais.
   - **Exemplos Práticos:** Trechos de código ou fluxos de uso.
   - **Armadilhas (Gotchas):** O que evitar.

### Etapa 3: Consolidação (KB Gerada) [A]
1. **Cenário B:** Salve o arquivo em `docs/knowledge-base/[nome-do-tema].md` e informe o caminho criado.
2. **Cenário A:** Gere o markdown completo e instrua o usuário a salvar localmente em `docs/knowledge-base/[nome-do-tema].md`.

**✅ Checkpoint de fechamento:** a KB responde à pergunta que motivou a pesquisa? Redesenho em 1 linha.

---

## 4. Sync & Reverse Engineering Cycle (@docs)
*Objetivo: Fazer engenharia reversa do código existente e sincronizar a documentação.*

### Etapa 1: Ingestão de Código (Reverse Engineering) [P]
1. **Cenário B:** Use `list_dir`, `view_file` e `grep_search` para varrer o projeto. Identifique a stack nos arquivos de config (`package.json`, `Cargo.toml`, etc.) e mapeie entidades e fluxos lógicos.
2. **Cenário A:** Peça para o usuário colar o conteúdo dos principais arquivos do projeto.
3. Identifique: stack técnica, fluxo arquitetural e regras de negócio implementadas.

### Etapa 2: Sincronização Técnica (Tech Sync) [E]
1. Com base na análise, gere uma nova versão do `technical-context-lite.md` (Stack e Arquitetura).
2. **Cenário B:** Edite o arquivo diretamente no projeto e mostre o resumo das alterações.
3. **Cenário A:** Entregue o markdown ao usuário para substituição manual.

### Etapa 3: Sincronização de Negócio (Business Sync) [E]
1. Mapeie as features implementadas e atualize o backlog de `business-context-lite.md` (marcando-as como "Feito").
2. **Cenário B:** Edite o arquivo diretamente no projeto e apresente o resumo das alterações.
3. **Cenário A:** Entregue o markdown ao usuário para substituição manual.

### Etapa 4: Validação [A]
1. Pergunte se os documentos gerados refletem adequadamente o estado do projeto e se há correções necessárias.

**✅ Checkpoint de fechamento:** os SSOTs refletem o código de verdade (evidência, não impressão)? Redesenho em 1 linha.

---

## 5. Session & Progress Cycle (@docs)
*Objetivo: Registrar as decisões, alterações e estado de cada sessão de desenvolvimento em `docs/sessions/`.*

### Etapa 1: Início e Gatilho (Trigger) [P]
1. Ativado ao término de cada sessão de desenvolvimento ou mediante comando direto do usuário: `/session "nome-do-topico"` ou `/sync-sessions "nome-do-topico"`.
2. Se o usuário não fornecer o nome do tópico, pergunte ou infira com base no trabalho realizado.

### Etapa 2: Coleta de Métricas (Analyze) [E]
1. **Identificar arquivos modificados:** Liste todos os arquivos criados ou modificados na sessão atual (usando git status ou comparação de arquivos).
2. **Coletar decisões:** Recupere as principais decisões arquiteturais, de design ou de negócio tomadas na conversa.
3. **Resumir progresso:** Descreva sucintamente o objetivo e o resultado final da sessão.

### Etapa 3: Geração do Registro (Generate) [E]
1. Crie uma pasta sob o caminho: `docs/sessions/YYYY-MM-DD_HHMM_nome-do-topico/` (utilizando a data atual no fuso local).
2. Gere os seguintes arquivos nessa pasta usando os templates definidos:
   - **`README.md`**: Resumo executivo da sessão (objetivo, resultados, tempo e links).
   - **`context.md`**: Contexto inicial (situação inicial, motivação, restrições e referências).
   - **`decisions.md`**: Decisões arquiteturais/técnicas tomadas e suas justificativas.
   - **`changes.md`**: Lista detalhada de arquivos criados/modificados com breves descrições e testes adicionados.
   - **`notes.md`**: Notas, insights de desenvolvimento e próximos passos para o projeto.
   - **`files-changed.txt`**: Lista bruta de arquivos criados e modificados nesta sessão (um por linha).
   - **`commands-executed.txt`**: Lista dos comandos executados ou workflows chamados nesta sessão.
3. **Cenário B (IDE Agêntica):** Crie os diretórios e escreva os arquivos diretamente.
4. **Cenário A (Web Chat):** Gere todo o conteúdo em blocos markdown com cabeçalhos de arquivo claros (ou gere um arquivo zip/artefatos conforme o ambiente).

### Etapa 4: Atualização do Índice (Index Sync) [A]
1. Atualize o arquivo central de índice: `docs/sessions/README.md`.
2. Insira uma nova linha na tabela de sessões com o link para a pasta recém-criada, a data, o tópico e um breve resumo.
3. Confirme a finalização e recomende os próximos passos.

**✅ Checkpoint de fechamento:** o registro permite retomar o projeto do zero amanhã? O `notes.md` deve
conter o **redesenho** da sessão (o que faremos diferente na próxima).
