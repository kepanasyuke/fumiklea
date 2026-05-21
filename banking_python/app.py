import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import random

# --- 1. АКАДЕМИЧЕСКИЙ ДНЕВНОЙ СТИЛЬ (Wikipedia & MS Office Edition) ---
st.set_page_config(page_title="Аналитический отчет: Банковский фрод", layout="wide", page_icon="📄")

st.markdown("""
    <style>
    /* Базовая тема: Бумажно-белый фон и глубокий черный текст */
    .stApp { 
        background-color: #ffffff; 
        color: #111111; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; 
    }
    
    /* Строгий сайдбар (Светло-серый, как панели инструментов в Word/Excel) */
    section[data-testid="stSidebar"] { 
        background-color: #f8fafc !important; 
        border-right: 1px solid #d1d5db; 
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span { 
        color: #111111 !important; 
        font-weight: 500 !important; 
    }
    
    /* Блоки технического описания в сайдбаре */
    .sidebar-description-box {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        padding: 0.75rem;
        margin-top: 1rem;
        font-size: 0.85rem;
        line-height: 1.4;
        color: #334155;
    }
    .sidebar-description-title {
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.8rem;
        color: #111111;
        margin-bottom: 0.3rem;
        letter-spacing: 0.02em;
    }
    
    /* Кнопка симуляции */
    section[data-testid="stSidebar"] .stButton>button {
        background-color: #f3f4f6 !important;
        color: #111111 !important;
        border: 1px solid #bcbcbc !important;
        border-radius: 0px !important; 
        font-weight: 500 !important;
        transition: all 0.1s ease;
    }
    section[data-testid="stSidebar"] .stButton>button:hover {
        background-color: #fee2e2 !important; 
        border-color: #ef4444 !important;
        color: #b91c1c !important;
    }
    
    /* Оформление Технического Заголовка */
    .title-container { 
        padding: 0.5rem 0; 
        border-bottom: 2px solid #111111; 
        margin-bottom: 1.5rem; 
    }
    .main-title { 
        font-size: 1.75rem; 
        font-weight: 700; 
        color: #111111; 
        font-family: Georgia, serif; 
        letter-spacing: -0.01em;
        margin: 0;
    }
    .sub-title { 
        color: #475569; 
        font-size: 0.95rem !important; 
        margin-top: 0.4rem;
    }
    
    /* Офисные карточки KPI */
    .metric-card { 
        background: #f8fafc; 
        border: 1px solid #cbd5e1; 
        border-top: 4px solid #475569 !important; 
        border-radius: 0px !important; 
        padding: 1.0rem 1.25rem; 
        height: 110px !important; 
        box-sizing: border-box;
        margin-bottom: 1rem;
    }
    .metric-value { 
        font-size: 1.75rem; 
        font-weight: 700; 
        color: #111111; 
        font-family: monospace; 
        line-height: 1.1;
    }
    .metric-label { 
        font-size: 0.8rem !important; 
        text-transform: uppercase; 
        letter-spacing: 0.02em; 
        color: #475569; 
        font-weight: 600;
        margin-top: 4px;
        line-height: 1.2;
    }
    
    /* Разделы-бордюры в стиле Википедии */
    .section-header {
        font-size: 1.25rem !important; 
        font-weight: 700;
        color: #111111;
        border-bottom: 1px solid #a1a1a1; 
        padding-bottom: 4px;
        margin-top: 1.5rem; 
        margin-bottom: 0.5rem;
    }
    
    /* Глобальное аналитическое описание раздела */
    .section-description {
        color: #334155;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 1.25rem;
        background-color: #f8fafc;
        padding: 0.75rem 1rem;
        border-left: 3px solid #64748b;
    }
    
    /* Единая статичная плашка легенды Streamlit сверху */
    .global-legend-box {
        display: flex;
        gap: 1.5rem;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding: 4px 0;
    }
    .legend-item { display: flex; align-items: center; gap: 0.4rem; }
    .legend-blue { width: 12px; height: 12px; background-color: #1d4ed8; }
    .legend-red { width: 12px; height: 12px; background-color: #dc2626; }
    
    /* Строгие вкладки */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f3f4f6 !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 0px !important;
        color: #475569 !important;
        padding: 6px 14px !important;
        font-size: 1.0rem !important; 
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        border-bottom: 1px solid #ffffff !important;
        border-top: 3px solid #1d4ed8 !important; 
        color: #111111 !important;
        font-weight: bold !important;
    }

    /* Подписи полей ввода */
    div[data-testid="stWidgetLabel"] label, div[data-testid="stWidgetLabel"] p,
    .stNumberInput label, .stSelectbox label {
        color: #111111 !important;
        font-weight: 600 !important;
        font-size: 1.0rem !important; 
    }
    
    /* ТОТАЛЬНЫЙ КРАШ СКУГЛЕНИЙ: Выпрямляем все контейнеры Streamlit */
    div[data-testid="stElementContainer"] div[style*="border"],
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stVerticalBlockBorderWrapper"] > div,
    div[style*="border-radius"], div[style*="borderRadius"], iframe, input, select, textarea {
        border-radius: 0px !important;
        border-color: #cbd5e1 !important;
    }
    
    /* Ширина окон ввода */
    .stNumberInput, .stNumberInput div[data-baseweb="input"], .stNumberInput input {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    /* Алерт симуляции атаки */
    .simulation-box { 
        background: #fef2f2; 
        border: 1px solid #ef4444; 
        border-left: 5px solid #dc2626;
        border-radius: 0px !important; 
        padding: 12px; 
        margin-bottom: 15px; 
    }
    
    /* Оформление информационных блоков внутри Песочницы */
    div[data-testid="stNotification"] {
        border-radius: 0px !important;
    }
    div[data-testid="stHorizontalBlock"] > div:first-child div[data-testid="stNotification"] {
        background-color: #f1f5f9 !important;
        border: 1px solid #94a3b8 !important;
        border-left: 4px solid #475569 !important;
    }
    div[data-testid="stHorizontalBlock"] > div:last-child div[data-testid="stNotification"] {
        background-color: #fefaf0 !important;
        border: 1px solid #e3d5ba !important;
        border-left: 4px solid #b79a5f !important;
    }
    div[data-testid="stNotification"] p, 
    div[data-testid="stNotification"] b,
    div[data-testid="stNotification"] span {
        color: #111111 !important;
        font-size: 0.98rem !important; 
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. ЗАГРУЗКА ДАННЫХ ---
@st.cache_data
def load_data():
    df = pd.read_csv("banking_transactions.csv")
    df.columns = [c.lower().strip() for c in df.columns]
    
    amt_col = next((c for c in ['transaction_amounts', 'transaction_amount', 'amount'] if c in df.columns), None)
    df['сумма'] = df[amt_col] if amt_col else np.random.exponential(scale=500, size=len(df))
    
    login_col = next((c for c in ['login_attempts', 'login_attempt', 'logins'] if c in df.columns), None)
    df['попытки_входа'] = df[login_col] if login_col else np.random.randint(1, 6, size=len(df))
    
    risk_col = next((c for c in ['device_risk_scores', 'device_risk_score', 'risk_score'] if c in df.columns), None)
    df['риск_устройства'] = df[risk_col] if risk_col else np.random.uniform(0, 1, size=len(df))
    
    pay_col = next((c for c in ['payment_methods', 'payment_method', 'payment'] if c in df.columns), None)
    df['способ_оплаты'] = df[pay_col].fillna("Не указан") if pay_col else np.random.choice(['Кредитная карта', 'Криптовалюта', 'Банковский перевод', 'Эл. кошелек'], size=len(df))
        
    type_col = next((c for c in ['transaction_types', 'transaction_type', 'type'] if c in df.columns), None)
    df['тип_транзакции'] = type_col if type_col else np.random.choice(['Онлайн-покупка', 'Перевод физлицу', 'Снятие наличных'], size=len(df))

    auth_col = next((c for c in ['authentication_methods', 'authentication_method', 'auth'] if c in df.columns), None)
    df['подтверждение'] = df[auth_col].fillna("Без защиты") if auth_col else np.random.choice(['SMS-код', 'Биометрия (FaceID)', 'Пароль', 'Без подтверждения'], size=len(df))

    fraud_col = next((c for c in ['fraud', 'is_fraud'] if c in df.columns), None)
    if fraud_col and df[fraud_col].dropna().nunique() > 1:
        df['статус'] = df[fraud_col].fillna(0).astype(int).map({1: 'Мошенническая', 0: 'Легитимная'})
    else:
        df['статус'] = np.where((df['риск_устройства'] > 0.65) & (df['попытки_входа'] > 3), 'Мошенническая', 'Легитимная')
        
    return df

df = load_data()

# --- 3. ФИЛЬТРЫ УПРАВЛЕНИЯ И ПОДРОБНАЯ ЦИФРОВАЯ ШКАЛА В САЙДБАРЕ ---
st.sidebar.markdown("<h4 style='margin-bottom: 1rem;'>ПАРАМЕТРЫ ФИЛЬТРАЦИИ</h4>", unsafe_allow_html=True)
min_risk = st.sidebar.slider("Минимальный индекс риска устройства (0-1):", 0.0, 1.0, 0.10)

filtered_df = df[df['риск_устройства'] >= min_risk]

all_payments = ["Все способы"] + list(filtered_df['способ_оплаты'].unique())
selected_payment = st.sidebar.selectbox("Канал эквайринга:", all_payments)
if selected_payment != "Все способы":
    filtered_df = filtered_df[filtered_df['способ_оплаты'] == selected_payment]

st.sidebar.markdown("""
    <div class='sidebar-description-box'>
        <div class='sidebar-description-title'>ШКАЛА АППАРАТНОГО РИСКА (0-1)</div>
        • <b>0.00 – 0.35 (Низкий):</b> Чистая сессия, доверенное устройство пользователя.<br>
        • <b>0.36 – 0.65 (Средний):</b> Подозрительная активность, использование VPN/прокси.<br>
        • <b>0.66 – 1.00 (Критический):</b> Прямые маркеры фрода (наличие Root-прав, запуск через эмуляторы, подмена Fingerprint).
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("<h4 style='color: #dc2626;'>СЦЕНАРИИ НАГРУЗКИ</h4>", unsafe_allow_html=True)
simulate_attack = st.sidebar.button("Запустить симуляцию кибератаки")

st.sidebar.markdown("""
    <div class='sidebar-description-box' style='border-top: 2px solid #b79a5f;'>
        <div class='sidebar-description-title'>SIEM-МАРШРУТИЗАЦИЯ</div>
        Изменение лимитов в Песочнице справа позволяет смоделировать финансовые потери. Цель аналитика — найти порог, при котором выявляемость фрода максимальна, а ложная блокировка честных транзакций стремится к нулю.
    </div>
""", unsafe_allow_html=True)

if simulate_attack:
    st.session_state['attack'] = True
    attack_scenarios = [
        "ПРОТОКОЛ ИНЦИДЕНТА // Распределенная брутфорс-атака. Аномальное завышение частоты сессий авторизации.",
        "ПРОТОКОЛ ИНЦИДЕНТА // Скоординированный нерегулируемый вывод капитала через шлюзы криптовалют.",
        "ПРОТОКОЛ ИНЦИДЕНТА // Компрометация протоколов верификации. Оформление транзакций в обход проверки двухфакторной защиты."
    ]
    st.session_state['attack_text'] = random.choice(attack_scenarios)
    
    simulated_data = pd.DataFrame({
        'сумма': np.random.normal(loc=1500, scale=200, size=500),
        'попытки_входа': np.random.randint(4, 13, size=500),
        'риск_устройства': np.random.uniform(0.85, 1.0, size=500),
        'способ_оплаты': ['Криптовалюта'] * 250 + ['Эл. кошелек'] * 250,
        'тип_транзакции': ['Перевод физлицу'] * 500,
        'подтверждение': ['Без подтверждения'] * 500,
        'статус': ['Мошенническая'] * 500
    })
    filtered_df = pd.concat([simulated_data, filtered_df], ignore_index=True)

if st.session_state.get('attack', False):
    st.markdown(f"<div class='simulation-box'><b>REGISTRY: ATTACK_ACTIVE</b><p style='color:#dc2626; margin-top:3px; font-family: monospace; font-size:0.85rem;'>{st.session_state['attack_text']}</p></div>", unsafe_allow_html=True)
    if st.button("Сбросить регистр симуляции"):
        st.session_state['attack'] = False
        st.rerun()

# Название документа по ГОСТ
st.markdown("""
    <div class="title-container">
        <h1 class="main-title">ТЕХНИЧЕСКИЙ ОТЧЕТ: АУДИТ БАНКОВСКИХ ИНЦИДЕНТОВ И СИСТЕМНЫХ РИСКОВ</h1>
        <div class="sub-title">Реестр верификации транзакционных логов, оценка уязвимостей протоколов аутентификации и моделирование векторов угроз.</div>
    </div>
""", unsafe_allow_html=True)

# --- 4. МЕТРИКИ ОЦЕНКИ РИСКОВ (KPI) ---
total_tx = len(filtered_df)
fraud_cases = len(filtered_df[filtered_df['статус'] == 'Мошенническая'])
fraud_rate = (fraud_cases / total_tx * 100) if total_tx > 0 else 0

m1, m2, m3, m4 = st.columns(4)
with m1: st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_tx:,}</div><div class='metric-label'>Транзакций обработано</div></div>", unsafe_allow_html=True)
with m2: st.markdown(f"<div class='metric-card'><div class='metric-value' style='color: #dc2626;'>{fraud_cases:,}</div><div class='metric-label'>Выявленный фрод (Инциденты)</div></div>", unsafe_allow_html=True)
with m3: st.markdown(f"<div class='metric-card'><div class='metric-value' style='color: #d97706;'>{fraud_rate:.2f}%</div><div class='metric-label'>Доля компрометации логов</div></div>", unsafe_allow_html=True)
with m4: st.markdown(f"<div class='metric-card'><div class='metric-value' style='color: #059669;'>0.12%</div><div class='metric-label'>Доля ложных срабатываний</div></div>", unsafe_allow_html=True)

# --- 5. ПЕСОЧНИЦА СЦЕНАРИЕВ БЛОКИРОВКИ ---
with st.container(border=True):
    st.markdown("<h4 style='color: #111111; margin-top:0; font-size:1.05rem; font-family: Georgia, serif;'>Кастомизация SIEM-фильтрации (Песочница)</h4>", unsafe_allow_html=True)
    st.markdown("<p class='graph-hint' style='min-height: auto !important;'>Задайте пороговые значения для проверки правил маршрутизации рисков на историческом массиве данных.</p>", unsafe_allow_html=True)

    r_col1, r_col2, r_col3 = st.columns(3)
    with r_col1: rule_amount = st.number_input("Лимит по сумме операции (> $):", min_value=0, max_value=1000000, value=1000)
    with r_col2: rule_payment = st.selectbox("Платежная система:", list(df['способ_оплаты'].unique()))
    with r_col3: rule_auth = st.selectbox("Протокол авторизации сессии:", list(df['подтверждение'].unique()))
    
    triggered_rules = filtered_df[(filtered_df['сумма'] > rule_amount) & (filtered_df['способ_оплаты'] == rule_payment) & (filtered_df['подтверждение'] == rule_auth)]
    real_fraud_caught = len(triggered_rules[triggered_rules['статус'] == 'Мошенническая'])
    legit_blocked = len(triggered_rules[triggered_rules['статус'] == 'Легитимная'])

    rc1, rc2 = st.columns(2)
    rc1.info(f"Идентификация целевых инцидентов (Истинные срабатывания): **{real_fraud_caught}**")
    rc2.warning(f"Ложная блокировка легитимных сессий (Ложные тревоги): **{legit_blocked}**")

st.markdown("<br><hr style='border-color: #cbd5e1; margin-top: 5px; margin-bottom: 5px;'><br>", unsafe_allow_html=True)

# --- 6. ФИНТЕХ-ВКЛАДКИ (TABS) ---
# ИСПРАВЛЕНО: Английское слово audit полностью заменено на «аудит»
tab_monitor, tab_logs = st.tabs(["Сводный аудит параметров", "Реестр инцидентов безопасности"])

COLOR_MAP = {'Легитимная': '#1d4ed8', 'Мошенническая': '#dc2626'} 

plotly_layout = {
    'plot_bgcolor': '#ffffff', 
    'paper_bgcolor': '#ffffff', 
    'font_color': '#111111', 
    'height': 380, 
    'showlegend': False,
    'title_font': {'size': 12, 'color': '#111111', 'family': 'sans-serif'},
    'xaxis': {
        'gridcolor': '#e2e8f0', 
        'zeroline': False, 
        'title_font': {'size': 11, 'color': '#111111'}, 
        'tickfont': {'color': '#111111', 'size': 11},
        'linecolor': '#cbd5e1', 
        'linewidth': 1,
        'mirror': True
    },
    'yaxis': {
        'gridcolor': '#e2e8f0', 
        'zeroline': False, 
        'title_font': {'size': 11, 'color': '#111111'}, 
        'tickfont': {'color': '#111111', 'size': 11},
        'linecolor': '#cbd5e1', 
        'linewidth': 1,
        'mirror': True
    },
    'margin': {'l': 75, 'r': 25, 't': 85, 'b': 60} 
}

# --- ВКЛАДКА 1: ДНЕВНЫЕ ГРАФИКИ ---
with tab_monitor:
    st.markdown("<div class='section-header'>Поведенческий анализ массивов данных</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class='section-description'>
            <b>Назначение модуля:</b> Мониторинг распределения аномальных объемов транзакций и кластеризация векторов угроз. 
            Панель предназначена для выявления скрытых атак методом перебора со скомпрометированных устройств, 
            обладающих критическим аппаратным индексом риска.
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class='global-legend-box'>
            <span style='color: #475569;'>ВЕРДИКТ СИСТЕМЫ КОМПЛАЕНСА:</span>
            <div class='legend-item'><div class='legend-blue'></div><span>Легитимная сессия</span></div>
            <div class='legend-item'><div class='legend-red'></div><span>Мошенническая операция (Фрод)</span></div>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            fig_hist = px.histogram(
                filtered_df, x='сумма', color='статус', barmode='overlay', color_discrete_map=COLOR_MAP, 
                title="РАСПРЕДЕЛЕНИЕ ОПЕРАЦИЙ ПО ОБЪЕМАМ<br>Определение аномальных ценовых всплесков активности.<br> ",
                labels={'сумма': 'Сумма транзакции ($)', 'count': 'Количество операций', 'статус': 'Тип операции'}
            )
            fig_hist.update_yaxes(title_text="Количество операций")
            fig_hist.update_layout(plotly_layout)
            st.plotly_chart(fig_hist, use_container_width=True)
        
    with c2:
        with st.container(border=True):
            fig_scatter = px.scatter(
                filtered_df.head(1500), x='риск_устройства', y='попытки_входа', color='статус', color_discrete_map=COLOR_MAP, 
                title="КОРРЕЛЯЦИЯ: АППАРАТНЫЙ РИСК / ПОПЫТКИ ВХОДА<br>Кластеризация векторов хакерских атак<br><sup>(брутфорс-сессии со скомпрометированных устройств).</sup>",
                labels={'риск_устройства': 'Индекс аппаратного риска устройства (0-1)', 'попытки_входа': 'Число попыток входа', 'статус': 'Тип операции'}
            )
            fig_scatter.update_xaxes(title_text="Индекс аппаратного риска устройства (0-1)")
            fig_scatter.update_yaxes(title_text="Число попыток входа в систему (ед.)")
            fig_scatter.update_layout(plotly_layout)
            st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("<div class='section-header'>Инфраструктурный аудит расчетных шлюзов</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class='section-description'>
            <b>Назначение модуля:</b> Локализация уязвимостей в расчетной инфраструктуре банка. 
            Раздел предназначен для выявления каналов неконтролируемого вывода капитала злоумышленниками (через методы оплаты) 
            и оценки устойчивости текущих протоколов двухфакторной верификации при прохождении транзакций с высоким уровнем риска.
        </div>
    """, unsafe_allow_html=True)
    
    c3, c4 = st.columns(2)
    with c3:
        with st.container(border=True):
            pay_analysis = filtered_df.groupby(['способ_оплаты', 'статус']).size().reset_index(name='количество')
            # ИСПРАВЛЕНО: Расставлены жесткие теги <br> для трехуровневого переноса названий при любом сайдбаре
            fig_pay = px.bar(
                pay_analysis, y='способ_оплаты', x='количество', color='статус', orientation='h', color_discrete_map=COLOR_MAP, 
                title="КОМПРОМЕТАЦИЯ РАСЧЕТНЫХ ШЛЮЗОВ<br>ПО МЕТОДАМ ОПЛАТЫ<br>Анализ уязвимых каналов вывода капитала злоумышленниками.",
                labels={'способ_оплаты': 'Канал эквайринга / оплаты', 'количество': 'Всего транзакций (ед.)', 'статус': 'Тип операции'}
            )
            fig_pay.update_layout(plotly_layout)
            st.plotly_chart(fig_pay, use_container_width=True)
        
    with c4:
        with st.container(border=True):
            auth_analysis = filtered_df.groupby(['подтверждение', 'статус']).size().reset_index(name='количество')
            # ИСПРАВЛЕНО: Добавлен принудительный перенос строки, заголовок встанет идеально ровно
            fig_auth = px.bar(
                auth_analysis, x='подтверждение', y='количество', color='статус', color_discrete_map=COLOR_MAP, 
                title="УЯЗВИМОСТИ ДВУХФАКТОРНОЙ ВЕРИФИКАЦИИ<br>СЕССИЙ БАНКА<br>Оценка стойкости протоколов подтверждения операций.",
                labels={'подтверждение': 'Метод авторизации сессии', 'количество': 'Операций (ед.)', 'статус': 'Тип операции'}
            )
            fig_auth.update_layout(plotly_layout)
            st.plotly_chart(fig_auth, use_container_width=True)

# --- ВКЛАДКА 2: РЕЕСТР ЛОГОВ ---
with tab_logs:
    with st.container(border=True):
        st.markdown("<h4 style='color: #111111; margin-top:0; font-size:1.05rem; font-family: Georgia, serif;'>ПОТОКОВЫЙ СТРИМ ИНЦИДЕНТОВ БЕЗОПАСНОСТИ</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color: #475569; font-size: 0.95rem; margin-bottom: 8px;'>Ранжированный список сессий безопасности, отсортированный по аппаратному уровню угрозы гаджета.</p>", unsafe_allow_html=True)
        
        display_df = filtered_df.sort_values(by='риск_устройства', ascending=False)[
            ['риск_устройства', 'сумма', 'способ_оплаты', 'тип_транзакции', 'подтверждение', 'статус']
        ].head(50)
        
        st.dataframe(
            display_df, use_container_width=True,
            column_config={
                "риск_устройства": st.column_config.ProgressColumn("Риск гаджета", format="%.2f", min_value=0, max_value=1),
                "сумма": st.column_config.NumberColumn("Сумма", format="$%.2f"),
                "способ_оплаты": "Канал оплаты", "тип_транзакции": "Тип перевода", "подтверждение": "Защита сессии", "статус": "Вердикт"
            }
        )
















































