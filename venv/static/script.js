function getRecommendations(movieId) {
    fetch(`/recommend/${movieId}`)
        .then(response => response.json())
        .then(data => {
            const modal = document.getElementById('modal');
            const recommendationsDiv = document.getElementById('recommendations');
            recommendationsDiv.innerHTML = '';
            data.forEach(recommendation => {
                const p = document.createElement('p');
                p.textContent = recommendation;
                recommendationsDiv.appendChild(p);
            });
            modal.style.display = 'block';
        })
        .catch(error => console.error('Error:', error));
}

function closeModal() {
    const modal = document.getElementById('modal');
    modal.style.display = 'none';
}
