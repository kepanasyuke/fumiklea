const API_KEY = 'ege-token-2026';
const API_BASE = '/api/v1';
let currentUserId = null;
let currentUsername = null;
let currentAttemptId = null;
let loadedTasks = [];

window.addEventListener('DOMContentLoaded', initApp);

function api(method, path, body = null) {
    const headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    };
    const options = { method, headers };
    if (body) options.body = JSON.stringify(body);

    return fetch(path, options)
        .then(async r => {
            const content = await r.text();
            const json = content ? JSON.parse(content) : null;
            if (!r.ok) {
                const message = json?.detail || r.statusText || ('HTTP ' + r.status);
                throw new Error(message);
            }
            return json;
        });
}

function initApp() {
    const storedUser = window.localStorage.getItem('ege_user');
    if (storedUser) {
        const session = JSON.parse(storedUser);
        currentUserId = session.userId;
        currentUsername = session.username;
        showUserPanel();
    } else {
        showPanel('auth-container');
    }
}

function showPanel(panelId) {
    ['auth-container', 'actions-container', 'tasks-container', 'results-container', 'stats-container', 'bank-container', 'loading-container', 'error-container']
        .forEach(id => document.getElementById(id).style.display = 'none');
    document.getElementById(panelId).style.display = 'block';
}

function showUserPanel() {
    document.getElementById('user-info-display').innerHTML =
        `✅ <strong>${currentUsername}</strong> (ID: ${currentUserId})`;
    showPanel('actions-container');
}

function saveSession() {
    window.localStorage.setItem('ege_user', JSON.stringify({ userId: currentUserId, username: currentUsername }));
}

function clearSession() {
    window.localStorage.removeItem('ege_user');
    currentUserId = null;
    currentUsername = null;
}

function showError(message) {
    document.getElementById('error-message').textContent = message;
    showPanel('error-container');
}

function sanitizeHTML(value) {
    return value.replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, '');
}

function logoutUser() {
    clearSession();
    document.getElementById('username-input').value = '';
    showPanel('auth-container');
}

function toggleGraph(taskId) {
    const preview = document.getElementById(`graph-preview-${taskId}`);
    if (!preview) return;
    preview.style.display = preview.style.display === 'block' ? 'none' : 'block';
}

async function registerUser() {
    const username = document.getElementById('username-input').value.trim();
    if (!username) return showError('Введите имя пользователя');

    try {
        const data = await api('POST', `${API_BASE}/user/register?username=${encodeURIComponent(username)}`);
        currentUserId = data.user_id;
        currentUsername = data.username;
        saveSession();
        showUserPanel();
    } catch (e) {
        showError('Регистрация не прошла: ' + e.message);
    }
}

async function loadFullVariant() {
    if (!currentUserId) return showError('Сначала зарегистрируйтесь.');
    try {
        document.getElementById('loading-message').textContent = 'Генерируем полный вариант...';
        showPanel('loading-container');

        const data = await api('POST', `${API_BASE}/tasks/variant/generate?user_id=${currentUserId}`);
        currentAttemptId = data.attempt_id;
        loadedTasks = data.tasks;
        renderTasks(`Полный вариант (${loadedTasks.length} заданий)`);
        await MathJax.typesetPromise();
    } catch (e) {
        showError('Не удалось загрузить вариант: ' + e.message);
    }
}

async function loadTimeAttack() {
    if (!currentUserId) return showError('Сначала зарегистрируйтесь.');
    try {
        document.getElementById('loading-message').textContent = 'Готовим Time Attack...';
        showPanel('loading-container');

        const data = await api('POST', `${API_BASE}/tasks/time-attack/start?user_id=${currentUserId}`);
        currentAttemptId = data.attempt_id;
        loadedTasks = data.tasks;
        renderTasks(`Time Attack (${loadedTasks.length} заданий)`);
        await MathJax.typesetPromise();

        setTimeout(() => {
            if (currentAttemptId) {
                showError('Время вышло! Ответы отправляются автоматически.');
                submitAllAnswers();
            }
        }, 600000);
    } catch (e) {
        showError('Не удалось начать Time Attack: ' + e.message);
    }
}

function extractGraphLink(text) {
    const match = text.match(/https:\/\/www\.geogebra\.org\/graphing[^"'\s<]*/);
    return match ? match[0] : null;
}

function renderTasks(title) {
    document.getElementById('tasks-title').textContent = title;
    const container = document.getElementById('tasks-list');
    container.innerHTML = '';

    loadedTasks.forEach((task, i) => {
        const card = document.createElement('div');
        card.className = 'task-card';

        const isPart2 = task.part === 2;
        const safeText = sanitizeHTML(task.text || '');
        const graphLink = task.graph_url || extractGraphLink(safeText);
        const taskText = graphLink
            ? safeText.replace(/https:\/\/www\.geogebra\.org\/graphing[^"'\s<]*/g, '')
            : safeText;

        card.innerHTML = `
            <div class="task-number">
                📋 Задание №${i + 1}
                <span class="task-number-accent">(Часть ${task.part}${isPart2 ? ' — развёрнутый ответ' : ''})</span>
            </div>
            <div class="task-topic">📚 ${task.topic}</div>
            <div class="task-text">${taskText}</div>
            ${isPart2 ?
                `<textarea id="answer-${task.id}" class="answer-textarea" placeholder="Введите полное решение..." rows="6"></textarea>` :
                `<input type="text" id="answer-${task.id}" class="answer-input" placeholder="Введите ответ">`
            }
            <div class="task-tags">${(task.tags || []).map(tag => `<span class="tag-badge">${tag}</span>`).join('')}</div>
        `;

        if (graphLink) {
            const graphBlock = document.createElement('div');
            graphBlock.className = 'graph-block';
            graphBlock.innerHTML = `
                <button class="graph-toggle" type="button" onclick="toggleGraph(${task.id})">
                    📈 Показать график функции
                </button>
                <div id="graph-preview-${task.id}" class="graph-preview" style="display:none;">
                    <iframe class="graph-iframe" src="${graphLink}" title="График задачи ${i + 1}" loading="lazy"></iframe>
                    <div class="graph-footer">
                        График загружается из GeoGebra. Если он не отобразился, нажмите "Открыть в GeoGebra".
                        <a href="${graphLink}" target="_blank" rel="noopener noreferrer">Открыть в новом окне</a>
                    </div>
                </div>
            `;
            card.appendChild(graphBlock);
        }

        if (graphLink) {
            const hint = document.createElement('div');
            hint.className = 'graph-hint';
            hint.innerHTML = `
                <span>📈 График можно построить отдельно:</span>
                <a href="${graphLink}" target="_blank" rel="noopener noreferrer">Открыть GeoGebra</a>
            `;
            card.appendChild(hint);
        }

        container.appendChild(card);
    });

    document.getElementById('submit-section').style.display = 'block';
    showPanel('tasks-container');
}

async function submitAllAnswers() {
    if (!currentAttemptId) return showError('Нет активной попытки для отправки.');
    const answers = loadedTasks.map(t => ({
        task_id: t.id,
        answer: document.getElementById(`answer-${t.id}`)?.value || ''
    }));

    try {
        document.getElementById('loading-message').textContent = 'Отправляем ответы...';
        showPanel('loading-container');

        const data = await api('POST', `${API_BASE}/tasks/variant/submit`, {
            user_id: currentUserId,
            attempt_id: currentAttemptId,
            answers
        });

        displayResults(data);
        currentAttemptId = null;
    } catch (e) {
        showError('Не удалось отправить ответы: ' + e.message);
    }
}

function displayResults(data) {
    const container = document.getElementById('results-content');
    const items = data.details.map(d => `
        <div class="result-item ${d.is_correct ? 'result-correct' : 'result-incorrect'}">
            <div class="result-item-title">${d.is_correct ? '✅' : '❌'} ${d.topic}</div>
            <div>Ваш ответ: <strong>${d.your_answer || '—'}</strong></div>
            <div>Правильно: <strong>${d.correct_answer}</strong></div>
        </div>
    `).join('');

    container.innerHTML = `
        <div class="score-display">🎯 ${data.score} из ${data.max_score} баллов</div>
        ${items}
    `;
    showPanel('results-container');
}

async function showUserStats() {
    try {
        const data = await api('GET', `${API_BASE}/user/stats/${currentUserId}`);
        const container = document.getElementById('stats-content');
        container.innerHTML = `
            <div class="score-display">📊 Статистика</div>
            <div class="stats-grid">
                <div><strong>Попыток</strong><br>${data.total_attempts}</div>
                <div><strong>Средний балл</strong><br>${data.avg_score.toFixed(1)}</div>
                <div><strong>Лучший</strong><br>${data.best_score}</div>
            </div>
            <p><strong>Достижения:</strong> ${data.achievements?.length ? data.achievements.join(', ') : '—'}</p>
            ${data.weak_topics?.length ? `<p><strong>Слабые темы:</strong> ${data.weak_topics.join(', ')}</p>` : ''}
        `;
        showPanel('stats-container');
    } catch (e) {
        showError('Не удалось получить статистику: ' + e.message);
    }
}

async function loadTaskBank() {
    if (!currentUserId) return showError('Сначала зарегистрируйтесь.');
    try {
        document.getElementById('loading-message').textContent = 'Загружаем каталог заданий...';
        showPanel('loading-container');

        const data = await api('GET', `${API_BASE}/tasks/bank`);
        renderTaskBank(data.items);
    } catch (e) {
        showError('Не удалось загрузить каталог заданий: ' + e.message);
    }
}

function renderTaskBank(items) {
    const container = document.getElementById('bank-list');
    container.innerHTML = items.map(item => `
        <div class="bank-card">
            <div class="bank-card-header">
                <div>№${item.number} — Часть ${item.part}</div>
                <div class="bank-tag">${item.available} прим.</div>
            </div>
            <div class="bank-card-topic">${item.topic}</div>
            <div class="bank-card-text">${sanitizeHTML(item.sample_text)}</div>
            <div class="bank-card-meta">
                ${item.has_graph ? '📈 С графиком' : '✏️ Текстовое задание'}
            </div>
        </div>
    `).join('');

    showPanel('bank-container');
}

function showCompetitionsInfo() {
    showError('Соревнования доступны через /docs. Скоро добавим персональную панель!');
}

function hideError() {
    if (currentUserId) {
        showPanel('actions-container');
    } else {
        showPanel('auth-container');
    }
}
