#!/usr/bin/env python3
import requests
import re
import os
import xml.etree.ElementTree as ET
import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# --- CONFIGURATION ---
DEFAULT_LYRICS_DIR = os.path.join(os.path.dirname(__file__), 'lyrics')
TOKEN_FILE = "user_token.txt"
DEFAULT_BEARER_TOKEN = "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IldlYlBsYXl1ci1TaWcifQ.eyJpc3MiOiJBcHBsZSIsInHMiOiJjZW50YXVyLndlYnBsYXllciIsImV4cCI6MTgwMDAwMDAwMH0.1_d0_2A43J-a0-7F-80-00-5A-05-6B-4C-05-4D-3E-01-7F-5F-1C-03-3E-5C-2D-6F-5F-7C-1E-2B-3F-4D-5E-6A"

class AppleMusicLyrics:
    def __init__(self, output_dir=DEFAULT_LYRICS_DIR):
        self.output_dir = output_dir
        self.lock = Lock()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Origin': 'https://music.apple.com',
            'Accept': 'application/json'
        })
        self.bearer_token = self._get_bearer_token()
        self.media_user_token = self._load_user_token()
        self._update_auth_headers()
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _get_bearer_token(self):
        """Récupère le Bearer Token depuis le site web d'Apple Music ou utilise le défaut."""
        try:
            r = self.session.get('https://music.apple.com/us/browse')
            r.raise_for_status()
            js_files = re.findall(r'src="(/assets/[^"]+\.js)"', r.text)
            for js_file in js_files:
                try:
                    jr = self.session.get('https://music.apple.com' + js_file)
                    if jr.status_code == 200:
                        m = re.search(r'(eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVC[\w\-]+\.eyJ[\w\-]+\.[\w\-]+)', jr.text)
                        if m:
                            return m.group(1)
                except Exception:
                    continue
        except Exception as e:
            print(f"⚠️ Impossible de récupérer le token web, utilisation du défaut. ({e})")
        return DEFAULT_BEARER_TOKEN

    def _load_user_token(self):
        """Charge ou demande le Media-User-Token."""
        token = ""
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                token = f.read().strip()
        
        if not token:
            print("\n⚠️ Media-User-Token manquant.")
            print("Pour l'obtenir : Connectez-vous sur music.apple.com, ouvrez la console développeur (F12),")
            print("allez dans l'onglet Application > Storage > Local Storage, et copiez la valeur de 'media-user-token'.")
            token = input("Collez votre media-user-token ici : ").strip()
            if token:
                with open(TOKEN_FILE, 'w') as f:
                    f.write(token)
        return token

    def _update_auth_headers(self):
        self.session.headers.update({
            'Authorization': f'Bearer {self.bearer_token}',
            'Media-User-Token': self.media_user_token
        })

    def search(self, term, limit=5):
        """Recherche une chanson."""
        url = "https://amp-api.music.apple.com/v1/catalog/fr/search"
        params = {'term': term, 'types': 'songs', 'limit': limit}
        try:
            res = self.session.get(url, params=params)
            res.raise_for_status()
            data = res.json()
            return data.get('results', {}).get('songs', {}).get('data', [])
        except Exception as e:
            print(f"❌ Erreur lors de la recherche '{term}': {e}")
            return []

    def get_user_playlists(self):
        """Récupère toutes les playlists de la bibliothèque."""
        url = "https://amp-api.music.apple.com/v1/me/library/playlists"
        playlists = []
        offset = 0
        limit = 100
        
        print("⏳ Chargement des playlists...")
        while True:
            params = {'offset': offset, 'limit': limit}
            try:
                res = self.session.get(url, params=params)
                res.raise_for_status()
                data = res.json()
                batch = data.get('data', [])
                if not batch: break
                playlists.extend(batch)
                if len(batch) < limit: break
                offset += limit
            except Exception as e:
                print(f"❌ Erreur récupération playlists: {e}")
                break
        return playlists

    def get_playlist_tracks(self, playlist_id):
        """Récupère les pistes d'une playlist."""
        url = f"https://amp-api.music.apple.com/v1/me/library/playlists/{playlist_id}/tracks"
        tracks = []
        offset = 0
        limit = 100
        
        print("⏳ Chargement des pistes...", end='\r')
        while True:
            params = {'offset': offset, 'limit': limit}
            try:
                res = self.session.get(url, params=params)
                res.raise_for_status()
                data = res.json()
                batch = data.get('data', [])
                if not batch: break
                tracks.extend(batch)
                print(f"⏳ Chargement des pistes... ({len(tracks)})", end='\r')
                if len(batch) < limit: break
                offset += limit
            except Exception as e:
                print(f"\n❌ Erreur récupération pistes: {e}")
                break
        print("") # Newline
        return tracks

    def get_library_songs(self):
        """Récupère toutes les chansons de la bibliothèque."""
        url = "https://amp-api.music.apple.com/v1/me/library/songs"
        songs = []
        offset = 0
        limit = 100
        
        print("⏳ Chargement de la bibliothèque...", end='\r')
        while True:
            params = {'offset': offset, 'limit': limit}
            try:
                res = self.session.get(url, params=params)
                res.raise_for_status()
                data = res.json()
                batch = data.get('data', [])
                if not batch: break
                songs.extend(batch)
                print(f"⏳ Chargement de la bibliothèque... ({len(songs)})", end='\r')
                if len(batch) < limit: break
                offset += limit
            except Exception as e:
                print(f"\n❌ Erreur récupération bibliothèque: {e}")
                break
        print("") 
        return songs

    def search_artist(self, term, limit=5):
        """Recherche un artiste."""
        url = "https://amp-api.music.apple.com/v1/catalog/fr/search"
        params = {'term': term, 'types': 'artists', 'limit': limit}
        try:
            res = self.session.get(url, params=params)
            res.raise_for_status()
            return res.json().get('results', {}).get('artists', {}).get('data', [])
        except Exception as e:
            print(f"❌ Erreur recherche artiste: {e}")
            return []

    def get_artist_albums(self, artist_id):
        """Récupère tous les albums d'un artiste."""
        url = f"https://amp-api.music.apple.com/v1/catalog/fr/artists/{artist_id}/albums"
        albums = []
        offset = 0
        limit = 100
        
        print(f"⏳ Chargement des albums...", end='\r')
        while True:
            params = {'offset': offset, 'limit': limit}
            try:
                res = self.session.get(url, params=params)
                res.raise_for_status()
                data = res.json()
                batch = data.get('data', [])
                if not batch: break
                albums.extend(batch)
                print(f"⏳ Chargement des albums... ({len(albums)})", end='\r')
                if len(batch) < limit: break
                offset += limit
            except Exception as e:
                print(f"\n❌ Erreur récupération albums: {e}")
                break
        print("")
        return albums

    def get_album_tracks(self, album_id):
        """Récupère les pistes d'un album (Catalogue)."""
        url = f"https://amp-api.music.apple.com/v1/catalog/fr/albums/{album_id}/tracks"
        try:
            res = self.session.get(url)
            res.raise_for_status()
            data = res.json()
            return data.get('data', [])
        except Exception:
            return []

    def get_charts(self, limit=50):
        """Récupère le classement (Top morceaux)."""
        url = "https://amp-api.music.apple.com/v1/catalog/fr/charts"
        params = {'types': 'songs', 'limit': limit}
        try:
            res = self.session.get(url, params=params)
            res.raise_for_status()
            data = res.json()
            # La structure des charts est un peu imbriquée
            return data.get('results', {}).get('songs', [])[0].get('data', [])
        except Exception as e:
            print(f"❌ Erreur récupération charts: {e}")
            return []

    def get_lyrics_ttml(self, song_id):
        """Tente de récupérer les paroles (Syllable > Standard)."""
        # Essai 1: Syllable Lyrics (Karaoke précis)
        try:
            url = f"https://amp-api.music.apple.com/v1/catalog/fr/songs/{song_id}/syllable-lyrics"
            res = self.session.get(url)
            if res.status_code == 200:
                data = res.json()
                if data['data']:
                    return data['data'][0]['attributes'].get('ttml'), "Syllable"
        except Exception:
            pass

        # Essai 2: Standard Lyrics
        try:
            url = f"https://amp-api.music.apple.com/v1/catalog/fr/songs/{song_id}/lyrics"
            res = self.session.get(url)
            if res.status_code == 200:
                data = res.json()
                if data['data']:
                    return data['data'][0]['attributes'].get('ttml'), "Standard"
        except Exception:
            pass
        
        return None, None

    @staticmethod
    def format_lrc_time(time_str):
        """Formate le temps pour LRC [mm:ss.xx]."""
        if not time_str: return "00:00.00"
        # Format attendu souvent HH:MM:SS.mmm ou MM:SS.mmm
        parts = time_str.split(':')
        try:
            if len(parts) == 3: # HH:MM:SS.mmm
                h, m, s = int(parts[0]), int(parts[1]), float(parts[2])
                total_min = h * 60 + m
                return f"{total_min:02d}:{s:05.2f}"
            elif len(parts) == 2: # MM:SS.mmm
                m, s = int(parts[0]), float(parts[1])
                return f"{m:02d}:{s:05.2f}"
            else:
                return time_str
        except ValueError:
            return time_str

    def ttml_to_lrc(self, ttml):
        """Convertit le XML TTML en format LRC."""
        if not ttml: return None, False
        
        # Nettoyage des namespaces
        ttml = re.sub(r'\sxmlns[^\"]+\"[^\"]+"', '', ttml)
        ttml = ttml.replace('itunes:', '').replace('ttm:', '')
        
        try:
            root = ET.fromstring(ttml)
            lines = []
            is_karaoke = False
            
            for p in root.findall('.//p'):
                begin = p.attrib.get('begin', '00:00.000')
                lrc_time = self.format_lrc_time(begin)
                agent = p.attrib.get('agent', '')
                prefix = f"{agent}: " if agent else "" # Espace ajouté après l'agent pour lisibilité
                
                spans = p.findall('./span')
                # Vérifie si on a des timings syllabiques
                has_sub_timings = spans and any('begin' in s.attrib for s in spans)
                
                if has_sub_timings:
                    is_karaoke = True
                    content = ""
                    for s in spans:
                        txt = "".join(s.itertext())
                        s_begin = s.attrib.get('begin')
                        if s_begin:
                            content += f"<{self.format_lrc_time(s_begin)}>{txt}"
                        else:
                            content += txt
                    lines.append(f"[{lrc_time}]{prefix}{content}")
                else:
                    txt = "".join(p.itertext()).strip()
                    # Si c'est vide, parfois c'est une pause instrumentale, on peut l'ignorer ou mettre un saut
                    if txt:
                        lines.append(f"[{lrc_time}]{prefix}{txt}")
            
            return "\n".join(lines), is_karaoke
        except Exception as e:
            print(f"❌ Erreur parsing XML: {e}")
            return None, False

    def save_to_file(self, song, lrc_content):
        """Sauvegarde le fichier .lrc avec gestion des doublons et noms valides."""
        artist = song['attributes']['artistName']
        title = song['attributes']['name']
        
        # Nettoyage strict pour Windows
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title).strip()
        safe_artist = re.sub(r'[\\/*?:"<>|]', "", artist).strip()
        
        # Tronquer si trop long
        if len(safe_title) > 80: safe_title = safe_title[:80].strip()
        if len(safe_artist) > 80: safe_artist = safe_artist[:80].strip()
        
        filename = f"{safe_title} - {safe_artist}.lrc"
        
        # Section critique : Vérification et écriture atomique
        with self.lock:
            filepath = os.path.join(self.output_dir, filename)
            
            # Gestion des doublons : Ajout (1), (2)...
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(filepath):
                # Check contenu identique pour éviter doublon inutile
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        existing_content = f.read()
                    if lrc_content in existing_content:
                         return filepath
                except:
                    pass
                
                new_filename = f"{base_name} ({counter}){ext}"
                filepath = os.path.join(self.output_dir, new_filename)
                counter += 1
                
            header = f"[ti:{title}]\n[ar:{artist}]\n[offset:0]\n"
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(header + lrc_content)
                return filepath
            except Exception as e:
                print(f"❌ Erreur d'écriture fichier '{filename}': {e}")
                return None

    def process_song(self, song):
        """Télécharge et sauvegarde les paroles d'une chanson donnée."""
        title = song['attributes']['name']
        artist = song['attributes']['artistName']
        # print(f"🔄 Récupération : {title} - {artist}...", end=' ') # Désactivé pour le threading propre
        
        ttml, source = self.get_lyrics_ttml(song['id'])
        if not ttml:
            return False, f"❌ {title} - {artist} : Pas de paroles."
            
        lrc, is_k = self.ttml_to_lrc(ttml)
        if lrc:
            path = self.save_to_file(song, lrc)
            if path:
                filename = os.path.basename(path)
                return True, f"✅ {title} : {filename} ({source})"
        return False, f"❌ {title} - {artist} : Erreur conversion."

def main():
    parser = argparse.ArgumentParser(description="Apple Music Lyrics Downloader")
    parser.add_argument("query", nargs="?", help="Terme de recherche ou chemin vers un fichier texte (mode batch)")
    parser.add_argument("-b", "--batch", action="store_true", help="Traiter l'argument 'query' comme un fichier liste")
    parser.add_argument("-a", "--auto", action="store_true", help="Télécharger automatiquement le premier résultat")
    parser.add_argument("-p", "--playlist", action="store_true", help="Mode playlist : télécharger depuis une playlist utilisateur")
    parser.add_argument("-lib", "--library", action="store_true", help="Mode bibliothèque : télécharger TOUTES les chansons de la bibliothèque")
    parser.add_argument("-ar", "--artist", action="store_true", help="Mode artiste : télécharger la discographie complète d'un artiste")
    parser.add_argument("-c", "--charts", action="store_true", help="Mode Charts : télécharger le Top 100 actuel")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Nombre de téléchargements simultanés (défaut: 10)")
    parser.add_argument("-l", "--limit", type=int, default=5, help="Nombre de résultats à afficher en recherche")
    parser.add_argument("-o", "--output", help="Dossier de sortie personnalisé")
    
    args = parser.parse_args()
    
    # Initialisation
    output_dir = args.output if args.output else DEFAULT_LYRICS_DIR
    app = AppleMusicLyrics(output_dir=output_dir)

    def process_track_list(tracks, label="Morceaux"):
        """Fonction locale pour traiter une liste de pistes avec Multi-threading."""
        if not tracks:
            print(f"❌ Aucun {label} trouvé.")
            return

        print(f"🚀 Démarrage du téléchargement multi-thread ({args.threads} workers) pour {len(tracks)} {label}...\n")
        
        songs_to_process = []
        
        # Préparation des objets chansons
        for t in tracks:
            catalog_id = t.get('id')
            if 'playParams' in t['attributes']:
                 catalog_id = t['attributes']['playParams'].get('catalogId')
            
            if catalog_id:
                songs_to_process.append({
                    'id': catalog_id,
                    'attributes': {
                        'name': t['attributes']['name'],
                        'artistName': t['attributes']['artistName']
                    }
                })
            elif 'id' in t and t['type'] == 'songs': # Fallback direct catalog
                 songs_to_process.append(t)

        success_count = 0
        total = len(songs_to_process)
        
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            future_to_song = {executor.submit(app.process_song, s): s for s in songs_to_process}
            
            for i, future in enumerate(as_completed(future_to_song)):
                try:
                    success, message = future.result()
                    # Affichage d'un progress simple
                    print(f"[{i+1}/{total}] {message}")
                    if success:
                        success_count += 1
                except Exception as exc:
                    print(f"[{i+1}/{total}] ❌ Exception générée: {exc}")

        print(f"\n✨ Terminé ! {success_count}/{total} paroles téléchargées.")

    # Mode Charts
    if args.charts:
        print("🏆 Mode Charts : Récupération du Top 100...")
        tracks = app.get_charts(limit=100)
        process_track_list(tracks, "hits")
        return

    # Mode Artiste (Discographie)
    if args.artist:
        query = args.query
        if not query:
            query = input("Nom de l'artiste : ").strip()
        
        print(f"🔍 Recherche de l'artiste '{query}'...")
        artists = app.search_artist(query, limit=args.limit)
        
        if not artists:
            print("❌ Artiste introuvable.")
            return

        print("\nArtistes trouvés :")
        for i, a in enumerate(artists):
            print(f"{i+1}. {a['attributes']['name']} ({a['attributes'].get('genreNames', ['Inconnu'])[0]})")
            
        choice = 0
        if not args.auto and len(artists) > 1:
            try:
                inp = input(f"\nChoix (1-{len(artists)}) : ").strip()
                if inp.isdigit() and 1 <= int(inp) <= len(artists):
                    choice = int(inp) - 1
                else:
                    print("❌ Choix invalide.")
                    return
            except KeyboardInterrupt:
                return
        
        selected_artist = artists[choice]
        print(f"\n📂 Discographie de : {selected_artist['attributes']['name']}")
        
        albums = app.get_artist_albums(selected_artist['id'])
        if not albums:
            print("❌ Aucun album trouvé.")
            return

        all_tracks = []
        print(f"📦 Récupération des pistes de {len(albums)} albums...")
        for alb in albums:
            tracks = app.get_album_tracks(alb['id'])
            all_tracks.extend(tracks)
            
        unique_tracks = {t['id']: t for t in all_tracks}.values()
        process_track_list(list(unique_tracks), "chansons (discographie)")
        return

    # Mode Library
    if args.library:
        print("📂 Mode Bibliothèque complète")
        songs = app.get_library_songs()
        process_track_list(songs, "chansons")
        return

    # Mode Playlist
    if args.playlist:
        playlists = app.get_user_playlists()
        if not playlists:
            print("❌ Aucune playlist trouvée ou erreur de connexion.")
            return

        print("\nPlaylists disponibles :")
        for i, p in enumerate(playlists):
            print(f"{i+1}. {p['attributes']['name']}")
        
        try:
            inp = input(f"\nChoix (1-{len(playlists)}) : ").strip()
            if inp.isdigit():
                choice = int(inp) - 1
                if 0 <= choice < len(playlists):
                    selected = playlists[choice]
                    print(f"\n📂 Playlist : {selected['attributes']['name']}")
                    tracks = app.get_playlist_tracks(selected['id'])
                    process_track_list(tracks, "pistes")
                else:
                    print("❌ Choix invalide.")
            else:
                print("❌ Entrée invalide.")
        except KeyboardInterrupt:
            print("\nAnnulé.")
        return
    
    # Mode Batch (Liste de fichiers)
    if args.batch and args.query:
        if not os.path.isfile(args.query):
            print(f"❌ Le fichier '{args.query}' est introuvable.")
            return
            
        print(f"📂 Mode Batch : Lecture de '{args.query}'...")
        with open(args.query, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]
        
        print(f"Traitement de {len(lines)} termes de recherche...")
        # Pour le batch search, on garde une logique séquentielle ou on adapte ?
        # Adapter pour le multi-thread serait complexe car 'search' retourne une liste.
        # On va simplifier en faisant une recherche multi-threadée
        
        def batch_search_and_dl(term):
            res_songs = app.search(term, limit=1)
            if res_songs:
                return app.process_song(res_songs[0])
            return False, f"❌ '{term}' : Introuvable."

        success_count = 0
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            future_to_term = {executor.submit(batch_search_and_dl, line): line for line in lines}
            for i, future in enumerate(as_completed(future_to_term)):
                success, message = future.result()
                print(f"[{i+1}/{len(lines)}] {message}")
                if success: success_count += 1
                
        print(f"\n✨ Terminé ! {success_count}/{len(lines)} paroles téléchargées.")
        return

    # Mode interactif ou Single Command
    while True:
        query = args.query
        if not query:
            try:
                query = input("\nRecherche (ou 'q' pour quitter) : ").strip()
            except KeyboardInterrupt:
                break
        
        if query.lower() in ['q', 'quit', 'exit']:
            break
            
        songs = app.search(query, limit=args.limit)
        
        if not songs:
            print("❌ Aucun résultat.")
            if args.query: break
            continue
            
        choice = 0
        if args.auto or (args.query and len(songs) == 1):
            choice = 0
        else:
            print("\nRésultats :")
            for i, s in enumerate(songs):
                print(f"{i+1}. {s['attributes']['name']} - {s['attributes']['artistName']}")
            
            try:
                inp = input(f"Choix (1-{len(songs)}, défaut 1) : ").strip()
                if inp == '':
                    choice = 0
                elif inp.isdigit() and 1 <= int(inp) <= len(songs):
                    choice = int(inp) - 1
                else:
                    print("Choix invalide.")
                    if args.query: break
                    continue
            except KeyboardInterrupt:
                break

        # Single command process
        success, msg = app.process_song(songs[choice])
        print(msg)
        
        if args.query:
            break
        args.query = None 

if __name__ == "__main__":
    main()
