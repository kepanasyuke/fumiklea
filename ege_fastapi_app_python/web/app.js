const API_KEY = 'ege-token-2026';
const BASE_URL = '';
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
    
    return fetch(BASE_URL + path, options)
        .then(r => {
            if (!r.ok) throw new Error('HTTP ' + r.status + ': ' + r.statusText);
            return r.json();
        });
}

function hideAllPanels() {
    const panels = ['auth-container', 'actions-container', 'tasks-container', 
                    'results-container', 'stats-container', 'loading-container', 'error-container'];
    panels.forEach(id => {
        document.getElementById(id).style.display = 'none';
    });
}

function showPanel(panelId) {
    hideAllPanels();
    document.getElementById(panelId).style.display = 'block';
}

function showLoading(message) {
    document.getElementById('loading-message').textContent = message || 'Загрузка...';
    showPanel('loading-container');
}

function showError(message) {
    document.getElementById('error-message').textContent = message;
    showPanel('error-container');
}

function hideError() {
    document.getElementById('auth-container').style.display = 'block';
    if (currentUserId) {
        document.getElementById('actions-container').style.display = 'block';
    }
}

async function registerUser() {
    const username = document.getElementById('username-input').value.trim();
    if (!username) {
        alert('Пожалуйста, введите имя');
        return;
    }
    
    try {
        showLoading('Регистрация...');
        const data = await api('POST', '/api/v1/user/register?username=' + encodeURIComponent(username));
        currentUserId = data.user_id;
        
        document.getElementById('user-info-display').innerHTML = 
            '✅ Добро пожаловать, <strong>' + username + '</strong>! (ID: ' + currentUserId + ')';
        
        showPanel('actions-container');
    } catch (e) {
        showError('Ошибка регистрации: ' + e.message);
    }
}

async function loadFullVariant() {
    try {
        showLoading('Генерируем вариант из 19 заданий...');
        
        const data = await api('POST', '/api/v1/tasks/variant/generate?user_id=' + currentUserId);
        
        currentAttemptId = data.attempt_id;
        loadedTasks = data.tasks;
        
        if (!loadedTasks || loadedTasks.length === 0) {
            showError('Не удалось загрузить задания. Сервер вернул пустой список.');
            return;
        }
        
        displayTasks('Полный вариант (' + loadedTasks.length + ' заданий)');
    } catch (e) {
        showError('Ошибка загрузки варианта: ' + e.message);
    }
}

async function loadTimeAttack() {
    try {
        showLoading('Готовим блиц-вариант из 12 заданий...');
        
        const data = await api('POST', '/api/v1/tasks/time-attack/start?user_id=' + currentUserId);
        
        currentAttemptId = data.attempt_id;
        loadedTasks = data.tasks;
        
        if (!loadedTasks || loadedTasks.length === 0) {
            showError('Не удалось загрузить задания.');
            return;
        }
        
        displayTasks('Time Attack (' + loadedTasks.length + ' заданий, 10 минут)');
        
        setTimeout(() => {
            if (currentAttemptId) {
                alert('⏰ Время вышло! Ответы отправляются автоматически.');
                submitAllAnswers();
            }
        }, 600000);
    } catch (e) {
        showError('Ошибка загрузки Time Attack: ' + e.message);
    }
}

function displayTasks(title) {
    document.getElementById('tasks-title').textContent = title;
    
    const listContainer = document.getElementById('tasks-list');
    listContainer.innerHTML = '';
    
    loadedTasks.forEach(task => {
        const card = document.createElement('div');
        card.className = 'task-card';
        card.id = 'task-card-' + task.id;
        
        card.innerHTML = 
            '<div class="task-number">📋 Задание №' + task.id + '</div>' +
            '<div class="task-topic">📚 ' + task.topic + ' | Часть ' + task.part + '</div>' +
            '<div class="task-text">' + task.text + '</div>' +
            '<input type="text" ' +
            'id="answer-input-' + task.id + '" ' +
            'class="answer-input" ' +
            'placeholder="Введите ваш ответ" ' +
            'onkeypress="if(event.key===\'Enter\') submitAllAnswers()">';
        
        listContainer.appendChild(card);
    });
    
    document.getElementById('submit-section').style.display = 'block';
    showPanel('tasks-container');
    
    document.getElementById('tasks-container').scrollIntoView({ behavior: 'smooth' });
}

async function submitAllAnswers() {
    const answers = loadedTasks.map(task => {
        const input = document.getElementById('answer-input-' + task.id);
        return {
            task_id: task.id,
            answer: input ? input.value : ''
        };
    });
    
    try {
        showLoading('Проверяем ответы...');
        
        const data = await api('POST', '/api/v1/tasks/variant/submit', {
            user_id: currentUserId,
            attempt_id: currentAttemptId,
            answers: answers
        });
        
        displayResults(data);
        currentAttemptId = null;
    } catch (e) {
        showError('Ошибка при отправке ответов: ' + e.message);
    }
}

function displayResults(data) {
    const container = document.getElementById('results-content');
    
    let html = '<div class="score-display">🎯 ' + data.score + ' из ' + data.max_score + ' баллов</div>';
    
    if (data.details && data.details.length > 0) {
        data.details.forEach(detail => {
            html += 
                '<div class="result-item ' + (detail.is_correct ? 'result-correct' : 'result-incorrect') + '">' +
                '<strong>Задание ' + detail.task_id + '</strong> (' + detail.topic + ')<br>' +
                'Ваш ответ: <strong>' + (detail.your_answer || 'нет ответа') + '</strong><br>' +
                'Правильный ответ: <strong>' + detail.correct_answer + '</strong><br>' +
                (detail.is_correct ? '✅ Верно' : '❌ Неверно') +
                '</div>';
        });
    }
    
    container.innerHTML = html;
    showPanel('results-container');
    document.getElementById('results-container').scrollIntoView({ behavior: 'smooth' });
}

async function showUserStats() {
    try {
        showLoading('Загружаем статистику...');
        
        const data = await api('GET', '/api/v1/user/stats/' + currentUserId);
        
        const container = document.getElementById('stats-content');
        let html = '<div class="score-display">📊 Статистика</div>';
        html += '<p><strong>Всего попыток:</strong> ' + data.total_attempts + '</p>';
        html += '<p><strong>Средний балл:</strong> ' + data.avg_score + '</p>';
        html += '<p><strong>Лучший результат:</strong> ' + data.best_score + '</p>';
        html += '<p><strong>Достижения:</strong> ' + (data.achievements?.join(', ') || 'пока нет') + '</p>';
        
        if (data.weak_topics && data.weak_topics.length > 0) {
            html += '<p><strong>Темы для повторения:</strong> ' + data.weak_topics.join(', ') + '</p>';
        }
        
        container.innerHTML = html;
        showPanel('stats-container');
        document.getElementById('stats-container').scrollIntoView({ behavior: 'smooth' });
    } catch (e) {
        showError('Ошибка загрузки статистики: ' + e.message);
    }
}

function showCompetitionsInfo() {
    alert('🏆 Функция соревнований доступна через API.\n\nОткройте /docs для просмотра документации.');
}

window.onload = function() {
    hideAllPanels();
    document.getElementById('auth-container').style.display = 'block';
};