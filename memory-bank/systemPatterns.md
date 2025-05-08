# Padrões do Sistema: Griô Local

## 1. Arquitetura Geral

O Griô Local segue uma arquitetura modular baseada em Python, projetada para operar de forma independente e offline. Os componentes principais interagem da seguinte forma:

```mermaid
graph TD
    A[Usuário] -->|Interage com| UI(Interface Tkinter)
    UI -->|Inicia/Para| Core(Loop Principal Griô - grio_main.py)
    
    subgraph Core
        B[Captura de Áudio (sounddevice)] -->|Dados de áudio| Q(Fila de Áudio - queue.Queue)
        Q --> C[Reconhecimento de Fala (Vosk)]
        C -->|Texto Reconhecido| D[Lógica de Processamento de Eventos]
        D -->|Consulta| E[Mapeamento de Eventos (JSON)]
        D -->|Comandos de Áudio| F[Reprodutor de Áudio (pygame.mixer)]
    end

    F -->|Saída de Som| G[Alto-falantes]
    Core -->|Logs e Status| UI
```

**Fluxo de Dados e Controle:**

1.  **Interface do Usuário (UI - Tkinter):**
    *   Permite ao usuário iniciar e parar o sistema Griô.
    *   Exibe logs de eventos e o status atual do sistema.
    *   Executa o loop principal do Griô em uma thread separada para não bloquear a UI.
2.  **Loop Principal Griô (`grio_main.py`):
    *   Gerencia o ciclo de vida da captura de áudio e do reconhecimento de fala.
    *   Inicializa e coordena os outros módulos.
    *   Contém a lógica para carregar o modelo Vosk e o arquivo de mapeamento de eventos.
3.  **Captura de Áudio (`sounddevice`):
    *   Configurado para capturar áudio do microfone padrão (ou dispositivo especificado).
    *   Usa um callback (`audio_callback_global`) para colocar os blocos de dados de áudio crus em uma fila (`q_audio`).
4.  **Fila de Áudio (`queue.Queue`):
    *   Atua como um buffer entre a thread de captura de áudio e a thread de processamento do Vosk, desacoplando-as.
5.  **Reconhecimento de Fala (Vosk):
    *   Consome dados da fila de áudio.
    *   Utiliza um modelo de linguagem treinado (português) para converter a forma de onda de áudio em texto.
    *   Pode fornecer resultados parciais e finais.
6.  **Lógica de Processamento de Eventos (`processar_eventos_logica` em `grio_main.py`):
    *   Recebe o texto reconhecido pelo Vosk.
    *   Compara o texto (em minúsculas) com os "gatilhos" definidos no arquivo `mapeamento_eventos.json`.
    *   Se um gatilho é encontrado, aciona as ações correspondentes (parar trilha, tocar nova trilha, tocar efeitos).
7.  **Mapeamento de Eventos (JSON - `mapeamento_eventos.json`):
    *   Arquivo de configuração externo que define a relação entre frases/palavras gatilho e as ações sonoras (arquivos de áudio, looping, volume, etc.).
8.  **Reprodutor de Áudio (`reprodutor_audio.py` usando `pygame.mixer`):
    *   Responsável por carregar e reproduzir arquivos de trilha sonora e efeitos sonoros.
    *   Gerencia canais de áudio para permitir a reprodução simultânea de múltiplos efeitos e uma trilha de fundo.
    *   Suporta looping de efeitos sonoros com IDs específicos e controle de volume individual.
    *   Utiliza um cache para efeitos sonoros já carregados para otimizar o desempenho.

## 2. Padrões de Design Chave

*   **Produtor-Consumidor (com Fila):** A captura de áudio (produtor) e o reconhecimento de fala (consumidor) são desacoplados por uma fila (`q_audio`). Isso ajuda a lidar com as diferentes taxas de processamento e evita o bloqueio da captura de áudio.
*   **Threading:** A interface gráfica (Tkinter) roda na thread principal, enquanto o loop principal do Griô (que inclui captura de áudio, STT e processamento de eventos) roda em uma thread separada (`threading.Thread`). Isso mantém a UI responsiva.
    *   Atualizações da UI a partir da thread do Griô são feitas usando `root.after(0, callback)` para garantir a segurança da thread com Tkinter.
*   **Baseado em Eventos (Simplificado):** A lógica central reage a "eventos" de fala que correspondem a gatilhos predefinidos.
*   **Configuração Externa:** O comportamento dos eventos sonoros é definido em um arquivo JSON externo (`mapeamento_eventos.json`), permitindo customização sem alterar o código Python. Isso é um tipo de padrão de Estratégia ou Tabela de Decisão, onde as regras são externalizadas.
*   **Módulos Coesos:** O código é organizado em módulos com responsabilidades relativamente claras: `grio_main.py` (orquestração e UI), `reprodutor_audio.py` (lógica de som), `captura_e_stt.py` (script autônomo de teste, não diretamente usado por `grio_main` mas demonstra os componentes). *Nota: A lógica de captura e STT está integrada em `grio_main.py` para a aplicação principal.*
*   **Gerenciamento de Estado da UI:** A UI é atualizada (botões ativados/desativados, rótulos de status) com base no estado interno da flag `rodando_grio_flag`.
*   **Limpeza de Recursos:** O sistema tenta gerenciar o ciclo de vida dos recursos, como o stream de áudio (`sd.InputStream`), o mixer do Pygame, e a thread do Griô, especialmente durante as operações de parada e ao fechar a janela.
    *   Uso de `try...finally` para garantir que o stream de áudio seja fechado.
    *   Uso de "poison pill" (enviando `None` para a fila `q_audio`) para sinalizar à thread do Griô que ela deve terminar seu loop de processamento.

## 3. Tratamento de Concorrência

*   **Thread Principal:** Executa a interface gráfica Tkinter.
*   **Thread Griô:** Executa o `_loop_principal_grio` que lida com:
    *   Carregamento do modelo Vosk.
    *   Abertura e gerenciamento do stream de áudio `sounddevice`.
    *   Loop de obtenção de dados da `q_audio`.
    *   Chamada ao `recognizer.AcceptWaveform()`.
    *   Chamada ao `processar_eventos_logica()`.
*   **Thread de Callback do `sounddevice`:** Adiciona dados de áudio à `q_audio` de forma assíncrona.
*   **Comunicação UI -> Thread Griô:** Principalmente através da flag `rodando_grio_flag` (para sinalizar parada) e do envio do "poison pill" para `q_audio`.
*   **Comunicação Thread Griô -> UI:** Através de `self.root.after(0, lambda: ...)`, para enfileirar atualizações da UI (como adicionar logs ou mudar status) para serem executadas pela thread principal da Tkinter.

## 4. Gerenciamento de Dependências e Ativos

*   **Modelo Vosk:** É uma dependência externa crucial, armazenada localmente na pasta `modelos_vosk/` (ou `modelos_vosk_Maior/`). O caminho para o modelo é construído dinamicamente.
*   **Arquivos de Som:** Localizados nas subpastas `sons/efeitos/` e `sons/trilhas/`. Os caminhos também são construídos dinamicamente.
*   **Arquivo de Mapeamento:** `config/mapeamento_eventos.json`.
*   **Desafio para Empacotamento:** Garantir que todos esses ativos (modelos, sons, JSON) sejam incluídos corretamente no executável final e que os caminhos sejam resolvidos adequadamente no ambiente empacotado. 