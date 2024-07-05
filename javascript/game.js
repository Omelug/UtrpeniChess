document.getElementById('createGame').addEventListener('click', function() {
    fetch('/create_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            // Example data
            playerName: 'John Doe',
            gameLevel: 'Easy'
        })
    })
    .then(response => {
        if (response.ok) {
            // Assuming the server sends back the URL to redirect to
            return response.text(); // Get the URL from the response
        }
        throw new Error('Request failed');
    })
    .then(url => {
        window.location.href = url; // Redirect to the URL provided by the server
    })
    .catch(error => {
        console.log('Error:', error);
    });
});