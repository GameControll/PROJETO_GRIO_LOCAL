# Contexto do Produto: Griô Local

## 1. Problema a Ser Resolvido

A narração de histórias e a leitura em voz alta, embora formas poderosas de comunicação e entretenimento, muitas vezes carecem de um enriquecimento auditivo dinâmico que poderia aumentar o engajamento e a imersão do ouvinte. A criação manual de paisagens sonoras em tempo real é complexa e requer habilidades técnicas ou software especializado, que nem sempre estão disponíveis ou são práticos para o narrador comum.

O Griô Local visa resolver isso fornecendo uma ferramenta acessível que automatiza a adição de trilhas sonoras e efeitos sonoros com base no conteúdo da fala, tornando a experiência mais rica e interativa sem exigir esforço adicional significativo do narrador durante a performance.

## 2. Como o Produto Deve Funcionar

O Griô Local deve funcionar da seguinte maneira:

1.  **Inicialização Simples:** O usuário inicia o aplicativo através de uma interface gráfica simples.
2.  **Captura de Áudio Contínua:** Ao ser iniciado, o sistema começa a escutar ativamente o microfone do computador.
3.  **Reconhecimento de Fala em Tempo Real (Offline):** A fala capturada é processada localmente por um motor de reconhecimento de fala (Vosk) para converter o áudio em texto.
4.  **Análise Semântica e Detecção de Gatilhos:** O texto reconhecido é comparado com uma lista de "gatilhos" (palavras-chave ou frases) definidos em um arquivo de mapeamento.
5.  **Acionamento de Eventos Sonoros:** Se um gatilho é detectado, o sistema consulta o arquivo de mapeamento para determinar quais trilhas sonoras ou efeitos sonoros devem ser reproduzidos.
6.  **Reprodução de Áudio:** As trilhas e efeitos são tocados usando um sistema de áudio local (Pygame Mixer), permitindo a sobreposição de efeitos e a continuidade de trilhas de fundo.
7.  **Controle do Usuário:** O usuário pode iniciar e parar o processo de escuta e reprodução de áudio através da interface gráfica.
8.  **Operação 100% Offline:** Todo o processamento, desde a captura de áudio até a reprodução, ocorre na máquina local, sem necessidade de conexão com a internet.

## 3. Objetivos da Experiência do Usuário (UX)

*   **Facilidade de Uso:** A interface deve ser minimalista e intuitiva, permitindo que usuários com pouco conhecimento técnico possam operar o sistema facilmente (ex: botões claros de "Iniciar" e "Parar").
*   **Imersão Aumentada:** A resposta sonora deve ser relevante e sincronizada o suficiente para enriquecer a narrativa sem distrair ou parecer deslocada.
*   **Feedback Claro:** O usuário deve ter indicações visuais do estado do sistema (ex: "Ouvindo...", "Processando...", "Ocioso", logs de eventos).
*   **Responsividade:** O sistema deve responder rapidamente aos gatilhos de fala para manter a sensação de dinamismo.
*   **Privacidade Garantida:** O usuário deve se sentir seguro sabendo que sua fala não está sendo transmitida ou armazenada externamente.
*   **Customização (Implícita pelo Mapeamento):** Embora a interação direta seja simples, o sistema deve ser flexível através da edição do arquivo JSON de mapeamento para usuários mais avançados que desejam personalizar os eventos sonoros.

## 4. Proposta de Valor Única

O Griô Local oferece uma maneira inovadora e acessível de transformar narrações de histórias e leituras em voz alta em experiências auditivas imersivas, de forma totalmente offline e privada. Diferente de soluções que podem exigir conectividade ou assinaturas, o Griô foca na simplicidade, autonomia do usuário e na resposta em tempo real ao conteúdo falado. 