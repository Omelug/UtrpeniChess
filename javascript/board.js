import { getCookie } from "./basic.js";

let gameMap = {};
const chessboard = document.getElementById('chessboard');
const cellSize = 50;
let figStyle;
let socket;

async function fetchInitialMap() {
    try {
        const response = await fetch('/get_map');
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        gameMap = await response.json();
        renderChessboard(gameMap);
    } catch (error) {
        console.error('Error fetching initial game map:', error);
    }
}
function hexToRgb(hex) {
    hex = hex.replace(/^#?([a-f\d])([a-f\d])([a-f\d])$/i, (m, r, g, b) => r + r + g + g + b + b);
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? { r: parseInt(result[1], 16), g: parseInt(result[2], 16), b: parseInt(result[3], 16) } : null;
}

function transformSvg(figure_id,to_x, to_y) {
    const pieceSvg = document.querySelector(`svg[id="${figure_id}"]`);
    if (pieceSvg) {
        pieceSvg.setAttribute('pos_x', to_x);
        pieceSvg.setAttribute('pos_y', to_y);
        let viewAngle = (90 * getCookie('view')) % 360;
        pieceSvg.style.transform = `translate(${to_x * cellSize}px, ${to_y * cellSize}px) rotate(${-viewAngle}deg)`;
    } else {
        console.error(`No SVG found for figure_id ${figure_id}`);
    }
}
function removeFigureById(kill_id) {
    const pieceSvg = document.querySelector(`svg[id="${kill_id}"]`);
    if (pieceSvg) pieceSvg.remove();
    else console.error(`No SVG found for kill_id ${kill_id}`);
}
const filterCache = new Map();
//TODO all these colors fix somehow
function generateFilterValues(rgb) {
    const rgbKey = `${rgb.r},${rgb.g},${rgb.b}`;
    if (filterCache.has(rgbKey)) return filterCache.get(rgbKey);
    const { r, g, b } = rgb;
    const sepia = 1;
    const rgbToHsl = (r, g, b) => {
        r /= 255;
        g /= 255;
        b /= 255;
        const max = Math.max(r, g, b), min = Math.min(r, g, b);
        let h, s, l = (max + min) / 2;
        if (max === min) {
            h = s = 0; // achromatic
        } else {
            const d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
            switch (max) {
                case r: h = (g - b) / d + (g < b ? 6 : 0); break;
                case g: h = (b - r) / d + 2; break;
                case b: h = (r - g) / d + 4; break;
            }
            h /= 6;
        }
        return [h * 360, s, l];
    };

    const [h, s, l] = rgbToHsl(r, g, b);
    const filterValues = `sepia(${sepia}) saturate(${s * 100}%) hue-rotate(${h}deg) brightness(${l * 2}) contrast(${1 + (l - 0.5) * 2})`;
    filterCache.set(rgbKey, filterValues);
    return filterValues;
}

let selectedRow = -1, selectedCol = -1, targetRow = -1, targetCol = -1;
function renderChessboard(data) {
    chessboard.innerHTML = '';
    const boardSize = data.start.size;
    const chessboardWidth = boardSize * cellSize;

    chessboard.style.width = `${chessboardWidth}px`;
    chessboard.style.height = `${chessboardWidth}px`;
    chessboard.style.position = 'relative';


    let viewAngle = (90 * getCookie('view')) % 360;
    chessboard.style.transform = `rotate(${viewAngle}deg)`;

    //First turn label
    document.getElementById('turn').textContent = 'Turn: ' + data.status.turn;

    for (let row = 0; row < boardSize; row++) {
        for (let col = 0; col < boardSize; col++) {
            const cell = document.createElement('div');
            cell.classList.add('cell', (row + col) % 2 === 0 ? 'light' : 'dark');
            cell.setAttribute('cell_x', col);
            cell.setAttribute('cell_y', row);
            cell.style.width = `${cellSize}px`;
            cell.style.height = `${cellSize}px`;
            chessboard.appendChild(cell);
            cell.addEventListener('click', () => {
                if (selectedRow === -1 && selectedCol === -1) {
                    cell.classList.add('selected');
                    cell.style.background = 'green';
                    selectedCol = col;
                    selectedRow = row;
                } else if (targetRow === -1 && targetCol === -1) {
                    //Basic check for less server calls
                    // SAme check are in python for security reasons
                    if (selectedRow !== targetRow || selectedCol !== targetRow) {
                        //console.log("Try ", selectedCol, selectedRow," to ", col, row)
                        turn(selectedCol, selectedRow, col, row);
                    }
                    const previousSelectedCell = document.querySelector('.cell.selected');
                    if (previousSelectedCell) {
                        previousSelectedCell.style.background = '';
                        previousSelectedCell.classList.remove('selected');
                    }
                    selectedRow = selectedCol = targetRow = targetCol = -1;
                }
            });
        }
    }

//const piece = findPieceAtPosition(data, col, row);
    for (const key in data.status.figures) {
        const figure = data.status.figures[key];
        const fig_Svg = document.createElement('svg');
        fig_Svg.style.position = 'absolute';
        fig_Svg.style.width = `${cellSize}px`;
        fig_Svg.style.height = `${cellSize}px`;
        fig_Svg.setAttribute('pos_x', figure.x);
        fig_Svg.setAttribute('pos_y', figure.y);
        fig_Svg.setAttribute('id', key);
        fig_Svg.setAttribute('color', figure.color);
        fig_Svg.style.top ="0";
        fig_Svg.style.left = "0";
        figStyle = data.start.fig_style;
        fig_Svg.style.backgroundImage = `url("../static/figures/${figStyle}/${figure.fig_type}.svg")`;
        fig_Svg.style.backgroundSize = 'contain';
        fig_Svg.style.backgroundRepeat = 'no-repeat';
        fig_Svg.style.backgroundPosition = 'center';
        fig_Svg.style.pointerEvents = 'none';

        const rgb = hexToRgb(data.start.colors[figure.color]);
        fig_Svg.style.filter = generateFilterValues(rgb);

        fig_Svg.style.transform = `translate(${figure.x * cellSize}px, ${figure.y * cellSize}px) rotate(${-viewAngle}deg)`;
        chessboard.appendChild(fig_Svg);
    }
}

function turn(x,y, targetCol, targetRow) {
    const figureSvg = document.querySelector(`svg[pos_x="${x}"][pos_y="${y}"]`);
    if (figureSvg) {
        const postData = { id: figureSvg.id, to: { x: targetCol, y: targetRow } }
        fetch('/turn', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(postData),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) console.log('Turn error:', data.error);
            else if (data.action_type) {
                if (data.action_type === 'change') showSelectionWindow(data.avaible, data.fig_id);
                else console.error("Not Implemented yet");
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}

function loadChat() {
    fetch('/chat')
        .then(response => response.text())
        .then(data => {
            document.getElementById('chatContainer').innerHTML = data;

            // Check if the chat script is already loaded
            if (!document.getElementById('chatScript')) {
                const script = document.createElement('script');
                script.src = '/javascript/chat.js';
                script.id = 'chatScript';
                script.type = 'module';
                document.body.appendChild(script);
            }
        })
        .catch(error => console.error('Error loading chat:', error));
}


function changeSvg(active_fig, fig_type) {
    const pieceSvg = document.querySelector(`svg[id="${active_fig}"]`);
    if (pieceSvg) pieceSvg.style.backgroundImage = `url("../static/figures/${figStyle}/${fig_type}.svg")`;
    else console.error(`No SVG ${active_fig}`);
}

function initBoard(){
    fetchInitialMap();
    socket = io();
    //set room for board (chat has separated socket) //TODO vyřešit nějak left kdyz hra skonci
    const gameCode = getCookie('game_code');
    if (gameCode) socket.emit('join_board', { game_code: gameCode });

    socket.on('fig_action', function (data) {
        if (data.killed) removeFigureById(data.killed);
        if (data.turn != null) document.getElementById('turn').textContent = 'Turn: ' + data.turn;
        if (data.active_fig != null && data.to != null) transformSvg(data.active_fig, data.to.x, data.to.y);
        if (data.change_fig != null) changeSvg(data.change_fig, data.fig_type);
    });
}

function showSelectionWindow(changeOptions, figureId) {
    const modal = document.createElement('div');
    modal.style.position = 'fixed';
    modal.style.top = '50%';
    modal.style.left = '50%';
    modal.style.transform = 'translate(-50%, -50%)';
    modal.style.backgroundColor = 'white';
    modal.style.border = '1px solid black';
    modal.style.padding = '20px';
    modal.style.zIndex = '1000';

    const title = document.createElement('h3');
    title.textContent = 'Select a new figure';
    modal.appendChild(title);

    changeOptions.forEach(fig_type => {
        const button = document.createElement('button');
        button.textContent = fig_type;
        button.addEventListener('click', () => {
            console.log(`Selected figure: ${fig_type}`);
            document.body.removeChild(modal);
            socket.emit('figure_selected', { fig_type: fig_type, fig_id: figureId });
        });
        modal.appendChild(button);
    });
    document.body.appendChild(modal);
}

document.addEventListener('DOMContentLoaded', initBoard);
document.addEventListener('DOMContentLoaded', loadChat);

