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
    const username = document.getElementById('username').value;
    if (!username) return alert('Введите имя');
    try {
        const data = await api(`/api/v1/user/register?username=${encodeURIComponent(username)}`, 'POST');
        userId = data.user_id;
        document.getElementById('userInfo').innerText = `Вы: ${username} (ID ${userId})`;
        document.getElementById('auth').style.display = 'none';
        document.getElementById('actions').style.display = 'block';
    } catch(e) { alert('Ошибка: ' + e.message); }
}

async function startVariant() {
    try {
        const data = await api(`/api/v1/tasks/variant/generate?user_id=${userId}`, 'POST');
        console.log('Ответ сервера:', data);
        currentAttemptId = data.attempt_id;
        tasks = data.tasks;
        if (!tasks || tasks.length === 0) {
            alert('Не удалось загрузить задания. Попробуйте ещё раз.');
            return;
        }
        renderTasks();
    } catch(e) {
        alert('Ошибка загрузки варианта: ' + e.message);
    }
}

async function startTimeAttack() {
    try {
        const data = await api(`/api/v1/tasks/time-attack/start?user_id=${userId}`, 'POST');
        console.log('Ответ сервера:', data);
        currentAttemptId = data.attempt_id;
        tasks = data.tasks;
        if (!tasks || tasks.length === 0) {
            alert('Не удалось загрузить задания. Попробуйте ещё раз.');
            return;
        }
        renderTasks();
        setTimeout(() => {
            if (currentAttemptId) {
                alert('Время вышло! Отправляем ответы...');
                submitAnswers();
            }
        }, 600000);
    } catch(e) {
        alert('Ошибка загрузки Time Attack: ' + e.message);
    }
}

function renderTasks() {
    const area = document.getElementById('taskArea');
    area.style.display = 'block';
    let html = '<h2>Решите задания:</h2>';
    tasks.forEach(task => {
        html += `
            <div class="task">
                <p><strong>Задание №${task.id}</strong> (${task.topic})</p>
                <p>${task.text}</p>
                <input type="text" id="answer_${task.id}" placeholder="Ваш ответ">
            </div>
        `;
    });
    html += '<button onclick="submitAnswers()">Отправить ответы</button>';
    area.innerHTML = html;
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
        alert('Ошибка отправки ответов: ' + e.message);
    }
}

function showResult(data) {
    let html = `<h2>Результат: ${data.score}/${data.max_score}</h2>`;
    data.details.forEach(d => {
        html += `<p class="${d.is_correct ? 'correct' : 'incorrect'}">
            Задача ${d.task_id}: ваш ответ "${d.your_answer}" | верный "${d.correct_answer}"
        </p>`;
    });
    document.getElementById('resultArea').innerHTML = html;
    document.getElementById('taskArea').style.display = 'none';
}

async function listCompetitions() {
    alert('Создание и просмотр соревнований пока через API. Используйте /docs');
}

async function showStats() {
    try {
        const data = await api(`/api/v1/user/stats/${userId}`);
        let html = `<p>Попыток: ${data.total_attempts}, Средний балл: ${data.avg_score}, Лучший: ${data.best_score}</p>`;
        html += `<p>Достижения: ${data.achievements?.join(', ') || 'нет'}</p>`;
        if (data.weak_topics?.length) html += `<p>Слабые темы: ${data.weak_topics.join(', ')}</p>`;
        document.getElementById('resultArea').innerHTML = html;
    } catch(e) {
        alert('Ошибка загрузки статистики: ' + e.message);
    }
}
