## ✅ PROJETO GRIÔ (VERSÃO LOCAL)

## ✅ CONCEITO: Leitura com Áudio Dinâmico Semântico (modo leitura em voz alta)

---

### 🌟 PROPÓSITO

Permitir que qualquer pessoa **conte ou leia uma história em voz alta**, enquanto um sistema local (Griô) **ouve a narração em tempo real** e **dispara trilhas sonoras e efeitos sonoros** com base no conteúdo semântico da fala — tudo rodando **localmente na máquina**, sem conexão com servidores externos.

---

### 🥉 EXPERIÊNCIA DO USUÁRIO (UX)

1. O usuário executa o aplicativo local na sua máquina (via terminal ou interface simples).
2. Ao iniciar, o sistema já escuta o microfone automaticamente.
3. Quando estiver pronto para ler ou contar sua história, **fala naturalmente**.
4. O sistema (Griô) **ouve em tempo real usando Vosk + sounddevice**.
5. Com base no que é falado, o sistema **detecta eventos, ações ou climas narrativos**, e **dispara efeitos sonoros e trilhas automáticas**.
6. A experiência acontece **sem delay de rede e sem necessidade de internet**.

---

### ⚙️ MÓDULOS DO SISTEMA (Griô Local)

| Módulo                           | Função                                                                    |
| -------------------------------- | ------------------------------------------------------------------        |
| **Captura de áudio**             | Usa `sounddevice` para ouvir o microfone em tempo real                    |
| **Reconhecimento de fala (STT)** | Usa `Vosk` local para converter fala em texto offline                     |
| **Analisador semântico**         | Detecta contextos por palavras/frases e ativa áudio correspondente        |
| **Reprodutor de áudio**          | Usa `pygame.mixer` para tocar efeitos simultaneaos com trilhas sonoras    |
| **JSON de mapeamento**           | Lista eventos semânticos com seus gatilhos e sons                         |
| **Interface CLI ou Tkinter**     | Interface opcional simples para iniciar/parar o sistema                   |

---

### 🧠 EXEMPLOS DE EVENTOS SEMÂNTICOS DETECTADOS

```json
{
  "evento": "invasao",
  "gatilhos": ["explodiu", "gritaram", "os soldados chegaram", "a tropa invadiu", "tiros", "alarme"],
  "sons": ["explosion_01.mp3", "alarm_loop.mp3", "gunfire.mp3", "chaos_theme.mp3"]
}
```

---

### ✅ DIFERENCIAIS DO PRODUTO LOCAL

* **100% offline**: não depende de internet ou servidores.
* Funciona com **qualquer história falada ou lida**.
* **Privacidade total**: nada é enviado para fora da máquina.
* Leve, rápido e responsivo.
* Ideal para ambientes sem rede (escolas, treinamentos, etc).

---

### 🔒 PRIVACIDADE E FLUXO

* Nenhum dado é armazenado ou enviado.
* Todos os sons são tocados localmente.
* O sistema atua como maestro sonoro, totalmente autônomo e local.


🧱 ESTRUTURA GERAL DO PROJETO

┌──────────────┐
│   Frontend   │
├──────────────┤
│  React (Web) │   → Web app: roda no navegador
│React Native  │   → App mobile (Android/iOS)
└────┬─────────┘
     ↓
┌──────────────┐
│   Backend    │
├──────────────┤
│  Node.js     │ → API REST/GraphQL, orquestra lógica
│  Express.js  │ → Gerencia rotas, autenticação etc.
│  Vosk (STT)  │ → Reconhecimento de fala (em voz alta)
└────┬─────────┘
     ↓
┌──────────────┐
│Banco de Dados│
├──────────────┤
│ Local        │ → soundTracks e soundeffects.
│              │   
└──────────────┘
🔧 JUSTIFICATIVA DE CADA TECNOLOGIA
Camada	Tecnologia	Por que usar?
Frontend Web	React	Alto desempenho, fácil integração com áudio e microfone via Web APIs, responsivo.
Frontend Mobile	React Native	Compartilha código com React web, compila para Android/iOS, controle nativo de microfone e player de áudio.
Backend	Node.js + Express	Leve, escalável, ideal para APIs. Excelente para lidar com áudio, websockets (tempo real), e integrações com Vosk.
Reconhecimento	Vosk (via Node.js bridge ou microserviço Python)	Funciona offline e online, suporte a múltiplos idiomas, preciso e leve.
Banco de Dados	MongoDB	Flexível, orientado a documentos, ideal para armazenar trechos de livros, configurações de trilhas por usuário, etc.
Hospedagem	Vercel / Firebase / Render / Railway	Fáceis de usar, suporte a deploy contínuo e escalável, boa para apps públicos.

🔄 FLUXO DO USUÁRIO (modo leitura em voz alta)
Usuário abre app web ou mobile (React ou React Native)

Permite acesso ao microfone

O app envia o áudio para o backend (via WebSocket)

O backend (Node.js) processa o áudio com Vosk

O texto reconhecido é comparado com os arquivos de soundtrack e soundeffects

O sistema ativa trilhas sonoras e efeitos sincronizados

O áudio é reproduzido localmente via fone ou alto-falante

🧠 BENEFÍCIOS DESSA ARQUITETURA
Código reutilizável (lógica de leitura/controle compartilhada)

Escalável (backend desacoplado do frontend)

Compatível com offline e online

Fácil de testar, manter e hospedar

