import sounddevice as sd
import vosk
import queue
import json
import os
import sys # Adicionado para sys.frozen e sys._MEIPASS
import time
import pygame

# NOVAS IMPORTAÇÕES PARA UI
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading

# Importa as funções do nosso reprodutor de áudio
from reprodutor_audio import (
    inicializar_audio as reprodutor_inicializar_audio,
    tocar_efeito_sonoro,
    tocar_trilha_sonora,
    parar_trilha_sonora,
    definir_volume_trilha,
    parar_efeito_em_loop,
    set_base_path_for_sounds # NOVA FUNÇÃO A SER ADICIONADA EM reprodutor_audio.py
)

# --- Função para resolver caminhos de recursos ---
def resource_path(relative_path):
    """ Obtém o caminho absoluto para o recurso, funciona para dev e para PyInstaller. """
    try:
        # PyInstaller cria uma pasta temp e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Se _MEIPASS não existir, estamos em modo de desenvolvimento
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    return os.path.join(base_path, relative_path)

# --- Configurações Iniciais Globais ---
MODEL_DIR_NAME = "vosk-model-small-pt-0.3"
# MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "modelos_vosk", MODEL_DIR_NAME)
MODEL_PATH = resource_path(os.path.join("modelos_vosk", MODEL_DIR_NAME))

# --- NOVO: Configurações para o modelo maior ---
MODEL_DIR_NAME_LARGE = "vosk-model-pt-fb-v0.1.1-pruned"
# MODEL_PATH_LARGE = os.path.join(os.path.dirname(__file__), "..", "modelos_vosk_Maior", MODEL_DIR_NAME_LARGE)
MODEL_PATH_LARGE = resource_path(os.path.join("modelos_vosk_Maior", MODEL_DIR_NAME_LARGE))

# --- NOVO: Flag para selecionar o modelo ---
USAR_MODELO_GRANDE = False # Mude para False para usar o modelo pequeno
# ------------------------------------------

# MAP_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "mapeamento_eventos.json")
MAP_FILE_PATH = resource_path(os.path.join("config", "mapeamento_eventos.json"))

SAMPLE_RATE = 16000
DEVICE_ID = None 
CHANNELS = 1

# Fila global para áudio
q_audio = queue.Queue()


def audio_callback_global(indata, frames, time, status):
    """Callback global para sounddevice, coloca dados na fila q_audio."""
    if status:
        print(f"Status da captura de áudio: {status}", flush=True)
    q_audio.put(bytes(indata))

def carregar_mapeamento_eventos_global(caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        print(f"ERRO: Arquivo de mapeamento não encontrado em: {caminho_arquivo}")
        return None
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            mapeamento = json.load(f)
        print("Arquivo de mapeamento de eventos carregado com sucesso.")
        return mapeamento
    except Exception as e:
        print(f"Erro ao carregar ou parsear o arquivo de mapeamento: {e}")
        return None

# Esta função será chamada pela thread do Griô
def processar_eventos_logica(texto_reconhecido, mapeamento_eventos_carregado, app_ref):
    texto_reconhecido_lower = texto_reconhecido.lower()
    evento_acionado_neste_chunk = False # Flag para garantir que só agimos uma vez por chunk de texto

    for evento_mapeado in mapeamento_eventos_carregado:
        gatilho_que_ativou_este_evento = None # Guarda qual gatilho foi encontrado para ESTE evento

        for gatilho in evento_mapeado.get("gatilhos", []):
            if gatilho.lower() in texto_reconhecido_lower:
                # LOG SEMPRE QUE A STRING DO GATILHO FOR ENCONTRADA
                mensagem_log_gatilho_encontrado = f"🔎 Texto reconhecido contém gatilho: '{gatilho}' (para evento '{evento_mapeado['evento_id']}')"
                print(mensagem_log_gatilho_encontrado)
                if app_ref:
                    app_ref.adicionar_log_evento(mensagem_log_gatilho_encontrado)

                # Se ainda não agimos neste chunk de texto E este é o primeiro gatilho encontrado PARA ESTE evento
                if not evento_acionado_neste_chunk and gatilho_que_ativou_este_evento is None:
                    gatilho_que_ativou_este_evento = gatilho # Guarda o gatilho específico

                # Não damos break aqui no loop de gatilhos para logar todos os gatilhos do mesmo evento

        # Se encontramos um gatilho para este evento E ainda não agimos neste chunk de texto
        if gatilho_que_ativou_este_evento and not evento_acionado_neste_chunk:
            evento_acionado_neste_chunk = True # Marcamos que vamos agir (apenas uma vez por chunk)
            mensagem_log_acao = f"🎬 Ação disparada pelo gatilho '{gatilho_que_ativou_este_evento}' para evento '{evento_mapeado['evento_id']}'"
            print(mensagem_log_acao)
            if app_ref:
                app_ref.adicionar_log_evento(mensagem_log_acao)

            # --- Início das Ações (código existente) ---
            # 1. Parar efeito em loop específico, se solicitado pelo evento
            id_efeito_para_parar = evento_mapeado.get("parar_efeito_loop_id")
            if id_efeito_para_parar:
                msg_parar_efeito = f"  -> Solicitando parada do efeito em loop ID: '{id_efeito_para_parar}'"
                print(msg_parar_efeito)
                if app_ref: app_ref.adicionar_log_evento(msg_parar_efeito)
                parar_efeito_em_loop(id_efeito_para_parar) # Função do reprodutor_audio

            # 2. Parar trilha sonora atual, se solicitado
            if evento_mapeado.get("parar_trilha_atual", False):
                msg_parar_trilha = "  -> Parando trilha sonora atual (se houver)..."
                print(msg_parar_trilha)
                if app_ref: app_ref.adicionar_log_evento(msg_parar_trilha)
                parar_trilha_sonora()
                time.sleep(0.2)

            # 3. Tocar nova trilha sonora, se definida
            trilha_info = evento_mapeado.get("trilha_sonora")
            if trilha_info and trilha_info.get("arquivo"):
                arquivo_trilha = trilha_info["arquivo"]
                loop_trilha = -1 if trilha_info.get("loop", False) else 0
                volume_trilha = float(trilha_info.get("volume", 1.0))

                msg_tocar_trilha = f"  -> Solicitando trilha: {arquivo_trilha}, Loop: {trilha_info.get('loop', False)}, Volume: {volume_trilha}"
                print(msg_tocar_trilha)
                if app_ref: app_ref.adicionar_log_evento(msg_tocar_trilha)

                tocar_trilha_sonora(arquivo_trilha, loop=loop_trilha, volume=volume_trilha)

            # 4. Tocar efeitos sonoros
            efeitos_lista = evento_mapeado.get("efeitos_sonoros", [])
            for efeito_info in efeitos_lista:
                arquivo_efeito = efeito_info.get("arquivo")
                if arquivo_efeito:
                    loop_efeito = efeito_info.get("loop", False)
                    id_loop_efeito = efeito_info.get("id_loop", None)
                    volume_efeito = float(efeito_info.get("volume", 1.0))

                    msg_tocar_efeito = f"  -> Solicitando efeito: {arquivo_efeito}, Loop: {loop_efeito}, ID Loop: {id_loop_efeito}, Volume: {volume_efeito}"
                    print(msg_tocar_efeito)
                    if app_ref: app_ref.adicionar_log_evento(msg_tocar_efeito)

                    tocar_efeito_sonoro(arquivo_efeito,
                                        looping=loop_efeito,
                                        id_loop=id_loop_efeito,
                                        volume=volume_efeito)
            # --- Fim das Ações ---

        # Continua o loop de eventos para LOGAR outros gatilhos, mas não aciona mais ações neste chunk


class AppGrioInterface:
    def __init__(self, root_tk):
        self.root = root_tk
        self.root.title("Griô Local v0.1")
        # --- NOVO: Define o caminho base para os sons no reprodutor_audio ---
        # Isso precisa ser feito antes de qualquer tentativa de carregar sons.
        # A função resource_path aqui garante que o caminho base para 'sons'
        # seja relativo à raiz do projeto (ou ao _MEIPASS no .exe).
        sound_base_actual_path = resource_path("sons")
        set_base_path_for_sounds(sound_base_actual_path)
        # -------------------------------------------------------------------

        self.root.geometry("550x450")

        self.rodando_grio_flag = False
        self.thread_grio_principal = None
        self.mapeamento_eventos_app = None
        self.current_stream = None # NOVO: Para guardar a referência do stream ativo

        # --- Widgets ---
        self.frame_controles = tk.Frame(self.root, pady=10)
        self.frame_controles.pack(fill=tk.X)

        self.btn_iniciar = tk.Button(self.frame_controles, text="Iniciar Griô", command=self.iniciar_grio_logica_thread, width=15, height=2, bg="lightgreen")
        self.btn_iniciar.pack(side=tk.LEFT, padx=20)

        self.btn_parar = tk.Button(self.frame_controles, text="Parar Griô", command=self.parar_grio_logica, width=15, height=2, state=tk.DISABLED, bg="salmon")
        self.btn_parar.pack(side=tk.LEFT, padx=20)

        self.status_label_var = tk.StringVar(value="Status: Ocioso")
        self.status_label = tk.Label(self.root, textvariable=self.status_label_var, pady=5, font=("Arial", 10))
        self.status_label.pack(fill=tk.X)

        self.log_text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=65, height=15, state=tk.DISABLED, font=("Arial", 9))
        self.log_text_area.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)
        
        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar_janela_app)
        
        # Inicializa o mixer do Pygame uma vez para a UI
        if not pygame.mixer.get_init():
            if not reprodutor_inicializar_audio(): # Usa a função do nosso módulo
                messagebox.showerror("Erro Pygame", "Não foi possível inicializar o Pygame Mixer.\nO aplicativo pode não funcionar corretamente.")
                self.root.destroy()


    def atualizar_status_ui(self, mensagem):
        self.status_label_var.set(f"Status: {mensagem}")

    def adicionar_log_evento(self, mensagem):
        if self.log_text_area:
            self.log_text_area.config(state=tk.NORMAL)
            self.log_text_area.insert(tk.END, mensagem + "\n")
            self.log_text_area.see(tk.END)
            self.log_text_area.config(state=tk.DISABLED)

    def limpar_log(self):
        self.log_text_area.config(state=tk.NORMAL)
        self.log_text_area.delete('1.0', tk.END)
        self.log_text_area.config(state=tk.DISABLED)

    def iniciar_grio_logica_thread(self):
        if self.rodando_grio_flag:
            messagebox.showwarning("Atenção", "O Griô já está em execução.")
            return

        self.limpar_log()
        self.adicionar_log_evento("Iniciando Griô...")

        self.mapeamento_eventos_app = carregar_mapeamento_eventos_global(MAP_FILE_PATH)
        if not self.mapeamento_eventos_app:
            messagebox.showerror("Erro de Configuração", f"Falha ao carregar: {MAP_FILE_PATH}")
            self.adicionar_log_evento(f"ERRO: Falha ao carregar {MAP_FILE_PATH}")
            return
        
        # Garante que o mixer está ok antes de iniciar a thread
        if not pygame.mixer.get_init():
            if not reprodutor_inicializar_audio():
                messagebox.showerror("Erro Pygame", "Pygame Mixer não está inicializado. Tente reiniciar o app.")
                self.adicionar_log_evento("ERRO: Pygame Mixer não inicializado.")
                return

        self.rodando_grio_flag = True
        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_parar.config(state=tk.NORMAL)
        self.atualizar_status_ui("Iniciando captura e modelo...")

        self.thread_grio_principal = threading.Thread(target=self._loop_principal_grio, daemon=False)
        self.thread_grio_principal.start()

    def parar_grio_logica(self):
        if not self.rodando_grio_flag:
            return
        
        self.adicionar_log_evento("Sinal de parada enviado ao Griô...")
        self.rodando_grio_flag = False 

        if self.thread_grio_principal and self.thread_grio_principal.is_alive():
            print("[parar_grio_logica] Enviando poison pill para a fila de áudio...")
            q_audio.put(None) # ENVIAR A POISON PILL
            print("[parar_grio_logica] Tentando aguardar finalização da thread Griô (timeout 4s)...")
            self.thread_grio_principal.join(timeout=4.0)
            if self.thread_grio_principal.is_alive():
                print("[parar_grio_logica] AVISO: Thread Griô não finalizou dentro do timeout de 4s.")
            else:
                print("[parar_grio_logica] Thread Griô finalizada (detectado pelo join).")
        
        # --- LÓGICA MOVIDA DE _grio_thread_finalizada_ui_update PARA CÁ ---
        self.rodando_grio_flag = False 
        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_parar.config(state=tk.DISABLED)
        self.atualizar_status_ui("Ocioso (Parado)")
        
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            print("[parar_grio_logica] Parando trilha sonora...")
            parar_trilha_sonora() 
        
        self.adicionar_log_evento("🛑 Processamento do Griô finalizado.")
        print("[parar_grio_logica] Lógica de finalização da UI e Pygame Mixer concluída.")
        # -------------------------------------------------------------------

        print("[parar_grio_logica] Desinicializando Pygame Mixer e Pygame...")
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        if pygame.get_init(): # Verifica se o Pygame principal foi inicializado
            pygame.quit()
        print("[parar_grio_logica] Pygame Mixer e Pygame desinicializados.")


    def _loop_principal_grio(self):
        # Esta função é o coração da lógica Griô, executada na thread.
        
        # --- NOVO: Determinar qual modelo usar ---
        if USAR_MODELO_GRANDE:
            active_model_path = MODEL_PATH_LARGE
            active_model_name = MODEL_DIR_NAME_LARGE
            model_size_label = "Grande"
            print(f"[Griô Config] Usando modelo GRANDE: {active_model_name}")
        else:
            active_model_path = MODEL_PATH
            active_model_name = MODEL_DIR_NAME
            model_size_label = "Pequeno"
            print(f"[Griô Config] Usando modelo PEQUENO: {active_model_name}")
        # -----------------------------------------

        self.root.after(0, lambda: self.atualizar_status_ui(f"Carregando modelo Vosk ({model_size_label})..."))
        self.root.after(0, lambda: self.adicionar_log_evento(f"Carregando modelo Vosk ({model_size_label})..."))

        if not os.path.exists(active_model_path):
            msg_erro_modelo = f"ERRO CRÍTICO: Modelo Vosk não encontrado em {active_model_path}"
            print(msg_erro_modelo)
            self.root.after(0, lambda m=msg_erro_modelo: self.adicionar_log_evento(m))
            self.root.after(0, lambda: messagebox.showerror("Erro Modelo", msg_erro_modelo))
            self.root.after(0, self._grio_thread_finalizada_ui_update)
            return
            
        try:
            print(f"Carregando modelo de: {active_model_path}") # Log atualizado
            vosk_model = vosk.Model(active_model_path) # USA O CAMINHO ATIVO
            recognizer = vosk.KaldiRecognizer(vosk_model, SAMPLE_RATE)
            recognizer.SetWords(True) 
            
            self.current_stream = None # Garante que está None no início
            stream = None # Variável local ainda útil no try/except/finally
            try:
                # --- MANUAL STREAM CREATION ---
                stream = sd.InputStream( # Atribui à variável local 'stream'
                    samplerate=SAMPLE_RATE, 
                    device=DEVICE_ID, 
                    channels=CHANNELS, 
                    dtype='int16', 
                    callback=audio_callback_global
                )
                self.current_stream = stream # GUARDA A REFERÊNCIA EM self
                stream.start() # Inicia o stream manualmente
                # ------------------------------
                
                self.root.after(0, lambda: self.atualizar_status_ui("Ouvindo..."))
                self.root.after(0, lambda: self.adicionar_log_evento("🎤 Griô está ouvindo! Fale algo..."))

                while True: 
                    if not self.rodando_grio_flag:
                        print("Flag de parada detectada no início do loop da thread.")
                        break 

                    try:
                        data = q_audio.get(timeout=0.1) 

                        if data is None: # VERIFICAR POISON PILL PRIMEIRO
                            print("[_loop_principal_grio] Poison pill (None) recebido da fila. Encerrando loop de áudio.")
                            break

                        if not self.rodando_grio_flag:
                             print("Flag de parada detectada após q_audio.get().")
                             break 
                        
                        if recognizer.AcceptWaveform(data):
                            result = json.loads(recognizer.Result())
                            texto = result.get("text", "")
                            if texto:
                                self.root.after(0, lambda t=texto: self.adicionar_log_evento(f'Você disse: \"{t}\"'))
                                processar_eventos_logica(texto, self.mapeamento_eventos_app, self)
                            
                    except queue.Empty:
                        if not self.rodando_grio_flag:
                            print("Flag de parada detectada durante timeout da fila.")
                            break 
                        continue 
                
                print("Loop principal da thread Griô interrompido.") # Mensagem ajustada

            except Exception as e:
                msg_erro_stream = f"Erro durante a captura/processamento de áudio: {e}"
                print(msg_erro_stream)
                self.root.after(0, lambda m=msg_erro_stream: self.adicionar_log_evento(m))
        finally:
            print("[_loop_principal_grio] Entrou no bloco finally.") 
            
            # Limpeza de recursos da thread de áudio
            stream_local_ref = self.current_stream # Pega a referência antes de potencialmente anular
            if stream_local_ref is not None: 
                try:
                    print("[_loop_principal_grio] Tentando abortar e fechar o stream de áudio...")
                    stream_local_ref.abort()
                    stream_local_ref.close()
                    print("[_loop_principal_grio] Stream de áudio abortado e fechado.")
                except Exception as e_stream_cleanup:
                    print(f"[_loop_principal_grio] Erro ao abortar/fechar stream: {e_stream_cleanup}")
            else:
                print("[_loop_principal_grio] Nenhuma referência de stream self.current_stream para limpar.")
            
            self.current_stream = None # Garante que a referência da instância seja limpa

            print("[_loop_principal_grio] Limpando a fila q_audio...") 
            q_clear_count = 0
            while not q_audio.empty():
                try: 
                    q_audio.get_nowait()
                    q_clear_count += 1
                except queue.Empty: 
                    break
            print(f"[_loop_principal_grio] Fila q_audio limpa. Itens removidos: {q_clear_count}.") 
            
            print("[_loop_principal_grio] Saindo do finally. Thread de áudio deve terminar agora.")


    def ao_fechar_janela_app(self):
        if self.rodando_grio_flag:
            if messagebox.askokcancel("Sair?", "O Griô está ativo. Deseja parar e sair?"):
                self.parar_grio_logica()
                # Dá um tempo para a thread tentar terminar.
                # O join aqui pode travar a UI se a thread demorar.
                if self.thread_grio_principal and self.thread_grio_principal.is_alive():
                     self.root.after(200, self._tentar_fechar_novamente) # Tenta fechar de novo
                else:
                    self._finalizar_e_destruir()
            else:
                return # Cancela o fechamento
        else:
            self._finalizar_e_destruir()
            
    def _tentar_fechar_novamente(self):
        if self.thread_grio_principal and self.thread_grio_principal.is_alive():
            print("A thread do Griô ainda está ativa. Forçando o fechamento da janela.")
        self._finalizar_e_destruir()

    def _finalizar_e_destruir(self):
        print("Finalizando Pygame Mixer e Pygame ao fechar a aplicação...")
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        # --- NOVO: Finalizar Pygame completamente ---
        pygame.quit() 
        # ------------------------------------------
        print("Aplicação Griô Local encerrada.")
        self.root.destroy()


if __name__ == "__main__":
    root_tk_main = tk.Tk()
    app_grio = AppGrioInterface(root_tk_main)
    root_tk_main.mainloop()