document.getElementById('createGame').addEventListener('click', function() {
    fetch('/create_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
        })
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Request failed');
    })
    .then(data => {
        window.location.href = data.redirect; // Redirect to the URL provided by the server
    })
    .catch(error => {
        console.log('Error:', error);
    });
});