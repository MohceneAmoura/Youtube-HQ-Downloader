import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import subprocess
import sys
import json
import urllib.request


class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader Pro")
        self.root.geometry("800x620")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f0f1a")

        self.download_thread = None
        self.is_downloading = False

        self.setup_styles()
        self.setup_ui()

    # ─────────────────────────── Styles ───────────────────────────
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Labels
        style.configure("Title.TLabel",
                         font=("Segoe UI", 26, "bold"),
                         foreground="#c9b8ff",
                         background="#0f0f1a")
        style.configure("Sub.TLabel",
                         font=("Segoe UI", 11),
                         foreground="#8b8ba7",
                         background="#0f0f1a")
        style.configure("Info.TLabel",
                         font=("Segoe UI", 10),
                         foreground="#6ee7b7",
                         background="#1a1a2e")
        style.configure("Error.TLabel",
                         font=("Segoe UI", 10),
                         foreground="#f87171",
                         background="#0f0f1a")

        # Entry
        style.configure("Custom.TEntry",
                         font=("Segoe UI", 12),
                         fieldbackground="#1e1e35",
                         foreground="#e2e2f0",
                         insertcolor="#c9b8ff",
                         borderwidth=0)

        # Buttons
        style.configure("Primary.TButton",
                         font=("Segoe UI", 13, "bold"),
                         foreground="#0f0f1a",
                         background="#a78bfa",
                         padding=(20, 12))
        style.map("Primary.TButton",
                  background=[("active", "#7c3aed"), ("disabled", "#3a3a5c")])

        style.configure("Secondary.TButton",
                         font=("Segoe UI", 11),
                         foreground="#c9b8ff",
                         background="#1e1e35",
                         padding=(10, 8))
        style.map("Secondary.TButton",
                  background=[("active", "#2a2a4a")])

        # OptionMenu
        style.configure("TMenubutton",
                         font=("Segoe UI", 11),
                         foreground="#e2e2f0",
                         background="#1e1e35",
                         relief="flat",
                         padding=(8, 6))

        # Progressbar
        style.configure("Custom.Horizontal.TProgressbar",
                         troughcolor="#1e1e35",
                         background="#a78bfa",
                         thickness=12)

    # ─────────────────────────── UI Layout ────────────────────────
    def setup_ui(self):
        # ── Header ──
        header = tk.Frame(self.root, bg="#0f0f1a")
        header.pack(pady=(28, 4), padx=40, fill=tk.X)

        tk.Label(header, text="⬇  YouTube Downloader Pro",
                 font=("Segoe UI", 24, "bold"),
                 fg="#c9b8ff", bg="#0f0f1a").pack(side=tk.LEFT)

        ttk.Label(self.root,
                  text="Téléchargez en Haute Qualité — MP4 · MP3 · 4K · 1080p",
                  style="Sub.TLabel").pack(pady=(0, 18))

        # ── URL ──
        self._section(self.root, "🔗  Lien de la vidéo YouTube")
        url_frame = tk.Frame(self.root, bg="#0f0f1a")
        url_frame.pack(padx=40, fill=tk.X, pady=(0, 4))

        self.link_entry = ttk.Entry(url_frame, style="Custom.TEntry",
                                    font=("Segoe UI", 12))
        self.link_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        self.link_entry.bind("<Return>", lambda e: self.fetch_info())

        ttk.Button(url_frame, text="Aperçu",
                   command=self.fetch_info,
                   style="Secondary.TButton").pack(side=tk.LEFT, padx=(8, 0))

        # ── Video Info Card ──
        self.info_frame = tk.Frame(self.root, bg="#1a1a2e",
                                   relief="flat", bd=0)
        self.info_frame.pack(padx=40, fill=tk.X, pady=(8, 4))
        self.info_label = tk.Label(self.info_frame, text="",
                                   font=("Segoe UI", 10),
                                   fg="#6ee7b7", bg="#1a1a2e",
                                   anchor="w", justify="left")
        self.info_label.pack(padx=12, pady=8, fill=tk.X)

        # ── Format + Quality Row ──
        options_row = tk.Frame(self.root, bg="#0f0f1a")
        options_row.pack(padx=40, fill=tk.X, pady=(10, 0))

        # Format
        fmt_col = tk.Frame(options_row, bg="#0f0f1a")
        fmt_col.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        self._section(fmt_col, "📁  Format")
        self.format_var = tk.StringVar(value="MP4 (Vidéo)")
        fmt_menu = ttk.OptionMenu(fmt_col, self.format_var,
                                  "MP4 (Vidéo)",
                                  "MP4 (Vidéo)",
                                  "MP3 (Audio seulement)",
                                  command=self._on_format_change)
        fmt_menu.pack(fill=tk.X, ipady=4)

        # Quality
        qual_col = tk.Frame(options_row, bg="#0f0f1a")
        qual_col.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(10, 0))
        self._section(qual_col, "🎬  Qualité")
        self.quality_var = tk.StringVar(value="Meilleure qualité")
        self.quality_options = [
            "Meilleure qualité", "2160p (4K)", "1440p (2K)",
            "1080p (Full HD)", "720p (HD)", "480p", "360p"
        ]
        self.quality_menu = ttk.OptionMenu(qual_col, self.quality_var,
                                           "Meilleure qualité",
                                           *self.quality_options)
        self.quality_menu.pack(fill=tk.X, ipady=4)

        # ── Destination ──
        self._section(self.root, "📂  Dossier de destination")
        path_frame = tk.Frame(self.root, bg="#0f0f1a")
        path_frame.pack(padx=40, fill=tk.X, pady=(0, 14))

        self.path_var = tk.StringVar(value=os.path.expanduser("~\\Downloads"))
        self.path_entry = ttk.Entry(path_frame, style="Custom.TEntry",
                                    textvariable=self.path_var,
                                    font=("Segoe UI", 11))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)

        ttk.Button(path_frame, text="Parcourir",
                   command=self.browse_folder,
                   style="Secondary.TButton").pack(side=tk.LEFT, padx=(8, 0))

        # ── Download Button ──
        self.download_btn = ttk.Button(self.root,
                                       text="⬇  Télécharger",
                                       command=self.start_download,
                                       style="Primary.TButton")
        self.download_btn.pack(pady=(4, 10))

        # ── Progress ──
        prog_frame = tk.Frame(self.root, bg="#0f0f1a")
        prog_frame.pack(padx=40, fill=tk.X)

        self.progress = ttk.Progressbar(prog_frame,
                                         orient=tk.HORIZONTAL,
                                         mode="determinate",
                                         style="Custom.Horizontal.TProgressbar")
        self.progress.pack(fill=tk.X, ipady=2)

        self.pct_label = tk.Label(prog_frame, text="",
                                   font=("Segoe UI", 9),
                                   fg="#8b8ba7", bg="#0f0f1a", anchor="e")
        self.pct_label.pack(fill=tk.X)

        # ── Status ──
        self.status_label = tk.Label(self.root, text="",
                                      font=("Segoe UI", 11),
                                      fg="#a78bfa", bg="#0f0f1a")
        self.status_label.pack(pady=(6, 2))

        # ── Footer note ──
        tk.Label(self.root,
                 text="Utilise yt-dlp + FFmpeg • Haute qualité garantie",
                 font=("Segoe UI", 9),
                 fg="#3d3d5c", bg="#0f0f1a").pack(pady=(4, 8))

    # ─────────────── Helpers ───────────────
    def _section(self, parent, text):
        ttk.Label(parent, text=text, style="Sub.TLabel").pack(
            anchor=tk.W, padx=(0 if parent != self.root else 40), pady=(6, 2))

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)

    def _on_format_change(self, value):
        if "MP3" in value:
            self.quality_menu.configure(state="disabled")
        else:
            self.quality_menu.configure(state="normal")

    def set_status(self, text, color="#a78bfa"):
        self.root.after(0, lambda: self.status_label.config(text=text, fg=color))

    def set_progress(self, pct):
        self.root.after(0, lambda: self.progress.config(value=pct))
        self.root.after(0, lambda: self.pct_label.config(
            text=f"{pct:.1f}%" if pct > 0 else ""))

    # ─────────────── Check / Install yt-dlp ───────────────
    def check_ytdlp(self):
        """Return yt-dlp invocation list. Uses 'python -m yt_dlp' to avoid PATH issues."""
        # Prefer module invocation — always works regardless of PATH
        result = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--version"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return [sys.executable, "-m", "yt_dlp"]

        # Not installed — try to install automatically
        self.set_status("Installation de yt-dlp…")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "yt-dlp"],
                check=True, capture_output=True
            )
            return [sys.executable, "-m", "yt_dlp"]
        except Exception:
            raise RuntimeError(
                "yt-dlp introuvable. Installez-le avec : pip install yt-dlp"
            )

    # ─────────────── Fetch video info ───────────────
    def fetch_info(self):
        url = self.link_entry.get().strip()
        if not url:
            return
        self.info_label.config(text="Chargement des informations…", fg="#8b8ba7")
        threading.Thread(target=self._fetch_info_thread,
                         args=(url,), daemon=True).start()

    def _fetch_info_thread(self, url):
        try:
            ytdlp = self.check_ytdlp()
            result = subprocess.run(
                ytdlp + ["--dump-json", "--no-playlist", url],
                capture_output=True, text=True, encoding="utf-8"
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip())
            data = json.loads(result.stdout)
            title = data.get("title", "Inconnu")
            duration = data.get("duration", 0)
            uploader = data.get("uploader", "")
            mins, secs = divmod(int(duration), 60)
            info = f"🎬  {title}\n⏱  {mins}:{secs:02d}   👤  {uploader}"
            self.root.after(0, lambda: self.info_label.config(
                text=info, fg="#6ee7b7"))
        except Exception as e:
            self.root.after(0, lambda: self.info_label.config(
                text=f"⚠  {e}", fg="#f87171"))

    # ─────────────── Download ───────────────
    def start_download(self):
        if self.is_downloading:
            messagebox.showwarning("En cours", "Un téléchargement est déjà en cours.")
            return
        url = self.link_entry.get().strip()
        if not url:
            messagebox.showwarning("Attention", "Veuillez entrer un lien YouTube.")
            return
        save_path = self.path_var.get().strip()
        if not os.path.isdir(save_path):
            messagebox.showwarning("Dossier invalide",
                                   "Le dossier de destination n'existe pas.")
            return

        self.is_downloading = True
        self.download_btn.config(state="disabled")
        self.progress.config(value=0)
        self.pct_label.config(text="")
        self.set_status("Démarrage du téléchargement…")

        self.download_thread = threading.Thread(
            target=self._download_thread,
            args=(url, save_path),
            daemon=True
        )
        self.download_thread.start()

    def _build_quality_format(self):
        """Convert UI quality choice to yt-dlp format string."""
        fmt = self.format_var.get()
        qual = self.quality_var.get()

        if "MP3" in fmt:
            return None  # audio-only handled separately

        res_map = {
            "Meilleure qualité": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
            "2160p (4K)":       "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best[height<=2160]",
            "1440p (2K)":       "bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]/best[height<=1440]",
            "1080p (Full HD)":  "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]",
            "720p (HD)":        "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]",
            "480p":             "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]",
            "360p":             "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]",
        }
        return res_map.get(qual, res_map["Meilleure qualité"])

    def _download_thread(self, url, save_path):
        try:
            ytdlp = self.check_ytdlp()
            fmt = self.format_var.get()
            is_audio = "MP3" in fmt

            output_template = os.path.join(save_path, "%(title)s.%(ext)s")

            cmd = ytdlp + ["--no-playlist", "--ffmpeg-location", "ffmpeg",
                          "--newline",  # one line per progress update
                          "-o", output_template]

            if is_audio:
                cmd += ["-x", "--audio-format", "mp3",
                        "--audio-quality", "0"]
                self.set_status("Téléchargement MP3 en cours…")
            else:
                fmt_str = self._build_quality_format()
                cmd += ["-f", fmt_str,
                        "--merge-output-format", "mp4"]
                self.set_status("Téléchargement en cours…")

            cmd.append(url)

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            for line in process.stdout:
                line = line.strip()
                if "[download]" in line and "%" in line:
                    # Parse percentage from yt-dlp output
                    try:
                        parts = line.split()
                        for p in parts:
                            if "%" in p:
                                pct = float(p.replace("%", ""))
                                self.set_progress(min(pct, 100))
                                self.set_status(f"Téléchargement : {line}")
                                break
                    except ValueError:
                        pass
                elif "[Merger]" in line or "[ffmpeg]" in line:
                    self.set_status("🔀 Fusion vidéo + audio…")
                elif "[ExtractAudio]" in line:
                    self.set_status("🎵 Conversion en MP3…")

            process.wait()

            if process.returncode != 0:
                raise RuntimeError(
                    "yt-dlp a échoué. Vérifiez le lien ou réessayez."
                )

            self.set_progress(100)
            self.set_status("✅  Téléchargement terminé avec succès !", "#6ee7b7")
            self.root.after(0, lambda: messagebox.showinfo(
                "Succès",
                f"Votre {'MP3' if is_audio else 'vidéo'} a été téléchargé(e) avec succès !\n\nDossier : {save_path}"
            ))

        except Exception as e:
            self.set_status(f"❌  Erreur : {e}", "#f87171")
            self.root.after(0, lambda: messagebox.showerror(
                "Erreur", str(e)))
        finally:
            self.is_downloading = False
            self.root.after(0, lambda: self.download_btn.config(state="normal"))


# ─────────────── Entry point ───────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()
