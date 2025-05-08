import sounddevice as sd
import vosk
import queue
import json
import os # Adicionado para construir caminhos de forma mais robusta

# --- Configurações Iniciais ---
# ATENÇÃO: Atualize este caminho para o nome exato da pasta do seu modelo Vosk
# Exemplo: se o modelo está em 'modelos_vosk/vosk-model-small-pt-0.3',
# então MODEL_DIR_NAME = 'vosk-model-small-pt-0.3'
MODEL_DIR_NAME = "vosk-model-small-pt-0.3" # IMPORTANTE: Substitua isso!
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "modelos_vosk", MODEL_DIR_NAME)

SAMPLE_RATE = 16000  # Taxa de amostragem comum para Vosk
DEVICE_ID = None     # Deixe None para usar o dispositivo padrão, ou especifique o índice do microfone
CHANNELS = 1         # Mono

# Fila para comunicação entre a thread de áudio e a thread principal
q = queue.Queue()

def audio_callback(indata, frames, time, status):
    """Esta função é chamada (de uma thread separada) para cada bloco de áudio."""
    if status:
        print(status, flush=True)
    q.put(bytes(indata))

def main():
    # --- Debugging Paths ---
    script_file_path = __file__
    script_location = os.path.dirname(script_file_path)
    project_root_guess = os.path.abspath(os.path.join(script_location, ".."))
    model_folder_base_guess = os.path.join(project_root_guess, "modelos_vosk")
    # Usando o MODEL_PATH original para consistência com o resto do script após o debug
    # Esta é a linha original, apenas reafirmada aqui para o debug:
    constructed_model_path = os.path.join(script_location, "..", "modelos_vosk", MODEL_DIR_NAME)
    absolute_model_path = os.path.abspath(constructed_model_path)


    print(f"--- Debugging Paths ---")
    print(f"Valor de __file__:                               '{script_file_path}'")
    print(f"Diretório do script (os.path.dirname(__file__)): '{script_location}'")
    print(f"Raiz do projeto (calculado com '..'):           '{project_root_guess}'")
    print(f"Pasta base dos modelos (calculado):             '{model_folder_base_guess}'")
    print(f"Nome da pasta do modelo (MODEL_DIR_NAME):       '{MODEL_DIR_NAME}'")
    print(f"Caminho construído para o modelo (MODEL_PATH):  '{MODEL_PATH}'") # Este é o MODEL_PATH global
    print(f"Caminho absoluto para o modelo (abspath):       '{absolute_model_path}'")
    print(f"--- End Debugging Paths ---")

    # A verificação original usa a variável global MODEL_PATH
    if not os.path.exists(MODEL_PATH): # ou podemos testar com absolute_model_path
        print(f"ERRO: O diretório do modelo Vosk não foi encontrado.")
        print(f"  Caminho completo verificado (MODEL_PATH):               '{MODEL_PATH}'")
        print(f"  Caminho absoluto tentado para verificação (abspath): '{absolute_model_path}'")
        print(f"  O sistema está procurando por uma pasta chamada '{MODEL_DIR_NAME}'")
        print(f"  Dentro do diretório:                             '{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modelos_vosk'))}'")
        print(f"Por favor, verifique se a pasta '{MODEL_DIR_NAME}' existe EXATAMENTE com este nome e se o modelo Vosk foi descompactado corretamente dentro dela.")
        return

    print(f"Carregando modelo Vosk de: {MODEL_PATH}")
    try:
        model = vosk.Model(MODEL_PATH)
        recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)
        recognizer.SetWords(True) # Para obter informações sobre palavras individuais (opcional)
        print("Modelo Vosk carregado com sucesso. Começando a ouvir...")
    except Exception as e:
        print(f"Erro ao carregar o modelo Vosk: {e}")
        print("Verifique se o caminho para o modelo está correto e se o modelo é compatível.")
        return

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, 
                             device=DEVICE_ID,
                             channels=CHANNELS, 
                             dtype='int16', # Vosk espera int16
                             callback=audio_callback):
            print("\nGravando... Pressione Ctrl+C para parar.")
            while True:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    print(f"Texto final: {result['text']}")
                # else:
                #     partial_result = json.loads(recognizer.PartialResult())
                #     if partial_result['partial']:
                #          print(f"Parcial: {partial_result['partial']}", end='\r', flush=True)
                
    except KeyboardInterrupt:
        print("\nParando a gravação.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        print("Encerrado.")

if __name__ == "__main__":
    main() 