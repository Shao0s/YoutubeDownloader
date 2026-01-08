import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog
from yt_dlp import YoutubeDL

FFMPEG_PATH = r""  # Ajusta si es necesario

# --- Descarga principal ---
def download_audio(url, output_dir, fmt, quality, log_text, progress_var):
    if not url.strip():
        log_text.set("⚠️ Ingresa una URL válida de YouTube.")
        return

    os.makedirs(output_dir, exist_ok=True)

    # Plantilla de salida — título limpio, sin ID
    out_template = os.path.join(output_dir, "%(title)s.%(ext)s")

    # Configuración de yt_dlp
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_template,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [lambda d: progress_hook(d, log_text, progress_var)],
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": fmt,
                "preferredquality": quality,
            },
            {"key": "FFmpegMetadata"},
        ],
        "ffmpeg_location": FFMPEG_PATH if FFMPEG_PATH else None,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            log_text.set("⏳ Descargando audio...")
            ydl.download([url])
            progress_var.set(100)
            log_text.set("✅ Descarga completada correctamente.")
    except Exception as e:
        log_text.set(f"❌ Error: {e}")


def progress_hook(d, log_text, progress_var):
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "0%").strip().replace("%", "")
        progress_var.set(float(percent))
        log_text.set(f"⬇️ Descargando... {percent}%")
    elif d["status"] == "finished":
        log_text.set("🔄 Convirtiendo a audio...")


def start_download(url_entry, output_dir, fmt_var, quality_var, log_text, progress_var):
    threading.Thread(
        target=download_audio,
        args=(url_entry.get(), output_dir, fmt_var.get(), quality_var.get(), log_text, progress_var),
        daemon=True,
    ).start()


def choose_directory(entry_widget):
    folder = filedialog.askdirectory()
    if folder:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, folder)


# --- Interfaz estilo VLC ---
def main():
    root = tk.Tk()
    root.title("🎧 YouTube Audio Downloader")
    root.geometry("520x580")
    root.configure(bg="#e6e6e6")
    root.resizable(False, False)

    # --- Tema y estilos tipo VLC ---
    style = ttk.Style(root)
    style.theme_use("clam")

    ORANGE = "#f77f00"
    DARK_ORANGE = "#d06900"
    BG = "#e6e6e6"
    TEXT = "#222"

    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
    style.configure("TEntry", padding=4, relief="flat", fieldbackground="white")
    style.configure(
        "TButton",
        background=ORANGE,
        foreground="white",
        font=("Segoe UI", 10, "bold"),
        borderwidth=0,
        padding=6,
    )
    style.map(
        "TButton",
        background=[("active", DARK_ORANGE)],
        relief=[("pressed", "sunken")],
    )
    style.configure(
        "Horizontal.TProgressbar",
        troughcolor="#cccccc",
        background=ORANGE,
        thickness=15,
    )

    # Variables
    fmt_var = tk.StringVar(value="mp3")
    quality_var = tk.StringVar(value="320")
    log_text = tk.StringVar(value="Esperando acción...")
    progress_var = tk.DoubleVar(value=0)

    # --- Cabecera ---
    header = ttk.Label(
        root,
        text="🎵 YouTube Audio Downloader",
        font=("Segoe UI", 16, "bold"),
        foreground=ORANGE,
        background=BG,
    )
    header.pack(pady=15)

    # --- Frame URL ---
    frame_url = ttk.LabelFrame(root, text="Enlace del video", padding=10)
    frame_url.pack(fill="x", padx=15, pady=5)
    url_entry = ttk.Entry(frame_url, width=60)
    url_entry.pack(pady=5)

    # --- Frame salida ---
    frame_out = ttk.LabelFrame(root, text="Carpeta de salida", padding=10)
    frame_out.pack(fill="x", padx=15, pady=5)
    out_entry = ttk.Entry(frame_out, width=45)
    out_entry.insert(0, os.getcwd())
    out_entry.pack(side="left", padx=5)
    ttk.Button(
        frame_out, text="Elegir...", command=lambda: choose_directory(out_entry)
    ).pack(side="left")

    # --- Configuración ---
    frame_cfg = ttk.LabelFrame(root, text="Configuración", padding=10)
    frame_cfg.pack(fill="x", padx=15, pady=5)

    ttk.Label(frame_cfg, text="Formato:").grid(row=0, column=0, sticky="w", padx=5)
    fmt_combo = ttk.Combobox(
        frame_cfg,
        textvariable=fmt_var,
        values=["mp3", "m4a", "wav", "opus"],  # ✅ OGG agregado
        width=10,
        state="readonly",
    )
    fmt_combo.grid(row=1, column=0, padx=5, pady=3)

    ttk.Label(frame_cfg, text="Calidad (kbps):").grid(row=0, column=1, sticky="w", padx=5)
    ttk.Entry(frame_cfg, textvariable=quality_var, width=10).grid(
        row=1, column=1, padx=5, pady=3
    )

    # --- Botón descargar ---
    ttk.Button(
        root,
        text="⬇️ Descargar",
        command=lambda: start_download(
            url_entry, out_entry.get(), fmt_var, quality_var, log_text, progress_var
        ),
    ).pack(pady=20)

    # --- Barra de progreso ---
    ttk.Progressbar(
        root,
        variable=progress_var,
        maximum=100,
        mode="determinate",
        length=460,
    ).pack(pady=5)

    # --- Estado ---
    ttk.Label(
        root,
        textvariable=log_text,
        wraplength=460,
        justify="center",
        foreground="#444",
    ).pack(pady=10)

    # --- Botón salir ---
    ttk.Button(root, text="Salir", command=root.destroy).pack(pady=5)

    root.mainloop()


if __name__ == "__main__":
    main()

