# Guide Complet d'Utilisation - Apple Music Lyrics Downloader

Ce script Python permet de télécharger les paroles synchronisées (format .LRC) directement depuis les serveurs d'Apple Music. Il prend en charge les paroles "syllabiques" (Karaoké précis) lorsqu'elles sont disponibles.

## ✨ Fonctionnalités Principales

*   **Recherche & Téléchargement** : Trouvez n'importe quelle chanson.
*   **Playlists** : Téléchargez toutes les chansons de vos playlists personnelles.
*   **Bibliothèque** : Téléchargez l'intégralité de votre bibliothèque musicale ("Ajouts récents").
*   **Discographie Artiste** : Téléchargez TOUS les albums et TOUTES les chansons d'un artiste en une seule commande.
*   **Charts** : Téléchargez le Top 100 actuel.
*   **Multi-threading** : Téléchargements ultra-rapides (parallélisés).
*   **Gestion des doublons** : Ne télécharge pas deux fois la même chose, et renomme intelligemment les fichiers si nécessaire.

---

## 🚀 Installation & Prérequis

1.  **Python 3** doit être installé.
2.  Installez les dépendances :
    ```bash
    pip install requests
    ```
3.  **Token Utilisateur** : Au premier lancement, le script vous demandera un "Media-User-Token".
    *   Connectez-vous sur [music.apple.com](https://music.apple.com).
    *   Ouvrez la console développeur (F12) -> Onglet "Application" -> "Storage" -> "Local Storage".
    *   Copiez la valeur de la clé `media-user-token` et collez-la dans le script. Elle sera sauvegardée dans `user_token.txt`.

---

## 📖 Exemples d'Utilisation

### 1. Recherche Simple (Mode Interactif)
Lancez simplement le script pour chercher manuellement :
```bash
python apple_lyrics.py
```
*Tapez votre recherche, choisissez le résultat, c'est téléchargé.*

Ou cherchez directement :
```bash
python apple_lyrics.py "Michael Jackson Thriller"
```

### 2. Télécharger une Playlist
Affiche vos playlists Apple Music et vous demande d'en choisir une pour tout télécharger.
```bash
python apple_lyrics.py --playlist
```
*Astuce : Ajoutez `-t 20` pour aller plus vite.*

### 3. Télécharger TOUTE votre Bibliothèque
Récupère toutes les chansons ajoutées à votre bibliothèque Apple Music.
```bash
python apple_lyrics.py --library --threads 20
```

### 4. Mode "Machine de Guerre" : Discographie Artiste
Télécharge **tous** les albums et **toutes** les chansons d'un artiste spécifique. Idéal pour compléter une collection.
```bash
python apple_lyrics.py --artist "Queen" --threads 50
```
*Note : Le script gère les doublons automatiquement.*

### 5. Mode Charts (Top 100)
Télécharge les 100 chansons les plus populaires du moment.
```bash
python apple_lyrics.py --charts
```

### 6. Mode Batch (Liste de fichiers)
Si vous avez un fichier texte `liste.txt` contenant des titres (un par ligne) :
```bash
python apple_lyrics.py -b liste.txt --threads 20
```

---

## ⚙️ Options Avancées

| Option | Description | Exemple |
| :--- | :--- | :--- |
| `-t`, `--threads` | Nombre de téléchargements simultanés (Défaut: 10). Augmentez pour aller plus vite. | `-t 50` |
| `-o`, `--output` | Dossier de sauvegarde personnalisé. | `-o "C:\Mes Paroles"` |
| `-a`, `--auto` | Ne pose pas de question, télécharge le 1er résultat trouvé (utile pour les scripts). | `--auto` |
| `-l`, `--limit` | Nombre de résultats à afficher lors d'une recherche (Défaut: 5). | `-l 10` |

---

## ❓ FAQ

**Q: Les fichiers ont des noms bizarres comme "Titre (1).lrc" ?**
R: C'est normal. Si une chanson existe déjà (ex: version Album et version Single), le script ajoute un numéro pour ne pas écraser l'ancien fichier tout en conservant les deux versions.

**Q: Le script plante ou s'arrête ?**
R: Vérifiez votre connexion internet. Si vous utilisez `-t 100` ou plus, Apple peut bloquer temporairement votre connexion. Restez autour de 20-50 threads.

**Q: Token expiré ?**
R: Si le script ne fonctionne plus, supprimez le fichier `user_token.txt` et relancez le script pour entrer un nouveau token.