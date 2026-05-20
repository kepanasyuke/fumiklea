const API_KEY = 'ege-token-2026';
const API_BASE = '/api/v1';
let currentUserId = null;
let currentUsername = null;
let currentAttemptId = null;
let currentAttemptSubmitPath = '/tasks/variant/submit';
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
    ['auth-container', 'actions-container', 'tasks-container', 'results-container', 'stats-container', 'achievements-container', 'competition-container', 'bank-container', 'loading-container', 'error-container']
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
    currentAttemptId = null;
    currentAttemptSubmitPath = '/tasks/variant/submit';
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
        currentAttemptSubmitPath = '/tasks/variant/submit';
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
        currentAttemptSubmitPath = '/tasks/variant/submit';
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
                `<textarea id="answer-${task.id}" class="answer-textarea" placeholder="Введите полное решение..." rows="6"></textarea>
                <button class="action-btn secondary-btn ai-check-btn" type="button" onclick="checkSolution(${task.id})">🤖 Проверить решение ИИ</button>
                <div id="ai-feedback-${task.id}" class="ai-feedback"></div>` :
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

        const data = await api('POST', `${API_BASE}${currentAttemptSubmitPath}`, {
            user_id: currentUserId,
            attempt_id: currentAttemptId,
            answers
        });

        displayResults(data);
        currentAttemptId = null;
        currentAttemptSubmitPath = '/tasks/variant/submit';
    } catch (e) {
        showError('Не удалось отправить ответы: ' + e.message);
    }
}

async function checkSolution(taskId) {
    const task = loadedTasks.find(t => t.id === taskId);
    if (!task) return showError('Задача не найдена.');
    const answer = document.getElementById(`answer-${taskId}`)?.value || '';
    if (!answer.trim()) return showError('Введите решение для проверки ИИ.');

    const feedback = document.getElementById(`ai-feedback-${taskId}`);
    feedback.innerHTML = 'Проверка...';

    try {
        const data = await api('POST', `${API_BASE}/ai/check`, {
            task_text: task.text,
            solution_text: answer
        });
        feedback.innerHTML = `<pre>${sanitizeHTML(data.evaluation || data.error || 'Нет ответа')}</pre>`;
    } catch (e) {
        feedback.innerHTML = `Ошибка ИИ: ${sanitizeHTML(e.message)}`;
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

async function loadAchievements() {
    if (!currentUserId) return showError('Сначала зарегистрируйтесь.');
    try {
        document.getElementById('loading-message').textContent = 'Загружаем достижения...';
        showPanel('loading-container');

        const data = await api('GET', `${API_BASE}/achievements/${currentUserId}`);
        renderAchievements(data);
    } catch (e) {
        showError('Не удалось загрузить достижения: ' + e.message);
    }
}

function renderAchievements(items) {
    const container = document.getElementById('achievements-list');
    if (!items.length) {
        container.innerHTML = '<div class="empty-state">Пока нет открытых достижений.</div>';
    } else {
        container.innerHTML = items.map(item => `
            <div class="achievement-card">
                <div class="achievement-icon">${item.icon || '🏅'}</div>
                <div class="achievement-body">
                    <div class="achievement-title">${item.name || item.code}</div>
                    <div class="achievement-description">${item.description || 'Достижение получено.'}</div>
                    <div class="achievement-meta">${new Date(item.unlocked_at).toLocaleString('ru-RU')}</div>
                </div>
            </div>
        `).join('');
    }
    showPanel('achievements-container');
}

function showCompetitionPanel() {
    document.getElementById('competition-create-result').innerHTML = '';
    document.getElementById('competition-join-result').innerHTML = '';
    document.getElementById('leaderboard-content').innerHTML = 'Укажите ID и загрузите лидерборд.';
    showPanel('competition-container');
}

async function createCompetition() {
    const name = document.getElementById('competition-name').value.trim();
    const duration = Number(document.getElementById('competition-duration').value);
    if (!name || !duration) return showError('Введите название и длительность соревнования.');

    try {
        document.getElementById('loading-message').textContent = 'Создаём соревнование...';
        showPanel('loading-container');

        const data = await api('POST', `${API_BASE}/competition/create?name=${encodeURIComponent(name)}&duration_minutes=${duration}`);
        document.getElementById('competition-create-result').innerHTML = `Соревнование <strong>${data.name}</strong> создано, ID ${data.id}.`;
        showPanel('competition-container');
    } catch (e) {
        showError('Не удалось создать соревнование: ' + e.message);
    }
}

async function joinCompetition() {
    const compId = Number(document.getElementById('competition-id').value);
    if (!compId || !currentUserId) return showError('Введите ID соревнования и зарегистрируйтесь.');

    try {
        document.getElementById('loading-message').textContent = 'Присоединяемся к соревнованию...';
        showPanel('loading-container');

        const data = await api('POST', `${API_BASE}/competition/${compId}/join?user_id=${currentUserId}`);
        currentAttemptId = data.attempt_id;
        currentAttemptSubmitPath = '/competition/submit';
        loadedTasks = data.tasks;
        renderTasks(`Соревнование #${compId} — ${loadedTasks.length} заданий`);
    } catch (e) {
        showError('Не удалось присоединиться: ' + e.message);
    }
}

async function loadLeaderboard() {
    const compId = Number(document.getElementById('competition-id').value);
    if (!compId) return showError('Введите ID соревнования.');

    try {
        const data = await api('GET', `${API_BASE}/competition/${compId}/leaderboard`);
        const container = document.getElementById('leaderboard-content');
        if (!data.length) {
            container.innerHTML = '<div class="empty-state">Лидерборд пуст или соревнование не найдено.</div>';
            return;
        }
        container.innerHTML = `
            <table class="leaderboard-table">
                <thead><tr><th>Игрок</th><th>Счёт</th><th>Время</th></tr></thead>
                <tbody>
                    ${data.map(item => `<tr><td>${item.username}</td><td>${item.score}/${item.max_score}</td><td>${new Date(item.timestamp).toLocaleString('ru-RU')}</td></tr>`).join('')}
                </tbody>
            </table>
        `;
    } catch (e) {
        showError('Не удалось загрузить лидерборд: ' + e.message);
    }
}

function hideError() {
    if (currentUserId) {
        showPanel('actions-container');
    } else {
        showPanel('auth-container');
    }
}
