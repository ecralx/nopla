const BACKEND_URL = window.location.host
const socket = io.connect(BACKEND_URL);
const FULL_DASH_ARRAY = 283;
const TIME_LIMIT = 60;
const WARNING_THRESHOLD = 30;
const ALERT_THRESHOLD = 15;
const COLOR_CODES = {
    info: {
        color: "green"
    },
    warning: {
        color: "orange",
        threshold: WARNING_THRESHOLD
    },
    alert: {
        color: "red",
        threshold: ALERT_THRESHOLD
    }
};
const remainingPathColor = COLOR_CODES.info.color;
document.getElementById('base-timer-path-remaining').classList.add(remainingPathColor)

let userId = '';
let gameState = {};
let canStartGame = false;
let interval;

// verify our websocket connection is established
socket.on('connect', function() {
    canStartGame = true;
});
// message handler for the 'join_room' channel
socket.on('join_room', function(resp) {
    if (resp.status == 'ok') {
        gameState = resp.game_state
        userId = gameState.user_id
        document.getElementById('pt1').style.display='none';
        document.getElementById('pt2-score').textContent=gameState.score
        document.getElementById('pt2-time').textContent=getRemainingTime(gameState.started_on).toString();
        document.getElementById('pt2-expression-text').textContent = gameState.user_sentence
        document.getElementById('pt2').style.display='block';
        document.getElementById('pt2-input').focus();
        interval = window.setInterval(check, 1000, userId)
    }
});
socket.on('update', function(resp) {
    if (resp.status == 'ok') {
        gameState = resp.game_state;
        document.getElementById('pt2-score').textContent=gameState.score;
        const timeLeft = getRemainingTime(gameState.started_on);
        document.getElementById('pt2-time').textContent = timeLeft.toString();
        document.getElementById('pt2-expression-text').textContent = gameState.user_sentence
        setCircleDasharray(timeLeft);
        setRemainingPathColor(timeLeft);
        if (gameState.answers.length > 0) {
            const isCorrect = gameState.answers[gameState.answers.length - 1].is_correct === true;
            setBordersOnAnswer(isCorrect)
        }
    }
    if (resp.status == 'finished') {
        window.clearInterval(interval);
        document.getElementById('pt2').style.display = 'none';
        document.getElementById('pt3').style.display = 'block';
        document.getElementById('pt3-score').textContent = gameState.score;
        document.getElementById('pt3-ul').innerHTML = '';
        gameState.answers.forEach(function(answer) {
            const isUserAnswerCorrect = answer.is_correct;
            const node = document.createElement('li');
            answer.sentence.forEach(function (word) {
                const wordSpan = document.createElement('span');
                wordSpan.textContent = word.text;
                if (word.style == 'answer') {
                    wordSpan.className = isUserAnswerCorrect ? 'correct' : 'incorrect';
                }
                node.appendChild(wordSpan);
            });
            document.getElementById('pt3-ul').appendChild(node);
        })
    }
})
// createGame onclick - emit a message on the 'create' channel to 
// create a new gameState with default parameters
function createGame(userId = '') {
    socket.emit('create', { user_id: userId });
}
function solve() {
    const answer = document.getElementById('pt2-input').value;
    socket.emit('solve', { user_id: userId, answer: answer });
    document.getElementById('pt2-input').value = '';
    document.getElementById('pt2-input').focus();
}
function check(id) {
    socket.emit('check', { user_id: id });
}
function onKeyPress(e) {
    if (e.keyCode == 13) {
        solve();
    }
}
function replay() {
    window.location.reload();
}
function calculateTimeFraction(timeLeft) {
    const rawTimeFraction = timeLeft / TIME_LIMIT;
    return rawTimeFraction - (1 / TIME_LIMIT) * (1 - rawTimeFraction);
}
// Update the dasharray value as time passes, starting with 283
function setCircleDasharray(timeLeft) {
    const circleDasharray = (calculateTimeFraction(timeLeft) * FULL_DASH_ARRAY).toFixed(0).toString() + ' 283';
    document.getElementById("base-timer-path-remaining").setAttribute("stroke-dasharray", circleDasharray);
}
function setRemainingPathColor(timeLeft) {
    // If the remaining time is less than or equal to 5, remove the "warning" class and apply the "alert" class.
    if (timeLeft <= COLOR_CODES.alert.threshold) {
        document
        .getElementById("base-timer-path-remaining")
        .classList.remove(COLOR_CODES.warning.color);
        document
        .getElementById("base-timer-path-remaining")
        .classList.add(COLOR_CODES.alert.color);

    // If the remaining time is less than or equal to 10, remove the base color and apply the "warning" class.
    } else if (timeLeft <= COLOR_CODES.warning.threshold) {
        document
        .getElementById("base-timer-path-remaining")
        .classList.remove(COLOR_CODES.info.color);
        document
        .getElementById("base-timer-path-remaining")
        .classList.add(COLOR_CODES.warning.color);
    }
}
function setBordersOnAnswer(isCorrect) {
    if (isCorrect) {
        document.getElementById('pt2-score-circle').classList.remove('incorrect');
        document.getElementById('pt2-score-circle').classList.add('correct');
        document.getElementById('pt2-input').classList.remove('incorrect');
        document.getElementById('pt2-input').classList.add('correct');
    } else {
        document.getElementById('pt2-score-circle').classList.add('incorrect');
        document.getElementById('pt2-score-circle').classList.remove('correct');
        document.getElementById('pt2-input').classList.add('incorrect');
        document.getElementById('pt2-input').classList.remove('correct');
    }
}
function getRemainingTime(timeString) {
    const now = new Date();
    const started_on = new Date(Date.parse(timeString + ' GMT'));
    return Math.max(0, (60 - Math.floor((now - started_on) / 1000)));
}