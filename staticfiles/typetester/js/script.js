let startTime = null;
let timerInterval = null;
let isTestRunning = false;

let originalText = '';
let currentText = '';
let saveResultUrl = '';

// === ЧЕСТНАЯ СТАТИСТИКА ===
const stats = {
    totalTyped: 0,
    correct: 0,
    mistakes: 0
};

document.addEventListener('DOMContentLoaded', function () {
    const originalField = document.getElementById('originalText');
    const urlField = document.getElementById('saveResultUrl');
    const textInput = document.getElementById('textInput');

    if (originalField) originalText = originalField.value;
    if (urlField) saveResultUrl = urlField.value;

    if (textInput) {
        textInput.focus();
        textInput.addEventListener('keydown', handleKeydown);
        textInput.addEventListener('input', handleInput);
        textInput.addEventListener('keydown', e => {
            if (e.key === 'Tab') e.preventDefault();
        });
    }

    updateTextDisplay();
});

// ======================
// CONTROL
// ======================
function startTest() {
    if (!isTestRunning) {
        startTime = Date.now();
        isTestRunning = true;

        const btn = document.getElementById('startBtn');
        if (btn) {
            btn.innerHTML = '<i class="fas fa-pause"></i> Пауза';
            btn.onclick = pauseTest;
        }

        timerInterval = setInterval(updateTimer, 100);
    }
}

function pauseTest() {
    clearInterval(timerInterval);
    isTestRunning = false;

    const btn = document.getElementById('startBtn');
    if (btn) {
        btn.innerHTML = '<i class="fas fa-play"></i> Продолжить';
        btn.onclick = startTest;
    }
}

function restartTest() {
    clearInterval(timerInterval);
    isTestRunning = false;
    startTime = null;

    currentText = '';
    stats.totalTyped = 0;
    stats.correct = 0;
    stats.mistakes = 0;

    const textInput = document.getElementById('textInput');
    if (textInput) textInput.value = '';

    document.getElementById('timer').textContent = '0.0';
    document.getElementById('wpm').textContent = '0';
    document.getElementById('accuracy').textContent = '100%';
    document.getElementById('errors').textContent = '0';

    const btn = document.getElementById('startBtn');
    if (btn) {
        btn.innerHTML = '<i class="fas fa-play"></i> Начать';
        btn.onclick = startTest;
    }

    document.getElementById('resultsModal').style.display = 'none';
    updateTextDisplay();
}

// ======================
// INPUT LOGIC
// ======================
function handleKeydown(e) {
    if (!isTestRunning && !startTime && e.key.length === 1) {
        startTest();
    }

    if (e.key === 'Backspace') {
        currentText = currentText.slice(0, -1);
        updateTextDisplay();
    }
}

function handleInput(e) {
    const value = e.target.value;

    if (value.length <= currentText.length) {
        e.target.value = currentText;
        return;
    }

    const pos = currentText.length;
    const typedChar = value[pos];
    const expectedChar = originalText[pos];

    currentText += typedChar;

    stats.totalTyped++;

    if (typedChar === expectedChar) {
        stats.correct++;
    } else {
        stats.mistakes++;
    }

    updateTextDisplay();

    if (currentText.length === originalText.length) {
        finishTest();
    }
}

// ======================
// METRICS
// ======================
function updateTimer() {
    if (!isTestRunning || !startTime) return;

    const elapsed = (Date.now() - startTime) / 1000;
    document.getElementById('timer').textContent = elapsed.toFixed(1);

    const minutes = elapsed / 60;
    const wpm = minutes > 0
        ? Math.round((stats.correct / 5) / minutes)
        : 0;

    const accuracy = stats.totalTyped > 0
        ? Math.round((stats.correct / stats.totalTyped) * 100)
        : 100;

    document.getElementById('wpm').textContent = wpm;
    document.getElementById('accuracy').textContent = accuracy + '%';
    document.getElementById('errors').textContent = stats.mistakes;
}

// ======================
// UI
// ======================
function updateTextDisplay() {
    const display = document.getElementById('textToType');
    if (!display) return;

    let html = '';
    for (let i = 0; i < originalText.length; i++) {
        if (i < currentText.length) {
            html += currentText[i] === originalText[i]
                ? `<span class="typed-text">${originalText[i]}</span>`
                : `<span class="error-char">${originalText[i]}</span>`;
        } else if (i === currentText.length) {
            html += `<span class="current-char">${originalText[i]}</span>`;
        } else {
            html += `<span class="text-to-type">${originalText[i]}</span>`;
        }
    }

    display.innerHTML = html;
}

// ======================
// FINISH
// ======================
function finishTest() {
    clearInterval(timerInterval);
    isTestRunning = false;

    const elapsed = (Date.now() - startTime) / 1000;
    const minutes = elapsed / 60;

    const wpm = minutes > 0
        ? Math.round((stats.correct / 5) / minutes)
        : 0;

    const accuracy = stats.totalTyped > 0
        ? Math.round((stats.correct / stats.totalTyped) * 100)
        : 100;

    document.getElementById('finalWPM').textContent = wpm;
    document.getElementById('finalAccuracy').textContent = accuracy + '%';
    document.getElementById('finalTime').textContent = elapsed.toFixed(1);
    document.getElementById('finalErrors').textContent = stats.mistakes;

    document.getElementById('resultsModal').style.display = 'flex';

    saveResult(wpm, accuracy, elapsed, stats.mistakes);
}

// ======================
// SAVE
// ======================
function saveResult(wpm, accuracy, time, mistakes) {
    const textIdElem = document.getElementById('textId');
    const textId = textIdElem ? textIdElem.value : null;

    fetch(saveResultUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            typed_text: currentText,
            original_text: originalText,
            time_seconds: time,
            mistakes,
            text_id: textId
        })
    });
}

function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let c of cookies) {
        c = c.trim();
        if (c.startsWith(name + '=')) {
            return decodeURIComponent(c.substring(name.length + 1));
        }
    }
    return null;
}
