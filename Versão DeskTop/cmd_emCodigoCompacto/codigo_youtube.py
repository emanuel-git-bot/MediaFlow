import yt_dlp as youtube_dl
import os
from pathlib import Path
import json
import threading
import queue
import time

# Diretório para salvar os downloads
DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Fila para armazenar atualizações de progresso
progress_queue = queue.Queue()

def get_video_info(url):
    """
    Verifica se a URL é válida e retorna o título e thumbnail do vídeo.
    
    Args:
        url (str): URL do vídeo a ser verificado
        
    Returns:
        dict: Dicionário com 'title' e 'thumbnail_url' ou None se ocorrer erro
    """
    try:
        with youtube_dl.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Extrai título
            title = info.get('title', '')
            
            # Extrai thumbnail (prioriza a maior resolução)
            thumbnail_url = info.get('thumbnail', '')
            thumbnails = info.get('thumbnails', [])
            
            # Se não encontrou thumbnail principal, busca na lista de thumbnails
            if not thumbnail_url and thumbnails:
                # Pega a última thumbnail que geralmente é a de maior resolução
                thumbnail_url = thumbnails[-1].get('url', '')
            
            return {
                'title': title,
                'thumbnail_url': thumbnail_url
            }
            
    except Exception as e:
        print(f"Erro ao verificar a URL: {str(e)}")
        return None

def custom_progress_hook(d):
    """
    Hook personalizado para monitorar o progresso do download
    """
    if d['status'] == 'downloading':
        progress_data = {
            'status': 'downloading',
            'percent': d.get('_percent_str', '0%'),
            'speed': d.get('_speed_str', 'N/A'),
            'eta': d.get('_eta_str', 'N/A')
        }
        progress_queue.put(progress_data)
    elif d['status'] == 'finished':
        progress_data = {
            'status': 'completed',
            'filename': d.get('filename', '')
        }
        progress_queue.put(progress_data)

def download_music(url, qualidade):
    """
    Download de música com qualidade específica
    """
    audio_format = {
        'high': 'bestaudio',
        'medium': 'bestaudio[abr<=128]',
        'low': 'bestaudio[abr<=64]'
    }.get(qualidade, 'bestaudio')

    ydl_opts = {
        'format': audio_format,
        'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'progress_hooks': [custom_progress_hook],
    }
    
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        progress_queue.put({
            'status': 'error',
            'error': str(e)
        })
        return False

def download_video(url, format_code):
    """
    Download de vídeo com formato específico
    """
    if format_code == "best":
        format_code = "bestvideo[ext=mp4]"
        
    ydl_opts = {
        'format': f'{format_code}+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
        'progress_hooks': [custom_progress_hook],
        'merge_output_format': 'mp4',
        'postprocessor_args': ['-threads', '4'],
    }
    
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        progress_queue.put({
            'status': 'error',
            'error': str(e)
        })
        return False

def show_formats(url):
    """
    Mostra os formatos disponíveis para download
    """
    with youtube_dl.YoutubeDL() as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            # Filtra apenas formatos com vídeo
            video_formats = [f for f in formats if f.get('vcodec') != 'none']
            
            print("\nFormatos disponíveis:")
            print("ID  | Resolução   | FPS  | Extensão | Codec Vídeo       | Codec Áudio")
            print("----------------------------------------------------------------------")
            
            for f in video_formats:
                print("{:<4} | {:<11} | {:<4} | {:<8} | {:<17} | {}".format(
                    f['format_id'],
                    f.get('resolution', '?'),
                    f.get('fps', '?'),
                    f.get('ext', '?'),
                    f.get('vcodec', 'none').split('.')[0],
                    f.get('acodec', 'none').split('.')[0]
                ))
            
            return True
        except Exception as e:
            print(f"\nErro ao obter formatos: {str(e)}")
            return False

def get_download_progress():
    """
    Retorna o próximo item da fila de progresso
    """
    try:
        return progress_queue.get_nowait()
    except queue.Empty:
        return None

def clear_progress_queue():
    """
    Limpa a fila de progresso
    """
    while not progress_queue.empty():
        try:
            progress_queue.get_nowait()
        except queue.Empty:
            break

if __name__ == "__main__":
    os.makedirs('./videos', exist_ok=True)
    
    url = input("Cole a URL do vídeo do YouTube: ")
    video_info = get_video_info(url)
    if video_info:
        print(f"Título: {video_info['title']}")
        print(f"Thumbnail: {video_info['thumbnail_url']}")
    else:
        print("URL inválida ou vídeo não encontrado")
    
    if show_formats(url):
        [

            
        ]
        VideoORmuscic = input("quer abaixar video ou musica (v/a):")
        if VideoORmuscic == "v":
            format_choice = input("\nDigite o ID do formato desejado (ou 'best' para melhor qualidade automática): ")
            download_video(url, format_choice)
        elif VideoORmuscic == "a":
            qualidade = input("Qualidade do áudio (high, medium, low): ").lower()
            download_music(url, qualidade)