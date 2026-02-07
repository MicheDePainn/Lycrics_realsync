let allLyrics = [];
let currentResults = [];
let selectedIndex = -1;

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    
    searchInput.disabled = true;
    searchInput.placeholder = "Chargement des paroles...";

    fetch('database.json')
        .then(response => response.json())
        .then(data => {
            allLyrics = data.map(item => {
                let name = item.filename.replace('.lrc', '');
                let parts = name.split(' - ');
                return {
                    ...item,
                    title: parts[0] || name,
                    artist: parts[1] || 'Artiste inconnu'
                };
            });
            searchInput.disabled = false;
            searchInput.placeholder = "Rechercher un titre ou un artiste...";
            searchInput.focus();
        })
        .catch(err => {
            console.error("Erreur chargement DB:", err);
            searchInput.placeholder = "Erreur de chargement.";
        });

    searchInput.addEventListener('input', (e) => handleSearch(e.target.value));
    searchInput.addEventListener('keydown', handleKeyNavigation);

    document.getElementById('close-modal').addEventListener('click', closeModal);
    document.getElementById('copy-btn').addEventListener('click', copyLyricsToClipboard);
    
    document.addEventListener('keydown', (event) => {
        if (event.key === "Escape") closeModal();
    });

    window.onclick = function(event) {
        const modal = document.getElementById('lyrics-modal');
        if (event.target == modal) closeModal();
    }
});

function handleSearch(query) {
    const container = document.getElementById('results-container');
    container.innerHTML = ''; 
    selectedIndex = -1;

    if (!query || query.trim().length < 1) {
        currentResults = [];
        return; 
    }

    const lowerQuery = query.toLowerCase();
    currentResults = allLyrics.filter(file => 
        file.title.toLowerCase().includes(lowerQuery) || 
        file.artist.toLowerCase().includes(lowerQuery) ||
        file.filename.toLowerCase().includes(lowerQuery)
    );

    displayResults(currentResults);
}

function displayResults(results) {
    const container = document.getElementById('results-container');
    
    if (results.length === 0) {
        const msg = document.createElement('div');
        msg.style.color = 'var(--text-muted)';
        msg.style.fontSize = '1rem';
        msg.style.textAlign = 'center';
        msg.style.padding = '40px 0';
        msg.innerText = 'Aucun titre trouvé.';
        container.appendChild(msg);
        return;
    }

    results.forEach((item, index) => {
        const card = document.createElement('div');
        card.className = 'result-card';
        card.id = `result-${index}`;
        
        card.innerHTML = `
            <div class="song-icon">🎵</div>
            <div class="song-info">
                <span class="song-title">${item.title}</span>
                <span class="song-artist">${item.artist}</span>
            </div>
        `;
        
        card.addEventListener('click', () => openFileModal(item.path, item.filename));
        
        card.addEventListener('mouseenter', () => {
            selectedIndex = index;
            updateSelection();
        });

        container.appendChild(card);
    });
}

function handleKeyNavigation(e) {
    if (currentResults.length === 0) return;

    if (e.key === 'ArrowDown') {
        e.preventDefault();
        selectedIndex = (selectedIndex + 1) % currentResults.length;
        updateSelection();
        scrollToSelection();
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        selectedIndex = (selectedIndex - 1 + currentResults.length) % currentResults.length;
        updateSelection();
        scrollToSelection();
    } else if (e.key === 'Enter') {
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < currentResults.length) {
            const item = currentResults[selectedIndex];
            openFileModal(item.path, item.filename);
        }
    }
}

function updateSelection() {
    const cards = document.querySelectorAll('.result-card');
    cards.forEach((card, index) => {
        if (index === selectedIndex) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
    });
}

function scrollToSelection() {
    const card = document.getElementById(`result-${selectedIndex}`);
    if (card) {
        card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

function formatLRCLines(text) {
    const lines = text.split('\n');
    return lines.map(line => {
        const timestampMatch = line.match(/^(\[[0-9]{2}:[0-9]{2}\.[0-9]{2}\])(.*)/);
        if (timestampMatch) {
            return `<span class="lrc-line"><span class="lrc-timestamp">${timestampMatch[1]}</span>${timestampMatch[2]}</span>`;
        }
        return `<span class="lrc-line">${line}</span>`;
    }).join('');
}

function openFileModal(path, filename) {
    fetch(path)
        .then(res => res.text())
        .then(text => {
            document.getElementById('modal-title').innerText = filename;
            document.getElementById('modal-body').innerHTML = formatLRCLines(text);
            
            const downloadBtn = document.getElementById('download-btn');
            downloadBtn.href = path;
            downloadBtn.download = filename;

            const copyBtn = document.getElementById('copy-btn');
            copyBtn.innerText = "Copier";
            copyBtn.classList.add('primary');

            const modal = document.getElementById('lyrics-modal');
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden'; // Prevent scroll
        });
}

function closeModal() {
    document.getElementById('lyrics-modal').classList.add('hidden');
    document.body.style.overflow = '';
    document.getElementById('search-input').focus();
}

function copyLyricsToClipboard() {
    // Extract raw text from innerHTML by replacing our spans or just use the textContent of container
    // Actually, textContent will give us everything without tags.
    const text = document.getElementById('modal-body').textContent;
    navigator.clipboard.writeText(text).then(() => {
        const copyBtn = document.getElementById('copy-btn');
        copyBtn.innerText = "Copié !";
        
        setTimeout(() => {
            copyBtn.innerText = "Copier";
        }, 2000);
    }).catch(err => {
        console.error('Erreur copie:', err);
    });
}