import { getCookie } from './basic.js';

document.getElementById('crateGamePlayBtn').addEventListener('click', function() {
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
    const gameCode = document.getElementById('game').textContent.split(': ')[1];
    socket.emit('join', { game_code: gameCode });
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
            document.getElementById('connectGameError').textContent = data.error;
            console.error('Error', data.error);
        }

    }).catch(error => {
        console.log('Error:', error);
    });
});


const gameCode = getCookie('game_code');
console.log('Resume code:', gameCode);
if (gameCode) {
    document.getElementById('resume_code').textContent = 'Connected in: ' + gameCode;
}