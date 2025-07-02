from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse, HttpResponse
from django.views.static import serve
import yt_dlp as youtube_dl
import os
import urllib
from pathlib import Path
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import threading
import queue
import time
import subprocess
from django.views.static import serve
import re 
from django.http import FileResponse
import hashlib
from django.conf import settings

# Diretório para salvar os downloads
DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'downloads')
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Fila para armazenar atualizações de progresso
progress_queue = queue.Queue()

def cleanup_old_files():
    """Remove arquivos antigos da pasta downloads (mais de 1 hora)"""
    try:
        current_time = time.time()
        for filename in os.listdir(DOWNLOADS_DIR):
            file_path = os.path.join(DOWNLOADS_DIR, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                # Remove arquivos com mais de 1 hora
                if file_age > 3600:  # 3600 segundos = 1 hora
                    try:
                        os.remove(file_path)
                        print(f"Arquivo antigo removido: {filename}")
                    except Exception as e:
                        print(f"Erro ao remover arquivo antigo {filename}: {e}")
    except Exception as e:
        print(f"Erro na limpeza automática: {e}")

def index(request):
    # Executa limpeza automática de arquivos antigos
    cleanup_old_files()
    return render(request, 'index.html')

# Função removida - não mais necessária sem boto3

def generate_safe_filename(original_filename):
    # Gera um hash único baseado no nome original
    
    hash_object = hashlib.md5(original_filename.encode())
    print("=====",hash_object)
    hash_hex = hash_object.hexdigest()[:8]  # Pega os primeiros 8 caracteres do hash
    
    # Divide o nome do arquivo e a extensão
    base, ext = os.path.splitext(original_filename)
    print("========", ext, "----------")
    
    # Remove sufixos como .fXXX do nome base
    base = re.sub(r'\.f\d+$', '', base)
    
    # Aplica slugify apenas no nome base
    safe_base = slugify(base)
    
    # Remove pontos restantes (exceto na extensão)
    safe_base = safe_base.replace('.', '')
    
    # Remove múltiplos hífens consecutivos
    safe_base = re.sub(r'-+', '-', safe_base)
    
    # Combina com o hash e a extensão original
    filename = f"{safe_base}-{hash_hex}{ext}"
    print("_+_+_+_+_+_+_+_+=",filename)
    
    # Verifica se o arquivo já existe e adiciona números sequenciais
    counter = 1
    while os.path.exists(os.path.join(DOWNLOADS_DIR, filename)):
        # Remove o número anterior se existir
        base_name = re.sub(r'\(\d+\)$', '', safe_base)
        # Adiciona o novo número
        filename = f"{base_name}({counter})-{hash_hex}{ext}"
        counter += 1
    print("+_+_+_+_+_+_+_+-==",filename)
    
    return filename

# Modifique o custom_progress_hook para enviar o percentual numérico
def custom_progress_hook(d):
    if d['status'] == 'downloading':
        # Limpa códigos ANSI de todos os campos
        def clean_ansi(text):
            return re.sub(r'\x1b\[[0-9;]*m', '', str(text)) if text else 'N/A'

        # Cálculo mais preciso do percentual
        total = (
            d.get('total_bytes') or 
            d.get('total_bytes_estimate') or 
            (d.get('total_fragments') or 1) * (d.get('fragment_size') or 0)
        )
        
        downloaded = d.get('downloaded_bytes', 0)
        current_fragment = d.get('fragment_index', 0)
        total_fragments = d.get('total_fragments', 0)
        
        # Cálculo mais preciso do percentual considerando fragmentos
        if total > 0:
            percent = (downloaded / total * 100)
        elif total_fragments > 0:
            percent = (current_fragment / total_fragments * 100)
        else:
            percent = 0

        # Força 100% se o último fragmento estiver sendo processado
        if current_fragment == total_fragments and total_fragments > 0:
            percent = 100.0

        # Calcula velocidade em MB/s
        speed = d.get('speed', 0)
        speed_mb = round(speed / (1024 * 1024), 2) if speed else 0
        speed_str = f"{speed_mb} MB/s" if speed_mb > 0 else "N/A"

        # Atualiza o progresso mais frequentemente
        progress_data = {
            'status': 'downloading',
            'percent': min(round(percent, 1), 100.0),
            'speed': speed_str,
            'eta': clean_ansi(d.get('_eta_str', 'N/A')),
            'downloaded_mb': round(downloaded / (1024 * 1024), 1),
            'total_mb': round(total / (1024 * 1024), 1) if total > 0 else 'N/A',
            'fragment': f"{current_fragment}/{total_fragments}" if total_fragments > 0 else 'N/A',
            'is_final': False
        }
        progress_queue.put(progress_data)
    
    elif d['status'] == 'finished':
        progress_queue.put({
            'status': 'processing',
            'message': 'Preparando para upload...'
        })

from django.utils.text import slugify

def sanitize_filename(filename):
    # Divide o nome do arquivo e a extensão
    base, ext = os.path.splitext(filename)
    print("+++++++++", ext, "+++++++++++")
    
    # Remove sufixos como .fXXX apenas do nome base
    cleaned_base = re.sub(r'\.f\d+$', '', base)
    
    # Aplica slugify apenas no nome base
    safe_base = slugify(cleaned_base)
    
    # Remove pontos restantes (exceto na extensão)
    safe_base = safe_base.replace('.', '')
    
    # Remove múltiplos hífens consecutivos
    safe_base = re.sub(r'-+', '-', safe_base)
    
    # Combina com a extensão original
    if ext == ".mp3":
        print("abababababababbababa")
        return f"{safe_base}"
    else:
        return f"{safe_base}{ext}"

# View para download direto com limpeza automática
def download_file(request, filename):
    decoded_name = urllib.parse.unquote(filename)
    file_path = os.path.join(DOWNLOADS_DIR, decoded_name)
    
    print(f"Procurando arquivo: {decoded_name}")
    print(f"Caminho completo: {file_path}")
    print(f"Arquivo existe: {os.path.exists(file_path)}")
    print(f"Arquivos na pasta: {os.listdir(DOWNLOADS_DIR)}")
    
    # Se o arquivo não for encontrado, procura por arquivos similares
    if not os.path.exists(file_path):
        print("Arquivo não encontrado, procurando alternativas...")
        
        # Lista todos os arquivos no diretório
        all_files = os.listdir(DOWNLOADS_DIR)
        print(f"Arquivos na pasta: {all_files}")
        
        # Procura por arquivos que correspondam ao padrão
        base_name = re.sub(r'\.f\d+\.', '.', decoded_name)
        base_name_without_ext = os.path.splitext(base_name)[0]
        ext = os.path.splitext(base_name)[1]
        
        print(f"Procurando por: {base_name_without_ext}*{ext}")
        
        # Busca simples - procura por arquivos que contenham o nome base
        for file in all_files:
            if base_name_without_ext.lower() in file.lower() and file.endswith(ext):
                file_path = os.path.join(DOWNLOADS_DIR, file)
                print(f"Arquivo encontrado: {file}")
                break
    
    if os.path.exists(file_path):
        try:
            print(f"Servindo arquivo: {file_path}")
            
            # Lê o arquivo em memória
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Cria a resposta HTTP
            response = HttpResponse(file_content, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{decoded_name}"'
            response['Content-Length'] = len(file_content)
            
            # Agenda a remoção do arquivo após o download
            def delete_file_after_download():
                import time
                time.sleep(2)  # Aguarda 2 segundos para garantir que o download iniciou
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"Arquivo removido automaticamente: {file_path}")
                except Exception as e:
                    print(f"Erro ao remover arquivo: {e}")
            
            # Inicia thread para remoção automática
            cleanup_thread = threading.Thread(target=delete_file_after_download)
            cleanup_thread.daemon = True
            cleanup_thread.start()
            
            return response
            
        except Exception as e:
            print(f"Erro ao servir arquivo: {e}")
            return JsonResponse({'error': 'Erro ao processar arquivo'}, status=500)
    
    print(f"Arquivo não encontrado: {decoded_name}")
    return JsonResponse({'error': 'Arquivo não encontrado'}, status=404)

@require_http_methods(["GET"])
def get_video_info_view(request):
    url = request.GET.get('url')
    if not url:
        return JsonResponse({'error': 'URL não fornecida'}, status=400)

    ydl_opts = {
            'noplaylist': True,  # Esta opção é crucial para focar apenas no vídeo individual
            'quiet': True,       # Suprime a saída de logs do yt-dlp para o console (opcional, mas útil em apps web)
            # Pode ser útil para extrair informações básicas rapidamente sem baixar tudo
                                 # No entanto, 'extract_info' sem download=False já faz isso
            'force_generic_extractor': False, # Geralmente não é necessário alterar, mas pode ser útil para depuração
        }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
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
            
            # Extrai formatos disponíveis
            formats = info.get('formats', [])
            lista_Resolucion = []
            def verificar(lista_Resolucion, resolucion):
                if resolucion in lista_Resolucion:
                    return True
                else:
                    False
                
            video_formats = [f for f in formats if f.get('vcodec') != 'none']
            for i in range(0, len(video_formats)): 
                resolucion = video_formats[i]['height']   
                if verificar(lista_Resolucion, resolucion):
                    pass
                else:
                    lista_Resolucion.append(resolucion)

            print(lista_Resolucion) 
            
          
            return JsonResponse({
                'title': title,
                'thumbnail_url': thumbnail_url,
                'formats': video_formats,
                'lista_Resolucion' : lista_Resolucion,
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def download(request):
    try:
        data = json.loads(request.body)
        url = data.get('url')
        download_type = data.get('type')
        print(download_type)
        resolution = data.get('resolution')
        extension = data.get('extension')
        vcodec = data.get('format')

        if not url:
            return JsonResponse({'error': 'URL não fornecida'}, status=400)

        # Limpa a fila de progresso
        while not progress_queue.empty():
            try:
                progress_queue.get_nowait()
            except queue.Empty:
                break
        
        ydl_info_opts = {
            'noplaylist': True,  # Adicione noplaylist aqui para a extração inicial de info
            'quiet': True,
        }

        # Primeiro, obtém as informações do vídeo para pegar o título e formatos
        with youtube_dl.YoutubeDL(ydl_info_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'video')
            formats = info.get('formats', [])
            
            # Gera um nome seguro para o arquivo
            if download_type == "video":
                safe_filename = generate_safe_filename(f"{title}.{extension}")
            else:
                print("audio2")
                safe_filename = generate_safe_filename(f"{title}")
            
            # Define o caminho completo do arquivo
            output_path = os.path.join(DOWNLOADS_DIR, safe_filename)
            
            print("-------",output_path)

            # Encontra o format_id se for download de vídeo
            format_id = None
            if download_type == 'video':
                format_id = find_format_id(formats, resolution, extension, vcodec)
                if not format_id:
                    return JsonResponse({
                        'error': 'Combinação de resolução/extensão/codec não encontrada'
                    }, status=400)

        def download_thread():
            try:
                if download_type == 'video':
                    format_spec = f'{format_id}+bestaudio[ext=m4a]/best[ext=mp4]/best'
                    
                    ydl_opts = {
                        'restrictfilenames': False,  # Desabilita para manter nome original
                        'windowsfilenames': False, 
                        'noplaylist': True,  # Desabilita para manter nome original
                        'format': format_spec,
                        'outtmpl': output_path,
                        'merge_output_format': extension.lower() if extension else 'mp4',
                        'postprocessor_args': ['-threads', '4'],
                        'progress_hooks': [custom_progress_hook],
                    }
                else:
                    # Configuração para áudio
                    audio_format = {
                        'high': 'bestaudio',
                        'medium': 'bestaudio[abr<=128]',
                        'low': 'bestaudio[abr<=64]'
                    }.get(resolution.lower(), 'bestaudio')

                    ydl_opts = {
                        'restrictfilenames': False,  # Desabilita para manter nome original
                        'windowsfilenames': False,
                        'noplaylist': True,   # Desabilita para manter nome original
                        'format': audio_format,
                        'outtmpl': output_path,
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                        'progress_hooks': [custom_progress_hook],
                    }

                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # Determina o caminho final do arquivo
                final_path = ""
                final_filename = ""
                if download_type == "audio":
                    final_path = f'{output_path}.mp3'
                    final_filename = f'{safe_filename}.mp3'
                else: 
                    final_path = f'{output_path}'
                    final_filename = f'{safe_filename}'

                # Verifica se o arquivo foi criado
                if os.path.exists(final_path):
                    print(f"Download concluído: {final_path}")
                    print(f"Nome do arquivo final: {final_filename}")
                    
                    # Atualiza o progresso com sucesso
                    progress_queue.put({
                        'status': 'completed',
                        'filename': final_filename,
                        'file_path': final_path,
                        'percent': 100.0,
                        'is_final': True,
                        'speed': 'Completo',
                        'eta': 'Concluído',
                        'downloaded_mb': 'Finalizado',
                        'total_mb': 'Finalizado'
                    })
                else:
                    # Lista arquivos na pasta para debug
                    print(f"Arquivo não encontrado em: {final_path}")
                    print("Arquivos na pasta downloads:")
                    for file in os.listdir(DOWNLOADS_DIR):
                        print(f"  - {file}")
                    raise Exception("Arquivo não foi criado após o download")

            except Exception as e:
                progress_queue.put({
                    'status': 'error',
                    'error': str(e)
                })

        thread = threading.Thread(target=download_thread)
        thread.start()

        # Determina o nome do arquivo final
        if download_type == "audio":
            final_filename = f'{safe_filename}.mp3'
        else:    
            final_filename = f'{safe_filename}'

        return JsonResponse({
            'status': 'download_started',
            'filename': final_filename
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



def download_progress(request):
    def event_stream():
        last_update = time.time()
        while True:
            try:
                # Verifica se há atualizações na fila
                if not progress_queue.empty():
                    data = progress_queue.get()
                    yield f"data: {json.dumps(data)}\n\n"
                    
                    # Se o download foi concluído ou houve erro, encerra o stream
                    if data.get('status') in ['completed', 'error']:
                        break
                
                # Reduz o intervalo de verificação para 0.05 segundos
                time.sleep(0.05)
                
                # Força uma atualização a cada 0.5 segundos mesmo sem mudanças
                current_time = time.time()
                if current_time - last_update >= 0.5:
                    last_update = current_time
                    yield f"data: {json.dumps({'status': 'heartbeat'})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'status': 'error', 'error': str(e)})}\n\n"
                break

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    
    # Headers apropriados para SSE
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    
    return response


def find_format_id(formats, target_resolution, target_extension, target_vcodec):
    """
    Encontra o format_id com base na resolução, extensão e codec de vídeo.
    Prioriza formatos com maior FPS e, em caso de empate, o maior format_id.
    """
    target_extension = target_extension.lower()
    target_vcodec = target_vcodec.lower()
    
    matching_formats = []
    
    print("cheguei aqui")
    print(target_resolution, target_extension, target_vcodec)
    for fmt in formats:
        # Extrai e normaliza os valores do formato
        fmt_resolution = fmt.get('height', '')
        fmt_extension = fmt.get('ext', '').lower()
        fmt_vcodec = fmt.get('vcodec', 'none').split('.')[0].lower()
        fmt_fps = fmt.get('fps', 0)
        print("------------")
        print(fmt_resolution)
        print(fmt_extension)
        print(fmt_vcodec)
        print("------------")

        # Verifica correspondência
        if (str(fmt_resolution) == str(target_resolution) and
            str(fmt_extension) == str(target_extension) and
            str(fmt_vcodec) == str(target_vcodec)):
            print("?????????!!!!!!!")
            matching_formats.append({
                'format_id': fmt['format_id'],
            })
        else:
            print("não encontrado")
    print(matching_formats)
    if not matching_formats:
        return None
  
    return matching_formats[0]['format_id']

def download_desktop_app(request):
    """
    View para download do aplicativo desktop MediaFlow (arquivo RAR)
    """
    # Caminho para o arquivo RAR do MediaFlow
    desktop_app_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'Versão DeskTop',
        'CodigoDaInterface',
        'MediaFlow.rar'
    )
    
    print(f"Tentando acessar arquivo: {desktop_app_path}")
    print(f"Arquivo existe: {os.path.exists(desktop_app_path)}")
    
    # Verifica se o arquivo existe
    if not os.path.exists(desktop_app_path):
        print(f"Arquivo não encontrado: {desktop_app_path}")
        return JsonResponse({
            'error': 'Aplicativo desktop não encontrado'
        }, status=404)
    
    try:
        # Usa o serve do Django para arquivos estáticos
        return serve(request, 'MediaFlow.rar', os.path.dirname(desktop_app_path))
        
    except Exception as e:
        print(f"Erro ao processar arquivo: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': f'Erro ao servir o arquivo: {str(e)}'
        }, status=500)