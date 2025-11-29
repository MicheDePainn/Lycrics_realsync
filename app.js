let allLyrics = [];

document.addEventListener('DOMContentLoaded', () => {
    fetch('database.json')
        .then(response => response.json())
        .then(data => {
            allLyrics = data;
        })
        .catch(err => console.error("Erreur chargement DB:", err));

    const searchInput = document.getElementById('search-input');
    searchInput.focus(); // Focus automatique au chargement
    searchInput.addEventListener('input', (e) => handleSearch(e.target.value));
});

function handleSearch(query) {
    const container = document.getElementById('results-container');
    container.innerHTML = ''; 

    if (!query || query.length < 1) return; // Recherche dès 1 caractère

    const lowerQuery = query.toLowerCase();
    const results = allLyrics.filter(file => 
        file.filename.toLowerCase().includes(lowerQuery)
    );

    displayResults(results);
}

function displayResults(results) {
    const container = document.getElementById('results-container');
    
    if (results.length === 0) {
        // Message discret si rien trouvé
        const msg = document.createElement('div');
        msg.style.color = '#999';
        msg.style.fontSize = '0.9rem';
        msg.style.padding = '10px 0';
        msg.innerText = 'Aucun fichier correspondant.';
        container.appendChild(msg);
        return;
    }

    results.forEach(item => {
        const card = document.createElement('div');
        card.className = 'result-card';
        
        // Liste simple avec une petite icône fichier texte
        card.innerHTML = `
            <span class="song-icon">📄</span>
            <span class="song-title">${item.filename}</span>
        `;
        
        card.addEventListener('click', () => openFileModal(item.path, item.filename));
        container.appendChild(card);
    });
}

function openFileModal(path, filename) {
    fetch(path)
        .then(res => res.text())
        .then(text => {
            document.getElementById('modal-title').innerText = filename;
            document.getElementById('modal-body').textContent = text;
            
            const downloadBtn = document.getElementById('download-btn');
            downloadBtn.href = path;
            downloadBtn.download = filename;

            const modal = document.getElementById('lyrics-modal');
            modal.classList.remove('hidden');
        });
}

document.getElementById('close-modal').addEventListener('click', () => {
    document.getElementById('lyrics-modal').classList.add('hidden');
});

// Fermeture avec la touche Echap
document.addEventListener('keydown', (event) => {
    if (event.key === "Escape") {
        document.getElementById('lyrics-modal').classList.add('hidden');
    }
});

window.onclick = function(event) {
    const modal = document.getElementById('lyrics-modal');
    if (event.target == modal) {
        modal.classList.add('hidden');
    }
}