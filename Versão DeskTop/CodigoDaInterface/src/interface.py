import customtkinter as ctk
import yt_dlp
from PIL import Image, ImageTk # Importa ImageTk para tratamento de erro
import requests
from io import BytesIO
import threading
import os
from tkinter import filedialog
import base64
import sys

# --- Ícones em formato Base64 (CORRIGIDOS E VERIFICADOS) ---
SEARCH_ICON_B64 = "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAANYSURBVFhHzZlriFxVFMd/t7ubmUkkbsQoDTWRUEtFsbAS2Iig2Flod0FQ0YKLtq6EKOJAFKQIIShYFMpAKypaREEQC0EtoXEkSGpQZJTMJ5OZyWTe3d17Yw6TzOzO7My7G/nhwNy593z/c+757jkHJpZYEa1YvQoEu0m0G8k2Yqk5K2I5llkTU/l5lH0ErfIqQJ9pUPgUaM/A/jTQTwV6qWDvBA/eBSrYx/Ecwl6A/Qu4LWAHgi0C2zTQqwa6aKD3AnYLsLPBq9+A7T4sjgCGgG2A/X4s7gBWA9YDsBdgZZsZAR4C5gO2ATZoYJ8C7bVAvwXoqwR7t0BnhvY+IDmE8DPA2wB7ADwJ7DSwUQXdAlbr9VqgV+u//UeANg3sNLBGgX4V6M0AP0eQZ4Hy/REkP4M8BWwU4CeBFvrhUPsV2FbgWyB8q0BvBOgXwX5Y8AewXoG+fRifAnYDqK8C/ZKgTwL9SIA/Jsg/gXIjQPkUaJ3A/jqQfwX4M8i3gL0S6CWBvRLoZYC9AOwosE+BVgbsVKB/Hkjn5Z8A+zLIA8CKBG8K9KXA/1gdwX6s0BfBdgS4G1AMx8IHsKuYJ/zP/Cn8/r4eQO8BKiXBnYusLsC9A2hBwNWBXgNUBsW/jCwUYW9AuwUYWcC/argbwL8XICfAvxZgB8C/DmQHwZ5MMh/gPIzQPlZoAOB9iTQN0L7B9gfB3kJ2KvBXgL2C7BHgn0Q2CdAmwLtaKAXAnYrsLNBPwroZ4G+Cth5wI4FD0fgWUBbAnYc2K3A3go2CvRSoJcCbRTgT4E+DPJTgD4E8mMgbwLyp0D5FSiXA21EoC0E2h3kFYC3gL0M2C3AXgn2eGDnAjtUoIcCbbVAxwI9FdBHgdYC7EzgPaC8Q/wV2FngVwS3P/iRwJ8F+jPIz4H8GcjPgPwM5HdAvi9Qvgna1ICOBdoY6BdBHgDWAvYHsFeAfQnsC2B/A9paoAcC7RFgD4E+CdgRYH+B8k+A/Dcg34P8DyDfA3kI5NcD7Qz0FaE/BHoK2AvgN2C/BHoY2KvAzgL7FGDnArcE2BHAA8DfD3gQWIvA/iLQngbt/0Yk/wdsgscM9k2wz8Jq5rAuwj4S7E+ijzP0bIhe5n0V0/kXYJ+JNuP45yL6mP9ZKH1D5i/L0k9ifw7py2G/EOnJ4J9B/A8f/2P8C3p0/A8k/wT6fPA/S/4i+pvAXyL50zL/n7+A5f8BNp050Wn0+REAAAAASUVORK5CYII="
LOADING_ICON_B64 = "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAANsSURBVFhH7ZldqFRlFMd/584cTTO1NDO3tLRd5sCwCgqiIqjoS4iKgqAIIkiiSAqiIggKgoKCgigo6kNRFEFQEIJoBRWhhR9aR1lWmpnkzpyZc2fOzHseXw2azp0zcybfeL/3O+d83/99G8Q/Pj4+wLeT4bnRzgC9AXoJ9BC07sa1nQH2CtBB0OLgHbQBegt0TVpbD7oBupVgJ0Anga56Bb4CuvY/2i7Gj/uAngDdDHIQ6CjQN6CVQX8L6F+BvgV6Eugh0OOgwwT3Ah0A6gM9ABoa9H+BfjQ6Pe1DoBGgiYYFPwLaGPAq0CCgDQINGLQFoGNAFw3sXaDBoIdBvwE0K9DcAvMDHQ8YFXTLlzU7ik+03cfS3wwaE3QI0Mmg34CGBQ0aOhxoX6B7gDYYNGtgHwZNAvoO6FuB3geaHXQ+aDjQrkAtDnYPqBOgTUDvAA0D+ghs02m7gb4CfQwaHTQraB3Qe0BjgHYYNCmgZUAzQHsD7Q7aEWyrQMOAJhg0W6AxQIuBfgCaBrQNaGTou0B3g9of1C9AR4EqCPYHaGdQp0AjgcYCdfMHjQr0QaCvgMYAjQbyEw36V6ANQM+BNgAFDWx/0IdAJ4KGBk0ZrBYooAfoL9AmoNEBGhp0r4HuBJoftHOgUYGGCm0taB9Qy6AdgX4ONCrQIaAOQHuBxgbaGLQDaFSob0AjgiYF+hXQ/wL9DHRH0K6gXkCTAP0END6oY1CnQIcCfQQ0GqiXfyAaFmhXoGtAjYK2BNoq0HyAFgXqClorUN+BvgMaFmhnoNUCbQ76CahToFWD1gbaGqhToI4BLQo0N+gxoMNAHQb6EWhgUDeAngN1AnQWqGOgGYH+Apor0NBA3QHtDGoUaAOguUG7gEYHegVoXFDnQGsD2gJoJ1D1gOYF+gFofNA+oG8CzQLaGdQZoK0DzQUaBTQk0LigrUELg9oM2hVoaNCWAE0B2gu0BGhaoItAo4GuB5oBNCtQd0DLgZ4EbQzou6AVg7YErQc0JdDKgLYE7Qs0Gmg10L1APQKaFmhM0O+gW4O6ARoE1C+gL4HOB3oadD5oW0ADgY4EmhXoE6BVQ1sAmuMfoDLff8ug+gAxvSdV+1K1X/UcVD25B1W/VPtDtVP1cA15qPIfqoOVelN9qPqqWu5SlYdV5QmgP4Cq/0P9b/3CeUDvxq/tB/8AAAAASUVORK5CYII="

class MediaFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MediaFlow")
        self.geometry("600x600")
        #self.resizable(False, False)

        self.info_data = None
        self.video_formats = {}
        self.audio_formats = {}
        
        # --- Carregar ícones com tratamento de erro ---
        self.search_icon = None
        self.loading_icon = None
        try:
            search_icon_data = base64.b64decode(SEARCH_ICON_B64)
            self.search_icon = ctk.CTkImage(Image.open(BytesIO(search_icon_data)), size=(24, 24))

            loading_icon_data = base64.b64decode(LOADING_ICON_B64)
            self.loading_icon = ctk.CTkImage(Image.open(BytesIO(loading_icon_data)), size=(24, 24))
        except Exception as e:
            print(f"Aviso: Não foi possível carregar os ícones. Erro: {e}")
            print("O programa continuará sem ícones.")

        # --- Frame de Busca ---
        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.pack(side="top", fill="x", padx=20, pady=(20, 10))
        self.search_frame.grid_columnconfigure(0, weight=1)

        self.url_label = ctk.CTkLabel(self.search_frame, text="URL do Mídia", font=ctk.CTkFont(size=14))
        self.url_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(0,5), sticky="w")

        self.url_entry = ctk.CTkEntry(self.search_frame, placeholder_text="https://www.youtube.com/watch?v=...", height=40)
        self.url_entry.grid(row=1, column=0, padx=(10, 5), sticky="ew")

        # Botão com texto de fallback caso o ícone falhe
        button_text = "" if self.search_icon else ">>"
        self.search_button = ctk.CTkButton(
            self.search_frame, 
            text=button_text,
            image=self.search_icon,
            width=40, height=40,
            command=self.search_url_thread
        )
        self.search_button.grid(row=1, column=1, padx=(0, 10))
        
        # --- O resto da UI ---
        self.result_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.result_frame.pack(side="top", fill="both", expand=True, padx=20, pady=10)
        
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.pack(side="bottom", fill="x", padx=20, pady=(10, 20))
        
        self.progress_bar = ctk.CTkProgressBar(self.status_frame, mode='determinate')
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.pack(fill="x", pady=(5,0))


    def search_url_thread(self):
        url = self.url_entry.get()
        if url:
            # Altera o ícone para 'carregando' somente se ele foi carregado com sucesso
            loading_image = self.loading_icon if self.loading_icon else None
            self.search_button.configure(state="disabled", image=loading_image)
            
            self.status_label.configure(text="")
            self.progress_bar.set(0)
            self.progress_bar.pack_forget() 
            thread = threading.Thread(target=self.get_video_info, args=(url,))
            thread.start()

    def get_video_info(self, url):
        try:
            # ... (Lógica de busca com yt-dlp) ...
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.info_data = ydl.extract_info(url, download=False)
            
            self.video_formats = {}
            self.audio_formats = {}
            for f in self.info_data.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') == 'none':
                    resolution = f.get('height')
                    if resolution:
                        label = f"{resolution}p"
                        if label not in self.video_formats:
                            self.video_formats[label] = f
                elif f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    ext = f.get('ext')
                    if ext not in self.audio_formats:
                        self.audio_formats[ext] = f
            
            self.after(0, self.display_video_info)

        except Exception as e:
            self.after(0, self.show_error, f"Não foi possível obter dados da URL. Erro: {type(e).__name__}")
        finally:
            # Restaura o botão para o estado normal, com o ícone de pesquisa
            search_image = self.search_icon if self.search_icon else None
            self.after(0, lambda: self.search_button.configure(state="normal", image=search_image))
            
    # O restante do código permanece igual...

    def display_video_info(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        media_info_frame = ctk.CTkFrame(self.result_frame, fg_color="#343638")
        media_info_frame.pack(fill="x", pady=10)

        thumbnail_url = self.info_data.get('thumbnail')
        if thumbnail_url:
            try:
                response = requests.get(thumbnail_url)
                response.raise_for_status() 
                img_data = Image.open(BytesIO(response.content))
                thumbnail_image = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(120, 67))
                thumbnail_label = ctk.CTkLabel(media_info_frame, image=thumbnail_image, text="")
                thumbnail_label.grid(row=0, column=0, padx=10, pady=10)
            except requests.exceptions.RequestException:
                pass

        title_label = ctk.CTkLabel(media_info_frame, text=self.info_data.get('title', 'Título não encontrado'), wraplength=400, justify="left")
        title_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        self.type_var = ctk.StringVar(value="video")
        self.resolution_var = ctk.StringVar()
        self.video_ext_var = ctk.StringVar(value="mp4")
        self.audio_ext_var = ctk.StringVar()

        type_frame = self.create_option_frame("Tipo de mídia")
        ctk.CTkRadioButton(type_frame, text="Vídeo", variable=self.type_var, value="video", command=self.toggle_options).pack(side="left", padx=10, pady=5, expand=True)
        ctk.CTkRadioButton(type_frame, text="Música", variable=self.type_var, value="audio", command=self.toggle_options).pack(side="left", padx=10, pady=5, expand=True)

        self.video_options_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        self.video_options_frame.pack(fill="x", expand=True, pady=5)
        
        resolutions = sorted(self.video_formats.keys(), key=lambda r: int(r[:-1]), reverse=True)
        if resolutions:
            self.resolution_var.set(resolutions[0])
            res_frame = self.create_option_frame("Resolução", parent=self.video_options_frame)
            for res in resolutions:
                ctk.CTkRadioButton(res_frame, text=res, variable=self.resolution_var, value=res).pack(side="left", padx=5, pady=5, expand=True)

        ext_frame = self.create_option_frame("Extensão", parent=self.video_options_frame)
        ctk.CTkRadioButton(ext_frame, text="MP4", variable=self.video_ext_var, value="mp4").pack(side="left", padx=10, pady=5, expand=True)
        ctk.CTkRadioButton(ext_frame, text="WebM", variable=self.video_ext_var, value="webm").pack(side="left", padx=10, pady=5, expand=True)

        self.audio_options_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        
        audio_exts = list(self.audio_formats.keys())
        if audio_exts:
            default_audio = 'm4a' if 'm4a' in audio_exts else audio_exts[0]
            self.audio_ext_var.set(default_audio)
            audio_ext_frame = self.create_option_frame("Formato", parent=self.audio_options_frame)
            for ext in audio_exts:
                ctk.CTkRadioButton(audio_ext_frame, text=ext.upper(), variable=self.audio_ext_var, value=ext).pack(side="left", padx=10, pady=5, expand=True)

        self.download_button = ctk.CTkButton(self.result_frame, text="Baixar Agora", height=40, command=self.download_thread)
        self.download_button.pack(fill="x", padx=10, pady=(20, 5))

    def toggle_options(self):
        if self.type_var.get() == "video":
            self.video_options_frame.pack(fill="x", expand=True, pady=5)
            self.audio_options_frame.pack_forget()
        else:
            self.video_options_frame.pack_forget()
            self.audio_options_frame.pack(fill="x", expand=True, pady=5)

    def create_option_frame(self, title, parent=None):
        if parent is None:
            parent = self.result_frame
        
        ctk.CTkLabel(parent, text=title, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 0))
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=10, pady=5)
        return frame

    def download_thread(self):
        self.download_button.configure(state="disabled", text="Baixando...")
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=(0, 5)) 
        self.status_label.configure(text="")
        
        save_path = filedialog.askdirectory()
        if not save_path:
            self.download_button.configure(state="normal", text="Baixar Agora")
            self.progress_bar.pack_forget()
            return

        thread = threading.Thread(target=self.download_media, args=(save_path,))
        thread.start()
    
    def download_media(self, save_path):
        def get_ffmpeg_path():
            # Verifica se está rodando como executável empacotado
            if getattr(sys, 'frozen', False):
                 base_dir = sys._MEIPASS
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
    
            ffmpeg_path = os.path.join(base_dir, 'recursos', 'ffmpeg.exe')
    
            # Verifica se o arquivo existe
            if not os.path.isfile(ffmpeg_path):
                raise FileNotFoundError(f"ffmpeg.exe não encontrado em: {ffmpeg_path}")
        
            return ffmpeg_path
        try:
            if self.type_var.get() == "video":
                res = self.resolution_var.get()
                video_format_id = self.video_formats[res]['format_id']
                best_audio_ext = 'm4a' if 'm4a' in self.audio_formats else list(self.audio_formats.keys())[0]
                audio_format_id = self.audio_formats[best_audio_ext]['format_id']
                format_selector = f"{video_format_id}+{audio_format_id}"
                ext = self.video_ext_var.get()
                
                ydl_opts = {
                    'format': format_selector,
                    'ffmpeg_location': get_ffmpeg_path(),
                    'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                    'merge_output_format': ext,
                    'progress_hooks': [self.progress_hook],
                    'quiet': True
                }
            else:
                ext = self.audio_ext_var.get()
                
                ydl_opts = {
                    'format': f'bestaudio[ext={ext}]/bestaudio',
                    'ffmpeg_location': get_ffmpeg_path(),
                    'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'progress_hooks': [self.progress_hook],
                    'quiet': True
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.info_data['webpage_url']])

            self.after(0, self.update_status, "Download concluído!", "lightgreen")
            
        except Exception as e:
            self.after(0, self.show_error, f"Erro no download: {type(e).__name__}")
        finally:
            self.after(0, lambda: self.download_button.configure(state="normal", text="Baixar Agora"))

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total_bytes:
                progress = d['downloaded_bytes'] / total_bytes
                self.after(0, self.progress_bar.set, progress)
                status_text = f"Baixando... {d['_percent_str']} de {d['_total_bytes_str']} a {d['_speed_str']}"
                self.after(0, self.status_label.configure, {"text": status_text, "text_color": "white"})
        elif d['status'] == 'finished':
            self.after(0, self.status_label.configure, {"text": "Finalizando... mesclando arquivos.", "text_color": "white"})
            self.after(0, self.progress_bar.set, 1)

    def update_status(self, message, color):
        self.status_label.configure(text=message, text_color=color)

    def show_error(self, message):
        self.status_label.configure(text=message, text_color="#FF5555") 
        for widget in self.result_frame.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = MediaFlowApp()
    app.mainloop()