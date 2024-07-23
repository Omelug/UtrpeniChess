document.getElementById('playBtn').addEventListener('click', function() {
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

function getCookie(name) {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith(name))
        ?.split('=')[1]; // Using optional chaining for safety

    return cookieValue ? decodeURIComponent(cookieValue) : null;
}
const gameCode = getCookie('game_code');
console.log('Resume code:', gameCode);
if (gameCode) {
    document.getElementById('resume_code').textContent = 'Connected in: ' + gameCode;
}