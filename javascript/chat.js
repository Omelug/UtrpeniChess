//TODO tohle dát do nějakého jiného souboru, je i v menu.js
function getCookie(name) {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith(name))
        ?.split('=')[1];
    return cookieValue ? decodeURIComponent(cookieValue) : null;
}

let socket = io('http://127.0.0.1:5000');
socket.on('message_received', function (data) {
    let messagesDiv = document.getElementById('chatWindow');
    messagesDiv.innerHTML += '<p class="msgP"><b>' + data.name + ': </b>' + data.message + '</p>';
    messagesDiv.scrollTop = messagesDiv.scrollHeight
});

 //set room for chat //TODO vyřešit nějak left kdyz hra skonci
const gameCode = getCookie('game_code');
if (gameCode) {
    socket.emit('join', { game_code: gameCode });
}

document.getElementById('sendMsg').addEventListener('click', sendMessageFromInput);
document.getElementById('messageInput').addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        sendMessageFromInput();
    }
});

function sendMessageFromInput() {
    let messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    if (message !== '') {
        sendMessage(message);
        messageInput.value = '';
    }
}

function sendMessage(message) {
    fetch('/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({message: message}),
    }).then(response => response.json()).catch((error) => {
        console.error('Error:', error);
    });
}

let messagesDiv = document.getElementById('chatWindow');
messagesDiv.scrollTop = messagesDiv.scrollHeight
