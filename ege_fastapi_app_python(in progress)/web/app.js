const API_KEY = 'ege-token-2026';
let currentUserId = null;
let currentAttemptId = null;
let loadedTasks = [];

function api(method, path, body = null) {
    const headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    };
    const options = { method, headers };
    if (body) options.body = JSON.stringify(body);
    
    return fetch(path, options)
        .then(r => {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.json();
        });
}

function hideAllPanels() {
    ['auth-container', 'actions-container', 'tasks-container', 
     'results-container', 'stats-container', 'loading-container', 'error-container']
    .forEach(id => document.getElementById(id).style.display = 'none');
}

function showPanel(panelId) {
    hideAllPanels();
    document.getElementById(panelId).style.display = 'block';
}

async function registerUser() {
    const username = document.getElementById('username-input').value.trim();
    if (!username) return alert('Введите имя');
    
    try {
        const data = await api('POST', '/api/v1/user/register?username=' + encodeURIComponent(username));
        currentUserId = data.user_id;
        document.getElementById('user-info-display').innerHTML = 
            '✅ <strong>' + username + '</strong> (ID: ' + currentUserId + ')';
        showPanel('actions-container');
    } catch(e) {
        alert('Ошибка: ' + e.message);
    }
}

async function loadFullVariant() {
    try {
        document.getElementById('loading-message').textContent = 'Генерируем вариант...';
        showPanel('loading-container');
        
        const data = await api('POST', '/api/v1/tasks/variant/generate?user_id=' + currentUserId);
        currentAttemptId = data.attempt_id;
        loadedTasks = data.tasks;
        
        renderTasks('Полный вариант (' + loadedTasks.length + ' заданий)');
        MathJax.typesetPromise();
    } catch(e) {
        alert('Ошибка: ' + e.message);
    }
}

async function loadTimeAttack() {
    try {
        document.getElementById('loading-message').textContent = 'Готовим блиц...';
        showPanel('loading-container');
        
        const data = await api('POST', '/api/v1/tasks/time-attack/start?user_id=' + currentUserId);
        currentAttemptId = data.attempt_id;
        loadedTasks = data.tasks;
        
        renderTasks('Time Attack (' + loadedTasks.length + ' заданий)');
        MathJax.typesetPromise();
        
        setTimeout(() => {
            if (currentAttemptId) {
                alert('Время вышло!');
                submitAllAnswers();
            }
        }, 600000);
    } catch(e) {
        alert('Ошибка: ' + e.message);
    }
}

function renderTasks(title) {
    document.getElementById('tasks-title').textContent = title;
    const container = document.getElementById('tasks-list');
    container.innerHTML = '';
    
    loadedTasks.forEach((task, i) => {
        const card = document.createElement('div');
        card.className = 'task-card';
        card.innerHTML = `
            <div class="task-number">📋 Задание №${i + 1} (Тип ${task.part === 1 ? task.id : '2'})</div>
            <div class="task-topic">📚 ${task.topic}</div>
            <div class="task-text">${task.text}</div>
            <input type="text" id="answer-${task.id}" class="answer-input" placeholder="Ваш ответ">
        `;
        container.appendChild(card);
    });
    
    document.getElementById('submit-section').style.display = 'block';
    showPanel('tasks-container');
}

async function submitAllAnswers() {
    const answers = loadedTasks.map(t => ({
        task_id: t.id,
        answer: document.getElementById('answer-' + t.id)?.value || ''
    }));
    
    try {
        document.getElementById('loading-message').textContent = 'Проверяем...';
        showPanel('loading-container');
        
        const data = await api('POST', '/api/v1/tasks/variant/submit', {
            user_id: currentUserId,
            attempt_id: currentAttemptId,
            answers: answers
        });
        
        displayResults(data);
        currentAttemptId = null;
    } catch(e) {
        alert('Ошибка: ' + e.message);
    }
}

function displayResults(data) {
    const container = document.getElementById('results-content');
    let html = `<div class="score-display">🎯 ${data.score} из ${data.max_score} баллов</div>`;
    
    data.details.forEach(d => {
        html += `
            <div class="result-item ${d.is_correct ? 'result-correct' : 'result-incorrect'}">
                <strong>Задание</strong> (${d.topic})<br>
                Ваш ответ: <strong>${d.your_answer || '—'}</strong><br>
                Правильно: <strong>${d.correct_answer}</strong>
                ${d.is_correct ? ' ✅' : ' ❌'}
            </div>
        `;
    });
    
    container.innerHTML = html;
    showPanel('results-container');
}

async function showUserStats() {
    try {
        const data = await api('GET', '/api/v1/user/stats/' + currentUserId);
        const container = document.getElementById('stats-content');
        container.innerHTML = `
            <div class="score-display">📊 Статистика</div>
            <p>Попыток: <strong>${data.total_attempts}</strong></p>
            <p>Средний балл: <strong>${data.avg_score}</strong></p>
            <p>Лучший результат: <strong>${data.best_score}</strong></p>
            <p>Достижения: ${data.achievements?.join(', ') || '—'}</p>
            ${data.weak_topics?.length ? '<p>Слабые темы: ' + data.weak_topics.join(', ') + '</p>' : ''}
        `;
        showPanel('stats-container');
    } catch(e) {
        alert('Ошибка: ' + e.message);
    }
}

function showCompetitionsInfo() {
    alert('Соревнования — через /docs');
}

function hideError() {
    showPanel('actions-container');
}

function renderTasks(title) {
    document.getElementById('tasks-title').textContent = title;
    const container = document.getElementById('tasks-list');
    container.innerHTML = '';
    
    loadedTasks.forEach((task, i) => {
        const card = document.createElement('div');
        card.className = 'task-card';
        
        const isPart2 = task.part === 2;
        
        card.innerHTML = `
            <div class="task-number">
                📋 Задание №${i + 1} 
                <span style="color: ${isPart2 ? '#dc2626' : '#1e3a8a'}">
                    (Часть ${task.part}${isPart2 ? ' — развёрнутый ответ' : ''})
                </span>
            </div>
            <div class="task-topic">📚 ${task.topic}</div>
            <div class="task-text">${task.text}</div>
            ${isPart2 ? 
                `<textarea id="answer-${task.id}" class="answer-textarea" 
                   placeholder="Введите полное решение задачи..." rows="6"></textarea>` :
                `<input type="text" id="answer-${task.id}" class="answer-input" 
                   placeholder="Введите ответ">`
            }
        `;
        container.appendChild(card);
    });
    
    document.getElementById('submit-section').style.display = 'block';
    showPanel('tasks-container');
    MathJax.typesetPromise();
}