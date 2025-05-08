# Contexto Ativo: Griô Local

## 1. Foco Atual

O foco principal no momento é **transformar o projeto Python existente do Griô Local em um arquivo executável (`.exe`) para Windows.** Isso permitirá que usuários não técnicos possam instalar e utilizar a aplicação sem a necessidade de configurar um ambiente Python ou instalar dependências manualmente.

## 2. Mudanças Recentes (com base na análise inicial e solicitação do usuário)

*   **Definição do Projeto:** O projeto Griô Local foi formalmente definido (através da criação do Memory Bank) como uma aplicação Python que usa Vosk para STT, Pygame para áudio, Tkinter para UI, e um JSON para mapeamento de eventos.
*   **Nova Solicitação:** O usuário solicitou explicitamente a criação de um executável `.exe`.
*   **Criação do Memory Bank:** Início da criação dos arquivos do Memory Bank (`projectbrief.md`, `productContext.md`, este `activeContext.md`, e os subsequentes) para documentar o projeto e guiar o desenvolvimento.

## 3. Próximos Passos Imediatos

1.  **Concluir a criação inicial do Memory Bank:**
    *   Criar e preencher `systemPatterns.md`.
    *   Criar e preencher `techContext.md`.
    *   Criar e preencher `progress.md`.
2.  **Pesquisar e selecionar uma ferramenta de empacotamento:** Avaliar opções como PyInstaller, auto-py-to-exe (que usa PyInstaller), cx_Freeze ou Nuitka para criar o executável `.exe`.
3.  **Desenvolver um plano de ação para a criação do `.exe`:** Detalhar os passos necessários, incluindo:
    *   Instalação da ferramenta escolhida.
    *   Identificação de todos os arquivos necessários (scripts, modelos Vosk, arquivos de som, DLLs, etc.).
    *   Criação de um script de build ou uso de comandos da ferramenta.
    *   Teste do executável gerado em um ambiente limpo.
    *   Tratamento de possíveis problemas (ex: arquivos não incluídos, caminhos incorretos no executável).
4.  **Implementar o plano de criação do `.exe`**.
5.  **Testar o executável.**
6.  **Documentar o processo de build** no `techContext.md` ou em um novo arquivo no Memory Bank, se necessário.

## 4. Decisões e Considerações Ativas

*   **Ferramenta de Empacotamento:** A escolha da ferramenta (PyInstaller, etc.) será crucial. PyInstaller é geralmente uma boa primeira opção devido à sua popularidade e suporte da comunidade.
*   **Inclusão de Ativos:** Será necessário garantir que o modelo Vosk, os arquivos de som (efeitos e trilhas), e quaisquer outras dependências não-Python sejam corretamente incluídos no pacote do executável.
*   **Caminhos de Arquivos:** O código que lida com caminhos de arquivos (para modelos, sons, JSON de mapeamento) precisará ser robusto para funcionar corretamente tanto no ambiente de desenvolvimento quanto no executável empacotado. Funções como `os.path.join(os.path.dirname(__file__), ...)` ou, para executáveis, abordagens que considerem `sys._MEIPASS` (comum com PyInstaller) podem ser necessárias.
*   **Tamanho do Executável:** Modelos de linguagem podem ser grandes. Precisamos estar cientes do tamanho final do `.exe` e se há otimizações possíveis (embora a funcionalidade seja prioritária sobre o tamanho neste momento).
*   **Teste em Ambiente Limpo:** É fundamental testar o `.exe` em uma máquina Windows que não tenha Python ou as dependências do projeto instaladas para simular o ambiente de um usuário final.

## 5. TO-DO (Nível Macro - Pós Memory Bank Básico)

1.  [ ] **Planejar e Implementar Criação de `.exe`**
    *   [ ] Pesquisar e escolher ferramenta (ex: PyInstaller)
    *   [ ] Instalar ferramenta
    *   [ ] Adaptar caminhos no código se necessário para o build
    *   [ ] Criar script de build/comando
    *   [ ] Gerar `.exe`
    *   [ ] Testar `.exe`
    *   [ ] Documentar processo de build
2.  [ ] **(Futuro - Pós .exe)** Revisitar e refinar a UI (Tkinter) para melhor usabilidade, se necessário.
3.  [ ] **(Futuro - Pós .exe)** Avaliar a necessidade de um instalador (ex: Inno Setup) em vez de apenas um `.exe` standalone, dependendo da complexidade da distribuição.
4.  [ ] **(Futuro - Pós .exe)** Testes mais exaustivos de diferentes cenários de narração.

*(Este TO-DO será detalhado e atualizado no arquivo `progress.md`)* 