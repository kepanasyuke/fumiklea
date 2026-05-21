import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import numpy as np
import os
import hashlib
import io

try:
    from st_aggrid import AgGrid, GridOptionsBuilder
except ImportError:
    AgGrid = None
    GridOptionsBuilder = None

# --- 1. СТИЛИ ---
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
    .stSlider, .stSelectbox { width: 100% !important; max-width: 100% !important; }
    .simulation-box { background: #fef2f2; border: 1px solid #ef4444; border-left: 5px solid #dc2626; padding: 12px; margin-bottom: 15px; color: #000000; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- 2. СЛОВАРИ МЭППИНГА ---
PAY_MAP = {
    'Credit Card': 'Кредитная карта', 
    'Crypto': 'Криптовалюта', 
    'Bank Transfer': 'Банковский перевод', 
    'Net Banking': 'Электронный кошелек',
    'Не указан': 'Не указан'
}
PAY_REV = {v: k for k, v in PAY_MAP.items()}

AUTH_MAP = {
    'SMS OTP': 'SMS-код', 
    'Biometric': 'Биометрия (FaceID)', 
    'Password': 'Пароль', 
    'None': 'Без подтверждения',
    'Без защиты': 'Без подтверждения'
}
AUTH_REV = {v: k for k, v in AUTH_MAP.items()}

# --- 3. ЗАГРУЗКА ДАННЫХ ---
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

# --- 4. САЙДБАР ---
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
analytic_button_label = "Скрыть панель аналитики" if st.session_state.get('show_analytics_tool', False) else "Открыть панель аналитики"
if st.sidebar.button(analytic_button_label):
    st.session_state['show_analytics_tool'] = not st.session_state.get('show_analytics_tool', False)
    st.rerun()

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

if st.session_state.get('show_analytics_tool', False):
    with st.expander("Инструменты аналитики и работы с таблицей", expanded=True):
        tool_df = filtered_df.copy()
        st.markdown("**Текущий аналитический срез**")
        preset_name = st.text_input("Название пресета", value=st.session_state.get('preset_name', ""))
        st.session_state['preset_name'] = preset_name

        export_csv = tool_df.to_csv(index=False).encode('utf-8')
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.download_button("Экспорт текущей выборки в CSV", export_csv, file_name="analytics_table.csv", mime="text/csv")
        with col2:
            try:
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                    tool_df.to_excel(writer, index=False, sheet_name="analytics")
                st.download_button("Экспорт текущей выборки в Excel", excel_buffer.getvalue(), file_name="analytics_table.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except Exception:
                st.info("Установите openpyxl для экспорта в Excel: pip install openpyxl")
        with col3:
            if st.button("Сохранить пресет фильтрации"):
                st.session_state['saved_preset'] = {
                    'name': preset_name or "Пресет без имени",
                    'min_risk': min_risk,
                    'payment': selected_payment_ru
                }
                st.success("Пресет сохранён в сессии")

        if AgGrid is not None and GridOptionsBuilder is not None:
            gb = GridOptionsBuilder.from_dataframe(tool_df)
            gb.configure_default_column(filter=True, sortable=True, resizable=True)
            gb.configure_selection(selection_mode='single', use_checkbox=True)
            grid_options = gb.build()
            AgGrid(tool_df, gridOptions=grid_options, enable_enterprise_modules=False, fit_columns_on_grid_load=True)
        else:
            st.info("Для интерактивной таблицы установите streamlit-aggrid: pip install streamlit-aggrid")
            st.dataframe(tool_df)

# --- 5. МЕТРИКИ ---
total_tx = len(filtered_df)
fraud_cases = len(filtered_df[filtered_df['статус'] == 'Мошенническая'])
fraud_rate = (fraud_cases / total_tx * 100) if total_tx > 0 else 0
total_volume = filtered_df['сумма'].sum()
formatted_volume = f"${total_volume / 1_000_000:.2f}M" if total_volume >= 1_000_000 else f"${total_volume:,.0f}"

m1, m2, m3, m4 = st.columns(4)
with m1: st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_tx:,}</div><div class='metric-label'>Сессий в логах</div></div>", unsafe_allow_html=True)
with m2: st.markdown(f"<div class='metric-card'><div class='metric-value' style='color: #dc2626;'>{fraud_cases:,}</div><div class='metric-label'>Инцидентов выявлено</div></div>", unsafe_allow_html=True)
with m3: st.markdown(f"<div class='metric-card'><div class='metric-value' style='color: #d97706;'>{fraud_rate:.2f}%</div><div class='metric-label'>Доля фрод-операций</div></div>", unsafe_allow_html=True)
with m4: st.markdown(f"<div class='metric-card'><div class='metric-value' style='color: #10b981;'>{formatted_volume}</div><div class='metric-label'>Оборот под мониторингом</div></div>", unsafe_allow_html=True)

# --- 6. БИЗНЕС-МОДЕЛИРОВАНИЕ ---
with st.container(border=True):
    st.markdown("<h4 style='color: #111111; margin-top:0; font-size:1.05rem; font-family: Georgia, serif;'>Кастомизация SIEM-фильтрации (Бизнес-моделирование)</h4>", unsafe_allow_html=True)
    
    max_database_amount = float(df['сумма'].max()) if not df.empty else 5000.0
    default_initial_value = min(1200.0, max_database_amount)
    
    ru_payments_list = [PAY_MAP.get(p, p) for p in df['способ_оплаты'].unique()]
    ru_auth_list = [AUTH_MAP.get(a, a) for a in df['подтверждение'].unique()]
    
    r_col1, r_col2, r_col3 = st.columns(3)
    with r_col1: rule_amount = st.slider("Порог жесткой блокировки транзакции ($):", min_value=0.0, max_value=max_database_amount, value=default_initial_value, step=10.0)
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
    rc1.metric("Предотвращенный ущерб", f"${saved_cash:,.0f}", delta=f"Инцидентов: {tp}")
    rc2.metric("Потери от ложных тревог", f"${lost_cash:,.0f}", delta=f"Блок клиентов: {fp}", delta_color="inverse")
    rc3.metric("Точность правила", f"{precision:.1f}%")
    
    st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
    
    export_df = triggered.copy()
    export_df['способ_оплаты'] = export_df['способ_оплаты'].map(PAY_MAP)
    export_df['подтверждение'] = export_df['подтверждение'].map(AUTH_MAP)
    
    csv_buffer = export_df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Сформировать выгрузку отфильтрованных логов комплаенс-контроля (CSV)", data=csv_buffer, file_name="siem_incidents_report.csv", mime="text/csv", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 7. ВКЛАДКИ ---
tab_monitor, tab_logs = st.tabs(["Сводный аудит параметров", "Продвинутый дата-майнинг и выгрузка рапортов"])
COLOR_MAP_PLOT = {'Легитимная': '#1d4ed8', 'Мошенническая': '#dc2626'}

def apply_bank_theme(fig):
    fig.update_layout({
        'plot_bgcolor': '#ffffff', 'paper_bgcolor': '#ffffff', 'font_color': '#000000', 'height': 400, 'showlegend': False,
        'title_font': {'size': 13, 'color': '#000000', 'family': 'sans-serif', 'weight': 'bold'},
        'xaxis': {
            'gridcolor': '#e2e8f0', 'zeroline': False, 'linecolor': '#cbd5e1', 'linewidth': 1, 'mirror': True,
            'title_font': {'size': 12, 'color': '#000000', 'weight': 'bold'},
            'tickfont': {'color': '#000000', 'size': 11, 'weight': 'bold'}
        },
        'yaxis': {
            'gridcolor': '#e2e8f0', 'zeroline': False, 'linecolor': '#cbd5e1', 'linewidth': 1, 'mirror': True,
            'title_font': {'size': 12, 'color': '#000000', 'weight': 'bold'},
            'tickfont': {'color': '#000000', 'size': 11, 'weight': 'bold'}
        },
        'margin': {'l': 75, 'r': 25, 't': 110, 'b': 60}
    })

with tab_monitor:
    st.markdown("<div class='section-header'>Поведенческий анализ массивов данных</div><div class='section-description'><b>Назначение модуля:</b> Мониторинг распределения аномальных объемов транзакций и кластеризация векторов угроз.</div>", unsafe_allow_html=True)
    st.markdown("<div class='global-legend-box'><span style='color: #000000;'>ВЕРДИКТ СИСТЕМЫ КОМПЛАЕНСА:</span><div class='legend-item'><div class='legend-blue'></div><span>Легитимная сессия</span></div><div class='legend-item'><div class='legend-red'></div><span>Мошенническая операция (Фрод)</span></div></div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            fig_hist = px.histogram(
                filtered_df, x='сумма', color='статус', barmode='overlay', color_discrete_map=COLOR_MAP_PLOT, 
                title="РАСПРЕДЕЛЕНИЕ ОПЕРАЦИЙ ПО ОБЪЕМАМ<br><span style='font-size:11px; font-weight:normal; color:#2d3748;'>Мониторинг плотности транзакционного потока банка.</span>", 
                labels={'сумма': 'Сумма транзакции ($)', 'count': 'Количество транзакций', 'статус': 'Статус'}
            )
            fig_hist.update_yaxes(title_text="Количество операций")
            apply_bank_theme(fig_hist)
            st.plotly_chart(fig_hist, use_container_width=True)
    with c2:
        with st.container(border=True):
            fig_scatter = px.scatter(
                filtered_df, x='риск_устройства', y='попытки_входа', color='статус', color_discrete_map=COLOR_MAP_PLOT, 
                title="КОРРЕЛЯЦИЯ: АППАРАТНЫЙ РИСК / ПОПЫТКИ ВХОДА<br><span style='font-size:11px; font-weight:normal; color:#2d3748;'>Выявление векторов распределенных хакерских атак.</span>",
                labels={'риск_устройства': 'Индекс риска устройства (0-1)', 'попытки_входа': 'Число попыток входа (ед.)', 'статус': 'Статус'}
            )
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
            fig_pay = px.bar(
                pay_data, y='способ_оплаты', x='количество', color='статус', orientation='h', color_discrete_map=COLOR_MAP_PLOT, 
                title="КОМПРОМЕТАЦИЯ ШЛЮЗОВ ПО МЕТОДАМ ОПЛАТЫ<br><span style='font-size:11px; font-weight:normal; color:#2d3748;'>Локализация уязвимостей в расчетной инфраструктуре.</span>", 
                labels={'способ_оплаты': 'Канал эквайринга банка', 'количество': 'Всего операций (ед.)', 'статус': 'Статус'}
            )
            apply_bank_theme(fig_pay)
            st.plotly_chart(fig_pay, use_container_width=True)
    with c4:
        with st.container(border=True):
            auth_analysis = filtered_df.copy()
            auth_analysis['подтверждение'] = auth_analysis['подтверждение'].map(AUTH_MAP)
            auth_data = auth_analysis.groupby(['подтверждение', 'статус']).size().reset_index(name='количество')
            fig_auth = px.bar(
                auth_data, x='подтверждение', y='количество', color='статус', color_discrete_map=COLOR_MAP_PLOT, 
                title="УЯЗВИМОСТИ ДВУХФАКТОРНОЙ ВЕРИФИКАЦИИ<br><span style='font-size:11px; font-weight:normal; color:#2d3748;'>Оценка стойкости защитных протоколов подтверждения.</span>", 
                labels={'подтверждение': 'Метод подтверждения сессии', 'количество': 'Операций (ед.)', 'статус': 'Статус'}
            )
            apply_bank_theme(fig_auth)
            st.plotly_chart(fig_auth, use_container_width=True)

# --- ВКЛАДКА 2 ---
with tab_logs:
    st.markdown("<h3 style='color: #111111; margin-top:0; font-family: Georgia, serif;'>КОНСТРУКТОР СВОДНЫХ ТАБЛИЦ И МАТЕМАТИЧЕСКИЙ АНАЛИЗ ЛОГОВ</h3>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'><b>Инструментарий углубленного дата-майнинга:</b> Раздел содержит конструктор многокритериальных выборок, матрицы финансовой уязвимости по типам переводов и криминалистическую проверку сумм.</div>", unsafe_allow_html=True)
    
    df_workspace = filtered_df.copy()
    df_workspace['способ_оплаты'] = df_workspace['способ_оплаты'].map(PAY_MAP)
    df_workspace['подтверждение'] = df_workspace['подтверждение'].map(AUTH_MAP)
    
    # Конструктор выборок
    st.markdown("<h4 style='color: #000000; font-family: Georgia, serif;'>1. Интерактивный конструктор выборок комплаенс-контроля</h4>", unsafe_allow_html=True)
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        f_status = st.multiselect("Вердикт системы:", list(df_workspace['статус'].unique()), default=list(df_workspace['статус'].unique()))
    with f_col2:
        f_payment = st.multiselect("Канал оплаты:", list(df_workspace['способ_оплаты'].unique()), default=list(df_workspace['способ_оплаты'].unique()))
    with f_col3:
        f_auth = st.multiselect("Протокол защиты:", list(df_workspace['подтверждение'].unique()), default=list(df_workspace['подтверждение'].unique()))
        
    df_filtered_workspace = df_workspace[
        (df_workspace['статус'].isin(f_status)) & 
        (df_workspace['способ_оплаты'].isin(f_payment)) & 
        (df_workspace['подтверждение'].isin(f_auth))
    ]
    
    st.info(f"Конструктор скомпилировал выборку: найдено **{len(df_filtered_workspace):,}** транзакций.")

    # Матрица потерь по типам
    st.markdown("<br><h4 style='color: #000000; font-family: Georgia, serif;'>2. Матрица финансовых потерь по типам транзакций</h4>", unsafe_allow_html=True)
    if not df_filtered_workspace.empty:
        pivot_type = df_filtered_workspace.groupby('тип_транзакции').agg(
            Всего_Транзакций=('сумма', 'count'),
            Выявлено_Фрода=('статус', lambda x: (x == 'Мошенническая').sum()),
            Общий_Оборот=('сумма', 'sum'),
            Максимальный_Чек=('сумма', 'max'),
            Общий_Ущерб=('сумма', lambda x: x[df_filtered_workspace.loc[x.index, 'статус'] == 'Мошенническая'].sum())
        ).reset_index()
        
        pivot_type['Доля фрода по объему (%)'] = (pivot_type['Общий_Ущерб'] / pivot_type['Общий_Оборот'] * 100).fillna(0).round(2)
        
        st.dataframe(
            pivot_type, use_container_width=True,
            column_config={
                "тип_транзакции": "Категория перевода",
                "Всего_Транзакций": st.column_config.NumberColumn("Обработано (ед)", format="%d"),
                "Выявлено_Фрода": st.column_config.NumberColumn("Фрод-сессии (ед)", format="%d"),
                "Общий_Оборот": st.column_config.NumberColumn("Общий оборот", format="$%.2f"),
                "Максимальный_Чек": st.column_config.NumberColumn("Пиковый чек", format="$%.2f"),
                "Общий_Ущерб": st.column_config.NumberColumn("Прямой ущерб фрода", format="$%.2f"),
                "Доля фрода по объему (%)": st.column_config.ProgressColumn("Коэффициент уязвимости", format="%.2f%%", min_value=0.0, max_value=100.0)
            }
        )

    # Бакетный анализ
    st.markdown("<br><h4 style='color: #000000; font-family: Georgia, serif;'>3. Сводный бакетный анализ по уровням риска устройств</h4>", unsafe_allow_html=True)
    if not df_filtered_workspace.empty:
        bins = [-0.01, 0.35, 0.65, 1.01]
        labels = ['Низкий аппаратный риск (0.00-0.35)', 'Средний риск / VPN (0.36-0.65)', 'Критический риск / Эмуляторы (0.66-1.00)']
        df_filtered_workspace['Бакет риска'] = pd.cut(df_filtered_workspace['риск_устройства'], bins=bins, labels=labels)
        
        pivot_bucket = df_filtered_workspace.groupby('Бакет риска').agg(
            Количество_Сессий=('сумма', 'count'),
            Мошеннических_Операций=('статус', lambda x: (x == 'Мошенническая').sum()),
            Средняя_Сумма_Фрода=('сумма', lambda x: x[df_filtered_workspace.loc[x.index, 'статус'] == 'Мошенническая'].mean())
        ).reset_index().fillna(0)
        
        st.dataframe(
            pivot_bucket, use_container_width=True,
            column_config={
                "Бакет риска": "Категория уязвимости гаджета",
                "Количество_Сессий": st.column_config.NumberColumn("Всего подключений", format="%d"),
                "Мошеннических_Операций": st.column_config.NumberColumn("Выявлено инцидентов", format="%d"),
                "Средняя_Сумма_Фрода": st.column_config.NumberColumn("Средняя сумма хищения", format="$%.2f")
            }
        )

    # Кросс-матрица
    st.markdown("<br><h4 style='color: #000000; font-family: Georgia, serif;'>4. Сводная кросс-матрица распределения фрода (Канал эквайринга / Защита сессии)</h4>", unsafe_allow_html=True)
    crosstab_df = pd.crosstab(
        df_filtered_workspace['способ_оплаты'], 
        df_filtered_workspace['подтверждение'], 
        values=df_filtered_workspace['статус'].apply(lambda x: 1 if x == 'Мошенническая' else 0), 
        aggfunc='sum'
    ).fillna(0).astype(int)
    st.dataframe(crosstab_df, use_container_width=True)

    # Закон Бенфорда
    st.markdown("<br><h4 style='color: #000000; font-family: Georgia, serif;'>5. Криминалистический анализ сумм по закону Бенфорда</h4>", unsafe_allow_html=True)
    valid_amounts = df_filtered_workspace[df_filtered_workspace['сумма'] >= 1]['сумма']
    first_digits = valid_amounts.astype(str).str.lstrip('0. $').str.slice(0, 1)
    first_digits = pd.to_numeric(first_digits, errors='coerce')
    first_digits = first_digits[first_digits.between(1, 9, inclusive='both')]
    
    if not first_digits.empty:
        digit_counts = first_digits.value_counts(normalize=True).sort_index()
        benford_ideal = pd.Series([np.log10(1 + 1/d) for d in range(1, 10)], index=range(1, 10))
        benford_df = pd.DataFrame({
            'Первая цифра': range(1, 10),
            'Реальная частота в логах': [digit_counts.get(d, 0) for d in range(1, 10)],
            'Закон Бенфорда': benford_ideal.values
        })
        fig_benford = px.line(
            benford_df, x='Первая цифра', y=['Реальная частота в логах', 'Закон Бенфорда'],
            title="СРАВНЕНИЕ РАСПРЕДЕЛЕНИЯ ЦИФР С ЭТАЛОНОМ КРИМИНАЛИСТИКИ<br><span style='font-size:11px; font-weight:normal; color:#2d3748;'>Аномальные пики указывают на искусственную генерацию фиксированных сумм.</span>",
            labels={'Первая цифра': 'Первая значащая цифра транзакции', 'value': 'Доля распределения частоты логов', 'variable': 'Тип распределения'}
        )
        apply_bank_theme(fig_benford)
        fig_benford.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_benford, use_container_width=True)

    # --- ИСПРАВЛЕНИЕ: fraud_only определена здесь ---
    fraud_only = df_filtered_workspace[df_filtered_workspace['статус'] == 'Мошенническая']

    st.markdown("<br><br><hr style='border-color: #cbd5e1;'><br>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #000000; font-family: Georgia, serif;'>6. Инспекционный генератор комплексной отчетности СБ</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color: #475569; font-size: 0.9rem; margin-top:-5px;'>Выберите тип документа. Отчет мгновенно пересчитывается и обновляется при любом изменении фильтров или интерактивного конструктора.</p>", unsafe_allow_html=True)
    
    st.markdown("""
        <style>
        div[data-testid="stHorizontalBlock"] button { height: 48px !important; display: flex; align-items: center; justify-content: center; }
        </style>
    """, unsafe_allow_html=True)

    if 'active_report_type' not in st.session_state:
        st.session_state['active_report_type'] = "Рапорт СБ"

    rep_col1, rep_col2, rep_col3 = st.columns(3)
    with rep_col1:
        if st.button("Внутренний рапорт СБ", use_container_width=True): st.session_state['active_report_type'] = "Рапорт СБ"
    with rep_col2:
        if st.button("Сформировать официальный доклад для ЦБ РФ", use_container_width=True): st.session_state['active_report_type'] = "Доклад ЦБ"
    with rep_col3:
        if st.button("Сформировать отчет по форме 115-ФЗ", use_container_width=True): st.session_state['active_report_type'] = "Отчет 115"

    # Теперь используем fraud_only, который определён выше
    top_pay = fraud_only['способ_оплаты'].mode().iloc[0] if not fraud_only.empty and not fraud_only['способ_оплаты'].mode().empty else "Не определен"
    top_auth = fraud_only['подтверждение'].mode().iloc[0] if not fraud_only.empty and not fraud_only['подтверждение'].mode().empty else "Не определен"
    total_fraud_sum = fraud_only['сумма'].sum() if not fraud_only.empty else 0.0
    mean_fraud_sum = fraud_only['сумма'].mean() if not fraud_only.empty else 0.0
    total_cases = len(fraud_only)

    if st.session_state['active_report_type'] == "Рапорт СБ":
        report_text = f"""СТРОГО КОНФИДЕНЦИАЛЬНО // РАПОРТ СЛУЖБЫ ВНУТРЕННЕГО КОНТРОЛЯ БАНКА
----------------------------------------------------------------------
Идентификатор транзакционной сессии: SHA-256:{data_hash}
Общее число проверенных сессий логов: {len(df_filtered_workspace):,} ед.

МАТЕМАТИЧЕСКИЕ РЕЗУЛЬТАТЫ ЭКСПЕРТИЗЫ:
1. Ключевая точка финансовой компрометации шлюзов: {top_pay}
2. Основной уязвимый вектор авторизации пользователей: {top_auth}
3. Суммарный объем прямого зафиксированного ущерба: ${total_fraud_sum:,.2f}
4. Средний размер мошеннического списания (чек фрода): ${mean_fraud_sum:,.2f}

ДИРЕКТИВА ДЛЯ ДЕПАРТАМЕНТА РИСК-МЕНЕДЖМЕНТА:
Немедленно активировать принудительное биометрическое/SMS подтверждение для всех 
операций, проходящих через шлюз {top_pay}. Снизить лимит разового списания до $500
для гаджетов, чей индекс аппаратного риска в системе SIEM превышает показатель 0.65."""

    elif st.session_state['active_report_type'] == "Доклад ЦБ":
        report_text = f"""УВЕДОМЛЕНИЕ О КИБЕРИНЦИДЕНТАХ // В ДЕПАРТАМЕНТ ИНФОРМАЦИОННОЙ БЕЗОПАСНОСТИ ЦБ РФ
----------------------------------------------------------------------
Направляется в соответствии с Положением Банка России № 683-П
Контрольный хэш-ключ реестра инцидентов: {data_hash}
Объем отфильтрованной выборки: {len(df_filtered_workspace)} операций

АКТ ПРОВЕРКИ ТРАНЗАКЦИОННОЙ ЛЕНТЫ:
В ходе межоперационного аудита логов комплаенс-контроля была локализована серия распределенных 
аномальных транзакций. Мошеннические операции со скомпрометированных устройств составили {total_cases} инцидентов на общую сумму ${total_fraud_sum:,.2f}.

При анализе законов криминалистического распределения Бенфорда выявлены аномальные отклонения
первой значащей цифры в логах шлюза, что свидетельствует об искусственном дроблении сумм.

МЕРЫ РЕАГИРОВАНИЯ:
Банком инициирован пересмотр скоринговых весов SIEM-маршрутизации. Уязвимые сессии заблокированы, 
скомпрометированные цифровые отпечатки внесены в черный список стоп-листов."""

    elif st.session_state['active_report_type'] == "Отчет 115":
        report_text = f"""СПЕЦИАЛЬНОЕ СООБЩЕНИЕ В ФЕДЕРАЛЬНУЮ СЛУЖБУ ПО ФИНАНСОВОМУ МОНИТОРИНГУ (115-ФЗ)
----------------------------------------------------------------------
Критерий выявления: Обязательный контроль кодов подозрительности операций
Реестр верификации логов: SHA256-HASH:{data_hash}

СВЕДЕНИЯ О ПОДОЗРИТЕЛЬНОЙ ДЕЯТЕЛЬНОСТИ:
Системой автоматического дата-майнинга зафиксированы множественные попытки несанкционированного
вывода капитала через нерегулируемые платежные инструменты.
- Основной используемый канал вывода: {top_pay}
- Объем операций, подлежащих обязательному комплаенс-контролю: ${total_fraud_sum:,.2f}
- Оценка вовлеченности аппаратного фрода: {total_cases} подтвержденных кибератак

ЗАКЛЮЧЕНИЕ ОТВЕТСТВЕННОГО ЛИЦА КОМПЛАЕНС-КОНТРОЛЯ БАНКА:
Характер транзакций (систематический брутфорс авторизации, обход двухфакторных протоколов защиты, 
высокий аппаратный риск подключений) имеет признаки легализации доходов. 
Данные переданы в уполномоченный орган для проведения финансовых расследований."""

    st.text_area(f"Печатная форма ({st.session_state['active_report_type']}) пересчитана автоматически:", report_text, height=250)
    
    st.download_button(
        label="Экспортировать сформированный текстовый отчет для печати (TXT)",
        data=report_text, file_name=f"antifraud_{st.session_state['active_report_type']}_report.txt", mime="text/plain", use_container_width=True
    )

    # Сквозной реестр
    st.markdown("<br><h4 style='color: #111111; font-family: Georgia, serif;'>7. Сквозной детальный реестр отфильтрованных транзакций из базы данных</h4>", unsafe_allow_html=True)
    st.dataframe(
        df_filtered_workspace[['риск_устройства', 'сумма', 'способ_оплаты', 'тип_транзакции', 'подтверждение', 'статус']], 
        use_container_width=True, 
        column_config={
            "риск_устройства": st.column_config.ProgressColumn("Риск гаджета", format="%.2f", min_value=0, max_value=1), 
            "сумма": st.column_config.NumberColumn("Сумма", format="$%.2f"), 
            "способ_оплаты": "Канал оплаты", "тип_транзакции": "Тип перевода", "подтверждение": "Защита сессии", "статус": "Вердикт"
        }
    )






























































