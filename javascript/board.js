import { getCookie } from "./basic.js";

let gameMap = {};
const chessboard = document.getElementById('chessboard');
const cellSize = 50;
let figStyle;
let socket;

async function fetchInitialMap() {
    try {
        const response = await fetch('/get_map');
        if (!response.ok) {
            console.error(`HTTP error! Status: ${response.status}`);
        }
        gameMap = await response.json();
        renderChessboard(gameMap);
    } catch (error) {
        console.error('Error fetching initial game map:', error);
    }
}
function hexToRgb(hex) {
    const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
    hex = hex.replace(shorthandRegex, (m, r, g, b) => r + r + g + g + b + b);
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

function transformSvg(figure_id,to_x, to_y) {
    const selector = `svg[id="${figure_id}"]`;
    const pieceSvg = document.querySelector(selector);
    pieceSvg.setAttribute('pos_x', to_x);
    pieceSvg.setAttribute('pos_y', to_y);
    if (pieceSvg) {
        let viewAngle = (90 * getCookie('view')) % 360; // Ensure the angle stays within 0-359 degrees
        pieceSvg.style.transform = `translate(${to_x * cellSize}px, ${to_y * cellSize}px) rotate(${-viewAngle}deg)`;
    } else {
        console.error(`No SVG found at position (${from_x}, ${from_y})`);
    }
}

function removeFigure(x, y) {
    const selector = `svg[pos_x="${x}"][pos_y="${y}"]`;
    const pieceSvg = document.querySelector(selector);
    if (pieceSvg) {
        pieceSvg.parentNode.removeChild(pieceSvg);
    } else{
        console.error(`No SVG found at position (${x}, ${y})`);
    }
}
const filterCache = new Map();
function generateFilterValues(rgb) {
    const rgbKey = `${rgb.r},${rgb.g},${rgb.b}`;
    if (filterCache.has(rgbKey)) {
        return filterCache.get(rgbKey);
    }
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
    const hueRotateValue = h;
    const saturateValue = s * 100;
    const brightnessValue = l * 2;
    const contrastValue = 1 + (l - 0.5) * 2;

    const filterValues = `sepia(${sepia}) saturate(${saturateValue}%) hue-rotate(${hueRotateValue}deg) brightness(${brightnessValue}) contrast(${contrastValue})`;
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


    let viewAngle = (90 * getCookie('view')) % 360; // Ensure the angle stays within 0-359 degrees
    chessboard.style.transform = `rotate(${viewAngle}deg)`;

    //First turn
    const turnDiv = document.getElementById('turn');
    turnDiv.textContent = 'Turn: ' + data.status.turn;

    for (let row = 0; row < boardSize; row++) {
        for (let col = 0; col < boardSize; col++) {
            const cell = document.createElement('div');
            cell.classList.add('cell');
            cell.classList.add('cell');
            cell.setAttribute('cell_x', col);
            cell.setAttribute('cell_y', row);
            cell.style.width = `${cellSize}px`;
            cell.style.height = `${cellSize}px`;

            if ((row + col) % 2 === 0) {
                cell.classList.add('light');
            } else {
                cell.classList.add('dark');
            }
            chessboard.appendChild(cell);
            cell.addEventListener('click', () => {
                if (selectedRow === -1 && selectedCol === -1) {
                    cell.classList.add('selected');
                    cell.style.background = 'green';
                    selectedCol = col;
                    selectedRow = row;
                } else if (targetRow === -1 && targetCol === -1) {

                    turn(selectedCol, selectedRow, col, row);

                    const previousSelectedCell = document.querySelector('.cell.selected');
                    if (previousSelectedCell) {
                        previousSelectedCell.style.background = '';
                        previousSelectedCell.classList.remove('selected');
                    }
                    selectedRow = -1;
                    selectedCol = -1;
                    targetRow = -1;
                    targetCol = -1;
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

        const colorHex = data.start.colors[figure.color];
        const rgb = hexToRgb(colorHex);
        fig_Svg.style.filter = generateFilterValues(rgb);

        fig_Svg.style.transform = `translate(${figure.x * cellSize}px, ${figure.y * cellSize}px) rotate(${-viewAngle}deg)`;
        chessboard.appendChild(fig_Svg);
    }
}

function turn(x,y, targetCol, targetRow) {
    const selector = `svg[pos_x="${x}"][pos_y="${y}"]`;
    const figureSvg = document.querySelector(selector);
    if (figureSvg != null) {
        const postData = {
            id: figureSvg.id,
            to: { x: targetCol, y: targetRow },
        };
        fetch('/turn', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(postData),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error != null){
              console.log('Turn error:', data.error);
            }else{
                if (data.action_type === 'change'){
                    console.log(data)
                    showSelectionWindow(data.avaible, data.fig_id);
                }else{
                    console.error("Not Implemented yet")
                }
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
            // Load chat content into the container
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
    const selector = `svg[id="${active_fig}"]`;
    const pieceSvg = document.querySelector(selector);
    if (pieceSvg) {
        pieceSvg.style.backgroundImage = `url("../static/figures/${figStyle}/${fig_type}.svg")`;
    } else{
        console.error(`No SVG ${active_fig}`);
    }
}
function initBoard(){
    fetchInitialMap();
    socket = io('http://127.0.0.1:5000');
    //set room for board (chat has separated socket) //TODO vyřešit nějak left kdyz hra skonci
    const gameCode = getCookie('game_code');
    if (gameCode) {
        socket.emit('join_chat', { game_code: gameCode });
    }

    socket.on('fig_action', function (data) {
        //console.log("Valid move");
        //console.log(data);
        if (data.killed) {
            removeFigure(data.killed.x, data.killed.y);
        }
        if (data.turn != null) {
            document.getElementById('turn').textContent = 'Turn: ' + data.turn;
        }
        if(data.active_fig != null && data.to != null){
            transformSvg(data.active_fig, data.to.x, data.to.y)
        }
        if (data.change_fig != null) {
            changeSvg(data.change_fig, data.fig_type)
        }
    })
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

