import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
import hashlib

# --- 1. АКАДЕМИЧЕСКИЙ ДНЕВНОЙ СТИЛЬ С ПОВЫШЕННОЙ КОНТРАСТНОСТЬЮ ШРИФТОВ ---
st.set_page_config(page_title="Антифрод-платформа верификации транзакций", layout="wide", page_icon="📄")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #111111; font-family: -apple-system, sans-serif; }
    section[data-testid="stSidebar"] { background-color: #f8fafc !important; border-right: 1px solid #d1d5db; }
    .sidebar-description-box { background-color: #ffffff; border: 1px solid #cbd5e1; padding: 0.75rem; margin-top: 1rem; font-size: 0.85rem; color: #111111; font-weight: 500; }
    .sidebar-description-title { font-weight: 700; text-transform: uppercase; font-size: 0.8rem; color: #000000; }
    .title-container { padding: 0.5rem 0; border-bottom: 2px solid #111111; margin-bottom: 1.5rem; }
    .main-title { font-size: 1.75rem; font-weight: 700; color: #111111; font-family: Georgia, serif; margin: 0; }
    .sub-title { color: #111111; font-weight: 500; font-size: 0.95rem !important; margin-top: 0.4rem; }
    .metric-card { background: #f8fafc; border: 1px solid #cbd5e1; border-top: 4px solid #475569 !important; padding: 1.0rem 1.25rem; height: 110px !important; box-sizing: border-box; margin-bottom: 1rem; }
    .metric-value { font-size: 1.75rem; font-weight: 700; color: #111111; font-family: monospace; line-height: 1.1; }
    .metric-label { font-size: 0.8rem !important; text-transform: uppercase; color: #000000; font-weight: 700; }
    .section-header { font-size: 1.25rem !important; font-weight: 700; color: #000000; border-bottom: 2px solid #000000; padding-bottom: 4px; margin-top: 1.5rem; }
    .section-description { color: #000000; font-weight: 500; font-size: 0.95rem; line-height: 1.5; margin-bottom: 1.25rem; background-color: #f8fafc; padding: 0.75rem 1rem; border-left: 4px solid #000000; }
    .global-legend-box { display: flex; gap: 1.5rem; font-size: 0.9rem; font-weight: 700; margin-bottom: 1rem; padding: 4px 0; color: #000000; }
    .legend-item { display: flex; align-items: center; gap: 0.4rem; }
    .legend-blue { width: 12px; height: 12px; background-color: #1d4ed8; }
    .legend-red { width: 12px; height: 12px; background-color: #dc2626; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { background-color: #f3f4f6 !important; border: 1px solid #cbd5e1 !important; border-radius: 0px !important; color: #000000 !important; font-weight: 600 !important; padding: 6px 14px !important; }
    .stTabs [aria-selected="true"] { background-color: #ffffff !important; border-bottom: 1px solid #ffffff !important; border-top: 3px solid #1d4ed8 !important; color: #000000 !important; font-weight: 700 !important; }
    div[data-testid="stWidgetLabel"] label, div[data-testid="stWidgetLabel"] p, .stSlider label, .stSelectbox label { color: #000000 !important; font-weight: 700 !important; font-size: 1.0rem !important; }
    div[data-testid="stElementContainer"] div[style*="border"], div[data-testid="stVerticalBlockBorderWrapper"], div[data-testid="stVerticalBlockBorderWrapper"] > div, iframe, input, select, textarea { border-radius: 0px !important; border-color: #cbd5e1 !important; }
    .stSlider, .stSelectbox { width: 100% !important; max-width: 100% !important; }
    .simulation-box { background: #fef2f2; border: 1px solid #ef4444; border-left: 5px solid #dc2626; padding: 12px; margin-bottom: 15px; color: #000000; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- 2. СЛОВAРИ ДВУХСТОРОННЕГО МЭППИНГА ДЛЯ ДАТАСЕТА KAGGLE ---
PAY_MAP = {'Credit Card': 'Кредитная карта', 'Crypto': 'Криптовалюта', 'Bank Transfer': 'Банковский перевод', 'Net Banking': 'Электронный кошелек', 'Не указан': 'Не указан'}
PAY_REV = {v: k for k, v in PAY_MAP.items()}

AUTH_MAP = {'SMS OTP': 'SMS-код', 'Biometric': 'Биометрия (FaceID)', 'Password': 'Пароль', 'None': 'Без подтверждения', 'Без защиты': 'Без подтверждения'}
AUTH_REV = {v: k for k, v in AUTH_MAP.items()}

# --- 3. ПОДГРУЗКА ВСЕЙ БАЗЫ ДАННЫХ ---
@st.cache_data
def load_data(file_name="banking_transactions.csv"):
    sha256_hash = "ВНУТРЕННЯЯ ГЕНЕРАЦИЯ"
    if os.path.exists(file_name):
        try:
            with open(file_name, "rb") as f:
                sha256_hash = hashlib.sha256(f.read()).hexdigest()[:16].upper()
            df = pd.read_csv(file_name)
            df.columns = [c.lower().strip() for c in df.columns]
        except Exception:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    if df.empty:
        size = 5000
        np.random.seed(42)
        df = pd.DataFrame({
            'transaction_amount': np.concatenate([np.random.exponential(scale=350, size=int(size*0.95)), np.random.normal(loc=1900, scale=300, size=int(size*0.05))]),
            'device_risk_score': np.concatenate([np.random.beta(a=2, b=5, size=int(size*0.95)), np.random.uniform(0.75, 1.0, size=int(size*0.05))]),
            'login_attempts': np.concatenate([np.random.randint(1, 3, size=int(size*0.95)), np.random.randint(4, 7, size=int(size*0.05))]),
            'payment_method': np.random.choice(list(PAY_MAP.keys()), size=size),
            'authentication_method': np.random.choice(list(AUTH_MAP.keys()), size=size),
            'transaction_type': np.random.choice(['Онлайн-покупка', 'Перевод физлицу', 'Снятие наличных'], size=size),
            'is_fraud': np.concatenate([np.zeros(int(size*0.95)), np.ones(int(size*0.05))])
        })

    df['сумма'] = df['transaction_amount'] if 'transaction_amount' in df.columns else (df['amount'] if 'amount' in df.columns else df.iloc[:, 0])
    df['риск_устройства'] = df['device_risk_score'] if 'device_risk_score' in df.columns else (df['risk_score'] if 'risk_score' in df.columns else np.random.uniform(0, 1, len(df)))
    df['попытки_входа'] = df['login_attempts'] if 'login_attempts' in df.columns else (df['login_attempt'] if 'login_attempt' in df.columns else np.random.randint(1, 5, len(df)))
    
    df['способ_оплаты'] = df['payment_method'].astype(str).str.strip() if 'payment_method' in df.columns else np.random.choice(list(PAY_MAP.keys()), size=len(df))
    df['подтверждение'] = df['authentication_method'].astype(str).str.strip() if 'authentication_method' in df.columns else np.random.choice(list(AUTH_MAP.keys()), size=len(df))
    df['тип_транзакции'] = df['transaction_type'] if 'transaction_type' in df.columns else np.random.choice(['Онлайн-покупка', 'Перевод физлицу', 'Снятие наличных'], size=len(df))
    
    if 'is_fraud' in df.columns:
        df['статус'] = df['is_fraud'].astype(int).map({1: 'Мошенническая', 0: 'Легитимная'})
    else:
        df['статус'] = np.where((df['риск_устройства'] > 0.65) & (df['попытки_входа'] > 3), 'Мошенническая', 'Легитимная')
        
    return df, sha256_hash

df, data_hash = load_data()

# --- 4. САЙДБАР (ПАНЕЛЬ АНАЛИТИКА И ФИЛЬТРЫ) ---
st.sidebar.markdown("<h4 style='margin-bottom: 1rem;'>ПАРАМЕТРЫ ФИЛЬТРАЦИИ</h4>", unsafe_allow_html=True)
min_risk = st.sidebar.slider("Минимальный индекс риска устройства (0-1):", 0.0, 1.0, 0.10)
filtered_df = df[df['риск_устройства'] >= min_risk]

unique_payments_en = filtered_df['способ_оплаты'].unique()
translated_payments = [PAY_MAP.get(p, p) for p in unique_payments_en]
all_payments_options = ["Все способы"] + list(set(translated_payments))
selected_payment_ru = st.sidebar.selectbox("Канал эквайринга:", all_payments_options)

if selected_payment_ru != "Все способы":
    selected_payment_en = PAY_REV.get(selected_payment_ru, selected_payment_ru)
    filtered_df = filtered_df[filtered_df['способ_оплаты'] == selected_payment_en]

st.sidebar.markdown(f"""
    <div class='sidebar-description-box'>
        <div class='sidebar-description-title'>ШКАЛА АППАРАТНОГО РИСКА (0-1)</div>
        • <b>0.00 – 0.35 (Низкий):</b> Штатное устройство.<br>
        • <b>0.36 – 0.65 (Средний):</b> Использование VPN/прокси.<br>
        • <b>0.66 – 1.00 (Критический):</b> Прямой фрод (эмуляторы).<br>
        <hr style='margin: 6px 0; border-color: #cbd5e1;'>
        <small style='color:#000000;'>Контрольная сумма логов:<br><b>{data_hash}</b></small>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("<h4 style='color: #dc2626;'>СЦЕНАРИИ НАГРУЗКИ</h4>", unsafe_allow_html=True)
simulate_attack = st.sidebar.button("Запустить симуляцию кибератаки")

if simulate_attack:
    st.session_state['attack'] = True
    sim_data = pd.DataFrame({
        'сумма': np.random.normal(loc=2300, scale=100, size=300),
        'риск_устройства': np.random.uniform(0.92, 1.0, size=300),
        'попытки_входа': np.random.randint(5, 9, size=300),
        'способ_оплаты': ['Crypto'] * 300,
        'подтверждение': ['None'] * 300,
        'тип_транзакции': ['Перевод физлицу'] * 300,
        'статус': ['Мошенническая'] * 300
    })
    filtered_df = pd.concat([sim_data, filtered_df], ignore_index=True)

if st.session_state.get('attack', False):
    st.markdown("<div class='simulation-box'><b>РЕГИСТР: ОБНАРУЖЕНА АТАКA</b><br><small>Вектор угрозы: распределенный перебор авторизации на шлюзе криптовалют без двухфакторной защиты.</small></div>", unsafe_allow_html=True)
    if st.button("Сбросить регистр симуляции"):
        st.session_state['attack'] = False
        st.rerun()

st.markdown("<div class='title-container'><h1 class='main-title'>КОРПОРАТИВНЫЙ МОНИТОР КОМПЛАЕНСА И АНТИФРОД-АНАЛИТИКИ</h1><div class='sub-title'>Адаптивный операционный комплекс верификации транзакционных логов, оценка уязвимостей и моделирование векторов угроз.</div></div>", unsafe_allow_html=True)

# --- 5. МЕТРИКИ ОЦЕНКИ РИСКОВ (KPI) ---
total_tx = len(filtered_df)
fraud_cases = len(filtered_df[filtered_df['статус'] == 'Мошенническая'])
fraud_rate = (fraud_cases / total_tx * 100) if total_tx > 0 else 0
total_volume = filtered_df['сумма'].sum()

formatted_volume = f"\({total_volume / 1_000_000:.2f}M" if total_volume >= 1_000_000 else f"\){total_volume:,.0f}"

m1, m2, m3, m4 = st.columns(4)
with m1: st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_tx:,}</div><div class='metric-label'>Сессий в логах</div></div>", unsafe_allow_html=True)
with m2: st.markdown(f"<div class='metric-card'><div class='metric-value' style='color: #dc2626;'>{fraud_cases:,}</div><div class='metric-label'>Инцидентов выявлено</div></div>", unsafe_allow_html=True)
with m3: st.markdown(f"<div class='metric-card'><div class='metric-value' style='color: #d97706;'>{fraud_rate:.2f}%</div><div class='metric-label'>Доля фрод-операций</div></div>", unsafe_allow_html=True)
with m4: st.markdown(f"<div class='metric-card'><div class='metric-value' style='color: #10b981;'>{formatted_volume}</div><div class='metric-label'>Оборот под мониторингом</div></div>", unsafe_allow_html=True)

# --- 6. БАНКОВСКИЙ ИНСТРУМЕНТ: БИЗНЕС-МОДЕЛИРОВАНИЕ И МАТРИЦА ОШИБОК ---
with st.container(border=True):
    st.markdown("<h4 style='color: #111111; margin-top:0; font-size:1.05rem; font-family: Georgia, serif;'>Кастомизация SIEM-фильтрации (Бизнес-моделирование)</h4>", unsafe_allow_html=True)
    
    max_database_amount = float(df['сумма'].max()) if not df.empty else 5000.0
    default_initial_value = min(1200.0, max_database_amount)
    
    ru_payments_list = [PAY_MAP.get(p, p) for p in df['способ_оплаты'].unique()]
    ru_auth_list = [AUTH_MAP.get(a, a) for a in df['подтверждение'].unique()]
    
    r_col1, r_col2, r_col3 = st.columns(3)
    with r_col1: rule_amount = st.slider("Порог жесткой блокировки транзакции (\$):", min_value=0.0, max_value=max_database_amount, value=default_initial_value, step=10.0)
    with r_col2: rule_payment_ru = st.selectbox("Целевая платежная система:", list(set(ru_payments_list)))
    with r_col3: rule_auth_ru = st.selectbox("Слабый протокол аутентификации:", list(set(ru_auth_list)))
    
    rule_payment_en = PAY_REV.get(rule_payment_ru, rule_payment_ru)
    rule_auth_en = AUTH_REV.get(rule_auth_ru, rule_auth_ru)
    
    triggered = filtered_df[(filtered_df['сумма'] > rule_amount) & (filtered_df['способ_оплаты'] == rule_payment_en) & (filtered_df['подтверждение'] == rule_auth_en)]
    tp = len(triggered[triggered['статус'] == 'Мошенническая'])
    fp = len(triggered[triggered['статус'] == 'Легитимная'])
    
    saved_cash = triggered[triggered['статус'] == 'Мошенническая']['сумма'].sum()
    lost_cash = triggered[triggered['статус'] == 'Легитимная']['сумма'].sum()
    precision = (tp / (tp + fp) * 100) if (tp + fp) > 0 else 100.0
    
    rc1, rc2, rc3 = st.columns(3)
    rc1.metric("Предотвращенный ущерб", f"\${saved_cash:,.0f}", delta=f"Инцидентов: {tp}")
    rc2.metric("Потери от ложных тревог", f"\${lost_cash:,.0f}", delta=f"Блок клиентов: {fp}", delta_color="inverse")
    rc3.metric("Точность правила", f"{precision:.1f}%")
    
    st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
    
    export_df = triggered.copy()
    export_df['способ_оплаты'] = export_df['способ_оплаты'].map(PAY_MAP)
    export_df['подтверждение'] = export_df['подтверждение'].map(AUTH_MAP)
    
    csv_buffer = export_df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Сформировать выгрузку отфильтрованных логов комплаенс-контроля (CSV)", data=csv_buffer, file_name="siem_incidents_report.csv", mime="text/csv", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 7. ФИНТЕХ-ВКЛАДКИ (TABS) ---
tab_monitor, tab_logs = st.tabs(["Сводный аудит параметров", "Реестр инцидентов безопасности"])
COLOR_MAP_PLOT = {'Легитимная': '#1d4ed8', 'Мошенническая': '#dc2626'}

def apply_bank_theme(fig):
    fig.update_layout({
        'plot_bgcolor': '#ffffff', 'paper_bgcolor': '#ffffff', 'font_color': '#000000', 'height': 400, 'showlegend': False,
        'title_font': {'size': 13, 'color': '#000000', 'family': 'sans-serif', 'weight': 'bold'},
        'xaxis': {
            'gridcolor': '#e2e8f0', 'zeroline': False, 'linecolor': '#cbd5e1', 'linewidth': 1, 'mirror': True,
            'title_font': {'size': 12, 'color': '#000000', 'weight': 'bold'}, 'tickfont': {'color': '#000000', 'size': 11, 'weight': 'bold'}
        },
        'yaxis': {
            'gridcolor': '#e2e8f0', 'zeroline': False, 'linecolor': '#cbd5e1', 'linewidth': 1, 'mirror': True,
            'title_font': {'size': 12, 'color': '#000000', 'weight': 'bold'}, 'tickfont': {'color': '#000000', 'size': 11, 'weight': 'bold'}
        },
        'margin': {'l': 75, 'r': 25, 't': 95, 'b': 60}
    })

with tab_monitor:
    st.markdown("<div class='section-header'>Поведенческий analysis массивов данных</div>", unsafe_allow_html=True)
    st.markdown("<div class='global-legend-box'><span style='color: #000000;'>ВЕРДИКТ СИСТЕМЫ КОМПЛАЕНСА:</span><div class='legend-item'><div class='legend-blue'></div><span>Легитимная сессия</span></div><div class='legend-item'><div class='legend-red'></div><span>Мошенническая операция (Фрод)</span></div></div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            fig_hist = px.histogram(filtered_df, x='сумма', color='статус', barmode='overlay', color_discrete_map=COLOR_MAP_PLOT, title="РАСПРЕДЕЛЕНИЕ ОПЕРАЦИЙ ПО ОБЪЕМАМ<br><span style='font-size:11px; font-weight:normal; color:#2d3748;'>Мониторинг плотности транзакционного потока банка.<br>Определение аномальных ценовых всплесков активности.</span>", labels={'сумма': 'Сумма транзакции (\$)', 'count': 'Количество транзакций', 'статус': 'Статус'})
            fig_hist.update_yaxes(title_text="Количество операций")
            apply_bank_theme(fig_hist)
            st.plotly_chart(fig_hist, use_container_width=True)
    with c2:
        with st.container(border=True):
            fig_scatter = px.scatter(filtered_df, x='риск_устройства', y='попытки_входа', color='статус', color_discrete_map=COLOR_MAP_PLOT, title="КОРРЕЛЯЦИЯ: АППАРАТНЫЙ РИСК / ПОПЫТКИ ВХОДА<br><span style='font-size:11px; font-weight:normal; color:#2d3748;'>Выявление векторов распределенных хакерских атак.<br>Кластеризация сессий брутфорса со скомпрометированных устройств.</span>", labels={'риск_устройства': 'Индекс риска устройства (0-1)', 'попытки_входа': 'Число попыток входа (ед.)', 'статус': 'Статус'})
            fig_scatter.update_xaxes(title_text="Индекс аппаратного риска устройства (0-1)")
            fig_scatter.update_yaxes(title_text="Число попыток входа в систему (ед.)")
            apply_bank_theme(fig_scatter)
            st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("<div class='section-header'>Инфраструктурный аудит расчетных шлюзов</div>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        with st.container(border=True):
            pay_analysis = filtered_df.copy()
            pay_analysis['способ_оплаты'] = pay_analysis['способ_оплаты'].map(PAY_MAP)
            pay_data = pay_analysis.groupby(['способ_оплаты', 'статус']).size().reset_index(name='количество')
            fig_pay = px.bar(pay_data, y='способ_оплаты', x='количество', color='статус', orientation='h', color_discrete_map=COLOR_MAP_PLOT, title="КОМПРОМЕТАЦИЯ ШЛЮЗОВ ПО МЕТОДАМ ОПЛАТЫ<br><span style='font-size:11px; font-weight:normal; color:#2d3748;'>Локализация уязвимостей в расчетной инфраструктуре.<br>Анализ каналов неконтролируемого вывода капитала.</span>", labels={'способ_оплаты': 'Канал эквайринга банка', 'количество': 'Всего операций (ед.)', 'статус': 'Статус'})
            apply_bank_theme(fig_pay)
            st.plotly_chart(fig_pay, use_container_width=True)
    with c4:
        with st.container(border=True):
            auth_analysis = filtered_df.copy()
            auth_analysis['подтверждение'] = auth_analysis['подтверждение'].map(AUTH_MAP)
            auth_data = auth_analysis.groupby(['подтверждение', 'статус']).size().reset_index(name='количество')
            fig_auth = px.bar(auth_data, x='подтверждение', y='количество', color='статус', color_discrete_map=COLOR_MAP_PLOT, title="УЯЗВИМОСТИ ДВУХФАКТОРНОЙ ВЕРИФИКАЦИИ<br><span style='font-size:11px; font-weight:normal; color:#2d3748;'>Оценка стойкости защитных протоколов подтверждения.<br>Мониторинг транзакций в обход авторизации сессии.</span>", labels={'подтверждение': 'Метод подтверждения сессии', 'количество': 'Операций (ед.)', 'статус': 'Статус'})
            apply_bank_theme(fig_auth)
            st.plotly_chart(fig_auth, use_container_width=True)

# --- ВКЛАДКА 2: РАСШИРЕННЫЙ РИСК-АНДЕРРАЙТИНГ И ИНСТРУМЕНТЫ АНАЛИТИКА ---
with tab_logs:
    st.markdown("<h3 style='color: #dc2626; margin-top:0; font-family: Georgia, serif;'>КРИТИЧЕСКИЕ ИНЦИДЕНТЫ (ЗОНА ДЛЯ РУЧНОЙ БЛОКИРОВКИ АНДЕРРАЙТИНГА)</h3>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'><b>Операционная инструкция:</b> Данный стрим содержит полный реестр аномальных сессий, упорядоченных по Индексу приоритета расследования (ИПР). Назначьте Категорию SLA комплаенс-контроля и проведите ручной скоринг.</div>", unsafe_allow_html=True)
    
    # 🛠️ РАСШИРЕННЫЙ БАНКОВСКИЙ ИНСТРУМЕНТАРИЙ: Создаем расчетные банковские метрики СБ
    threats_full = filtered_df[filtered_df['статус'] == 'Мошенническая'].copy()
    
    if not threats_full.empty:
        # 1. Индекс приоритета расследования (ИПР) = Сумма транзакции * Риск устройства * Попытки входа
        threats_full['индекс_приоритета'] = threats_full['сумма'] * threats_full['риск_устройства'] * threats_full['попытки_входа']
        
        # 2. Динамическое присвоение Категории SLA на основе скоринговых весов
        threats_full['категория_sla'] = np.where(threats_full['индекс_приоритета'] > 5000, 'Критический SLA (15 мин)', 'Стандартный SLA (60 мин)')
        
        # Сортируем строго по ИПР от самых тяжелых банковских преступлений вниз
        threats_full = threats_full.sort_values(by='индекс_приоритета', ascending=False)
        
        # Переводим технические поля логов Kaggle для отправки отчета в ЦБ РФ
        threats_full['способ_оплаты'] = threats_full['способ_оплаты'].map(PAY_MAP)
        threats_full['подтверждение'] = threats_full['подтверждение'].map(AUTH_MAP)
        
        # Выводим 100% записей без ограничений .head()
        st.dataframe(
            threats_full[['категория_sla', 'индекс_приоритета', 'риск_устройства', 'сумма', 'способ_оплаты', 'подтверждение']], 
            use_container_width=True,
            column_config={
                "категория_sla": st.column_config.SelectboxColumn("Категория SLA", width="medium"),
                "индекс_приоритета": st.column_config.ProgressColumn("Приоритет расследования (ИПР)", format="%.0f", min_value=0, max_value=int(threats_full['индекс_приоритета'].max() if not threats_full.empty else 10000)),
                "риск_устройства": st.column_config.NumberColumn("Риск гаджета (0-100)", format="%.2f"),
                "сумма": st.column_config.NumberColumn("Объем к похищению", format="$%.2f"),
                "способ_оплаты": "Шлюз вывода", 
                "подтверждение": "Защита"
            }
        )
    else:
        st.success("Критические инциденты комплаенс-контроля отсутствуют. Текущая сессия шлюза стабильна.")
    
    # --- ПОЛНЫЙ ПОТОКОВЫЙ СТРИМ СЕССИЙ БАНКА (ВСЯ БД БЕЗ ОБРЕЗКИ СТРОК) ---
    st.markdown("<br><h4 style='color: #111111; font-family: Georgia, serif;'>ПОЛНЫЙ ПОТОКОВЫЙ СТРИМ СЕССИЙ БЕЗОПАСНОСТИ БАНКА</h4>", unsafe_allow_html=True)
    display_df = filtered_df.sort_values(by='риск_устройства', ascending=False).copy()
    display_df['способ_оплаты'] = display_df['способ_оплаты'].map(PAY_MAP)
    display_df['подтверждение'] = display_df['подтверждение'].map(AUTH_MAP)
    
    # ИСПРАВЛЕНО: Полностью удален ограничитель .head(50), аналитик теперь контролирует 100% входящего трафика
    st.dataframe(
        display_df[['риск_устройства', 'сумма', 'способ_оплаты', 'тип_транзакции', 'подтверждение', 'статус']], 
        use_container_width=True, 
        column_config={
            "риск_устройства": st.column_config.ProgressColumn("Риск гаджета", format="%.2f", min_value=0, max_value=1), 
            "сумма": st.column_config.NumberColumn("Сумма", format="$%.2f"), 
            "способ_оплаты": "Канал оплаты", 
            "тип_транзакции": "Тип перевода", 
            "подтверждение": "Защита сессии", 
            "статус": "Вердикт"
        }
    )






















































