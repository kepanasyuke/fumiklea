import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
from simpleeval import simple_eval

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'replace-with-secure-secret')

MAX_HISTORY = 12

@app.route('/', methods=['GET', 'POST'])
def index():
    history = session.setdefault('history', [])
    expression = session.get('expression', '')
    result = session.pop('result', None)

    if request.method == 'POST':
        expr = request.form.get('expression', '').strip()
        if not expr:
            flash('Введите математическое выражение.', 'warning')
            return redirect(url_for('index'))

        try:
            res = simple_eval(expr)
            history.append(f'{expr} = {res}')
            session['history'] = history[-MAX_HISTORY:]
            session['result'] = res
            session['expression'] = expr
        except Exception:
            session['result'] = 'Ошибка'
            session['expression'] = expr
            flash('Неверное выражение. Попробуйте ещё раз.', 'error')

        session.modified = True
        return redirect(url_for('index'))

    return render_template('index.html', result=result, history=history, expression=expression)

@app.route('/history/clear', methods=['POST'])
def clear_history():
    session.pop('history', None)
    session.pop('expression', None)
    session.pop('result', None)
    flash('История очищена.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
