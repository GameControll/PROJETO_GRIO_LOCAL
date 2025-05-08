# Progresso do Projeto: Griô Local

## 1. O Que Funciona Atualmente (Com Base na Análise do Código)

*   **Interface Gráfica (Tkinter):**
    *   Janela principal com título e dimensões definidas.
    *   Botões "Iniciar Griô" e "Parar Griô" com lógica básica de ativação/desativação.
    *   Label de status para exibir o estado atual (Ocioso, Ouvindo, etc.).
    *   Área de texto rolável para exibir logs de eventos e mensagens do sistema.
    *   Manipulação do fechamento da janela com aviso se o Griô estiver ativo.
*   **Inicialização de Áudio (Pygame):**
    *   O `pygame.mixer` é inicializado (via `reprodutor_audio.py` e chamado em `grio_main.py`).
    *   Número de canais do mixer é configurado.
*   **Carregamento de Configurações:**
    *   O arquivo `mapeamento_eventos.json` é carregado e parseado.
    *   O caminho para o modelo Vosk (pequeno ou grande, baseado na flag `USAR_MODELO_GRANDE`) é determinado.
*   **Loop Principal do Griô (em Thread Separada):
    *   Modelo Vosk é carregado.
    *   Stream de áudio `sounddevice` é configurado e iniciado, com callback para popular uma fila (`q_audio`).
    *   O sistema entra em um loop para consumir dados da fila de áudio.
    *   Dados de áudio são passados para o reconhecedor Vosk.
    *   Quando o Vosk finaliza o reconhecimento de um trecho de fala:
        *   O texto reconhecido é logado na UI.
        *   A função `processar_eventos_logica` é chamada.
*   **Lógica de Processamento de Eventos:**
    *   Compara o texto reconhecido (convertido para minúsculas) com os "gatilhos" de cada evento no mapeamento.
    *   Loga a detecção de gatilhos e o acionamento de ações.
    *   Implementa ações baseadas no mapeamento:
        *   `parar_efeito_loop_id`: Chama `parar_efeito_em_loop()` do `reprodutor_audio`.
        *   `parar_trilha_atual`: Chama `parar_trilha_sonora()`.
        *   `trilha_sonora`: Chama `tocar_trilha_sonora()` com arquivo, loop e volume especificados.
        *   `efeitos_sonoros`: Itera sobre a lista e chama `tocar_efeito_sonoro()` para cada efeito, com arquivo, looping, id_loop e volume.
*   **Reprodutor de Áudio (`reprodutor_audio.py`):
    *   `inicializar_audio()`: Inicializa o mixer.
    *   `tocar_efeito_sonoro()`: Carrega (com cache) e toca efeitos. Suporta looping com `id_loop` e controle de volume. Gerencia canais para efeitos em loop através de `loops_de_efeito_ativos`.
    *   `parar_efeito_em_loop()`: Para um efeito em loop específico pelo seu ID.
    *   `tocar_trilha_sonora()`: Carrega e toca trilhas sonoras. Suporta looping e controle de volume.
    *   `parar_trilha_sonora()`: Para e descarrega a trilha atual.
    *   `definir_volume_trilha()`: Ajusta o volume da trilha sonora que está tocando.
*   **Gerenciamento de Parada:**
    *   A flag `rodando_grio_flag` é usada para sinalizar a parada para a thread do Griô.
    *   Um "poison pill" (`None`) é enviado para a `q_audio` para desbloquear `q_audio.get()` e permitir que a thread finalize.
    *   Tentativas de `join` na thread do Griô com timeout.
    *   Limpeza de recursos como parada da trilha sonora, e desinicialização do `pygame.mixer` e `pygame` ao parar ou fechar.
    *   O stream de áudio (`self.current_stream`) é abortado e fechado no `finally` do loop da thread.
    *   A fila `q_audio` é esvaziada.

## 2. O Que Falta Construir / Próximas Tarefas (Foco: `.exe` e Melhorias)

Este é o TO-DO principal, com foco inicial na criação do `.exe`:

**Prioridade Máxima:**

1.  **[ ] Empacotar como Executável (`.exe`) para Windows:**
    *   **[ ] 1.1. Pesquisar e Escolher Ferramenta:**
        *   [ ] Avaliar PyInstaller (principal candidato).
        *   [ ] Considerar auto-py-to-exe (GUI para PyInstaller), cx_Freeze, Nuitka como alternativas.
        *   [X] Decisão preliminar: Iniciar com PyInstaller devido à sua popularidade e documentação.
    *   **[ ] 1.2. Instalar PyInstaller:** (Ex: `pip install pyinstaller`)
    *   **[ ] 1.3. Adaptação de Caminhos para Ativos:**
        *   [ ] Revisar todo o código que carrega arquivos externos (`MODEL_PATH`, `MODEL_PATH_LARGE`, `MAP_FILE_PATH`, `CAMINHO_EFEITOS`, `CAMINHO_TRILHAS`).
        *   [ ] Implementar uma função utilitária para resolver caminhos de forma que funcione tanto no desenvolvimento quanto no executável empacotado (ex: usando `sys.frozen` e `sys._MEIPASS` para PyInstaller, ou `os.path.dirname(__file__)` de forma mais robusta).
    *   **[ ] 1.4. Criar Script de Build (.spec file ou comando direto):**
        *   [ ] Definir quais arquivos e diretórios de dados precisam ser incluídos (`--add-data` para PyInstaller): `modelos_vosk/`, `modelos_vosk_Maior/`, `sons/`, `config/`.
        *   [ ] Especificar o script principal (`src/grio_main.py`).
        *   [ ] Opções: `--onefile` (para um único executável) ou `--onedir`, `--windowed` (para não mostrar console), ícone.
    *   **[ ] 1.5. Gerar o Executável:** Executar o PyInstaller.
    *   **[ ] 1.6. Testar o Executável:**
        *   [ ] Testar em uma máquina Windows limpa (sem Python ou dependências do projeto instaladas).
        *   [ ] Verificar todas as funcionalidades: iniciar/parar, reconhecimento de fala, reprodução de trilhas e efeitos, parada de efeitos em loop.
    *   **[ ] 1.7. Iterar e Depurar:** Corrigir problemas comuns (arquivos não encontrados, DLLs ausentes, etc.).
    *   **[ ] 1.8. Documentar Processo de Build:** Adicionar instruções ao `techContext.md` ou um novo arquivo.

**Melhorias e Refinamentos (Pós-`.exe` funcional):**

2.  **[ ] Melhorias na Interface Gráfica (Tkinter):**
    *   [ ] Permitir seleção do modelo Vosk (pequeno/grande) via UI.
    *   [ ] (Opcional) Permitir seleção do dispositivo de entrada de áudio na UI.
    *   [ ] (Opcional) Melhorar o feedback visual durante o carregamento do modelo (pode ser demorado).
    *   [ ] (Opcional) Adicionar uma opção para limpar o log da UI.
3.  **[ ] Robustez e Tratamento de Erros:**
    *   [ ] Melhorar a exibição de mensagens de erro na UI (ex: se o modelo Vosk não for encontrado, se um arquivo de som estiver ausente).
    *   [ ] Garantir que o `pygame.quit()` seja chamado de forma consistente e apenas uma vez para evitar problemas ao reiniciar.
4.  **[ ] Testes Funcionais Mais Abrangentes:**
    *   [ ] Testar com uma variedade maior de frases e cenários de narração.
    *   [ ] Testar a estabilidade durante uso prolongado.
5.  **[ ] Documentação do Usuário:**
    *   [ ] Criar um breve guia de como usar o Griô Local (especialmente como editar o `mapeamento_eventos.json`).

## 3. Status Atual Geral

*   O núcleo da funcionalidade do Griô Local (ouvir, entender e reagir com som) está implementado e parece funcional no ambiente de desenvolvimento.
*   A interface gráfica é básica mas serve aos propósitos de controle e feedback.
*   O próximo grande passo é o empacotamento da aplicação para distribuição.

## 4. Problemas Conhecidos / Pontos de Atenção

*   **Caminhos de Arquivos no Executável:** Este é o principal desafio previsto para a criação do `.exe`.
*   **Desinicialização do Pygame:** No código de `parar_grio_logica` e `_finalizar_e_destruir`, `pygame.quit()` é chamado. É preciso garantir que `pygame.mixer.quit()` e `pygame.quit()` sejam chamados na ordem correta e sem redundância para evitar erros, especialmente se o Griô for iniciado e parado múltiplas vezes na mesma sessão da UI.
*   **Tamanho do Pacote Final:** Incluir os modelos Vosk (especialmente o grande) e todos os sons resultará em um executável ou pasta de distribuição consideravelmente grande.
*   **Performance do Modelo Grande:** O `MODEL_PATH_LARGE` sugere um modelo maior, mas o impacto na performance (CPU e memória) e no tempo de carregamento precisa ser considerado se for a opção padrão. 