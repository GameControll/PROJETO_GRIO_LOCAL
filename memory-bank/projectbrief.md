# Project Brief: Griô Local

## 1. Visão Geral do Projeto

O Griô Local é um sistema de software projetado para enriquecer a experiência de narração de histórias ou leitura em voz alta. Ele escuta a fala do usuário em tempo real e, com base no conteúdo semântico detectado, dispara trilhas sonoras e efeitos sonoros correspondentes. O sistema opera inteiramente offline, garantindo privacidade e acessibilidade em ambientes sem conexão com a internet.

## 2. Objetivos Principais

*   **Leitura com Áudio Dinâmico Semântico:** Permitir que a narração de histórias seja acompanhada por uma paisagem sonora que reage dinamicamente ao conteúdo da fala.
*   **Operação Offline:** Garantir que todas as funcionalidades principais (captura de áudio, reconhecimento de fala, processamento de eventos e reprodução de áudio) ocorram localmente na máquina do usuário, sem dependência de servidores externos ou conexão com a internet.
*   **Interface de Usuário Simples:** Fornecer uma interface gráfica intuitiva (atualmente Tkinter) para iniciar e parar o sistema Griô.
*   **Customização de Eventos:** Permitir a definição de eventos sonoros (gatilhos de fala, trilhas e efeitos) através de um arquivo de mapeamento configurável (JSON).
*   **Portabilidade:** O objetivo atual (conforme esta interação) é empacotar o projeto como um executável (`.exe`) para fácil distribuição e uso em máquinas Windows.

## 3. Escopo do Projeto (Versão Local Atual)

*   **Módulo de Captura de Áudio:** Utilização de `sounddevice` para capturar áudio do microfone.
*   **Módulo de Reconhecimento de Fala (STT):** Utilização do `Vosk` para transcrição de fala para texto offline.
*   **Módulo de Lógica de Eventos:** Processamento do texto reconhecido para identificar gatilhos definidos no arquivo de mapeamento e acionar as ações sonoras correspondentes.
*   **Módulo Reprodutor de Áudio:** Utilização do `pygame.mixer` para tocar trilhas sonoras e efeitos sonoros.
*   **Arquivo de Mapeamento de Eventos:** Um arquivo JSON (`mapeamento_eventos.json`) que define os gatilhos de fala e os arquivos de áudio associados.
*   **Interface Gráfica (UI):** Uma interface básica construída com `Tkinter` para controle do sistema.
*   **Empacotamento:** Criação de um executável `.exe` para distribuição.

## 4. Critérios de Sucesso (Iniciais)

*   O sistema consegue capturar áudio do microfone.
*   O sistema transcreve a fala em texto com precisão razoável usando o modelo Vosk configurado.
*   O sistema identifica corretamente os gatilhos de fala definidos no arquivo de mapeamento.
*   O sistema reproduz as trilhas sonoras e efeitos sonoros especificados quando os gatilhos são detectados.
*   A interface gráfica permite iniciar e parar o Griô de forma confiável.
*   O projeto pode ser compilado em um arquivo `.exe` funcional.
*   O sistema opera 100% offline.

## 5. Stack Tecnológico Principal (Versão Local)

*   **Linguagem:** Python
*   **Reconhecimento de Fala:** Vosk
*   **Captura de Áudio:** sounddevice
*   **Reprodução de Áudio:** Pygame (pygame.mixer)
*   **Interface Gráfica:** Tkinter
*   **Formato de Configuração:** JSON
*   **Empacotamento (Alvo):** PyInstaller ou similar para criar `.exe`

## 6. Partes Interessadas

*   Usuário (Narrador/Leitor)
*   Desenvolvedor(es) (Nós) 