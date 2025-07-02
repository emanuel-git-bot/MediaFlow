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
from botocore.client import Config
import boto3
from django.conf import settings

# Diretório para salvar os downloads
DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'downloads')
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Fila para armazenar atualizações de progresso
progress_queue = queue.Queue()

def index(request):
    return render(request, 'index.html')

def get_storj_client():
    return boto3.client(
        's3',
        endpoint_url=settings.STORJ_CONFIG['ENDPOINT_URL'],
        aws_access_key_id=settings.STORJ_CONFIG['ACCESS_KEY'],
        aws_secret_access_key=settings.STORJ_CONFIG['SECRET_KEY'],
        config=Config(
            signature_version='s3v4',
            s3={'addressing_style': 'path'}
        )
    )

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

# Adicione esta nova view para servir os arquivos baixados
def download_file(request, filename):
    decoded_name = urllib.parse.unquote(filename)
    file_path = os.path.join(DOWNLOADS_DIR, decoded_name)
    
    # Se o arquivo não for encontrado, tenta encontrar sem o sufixo .fXXX
    if not os.path.exists(file_path):
        # Procura por arquivos que correspondam ao padrão (nome base + qualquer sufixo .fXXX + extensão)
        base_name = re.sub(r'\.f\d+\.', '.', decoded_name)
        base_name_without_ext = os.path.splitext(base_name)[0]
        ext = os.path.splitext(base_name)[1]
        
        # Lista todos os arquivos no diretório
        for file in os.listdir(DOWNLOADS_DIR):
            if file.startswith(base_name_without_ext) and file.endswith(ext):
                file_path = os.path.join(DOWNLOADS_DIR, file)
                break
    
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{decoded_name}"'
        return response
    
    return JsonResponse({'error': 'Arquivo não encontrado'}, status=404)

@require_http_methods(["GET"])
def get_video_info_view(request):
    url = request.GET.get('url')
    if not url:
        return JsonResponse({'error': 'URL não fornecida'}, status=400)

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

        # Primeiro, obtém as informações do vídeo para pegar o título e formatos
        with youtube_dl.YoutubeDL() as ydl:
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
                        'restrictfilenames': True,
                        'windowsfilenames': True,
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
                        'restrictfilenames': True,
                        'windowsfilenames': True,
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
                
                novo_path_destine = ""
                novo_safe_filename = ""
                if download_type == "audio":
                    print("<<<<<<<<<<<",output_path)
                    novo_path_destine = f'{output_path}.mp3'
                    novo_safe_filename = f'{safe_filename}.mp3'
                    print("<<<<<<<<<<<",output_path)
                else: 
                    novo_path_destine = f'{output_path}'
                    novo_safe_filename = f'{safe_filename}'


                 # === NOVO: Upload para o Storj ===
                storj = get_storj_client()
                
                # Faz upload do arquivo
                with open(novo_path_destine, 'rb') as file_data:
                    file_content = file_data.read()
                    storj.put_object(
                        Bucket=settings.STORJ_CONFIG['BUCKET_NAME'],
                        Key=novo_safe_filename,
                        Body=file_content,
                        ContentLength=len(file_content)
                    )

                print("ubaibaubaubaubaubauba")
                
                # Gera URL pública
                public_url = storj.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': settings.STORJ_CONFIG['BUCKET_NAME'],
                        'Key': novo_safe_filename
                    },
                    ExpiresIn=604800  # 7 dias
                )

                # Atualiza o progresso com a URL do Storj
                progress_queue.put({
                    'status': 'completed',
                    'filename': novo_safe_filename,
                    'download_url': public_url,
                    'percent': 100.0,
                    'is_final': True,
                    'speed': 'Completo',
                    'eta': 'Concluído',
                    'downloaded_mb': 'Finalizado',
                    'total_mb': 'Finalizado'
                })

                # Remove arquivo local
                if os.path.exists(novo_path_destine):
                    os.remove(novo_path_destine)
                    print('removi', novo_path_destine , "com sucesso!!!")
                else:
                    print("ele não existe!!!!")

            except Exception as e:
                progress_queue.put({
                    'status': 'error',
                    'error': str(e)
                })

        thread = threading.Thread(target=download_thread)
        thread.start()

        if download_type == "audio":
            print("<<<<<<<<<<<",output_path)     
            novo_safe_filename = f'{safe_filename}.mp3'
            print("<<<<<<<<<<<",output_path)
        else:    
            novo_safe_filename = f'{safe_filename}'


        return JsonResponse({
            'status': 'download_started',
            'filename': novo_safe_filename
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
    View para download do aplicativo desktop MediaFlow
    """
    # Caminho para o executável do MediaFlow
    desktop_app_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'Versão DeskTop',
        'CodigoDaInterface',
        'dist',
        'MediaFlow',
        'MediaFlow.exe'
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
        return serve(request, 'MediaFlow.exe', os.path.dirname(desktop_app_path))
        
    except Exception as e:
        print(f"Erro ao processar arquivo: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': f'Erro ao servir o arquivo: {str(e)}'
        }, status=500)