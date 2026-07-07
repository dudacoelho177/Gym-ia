# Manual de Uso: Onion Mini 🧅

Bem-vindo ao **Onion Mini** (antes "Onion Portable") — **a versão mini e portátil do Sistema Onion**: a mesma metodologia Spec-as-Code, destilada para caber em qualquer IA. É o **começo ideal para quem está iniciando no desenvolvimento com IA** (especialmente na gestão de tasks de desenvolvimento), rodando em Web Chats gratuitos (Claude.ai, ChatGPT, Gemini) e nativamente em IDEs Agênticas (Antigravity, Cursor, Claude Code, Zed, ...). Traz o ciclo de Produto e os contextos de Negócio/Técnico como SSOT, o motor **Planejar→Executar→Avaliar** (fechando sempre com redesenho) e o task management agnóstico de ferramenta (SDAAL destilado).

---

## 1. O que tem no pacote?

A pasta `onion-mini` contém:
- **`AGENTS.md`**: Config universal para agentes de IA (padrão lido nativamente por Codex, Cursor, Copilot, Zed, Aider...) — aponta para o Master Prompt. **`CLAUDE.md`** importa-o para o Claude Code.
- **`ONION-MASTER-PROMPT.md`**: O "Cérebro". É a instrução que você deve dar à IA para que ela assuma as personas do Onion.
- **`docs/`**: A pasta com os 3 arquivos de contexto/ciclo que guiam a IA e guardam as informações do seu projeto:
  1. `business-context-lite.md` — Contexto de Negócio (o que construir)
  2. `technical-context-lite.md` — Contexto Técnico (como construir)
  3. `onion-cycles.md` — Etapas e regras de todos os Ciclos de Desenvolvimento (Produto, Engenharia, KB e Sync) consolidadas em arquivo único para respeitar os limites de arquivos de contas gratuitas de IA.
- **`docs/knowledge-base/`**: Pasta para armazenar Knowledge Bases temáticas criadas pelo `@meta`.

---

## 2. Como Instalar (Guia por Plataforma)

### 💻 Cenário A: Web Chats (IA atua como Motor Lógico - Sem Escrita Direta)
Neste cenário, a IA guiará as fases de Produto e Engenharia através de respostas no chat, mas a gravação e atualização dos arquivos `.md` locais é feita manualmente por você (copiar/colar).

*   **Claude.ai (Claude Projects) [Recomendado para Web]**:
    1. Crie um novo **Project** (disponível no plano Pro/Team).
    2. Adicione o conteúdo de [`ONION-MASTER-PROMPT.md`](./ONION-MASTER-PROMPT.md) nas *Custom Instructions* do Projeto.
    3. Faça o upload dos 3 arquivos da pasta `docs/` nos *Project Files* (Knowledge).
    4. *Fluxo:* Sempre que o Claude atualizar uma especificação, copie a resposta dele e atualize os arquivos correspondentes na sua máquina.
*   **ChatGPT (Custom GPTs ou ChatGPT Projects)**:
    *   **Opção A: Custom GPTs (Geral/Persistente)**:
        1. Crie um **Custom GPT** (acessando *Explore GPTs* -> *Create*).
        2. Cole o conteúdo de [`ONION-MASTER-PROMPT.md`](./ONION-MASTER-PROMPT.md) no campo de *Instructions*.
        3. Na área de *Knowledge*, faça o upload dos 3 arquivos da pasta `docs/` para servirem de referência de regras e templates.
        4. Certifique-se de habilitar o "Code Interpreter" nas configurações para melhor raciocínio e escrita lógica.
        5. Passo a passo campo-a-campo (nome, descrição, conversation starters, capabilities) em [`GPT-SETUP.md`](./GPT-SETUP.md).
        6. GPT já publicado: [Onion Mini no ChatGPT](https://chatgpt.com/g/g-6a4bf16ff65081919bfa7d98fe28b13f-onion-mini).
    *   **Opção B: ChatGPT Projects (Ideal para Repositórios/Times)**:
        1. Crie um **Project** (disponível para contas Team/Enterprise).
        2. Nas *Custom Instructions* do projeto, insira o conteúdo do [`ONION-MASTER-PROMPT.md`](./ONION-MASTER-PROMPT.md).
        3. Faça o upload dos 3 arquivos da pasta `docs/` e de qualquer outro código relevante do repositório em *Files* do projeto.
        4. O histórico de conversas e os arquivos compartilhados no projeto manterão o alinhamento de forma simplificada.
*   **Gemini (Advanced / Gems)**:
    1. Crie uma **Gem** personalizada.
    2. Cole o conteúdo de [`ONION-MASTER-PROMPT.md`](./ONION-MASTER-PROMPT.md) nas instruções da Gem.
    3. Anexe os 3 arquivos de contexto `docs/` na conversa inicial para dar o ponto de partida do seu projeto.

---

### ⚙️ Cenário B: IDEs Agênticas (Escrita Direta no Sistema de Arquivos)
Neste cenário, a própria IDE lerá e atualizará os arquivos de contexto de forma autônoma. Você não precisa copiar e colar nada, apenas aprovar as alterações.

*   **✅ Caminho rápido — qualquer IDE com suporte a `AGENTS.md` (Codex, Cursor, Copilot, Zed, Aider, Gemini CLI...):**
    1. Copie `AGENTS.md`, `CLAUDE.md`, `ONION-MASTER-PROMPT.md` e a pasta `docs/` para a raiz do seu projeto.
    2. Pronto — o agente auto-descobre o `AGENTS.md` (e o Claude Code lê o `CLAUDE.md`, que o importa via `@AGENTS.md`). As instruções por IDE abaixo são **fallback** para ambientes sem esse suporte.

*   **Antigravity IDE [Recomendado para Agentes Autônomos]**:
    1. Cole a pasta `docs/` na raiz do seu projeto.
    2. Coloque o arquivo [`ONION-MASTER-PROMPT.md`](./ONION-MASTER-PROMPT.md) na pasta `.agents/rules/` (ou importe-o como regra global da IDE).
    3. A IA gerenciará as fases e fará a gravação direta dos arquivos de contexto no disco.
*   **Cursor (Cursor Agents / `.cursorrules`)**:
    1. Cole a pasta `docs/` na raiz do seu projeto.
    2. Cole o conteúdo de [`ONION-MASTER-PROMPT.md`](./ONION-MASTER-PROMPT.md) dentro de um arquivo chamado `.cursorrules` na raiz do seu repositório (ou use o chat do Cursor referenciando-o).
*   **GitHub Copilot (VS Code / JetBrains - Copilot Edits)**:
    1. Cole a pasta `docs/` na raiz do seu projeto.
    2. No chat do **Copilot Edits** (modo agente), adicione os arquivos de contexto da pasta `docs/` e o [`ONION-MASTER-PROMPT.md`](./ONION-MASTER-PROMPT.md) na lista de arquivos em contexto.
    3. Instrua a IA a seguir rigorosamente as personas e etapas detalhadas no prompt.
*   **Claude Code / Cowork**:
    1. Cole a pasta `docs/` na raiz do seu projeto.
    2. Copie `CLAUDE.md` + `AGENTS.md` para a raiz (o Claude Code lê o `CLAUDE.md`, que importa o `AGENTS.md` — nada de pastas especiais).
    3. O agente CLI do Claude Code lerá os arquivos de ciclo e o contexto técnico/negócio para planejar e executar a escrita do código.
*   **Zed (Zed AI / Assistants)**:
    1. Cole a pasta `docs/` na raiz do seu projeto.
    2. Adicione o conteúdo do [`ONION-MASTER-PROMPT.md`](./ONION-MASTER-PROMPT.md) como prompt de sistema ou insira nas instruções do assistente do Zed.
    3. Use o editor Zed AI com suporte a escrita e alteração de múltiplos arquivos de contexto em disco.


---

## 3. Como usar no dia a dia (O Ciclo de Vida)

O Onion Mini não é um gerador de código descontrolado. Ele segue regras estritas. Aqui estão os gatilhos e fluxos que você deve usar na conversa com a IA:

### 💡 Criando algo novo (O Ciclo de Produto)
- **O que você diz:** *"Tive uma ideia: quero colocar uma funcionalidade de exportar para PDF."*
- **O que a IA faz:** Ativa a persona `@product`, faz perguntas para entender o negócio, gera as especificações e atualiza o `business-context-lite.md`.
  - No **Cenário B**, a IA edita o arquivo diretamente.
  - No **Cenário A**, a IA gera o markdown e pede para você salvar localmente.
- *(Nunca peça código nesta fase!)*

### ⚙️ Desenvolvendo a ideia (O Ciclo de Engenharia)
- **O que você diz:** *"O produto está especificado, pode iniciar o trabalho do @engineer."*
- **O que a IA faz:** Lê as especificações, cria um plano arquitetural passo a passo no `technical-context-lite.md`. Depois que você aprovar, ela gera o código.
  - No **Cenário B**, a IA cria/edita os arquivos de código diretamente no projeto.
  - No **Cenário A**, a IA gera blocos de código para você colar.

### 📚 Estudando algo novo (O Ciclo de Knowledge Base)
- **O que você diz:** *"Atue como @meta e faça uma pesquisa sobre o framework Tailwind. Crie uma KB para nós."*
- **O que a IA faz:** Estuda o assunto e gera um Markdown mastigado.
  - No **Cenário B**, a IA salva em `docs/knowledge-base/[nome-do-tema].md` diretamente.
  - No **Cenário A**, a IA gera o bloco e pede para você salvar no mesmo caminho.

### 🔄 Lidando com Código Legado (O Ciclo de Sincronismo)
- **O que você diz:** *"Atue como @docs e faça engenharia reversa do projeto."*
- **O que a IA faz:** Lê seu código e infere automaticamente o Produto e a Engenharia.
  - No **Cenário B**, a IA lê o código diretamente do filesystem e atualiza os contextos.
  - No **Cenário A**, a IA pede que você cole o código e depois gera os documentos.

---

## ⚠️ Regra de Ouro: Como os arquivos são salvos?

Como o Onion lida com a documentação depende inteiramente do seu ambiente:

**Se você está em um Web Chat restrito (Cenário A):**
Como a IA não pode editar seus arquivos locais diretamente, a entrega de múltiplos arquivos se adapta dinamicamente à plataforma utilizada:
*   **ChatGPT (com Code Interpreter):** A IA cria a estrutura de pastas internamente e gera um arquivo `.zip` para você baixar e descompactar na raiz do seu projeto.
*   **Claude (com Artifacts):** A IA disponibiliza os arquivos em blocos de artefatos interativos individuais para fácil download.
*   **Outros Chats (como Gemini):** A IA gera o conteúdo `.md` completo dentro de blocos de código separados. Sua tarefa é copiar e salvar nos caminhos indicados.
*   *Resumo:* A IA sempre acompanhará a entrega com um resumo sintético rápido para facilitar a leitura das alterações.

**Se você está em uma IDE Agêntica (Cenário B — Antigravity, Cursor):**
Você não precisa copiar nada! A IA tem permissão de escrita. Ela vai te mostrar o que planeja fazer, pedir a sua confirmação e, uma vez aprovada, **ela mesma vai editar e gravar o arquivo diretamente no seu projeto.** Apenas relaxe e deixe o motor trabalhar.

---

## 🛡️ O Guardião do Fluxo (Auto-Consciência & Diagnóstico)

Para garantir que o desenvolvimento siga o padrão Spec-as-Code de forma consistente, o Onion possui regras integradas de auto-monitoramento:

*   **Bloqueio de Bypass:** Se você pedir código diretamente sem antes especificar o Produto ou planejar a Engenharia, a IA fará um alerta de auto-consciência lembrando-o de seguir as fases necessárias para manter a qualidade e o sincronismo.
*   **Auto-Diagnóstico (`/status` ou `/health`):** A qualquer momento no chat, você pode digitar `/status` ou `/health`. A IA fará uma varredura completa nas pastas do projeto, validando se a documentação e o código real estão alinhados, retornando um status de saúde do Onion (OK, Desalinhado ou Incompleto) e as ações corretivas.
*   **Chamada por Comando ("Onion" ou `@onion`):** Ao chamar por "Onion" ou digitar `@onion` no chat, você sinaliza explicitamente para o Orquestrador assumir a liderança ativa, analisar o estado atual da conversa e do projeto, e propor o próximo passo lógico ou executar tarefas de sincronização/diagnóstico de forma autônoma.

---

## Quando o projeto crescer: o Sistema Onion completo

O Onion Mini é a porta de entrada. Quando seu projeto precisar de mais — 95+ comandos, 51 agentes
especialistas, compliance (ISO/SOC2), task managers plugados de verdade (Jira/ClickUp/Asana/Linear
via SDAAL), knowledge graphs de investigação, federação multi-repo — o caminho natural é a adoção
do [Sistema Onion completo](https://onionevolve.com) (plataforma: Claude Code). Tudo que você
construiu aqui (contextos SSOT, ciclos, sessões) migra sem retrabalho: o Mini é a mesma
metodologia, só que destilada.

## Publicação (web)

Vitrine pública em **https://onionevolve.com/mini/** (VPS do Onion, Caddy file_server).
Fonte = `site/index.html` deste repo (design system herdado do site); webroot é derivado.
Deploy: `rsync -a --delete site/ onion-vps:/var/www/onion-landing/mini/` após commit na main.

## Créditos

- O motor Planejar→Executar→Avaliar é baseado no modelo **PLEA** de **Pedro Rosário** (Autorregulação
  da Aprendizagem, Universidade do Minho); a adaptação aos ciclos é do Sistema Onion. Por desenho, o
  nome da teoria assina AQUI (créditos) e desaparece no fluxo — o usuário pratica sem precisar do jargão.
- O Onion Mini é a **destilação curada** do [Sistema Onion](https://onionevolve.com) — doutrina
  flui do core para cá por co-evolução; este repo nunca vira cópia do framework completo.
