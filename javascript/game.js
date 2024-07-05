document.getElementById('createGameButton').addEventListener('click', function() {
    fetch('/create_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            // You can include any data you want to send with the POST request here
            // Example:
            gameName: 'New Game',
            playerCount: 4
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        // Handle success, maybe update the UI or notify the user
    })
    .catch((error) => {
        console.error('Error:', error);
        // Handle error, maybe notify the user
    });
});