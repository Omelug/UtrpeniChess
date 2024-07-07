document.getElementById('createGame').addEventListener('click', function() {
    fetch('/create_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
    }).then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Request failed');
    }).then(data => {
        window.location.href = data.redirect;
    }).catch(error => {
        console.log('Error:', error);
    });
});

document.getElementById('connectGameBtn').addEventListener('click', function() {
    fetch('/connect_to_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            game_code: document.getElementById('gameCode').value,
            player_name: document.getElementById('playerName').value
        })
    }).then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Request failed');
    }).then(data => {
        if (data.redirect) {
            window.location.href = data.redirect;
        } else {
            console.error('Error', data.error);
        }

    }).catch(error => {
        console.log('Error:', error);
    });
});
