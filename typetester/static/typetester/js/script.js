let startTime = null;
let timerInterval = null;
let isTestRunning = false;
let totalErrors = 0;
let hasTypedChar = [];
let hasError = [];
let originalText = '';
let currentText = '';
let saveResultUrl = '';

document.addEventListener('DOMContentLoaded', function () {
    const originalField = document.getElementById('originalText');
    const urlField = document.getElementById('saveResultUrl');
    const textInput = document.getElementById('textInput');

    if (originalField) {
        originalText = originalField.value;
    }
    if (urlField) {
        saveResultUrl = urlField.value;
    }

    if (textInput) {
        textInput.focus();
        textInput.addEventListener('input', handleInput);
        textInput.addEventListener('keydown', function (e) {
            if (e.key === 'Tab') e.preventDefault();
        });
    }

    updateTextDisplay();
});

function startTest() {
    if (!isTestRunning) {
        startTime = new Date();
        isTestRunning = true;
        document.getElementById('textInput')?.focus();
        const btn = document.getElementById('startBtn');
        if (btn) {
            btn.innerHTML = '<i class="fas fa-pause"></i> Пауза';
            btn.onclick = pauseTest;
        }
        timerInterval = setInterval(updateTimer, 100);
    }
}

function pauseTest() {
    if (isTestRunning) {
        clearInterval(timerInterval);
        isTestRunning = false;
        const btn = document.getElementById('startBtn');
        if (btn) {
            btn.innerHTML = '<i class="fas fa-play"></i> Продолжить';
            btn.onclick = startTest;
        }
    }
}

function restartTest() {
    clearInterval(timerInterval);
    isTestRunning = false;
    startTime = null;
    totalErrors = 0;
    hasTypedChar = [];
    hasError = [];
    currentText = '';

    const textInput = document.getElementById('textInput');
    if (textInput) textInput.value = '';

    document.getElementById('timer')?.textContent = '0.0';
    document.getElementById('wpm')?.textContent = '0';
    document.getElementById('accuracy')?.textContent = '100%';
    document.getElementById('errors')?.textContent = '0';

    const btn = document.getElementById('startBtn');
    if (btn) {
        btn.innerHTML = '<i class="fas fa-play"></i> Начать';
        btn.onclick = startTest;
    }

    document.getElementById('resultsModal')?.style.display = 'none';
    updateTextDisplay();
}

function updateTimer() {
    if (!startTime || !isTestRunning) return;

    const currentTime = new Date();
    const elapsed = (currentTime - startTime) / 1000;
    document.getElementById('timer')?.textContent = elapsed.toFixed(1);

    const charsTyped = currentText.length;
    const wpm = elapsed > 0 ? Math.round((charsTyped / 5 / elapsed) * 60) : 0;
    document.getElementById('wpm')?.textContent = wpm;

    let correct = 0;
    for (let i = 0; i < charsTyped && i < originalText.length; i++) {
        if (hasTypedChar[i] && currentText[i] === originalText[i]) {
            correct++;
        }
    }
    const accuracy = charsTyped > 0 ? Math.round((correct / charsTyped) * 100) : 100;

    document.getElementById('accuracy')?.textContent = accuracy + '%';
    document.getElementById('errors')?.textContent = totalErrors;
}

function updateTextDisplay() {
    const display = document.getElementById('textToType');
    if (!display) return;

    let html = '';
    for (let i = 0; i < originalText.length; i++) {
        if (i < currentText.length) {
            if (hasTypedChar[i] && currentText[i] === originalText[i]) {
                html += `<span class="typed-text">${originalText[i]}</span>`;
            } else {
                html += `<span class="error-char">${originalText[i]}</span>`;
            }
        } else if (i === currentText.length) {
            html += `<span class="current-char">${originalText[i]}</span>`;
        } else {
            html += `<span class="text-to-type">${originalText[i]}</span>`;
        }
    }
    display.innerHTML = html;
}

function finishTest() {
    clearInterval(timerInterval);
    isTestRunning = false;

    const endTime = new Date();
    const elapsed = (endTime - startTime) / 1000;
    const charsTyped = currentText.length;
    const wpm = elapsed > 0 ? Math.round((charsTyped / 5 / elapsed) * 60) : 0;

    let correctChars = 0;
    for (let i = 0; i < originalText.length; i++) {
        if (hasTypedChar[i] && currentText[i] === originalText[i]) {
            correctChars++;
        }
    }
    const accuracy = Math.round((correctChars / originalText.length) * 100);

    document.getElementById('finalWPM')?.textContent = wpm;
    document.getElementById('finalAccuracy')?.textContent = accuracy + '%';
    document.getElementById('finalTime')?.textContent = elapsed.toFixed(1);
    document.getElementById('finalErrors')?.textContent = totalErrors;
    document.getElementById('resultsModal')?.style.display = 'flex';

    saveResult(wpm, accuracy, elapsed, totalErrors);
}

function saveResult(wpm, accuracy, time, errorCount) {
    const textIdElem = document.getElementById('textId');
    const textId = textIdElem ? textIdElem.value || null : null;

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
            mistakes: errorCount,
            text_id: textId
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Результат сохранён:', data);
    })
    .catch(error => {
        console.error('Ошибка при сохранении результата:', error);
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function handleInput(e) {
    if (!isTestRunning && startTime === null) {
        startTest();
    }

    const newValue = e.target.value;
    const oldLength = currentText.length;
    const newLength = newValue.length;

    if (newLength < oldLength) {
        currentText = newValue;
        hasTypedChar = hasTypedChar.slice(0, newLength);
        hasError = hasError.slice(0, newLength);
        updateTextDisplay();
        return;
    }

    if (newLength > oldLength && newLength <= originalText.length) {
        const pos = newLength - 1;
        const newChar = newValue[pos];
        const expectedChar = originalText[pos];

        hasTypedChar[pos] = true;

        if (newChar !== expectedChar && !hasError[pos]) {
            hasError[pos] = true;
            totalErrors++;
        }
    }

    currentText = newValue;
    updateTextDisplay();

    if (currentText.length === originalText.length) {
        finishTest();
    }
}