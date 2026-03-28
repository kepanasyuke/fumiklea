from flask import Flask, render_template, request, session
import math

app = Flask(__name__)
app.secret_key = 'secret_key'

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'history' not in session:
        session['history'] = []

    if request.method == 'POST':
        expr = request.form.get('expression', '')
        try:
            result = eval(expr, {'__builtins__': {}}, math.__dict__)
            session['history'].append(f'{expr} = {result}')
        except:
            result = 'Ошибка'
        return render_template('index.html', result=result, history=session['history'])
    
    return render_template('index.html', history=session['history'])