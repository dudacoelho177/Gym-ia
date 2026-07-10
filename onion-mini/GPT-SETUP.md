# Como montar o Custom GPT "Onion Mini" no ChatGPT

> ✅ **Já criado**: [chatgpt.com/g/g-6a4bf16ff65081919bfa7d98fe28b13f-onion-mini](https://chatgpt.com/g/g-6a4bf16ff65081919bfa7d98fe28b13f-onion-mini)
> (2026-07-06). Este guia continua valendo como referência para qualquer edição futura — o GPT
> Builder é uma tela autenticada da OpenAI; ninguém edita esse GPT por fora do próprio ChatGPT.

Guia complementar ao [`README.md`](./README.md) §2 (Cenário A → ChatGPT → Custom GPTs) — aqui vai o
conteúdo exato de cada campo do GPT Builder, pronto para copiar. Nenhum arquivo novo de conteúdo é
necessário: o **system prompt** já existe em [`ONION-MASTER-PROMPT.md`](./ONION-MASTER-PROMPT.md) e
os **arquivos de conhecimento** já existem em [`docs/`](./docs/) — este guia só reúne onde cada um
entra no formulário do ChatGPT, para você não precisar adivinhar.

## Passo a passo (chatgpt.com → Explore GPTs → Create → aba "Configure")

### 1. Name
```
Onion Mini
```

### 2. Description
Copie e ajuste se quiser (limite prático do GPT Store: ~300 caracteres):
```
A versão mini e portátil do Sistema Onion: metodologia Spec-as-Code (Produto → Engenharia,
documentado antes do código) para quem está começando a desenvolver com IA. Roda 100% no chat,
sem instalar nada. Guia você do zero até o primeiro código, sempre planejar → executar → avaliar.
```

### 3. Instructions
**Abra [`ONION-MASTER-PROMPT.md`](./ONION-MASTER-PROMPT.md) e copie o conteúdo inteiro do arquivo**
para este campo. Não copiamos o texto aqui dentro deste guia para não criar uma segunda cópia que
fica desatualizada — o arquivo é a única fonte. Ele cabe tranquilo no limite de 8.000 caracteres do
campo Instructions (tem ~6.500).

Sempre que o `ONION-MASTER-PROMPT.md` for atualizado no repositório, volte aqui e cole a versão nova
— o campo Instructions do GPT não se atualiza sozinho.

### 4. Conversation starters
```
Quero começar um projeto do zero com o Onion
Já tenho um projeto com código — quero sincronizar com o Onion
Qual o status do meu projeto agora?
Preciso de uma Knowledge Base sobre um tema técnico
```

### 5. Knowledge — upload estes 3 arquivos de `docs/`
- [`docs/business-context-lite.md`](./docs/business-context-lite.md)
- [`docs/technical-context-lite.md`](./docs/technical-context-lite.md)
- [`docs/onion-cycles.md`](./docs/onion-cycles.md)

Eles chegam como **templates vazios** — é assim mesmo. O GPT vai preenchendo o conteúdo *durante a
conversa* (ver "Persistência" abaixo); os arquivos de Knowledge servem para ele conhecer o formato e
as regras dos 5 ciclos desde a primeira mensagem.

### 6. Capabilities
| Capacidade | Estado | Por quê |
|---|---|---|
| **Code Interpreter & Data Analysis** | ✅ Ligado | Obrigatório — é o que o prompt usa (§4) para gerar o `.zip` com os arquivos de contexto quando você quiser salvar o progresso. |
| **Web Browsing** | ✅ Ligado (recomendado) | A persona `@meta` (§1) pesquisa temas técnicos para gerar Knowledge Bases — sem isso ela fica limitada ao que já sabe. Desligue se preferir um GPT mais previsível/offline. |
| **DALL·E Image Generation** | ❌ Desligado | Não faz parte do fluxo; deixar ligado só distrai o modelo com uma ferramenta irrelevante. |
| **Actions** | — | Nenhuma necessária nesta versão. |

### 7. Visibilidade
Em "Only me" enquanto testa. Se quiser publicar (como o GPT **Onion Pulse**, já usado no Pulse Mais),
troque para "Anyone with a link" ou liste no GPT Store — nenhuma mudança de conteúdo é necessária
para isso, é só a configuração de compartilhamento do próprio ChatGPT.

---

## Como funciona a persistência entre conversas (importante)

Diferente de uma IDE (Cenário B do README), o ChatGPT **não reescreve os arquivos de Knowledge**
durante a conversa — eles ficam estáticos, do jeito que foram enviados na criação do GPT. Isso muda
como o passo "5. Retomada de Sessão" do master prompt funciona na prática:

- **Numa conversa nova**, o Onion Mini não tem como saber sozinho o que você já decidiu numa
  conversa anterior — ele só vê os templates vazios do Knowledge.
- **Para retomar de verdade**: no início da conversa, cole (ou anexe como arquivo) o conteúdo atual
  de `business-context-lite.md` e `technical-context-lite.md` salvos na sua máquina. O prompt já
  espera isso — é o mesmo fluxo do "Cenário A" descrito no README.
- **Para salvar o progresso**: peça para o Onion Mini gerar o `.zip` (via Code Interpreter) ou
  colar os markdowns completos no chat, e guarde os arquivos localmente — eles são a sua fonte de
  verdade entre uma sessão e outra, não o Knowledge do GPT.

## Manutenção

Este guia e o GPT em si são **distribuição**, não fonte — se o comportamento do Onion Mini mudar,
a mudança acontece em [`ONION-MASTER-PROMPT.md`](./ONION-MASTER-PROMPT.md) e nos arquivos de
`docs/`; este arquivo só documenta onde colar cada um no ChatGPT.
