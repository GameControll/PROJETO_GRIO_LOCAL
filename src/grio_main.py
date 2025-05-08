import sounddevice as sd
import vosk
import queue
import json
import os
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
    parar_efeito_em_loop
)

# --- Configurações Iniciais Globais ---
MODEL_DIR_NAME = "vosk-model-small-pt-0.3"
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "modelos_vosk", MODEL_DIR_NAME)
MAP_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "mapeamento_eventos.json")

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
    # app_ref é a instância da AppGrioInterface para chamadas de UI

    for evento_mapeado in mapeamento_eventos_carregado:
        for gatilho in evento_mapeado.get("gatilhos", []):
            if gatilho.lower() in texto_reconhecido_lower:
                mensagem_log_evento = f"--- Gatilho '{gatilho}' detectado para '{evento_mapeado['evento_id']}' ---"
                print(mensagem_log_evento)
                if app_ref:
                    app_ref.adicionar_log_evento(mensagem_log_evento)

                # 1. Parar efeito em loop específico, se solicitado pelo evento
                id_efeito_para_parar = evento_mapeado.get("parar_efeito_loop_id")
                if id_efeito_para_parar:
                    msg_parar_efeito = f"Solicitando parada do efeito em loop ID: '{id_efeito_para_parar}'"
                    print(msg_parar_efeito)
                    if app_ref: app_ref.adicionar_log_evento(msg_parar_efeito)
                    parar_efeito_em_loop(id_efeito_para_parar) # Função do reprodutor_audio

                # 2. Parar trilha sonora atual, se solicitado
                if evento_mapeado.get("parar_trilha_atual", False):
                    print("Parando trilha sonora atual (se houver)...")
                    if app_ref: app_ref.adicionar_log_evento("Parando trilha sonora atual...")
                    parar_trilha_sonora()
                    time.sleep(0.2) 

                # 3. Tocar nova trilha sonora, se definida
                trilha_info = evento_mapeado.get("trilha_sonora")
                if trilha_info and trilha_info.get("arquivo"):
                    arquivo_trilha = trilha_info["arquivo"]
                    loop_trilha = -1 if trilha_info.get("loop", False) else 0
                    volume_trilha = float(trilha_info.get("volume", 1.0))
                    
                    msg_tocar_trilha = f"Solicitando trilha: {arquivo_trilha}, Loop: {trilha_info.get('loop', False)}, Volume: {volume_trilha}"
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

                        msg_tocar_efeito = f"Solicitando efeito: {arquivo_efeito}, Loop: {loop_efeito}, ID Loop: {id_loop_efeito}, Volume: {volume_efeito}"
                        print(msg_tocar_efeito)
                        if app_ref: app_ref.adicionar_log_evento(msg_tocar_efeito)
                        
                        tocar_efeito_sonoro(arquivo_efeito, 
                                            looping=loop_efeito, 
                                            id_loop=id_loop_efeito, 
                                            volume=volume_efeito)
                return # Processa apenas o primeiro evento correspondente encontrado


class AppGrioInterface:
    def __init__(self, root_tk):
        self.root = root_tk
        self.root.title("Griô Local v0.1")
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
            print("[parar_grio_logica] Tentando aguardar finalização da thread Griô (timeout 4s)...")
            self.thread_grio_principal.join(timeout=4.0)
            if self.thread_grio_principal.is_alive():
                print("[parar_grio_logica] AVISO: Thread Griô não finalizou dentro do timeout de 4s.")
            else:
                print("[parar_grio_logica] Thread Griô finalizada (detectado pelo join).")
        
        # A atualização da UI (_grio_thread_finalizada_ui_update) ainda será chamada
        # pelo `finally` da própria thread quando ela terminar.

    def _loop_principal_grio(self):
        # Esta função é o coração da lógica Griô, executada na thread.
        self.root.after(0, lambda: self.atualizar_status_ui("Carregando modelo Vosk..."))
        self.root.after(0, lambda: self.adicionar_log_evento("Carregando modelo Vosk..."))

        if not os.path.exists(MODEL_PATH):
            msg_erro_modelo = f"ERRO CRÍTICO: Modelo Vosk não encontrado em {MODEL_PATH}"
            print(msg_erro_modelo)
            self.root.after(0, lambda m=msg_erro_modelo: self.adicionar_log_evento(m))
            self.root.after(0, lambda: messagebox.showerror("Erro Modelo", msg_erro_modelo))
            self.root.after(0, self._grio_thread_finalizada_ui_update)
            return
            
        try:
            vosk_model = vosk.Model(MODEL_PATH)
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
                
                print("Loop principal da thread Griô interrompido pela flag.")

            except Exception as e:
                msg_erro_stream = f"Erro durante a captura/processamento de áudio: {e}"
                print(msg_erro_stream)
                self.root.after(0, lambda m=msg_erro_stream: self.adicionar_log_evento(m))
        finally:
            print("[_loop_principal_grio] Entrou no bloco finally.") 
            # Usa a variável local 'stream' aqui para o stop/abort
            if stream is not None: 
                try:
                    print("[_loop_principal_grio] Tentando abortar o stream de áudio (stream.abort())...")
                    stream.abort()
                    print("[_loop_principal_grio] Stream de áudio abortado (stream.abort() concluído).")
                    
                    # stream.close() FOI REMOVIDO DAQUI e movido para _grio_thread_finalizada_ui_update
                except Exception as e_abort:
                    print(f"[_loop_principal_grio] Erro ao abortar stream: {e_abort}")
            else:
                print("[_loop_principal_grio] Variável local 'stream' era None, nada a abortar.")
            
            print("[_loop_principal_grio] Limpando a fila q_audio...") 
            q_clear_count = 0
            while not q_audio.empty():
                try: 
                    q_audio.get_nowait()
                    q_clear_count += 1
                except queue.Empty: 
                    break
            print(f"[_loop_principal_grio] Fila q_audio limpa. Itens removidos: {q_clear_count}.") 
            
            print("[_loop_principal_grio] Agendando _grio_thread_finalizada_ui_update.") 
            self.root.after(0, self._grio_thread_finalizada_ui_update)
            print("[_loop_principal_grio] _grio_thread_finalizada_ui_update agendado. Saindo do finally.") 


    def _grio_thread_finalizada_ui_update(self):
        """Atualiza a UI quando a thread do Griô termina E TENTA FECHAR O STREAM."""
        # Atualiza UI primeiro para dar feedback rápido
        self.rodando_grio_flag = False 
        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_parar.config(state=tk.DISABLED)
        self.atualizar_status_ui("Ocioso (Parado)")
        
        # Para a música se estiver tocando
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            print("[_grio_thread_finalizada_ui_update] Parando trilha sonora...")
            parar_trilha_sonora() 
        
        self.adicionar_log_evento("🛑 Processamento do Griô finalizado.")
        print("Thread principal do Griô terminou sua execução.") # Mensagem ajustada

        # Tenta fechar o stream DEPOIS que a UI foi atualizada
        if self.current_stream:
            print("[_grio_thread_finalizada_ui_update] Tentando fechar o stream de áudio (self.current_stream.close())...")
            try:
                self.current_stream.close()
                print("[_grio_thread_finalizada_ui_update] Stream de áudio fechado com sucesso.")
            except Exception as e:
                print(f"[_grio_thread_finalizada_ui_update] Erro ao fechar stream de áudio: {e}")
            finally:
                 self.current_stream = None # Limpa a referência independentemente do resultado
        else:
             print("[_grio_thread_finalizada_ui_update] Nenhuma referência de stream ativa para fechar.")
             
        print("[_grio_thread_finalizada_ui_update] Atualização da UI e tentativa de fechar stream concluídas.") # Log final

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