import pygame
import os
import time # Para o teste

# --- Configurações de Áudio ---
# Obtém o diretório do script atual e constrói o caminho para a pasta 'sons'
# __file__ é o caminho do script atual (reprodutor_audio.py)
# os.path.dirname(__file__) é o diretório 'src'
# os.path.join(..., "..", "sons") sobe um nível para 'PROJETO_GRIO_LOCAL' e entra em 'sons'
CAMINHO_BASE_SONS = os.path.join(os.path.dirname(__file__), "..", "sons")
CAMINHO_EFEITOS = os.path.join(CAMINHO_BASE_SONS, "efeitos")
CAMINHO_TRILHAS = os.path.join(CAMINHO_BASE_SONS, "trilhas")

# Cache para sons carregados (efeitos) para evitar recarregar
cache_efeitos_sonoros = {}
loops_de_efeito_ativos = {} # Novo: Para rastrear canais de efeitos em loop {"id_loop": channel_object}

def inicializar_audio():
    """Inicializa o pygame.mixer."""
    try:
        pygame.mixer.init()
        # Aumentar o número de canais pode ser útil se muitos sons tocam simultaneamente
        pygame.mixer.set_num_channels(16) # Exemplo: aumentado para 16 canais
        print(f"Pygame Mixer inicializado com {pygame.mixer.get_num_channels()} canais.")
    except pygame.error as e:
        print(f"Erro ao inicializar Pygame Mixer: {e}")
        print("Certifique-se de que as bibliotecas SDL_mixer estão disponíveis.")
        return False
    return True

def tocar_efeito_sonoro(nome_arquivo_efeito, looping=False, id_loop=None, volume=1.0):
    """
    Toca um efeito sonoro.
    Carrega o som do cache se já foi carregado antes.
    """
    if not pygame.mixer.get_init():
        print("Mixer não inicializado. Chamando inicializar_audio().")
        if not inicializar_audio():
            return

    caminho_completo = os.path.join(CAMINHO_EFEITOS, nome_arquivo_efeito)

    if nome_arquivo_efeito in cache_efeitos_sonoros:
        som = cache_efeitos_sonoros[nome_arquivo_efeito]
    else:
        if not os.path.exists(caminho_completo):
            print(f"ERRO: Efeito sonoro não encontrado em: {caminho_completo}")
            return
        try:
            som = pygame.mixer.Sound(caminho_completo)
            cache_efeitos_sonoros[nome_arquivo_efeito] = som
        except pygame.error as e:
            print(f"Erro ao carregar efeito sonoro '{nome_arquivo_efeito}': {e}")
            return
    
    try:
        som.set_volume(float(volume)) # Define o volume do som
        
        if looping and id_loop:
            if id_loop in loops_de_efeito_ativos and loops_de_efeito_ativos[id_loop].get_sound() == som and loops_de_efeito_ativos[id_loop].get_busy():
                print(f"Efeito '{id_loop}' já está tocando em loop. Ignorando.")
                return

            # Tenta encontrar um canal não ocupado
            channel = pygame.mixer.find_channel() 
            if channel:
                channel.play(som, loops=-1) # loops=-1 para loop infinito
                loops_de_efeito_ativos[id_loop] = channel # Armazena o canal
                print(f"Tocando efeito em loop: '{nome_arquivo_efeito}' (ID: {id_loop}) no canal {channel} com volume {volume}")
            else:
                print(f"ERRO: Nenhum canal disponível para tocar o efeito em loop '{nome_arquivo_efeito}'")
        
        elif looping and not id_loop:
             print(f"AVISO: Efeito '{nome_arquivo_efeito}' solicitado para loop, mas sem id_loop. Tocando como one-shot.")
             som.play(loops=0) # Toca uma vez se id_loop não for fornecido para um loop
             print(f"Tocando efeito (one-shot por falta de id_loop): {nome_arquivo_efeito} com volume {volume}")

        else: # Efeito one-shot
            som.play(loops=0) # loops=0 para tocar uma vez
            print(f"Tocando efeito (one-shot): {nome_arquivo_efeito} com volume {volume}")

    except pygame.error as e:
        print(f"Erro ao tocar efeito sonoro '{nome_arquivo_efeito}': {e}")
    except ValueError:
        print(f"Erro: Volume '{volume}' inválido para '{nome_arquivo_efeito}'. Use um valor entre 0.0 e 1.0.")

def parar_efeito_em_loop(id_loop):
    if not pygame.mixer.get_init():
        return

    if id_loop in loops_de_efeito_ativos:
        channel = loops_de_efeito_ativos.pop(id_loop) # Remove e obtém o canal
        if channel and channel.get_busy(): # Verifica se o canal ainda está ativo
            channel.stop()
            print(f"Efeito em loop '{id_loop}' parado.")
        else:
            print(f"Efeito em loop '{id_loop}' já estava parado ou canal não encontrado.")
    else:
        print(f"Nenhum efeito em loop ativo encontrado com ID: '{id_loop}'")

def tocar_trilha_sonora(nome_arquivo_trilha, loop=-1, volume=1.0):
    """
    Toca uma trilha sonora. O loop -1 significa tocar indefinidamente.
    A música usa um canal dedicado do mixer.
    """
    if not pygame.mixer.get_init():
        print("Mixer não inicializado. Chamando inicializar_audio().")
        if not inicializar_audio():
            return

    caminho_completo = os.path.join(CAMINHO_TRILHAS, nome_arquivo_trilha)
    if not os.path.exists(caminho_completo):
        print(f"ERRO: Trilha sonora não encontrada em: {caminho_completo}")
        return
    
    try:
        pygame.mixer.music.load(caminho_completo)
        pygame.mixer.music.set_volume(float(volume)) # Define o volume ANTES de tocar
        pygame.mixer.music.play(loops=loop)
        print(f"Tocando trilha: {nome_arquivo_trilha} (loop={loop}, volume={volume})")
    except pygame.error as e:
        print(f"Erro ao carregar ou tocar trilha sonora '{nome_arquivo_trilha}': {e}")
    except ValueError:
        print(f"Erro: Volume '{volume}' inválido para trilha '{nome_arquivo_trilha}'.")

def parar_trilha_sonora():
    """Para a trilha sonora que estiver tocando."""
    if not pygame.mixer.get_init():
        return
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        print("Trilha sonora parada e descarregada.")
    except pygame.error as e:
        print(f"Erro ao parar trilha sonora: {e}")

def definir_volume_trilha(volume):
    """Define o volume da trilha sonora (0.0 a 1.0)."""
    if not pygame.mixer.get_init():
        return
    try:
        pygame.mixer.music.set_volume(float(volume))
        # print(f"Volume da trilha (já tocando) definido para: {volume}")
    except pygame.error as e:
        print(f"Erro ao definir volume da trilha: {e}")
    except ValueError:
        print(f"Erro: Volume '{volume}' inválido. Use um valor entre 0.0 e 1.0.")


# Bloco de teste para executar este script diretamente
if __name__ == "__main__":
    print("Iniciando teste do reprodutor de áudio (com loops de efeito)...")
    
    if not inicializar_audio():
        print("Falha ao inicializar áudio. Saindo do teste.")
        exit()

    efeito_one_shot = "Mina_Terrestre.wav"
    efeito_loop_helicoptero = "Helicoptero_loop.mp3"
    id_helicoptero = "helicoptero_teste"
    trilha_teste = "Trilha_Sonora_de_Acao.wav"

    print("\nTestando efeito one-shot (Mina Terrestre)...")
    tocar_efeito_sonoro(efeito_one_shot, volume=0.9)
    time.sleep(2)

    print(f"\nTestando efeito em loop (Helicoptero) com ID '{id_helicoptero}' por 5 segundos...")
    tocar_efeito_sonoro(efeito_loop_helicoptero, looping=True, id_loop=id_helicoptero, volume=0.7)
    time.sleep(5)
    
    print(f"\nParando efeito em loop (Helicoptero) com ID '{id_helicoptero}'...")
    parar_efeito_em_loop(id_helicoptero)
    time.sleep(1)

    print("\nTestando tocar efeito em loop novamente para ver se o canal foi liberado...")
    tocar_efeito_sonoro(efeito_loop_helicoptero, looping=True, id_loop="helicoptero_teste_2", volume=0.6)
    time.sleep(3)
    parar_efeito_em_loop("helicoptero_teste_2")
    time.sleep(1)

    print("\nTestando trilha sonora...")
    tocar_trilha_sonora(trilha_teste, loop=-1, volume=0.5)
    print("Trilha tocando por 3 segundos...")
    time.sleep(3)
    parar_trilha_sonora()
    time.sleep(1)

    print("\nTeste do reprodutor de áudio concluído.")
    pygame.mixer.quit() # Importante para liberar recursos ao final do teste
    print("Pygame Mixer finalizado.") 