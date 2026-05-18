let apiKey = 'ege-token-2026';
let userId = null;
let currentAttemptId = null;
let tasks = [];

async function api(url, method='GET', body=null) {
    const headers = { 'X-API-Key': apiKey, 'Content-Type': 'application/json' };
    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(url, opts);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
}

async function register() {
    const username = document.getElementById('username').value.trim();
    if (!username) return alert('Введите имя');
    try {
        const data = await api(`/api/v1/user/register?username=${encodeURIComponent(username)}`, 'POST');
        userId = data.user_id;
        document.getElementById('userInfo').innerHTML = `✅ Вы зарегистрированы как <strong>${username}</strong> (ID: ${userId})`;
        document.getElementById('actions').style.display = 'block';
    } catch(e) { 
        alert('Ошибка регистрации: ' + e.message); 
    }
}

async function startVariant() {
    try {
        showLoading('Генерируем вариант...');
        const data = await api(`/api/v1/tasks/variant/generate?user_id=${userId}`, 'POST');
        currentAttemptId = data.attempt_id;
        tasks = data.tasks;
        if (!tasks || tasks.length === 0) {
            alert('Не удалось загрузить задания. Попробуйте ещё раз.');
            return;
        }
        renderTasks();
        document.getElementById('resultArea').style.display = 'none';
    } catch(e) {
        alert('Ошибка: ' + e.message);
    }
}

async function startTimeAttack() {
    try {
        showLoading('Готовим блиц-вариант...');
        const data = await api(`/api/v1/tasks/time-attack/start?user_id=${userId}`, 'POST');
        currentAttemptId = data.attempt_id;
        tasks = data.tasks;
        if (!tasks || tasks.length === 0) {
            alert('Не удалось загрузить задания. Попробуйте ещё раз.');
            return;
        }
        renderTasks();
        document.getElementById('resultArea').style.display = 'none';
        setTimeout(() => {
            if (currentAttemptId) {
                alert('Время вышло! Отправляем ответы...');
                submitAnswers();
            }
        }, 600000);
    } catch(e) {
        alert('Ошибка: ' + e.message);
    }
}

function showLoading(message) {
    const container = document.getElementById('tasksContainer');
    container.innerHTML = `<p style="text-align:center; padding:40px;">⏳ ${message}</p>`;
    document.getElementById('taskArea').style.display = 'block';
    document.getElementById('submitBtn').style.display = 'none';
}

function renderTasks() {
    const container = document.getElementById('tasksContainer');
    container.innerHTML = '';
    
    tasks.forEach((task, index) => {
        const card = document.createElement('div');
        card.className = 'task-card';
        card.innerHTML = `
            <div class="task-header">📋 Задание №${task.id}</div>
            <div class="task-topic">📚 ${task.topic} | Часть ${task.part}</div>
            <div class="task-text">${task.text}</div>
            <input type="text" 
                   id="answer_${task.id}" 
                   class="answer-input" 
                   placeholder="Введите ответ"
                   onkeypress="if(event.key==='Enter') submitAnswers()">
        `;
        container.appendChild(card);
    });
    
    document.getElementById('taskArea').style.display = 'block';
    document.getElementById('submitBtn').style.display = 'block';
    document.getElementById('taskArea').scrollIntoView({ behavior: 'smooth' });
}

async function submitAnswers() {
    const answers = tasks.map(task => ({
        task_id: task.id,
        answer: document.getElementById(`answer_${task.id}`)?.value || ''
    }));
    
    try {
        const data = await api(`/api/v1/tasks/variant/submit`, 'POST', {
            user_id: userId,
            attempt_id: currentAttemptId,
            answers: answers
        });
        showResult(data);
        currentAttemptId = null;
    } catch(e) {
        alert('Ошибка отправки: ' + e.message);
    }
}

function showResult(data) {
    const container = document.getElementById('resultContent');
    let html = `<div class="result-score">🎯 Ваш результат: ${data.score} из ${data.max_score} баллов</div>`;
    
    if (data.details) {
        data.details.forEach(d => {
            html += `
                <div class="result-item ${d.is_correct ? 'result-correct' : 'result-incorrect'}">
                    <strong>Задача ${d.task_id}</strong> (${d.topic})<br>
                    Ваш ответ: <strong>${d.your_answer || 'нет ответа'}</strong><br>
                    Правильный ответ: <strong>${d.correct_answer}</strong><br>
                    ${d.is_correct ? '✅ Верно!' : '❌ Неверно'}
                </div>
            `;
        });
    }
    
    container.innerHTML = html;
    document.getElementById('resultArea').style.display = 'block';
    document.getElementById('taskArea').style.display = 'none';
    document.getElementById('resultArea').scrollIntoView({ behavior: 'smooth' });
}

async function listCompetitions() {
    alert('🏆 Соревнования доступны через API.\nОткройте /docs для управления соревнованиями.');
}

async function showStats() {
    try {
        const data = await api(`/api/v1/user/stats/${userId}`);
        const container = document.getElementById('resultContent');
        let html = '<div class="result-score">📊 Ваша статистика</div>';
        html += `<p><strong>Всего попыток:</strong> ${data.total_attempts}</p>`;
        html += `<p><strong>Средний балл:</strong> ${data.avg_score}</p>`;
        html += `<p><strong>Лучший результат:</strong> ${data.best_score}</p>`;
        html += `<p><strong>Достижения:</strong> ${data.achievements?.join(', ') || 'пока нет'}</p>`;
        if (data.weak_topics?.length) {
            html += `<p><strong>Слабые темы:</strong> ${data.weak_topics.join(', ')}</p>`;
        }
        container.innerHTML = html;
        document.getElementById('resultArea').style.display = 'block';
        document.getElementById('taskArea').style.display = 'none';
        document.getElementById('resultArea').scrollIntoView({ behavior: 'smooth' });
    } catch(e) {
        alert('Ошибка загрузки статистики: ' + e.message);
    }
}