# Contexto Técnico: Griô Local

## 1. Tecnologias Utilizadas

*   **Linguagem de Programação:** Python (versão 3.x)
*   **Interface Gráfica (UI):**
    *   `tkinter`: Biblioteca padrão do Python para criação de GUIs. Usada para a janela principal, botões de controle (Iniciar/Parar Griô), área de status e log de eventos.
*   **Captura de Áudio:**
    *   `sounddevice`: Biblioteca para gravação e reprodução de áudio com PortAudio. Usada para capturar áudio do microfone em tempo real.
*   **Reconhecimento de Fala (STT - Speech-to-Text):**
    *   `vosk`: Toolkit de reconhecimento de fala offline. Utiliza modelos de linguagem pré-treinados (atualmente configurado para português brasileiro, com um modelo pequeno e a opção de um maior).
*   **Reprodução de Áudio (Efeitos e Trilhas):**
    *   `pygame` (especificamente `pygame.mixer`): Biblioteca popular para desenvolvimento de jogos, usada aqui por suas capacidades robustas de mixagem e reprodução de áudio. Permite múltiplos canais, looping, e controle de volume.
*   **Manipulação de Dados e Configuração:**
    *   `json`: Biblioteca padrão para manipulação de arquivos JSON, usada para carregar e parsear o `mapeamento_eventos.json`.
    *   `queue`: Módulo padrão para implementação de filas, usado para comunicação assíncrona entre a thread de captura de áudio e a thread de processamento do Vosk.
    *   `threading`: Módulo padrão para trabalhar com múltiplas threads, essencial para manter a UI responsiva enquanto o processamento de áudio e STT ocorrem em segundo plano.
    *   `os`: Módulo padrão para interações com o sistema operacional, principalmente para construção de caminhos de arquivo de forma dinâmica e verificação de existência de arquivos/diretórios.
    *   `time`: Módulo padrão, usado para delays (ex: `time.sleep()`) em alguns pontos e para testes.

## 2. Configuração do Ambiente de Desenvolvimento

*   **Python:** Uma instalação Python 3.x é necessária.
*   **Bibliotecas (instaladas via pip):**
    *   `vosk`
    *   `sounddevice`
    *   `pygame`
    *   (Tkinter, json, queue, threading, os, time são geralmente incluídos na instalação padrão do Python)
*   **Modelo Vosk:**
    *   Download de um modelo de linguagem Vosk para português (ex: `vosk-model-small-pt-0.3` ou `vosk-model-pt-fb-v0.1.1-pruned`).
    *   O modelo deve ser descompactado e colocado no diretório `modelos_vosk/` (ou `modelos_vosk_Maior/`) na raiz do projeto.
*   **Arquivos de Som:**
    *   Efeitos sonoros na pasta `sons/efeitos/`.
    *   Trilhas sonoras na pasta `sons/trilhas/`.
*   **Arquivo de Mapeamento:**
    *   `config/mapeamento_eventos.json` deve existir e estar formatado corretamente.

## 3. Estrutura de Diretórios do Projeto (Simplificada)

```
PROJETO_GRIO_LOCAL/
│
├── src/                             # Código fonte Python
│   ├── grio_main.py               # Ponto de entrada principal, UI, lógica central
│   ├── reprodutor_audio.py        # Módulo para tocar sons com Pygame
│   └── captura_e_stt.py           # Script de teste/exemplo (não diretamente importado por grio_main)
│
├── config/                          # Arquivos de configuração
│   └── mapeamento_eventos.json    # Define gatilhos e sons
│
├── modelos_vosk/                    # Modelos de linguagem Vosk (pequeno)
│   └── vosk-model-small-pt-0.3/   # Exemplo de pasta de modelo
│       └── ... (arquivos do modelo)
│
├── modelos_vosk_Maior/              # Modelos de linguagem Vosk (grande, opcional)
│   └── vosk-model-pt-fb-v0.1.1-pruned/ # Exemplo
│       └── ...
│
├── sons/
│   ├── efeitos/                     # Arquivos de efeitos sonoros (ex: .wav, .mp3)
│   │   └── exemplo_efeito.wav
│   └── trilhas/                     # Arquivos de trilhas sonoras (ex: .wav, .mp3)
│       └── exemplo_trilha.mp3
│
├── memory-bank/                     # Documentação (ESTA PASTA)
│   ├── projectbrief.md
│   ├── productContext.md
│   ├── activeContext.md
│   ├── systemPatterns.md
│   ├── techContext.md
│   └── progress.md
│
├── DOCUMENTACAO/                    # Documentação original do usuário
│   └── Documentacao_Grio_Local.md
│
└── (outros arquivos como .gitignore, venv, etc.)
```

## 4. Processo de Build e Empacotamento (Alvo: .exe)

*   **Ferramenta a ser definida:** PyInstaller é o candidato principal. auto-py-to-exe (GUI para PyInstaller), cx_Freeze ou Nuitka são alternativas.
*   **Passos Gerais (a serem detalhados):**
    1.  Instalar a ferramenta de empacotamento (ex: `pip install pyinstaller`).
    2.  Executar a ferramenta apontando para o script principal (`src/grio_main.py`).
    3.  **Gerenciamento de Ativos:** Configurar a ferramenta para incluir:
        *   Os diretórios dos modelos Vosk (`modelos_vosk/`, `modelos_vosk_Maior/`).
        *   O diretório de sons (`sons/`).
        *   O arquivo de configuração (`config/mapeamento_eventos.json`).
        *   Quaisquer DLLs ou dependências específicas que não sejam automaticamente detectadas (ex: DLLs do PortAudio se necessário).
    4.  **Ajustes de Caminho no Código:** Pode ser necessário modificar como os caminhos para esses ativos são resolvidos no código para que funcionem corretamente quando o script é executado como um arquivo congelado (empacotado). Uma abordagem comum com PyInstaller é usar `sys._MEIPASS` para referenciar arquivos incluídos no pacote.
    5.  **Opções de Build:**
        *   `--onefile` vs. `--onedir`: Criar um único executável ou um diretório com o executável e suas dependências.
        *   `--windowed` (ou `--noconsole`): Para aplicações GUI, para não abrir uma janela de console.
        *   Adicionar dados/arquivos (`--add-data` para PyInstaller).
    6.  Testar o executável gerado em um ambiente limpo.

## 5. Considerações Técnicas e Desafios

*   **Tamanho do Modelo Vosk:** Os modelos de linguagem podem ser grandes, o que impactará o tamanho final do executável. O modelo "pequeno" é preferível para um download/distribuição mais fácil, mas pode ter precisão menor.
*   **Dependências de Bibliotecas Nativas:** `sounddevice` (via PortAudio) e `pygame` podem ter dependências de bibliotecas C/C++ que precisam ser corretamente empacotadas.
*   **Resolução de Caminhos em Tempo de Execução (Empacotado):** A maior dificuldade técnica no empacotamento de aplicações Python é garantir que todos os arquivos de dados (modelos, sons, configs) sejam encontrados pelo executável. O diretório de trabalho e `__file__` se comportam de maneira diferente.
*   **Performance:** O reconhecimento de fala pode ser intensivo em CPU. A performance em máquinas mais antigas precisa ser considerada, embora o foco seja em funcionalidade primeiro.
*   **Tratamento de Erros:** Robustez no tratamento de erros (ex: microfone não encontrado, arquivo de som ausente, modelo Vosk corrompido) é importante para a experiência do usuário.

## 6. Possíveis Melhorias Futuras (Técnicas)

*   Permitir seleção de dispositivo de áudio (microfone) na UI.
*   Interface para edição do `mapeamento_eventos.json` diretamente na UI.
*   Otimização do carregamento de modelos ou sons.
*   Criação de um instalador (ex: Inno Setup) para uma melhor experiência de instalação. 