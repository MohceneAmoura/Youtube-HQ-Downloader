# Installation de FFmpeg

FFmpeg est nécessaire pour télécharger des vidéos en haute qualité (1080p, 1440p, 2160p/4K).

## Méthode 1 : Utiliser Chocolatey (recommandé)

1. Ouvrez PowerShell en administrateur
2. Installez Chocolatey (si pas déjà installé) :
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```
3. Installez FFmpeg :
   ```powershell
   choco install ffmpeg
   ```

## Méthode 2 : Téléchargement manuel

1. Téléchargez FFmpeg depuis : https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z
2. Extraire le fichier zip
3. Renommez le dossier extrait en `ffmpeg`
4. Déplacez-le dans `C:\`
5. Ajoutez `C:\ffmpeg\bin` à votre variable d'environnement PATH

## Vérification de l'installation

Ouvrez un nouveau terminal et exécutez :
```bash
ffmpeg -version
```

Si FFmpeg est installé correctement, vous verrez les informations de version.
