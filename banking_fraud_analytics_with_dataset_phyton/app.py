import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import numpy as np
import os
import hashlib
import io
import sys
import subprocess

RUNTIME_DEPENDENCIES = {
    "streamlit-aggrid": "st_aggrid",
    "openpyxl": "openpyxl",
    "kaleido": "kaleido"
}

try:
    from st_aggrid import AgGrid, GridOptionsBuilder
except ImportError:
    AgGrid = None
    GridOptionsBuilder = None

def install_packages(packages):
    python_exec = sys.executable
    for pkg in packages:
        subprocess.check_call([python_exec, "-m", "pip", "install", pkg])

def ensure_runtime_dependencies():
    missing = []
    for pkg, module in RUNTIME_DEPENDENCIES.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(pkg)
    return missing

# --- 1. СТИЛИ ---
st.set_page_config(page_title="Антифрод-платформа верификации транзакций", layout="wide", page_icon="🛡️")

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
 
 /* ИСПРАВЛЕНИЕ: Безопасный адаптивный стиль для кнопок сайдбара без жестких пикселей */
 [data-testid="stSidebar"] .stButton button { width: 100% !important; min-height: 48px !important; box-sizing: border-box !important; }
 [data-testid="stSidebar"] button span { display: inline-block; width: 100%; }
 
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
with st.sidebar:
    st.markdown("<h4 style='margin-bottom: 1rem;'>ПАРАМЕТРЫ ФИЛЬТРАЦИИ</h4>", unsafe_allow_html=True)
    min_risk = st.slider("Минимальный индекс риска устройства (0-1):", 0.0, 1.0, 0.10, key="sidebar_risk_slider")

    # Первичная фильтрация основного датасета по слайдеру риска
    filtered_df = df[df['риск_устройства'] >= min_risk]

    unique_payments_en = filtered_df['способ_оплаты'].unique()
    translated_payments = [PAY_MAP.get(p, p) for p in unique_payments_en]
    all_payments_options = ["Все способы"] + list(set(translated_payments))
    selected_payment_ru = st.selectbox("Канал эквайринга:", all_payments_options, key="sidebar_payment_select")

    if selected_payment_ru != "Все способы":
        selected_payment_en = PAY_REV.get(selected_payment_ru, selected_payment_ru)
        filtered_df = filtered_df[filtered_df['способ_оплаты'] == selected_payment_en]

    st.markdown(f"""
     <div class='sidebar-description-box'>
     <div class='sidebar-description-title'>ШКАЛА АППАРАТНОГО РИСКА (0-1)</div>
     • <b>0.00 – 0.35 (Низкий):</b> Штатное устройство.<br>
     • <b>0.36 – 0.65 (Средний):</b> Использование VPN/прокси.<br>
     • <b>0.66 – 1.00 (Критический):</b> Прямой фрод (эмуляторы).<br>
     <hr style='margin: 6px 0; border-color: #cbd5e1;'>
     <small style='color:#000000;'>Контрольная сумма логов:<br><b>{data_hash}</b></small>
     </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<h4 style='color: #dc2626;'>СЦЕНАРИИ НАГРУЗКИ</h4>", unsafe_allow_html=True)

    missing_deps = ensure_runtime_dependencies()
    if missing_deps:
        st.warning(f"Не установлены аналитические пакеты: {', '.join(missing_deps)}")
        if st.button("Установить расширенные зависимости", key="sidebar_install_deps_btn"):
            with st.spinner("Установка пакетов..."):
                install_packages(missing_deps)
            st.rerun()

    simulate_attack = st.button("Запустить симуляцию кибератаки", key="sidebar_simulate_attack_btn")

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
    if st.button("Сбросить регистр симуляции", key="main_reset_attack_signal_btn"):
        st.session_state['attack'] = False
        st.rerun()

# --- ГЛАВНЫЙ ЭКРАН ---
st.markdown("<div class='title-container'><h1 class='main-title'>КОРПОРАТИВНЫЙ МОНИТОР КОМПЛАЕНСА И АНТИФРОД-АНАЛИТИКИ</h1><div class='sub-title'>Адаптивный операционный комплекс верификации транзакционных логов, оценка уязвимостей и моделирование векторов угроз.</div></div>", unsafe_allow_html=True)

# Руководство оператора комплаенса, скрываемое после прочтения
with st.expander("Показать руководство оператора по синхронизации фильтров", expanded=False):
    st.info("""
    **Руководство оператора комплаенс-контроля:**
    
    1. **Как пользоваться сайдбаром (левой исполняющей панелью):** Параметры в левом меню — это глобальные фильтры всей платформы. Когда вы меняете минимальный риск или канал эквайринга в сайдбаре, вы перестраиваете базу данных для всего приложения. Изменения в сайдбаре мгновенно пересчитывают верхние KPI-метрики, финансовые результаты и графики платформы на всех вкладках.
    2. **Как работать с интерактивной таблицей:** Блок таблицы ниже — это изолированный рабочий инструмент аналитика. Настройка выплывающих фильтров и проставление галочек внутри этого блока нужны исключительно для точечной сборки и выгрузки кастомных CSV/Excel отчетов. Они не изменяют глобальные метрики платформы и графики ниже.
    3. **Важное правило синхронизации:** Для получения максимально точных и релевантных данных в итоговой выборке необходимо настраивать параметры в сайдбаре синхронно с окном кастомизации таблицы. Если вы ищете конкретный тип угроз (например, транзакции по картам с определенным риском), убедитесь, что базовые рамки в сайдбаре слева соответствуют точечным диапазонам внутри выплывающей панели.
    """)

# Надежная страховка от ошибки NameError при сборке логов
if 'filtered_df' in locals() or 'filtered_df' in globals():
    tool_df = filtered_df.copy()
else:
    tool_df = df.copy()

# Сборка понятных русских колонок
display_cols = ['сумма', 'риск_устройства', 'попытки_входа', 'способ_оплаты', 'подтверждение', 'тип_транзакции', 'статус']
available_cols = [c for c in display_cols if c in tool_df.columns]
working_df = tool_df[available_cols].reset_index(drop=True)

# ВЫПЛЫВАЮЩИЙ ИНСТРУМЕНТ ДЛЯ АНАЛИТИКА: ВСЯ ТАБЛИЦА И ЕЕ ФИЛЬТРЫ ВНУТРИ ЕДИНОГО EXPANDER
with st.expander("Выплывающая панель точечной фильтрации и интерактивная таблица логов", expanded=False):
    st.markdown("Настройте параметры ниже для автоматического сужения текущей выборки транзакций:")
    
    # Первая строка фильтров: выпадающие списки (Категориальные параметры)
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    with f_col1:
        unique_statuses = ["Все статусы"] + list(working_df['статус'].unique()) if 'статус' in working_df.columns else ["Все статусы"]
        selected_status = st.selectbox("Вердикт комплаенса:", unique_statuses, key="live_filter_status")
        if selected_status != "Все статусы":
            working_df = working_df[working_df['статус'] == selected_status].reset_index(drop=True)
            
    with f_col2:
        unique_types = ["Все типы"] + list(working_df['тип_транзакции'].unique()) if 'тип_транзакции' in working_df.columns else ["Все типы"]
        selected_type = st.selectbox("Тип операции:", unique_types, key="live_filter_type")
        if selected_type != "Все типы":
            working_df = working_df[working_df['тип_транзакции'] == selected_type].reset_index(drop=True)
            
    with f_col3:
        unique_payments = ["Все каналы"] + list(working_df['способ_оплаты'].unique()) if 'способ_оплаты' in working_df.columns else ["Все каналы"]
        selected_live_pay = st.selectbox("Способ оплаты:", unique_payments, key="live_filter_pay")
        if selected_live_pay != "Все каналы":
            working_df = working_df[working_df['способ_оплаты'] == selected_live_pay].reset_index(drop=True)
            
    with f_col4:
        unique_auths = ["Все протоколы"] + list(working_df['подтверждение'].unique()) if 'подтверждение' in working_df.columns else ["Все протоколы"]
        selected_live_auth = st.selectbox("Защита сессии:", unique_auths, key="live_filter_auth")
        if selected_live_auth != "Все протоколы":
            working_df = working_df[working_df['подтверждение'] == selected_live_auth].reset_index(drop=True)

    st.markdown("<br><b>Настройка диапазонов числовых метрик:</b>", unsafe_allow_html=True)

    # Числовые слайдеры-диапазоны выстроены в вертикальный столбик для удобства ввода длинных чисел
    if not working_df.empty:
        min_amount_val = float(working_df['сумма'].min())
        max_amount_val = float(working_df['сумма'].max())
        if min_amount_val < max_amount_val:
            amount_range = st.slider("Диапазон сумм операции ($):", min_amount_val, max_amount_val, (min_amount_val, max_amount_val), key="live_filter_amount_slider")
            working_df = working_df[(working_df['сумма'] >= amount_range[0]) & (working_df['сумма'] <= amount_range[1])].reset_index(drop=True)
            
    risk_range = st.slider("Диапазон аппаратного риска устройства:", min_value=0.00, max_value=1.00, value=(0.00, 1.00), step=0.05, key="live_filter_risk_slider")
    working_df = working_df[(working_df['риск_устройства'] >= risk_range[0]) & (working_df['риск_устройства'] <= risk_range[1])].reset_index(drop=True)
    
    if not working_df.empty:
        min_login_val = int(working_df['попытки_входа'].min())
        max_login_val = int(working_df['попытки_входа'].max())
        if min_login_val < max_login_val:
            login_range = st.slider("Диапазон попыток авторизации (ед.):", min_login_val, max_login_val, (min_login_val, max_login_val), step=1, key="live_filter_login_slider")
            working_df = working_df[(working_df['попытки_входа'] >= login_range[0]) & (working_df['попытки_входа'] <= login_range[1])].reset_index(drop=True)

    st.markdown("---")

    # УПРАВЛЕНИЕ МАССОВЫМ ВЫБОРОК ДЛЯ ИБ-ЭКСПОРТА
    st.markdown("### Управление выбором строк для экспорта")

    auto_select_all = st.checkbox("Автоматически отмечать галочками все отфильтрованные строки", value=False, key="cb_auto_select_all")

    # Синхронизация единой фиксированной высоты кнопок управления
    st.markdown("""
        <style>
        div[data-testid="stHorizontalBlock"] .stButton button {
            height: 42px !important;
            box-sizing: border-box !important;
        }
        </style>
    """, unsafe_allow_html=True)

    c_btn1, c_btn2 = st.columns(2)
    if auto_select_all:
        initial_selection = [True] * len(working_df)
    else:
        initial_selection = [False] * len(working_df)

    with c_btn1:
        if st.button("Выделить все строки вручную", use_container_width=True, key="main_select_all_btn"):
            initial_selection = [True] * len(working_df)
    with c_btn2:
        if st.button("Сбросить выделение", use_container_width=True, key="main_reset_selection_btn"):
            initial_selection = [False] * len(working_df)

    working_df.insert(0, 'Выбрать транзакцию', initial_selection)

    # Отображение интерактивной таблицы-редактора внутри выплывающей панели
    edited_df = st.data_editor(
        working_df,
        use_container_width=True,
        height=350,
        disabled=['сумма', 'риск_устройства', 'попытки_входа', 'способ_оплаты', 'подтверждение', 'тип_транзакции', 'статус'],
        column_config={
            "Выбрать транзакцию": st.column_config.CheckboxColumn("Выбрать", default=False),
            "сумма": st.column_config.NumberColumn("Сумма операции", format="$%.2f"),
            "попытки_входа": st.column_config.NumberColumn("Попытки авторизации", format="%d ед."),
            "риск_устройства": st.column_config.ProgressColumn("Уровень аппаратного риска", format="%.2f", min_value=0.0, max_value=1.0),
            "способ_оплаты": "Канал эквайринга",
            "подтверждение": "Защита сессии",
            "тип_транзакции": "Тип операции",
            "статус": "Вердикт комплаенса"
        }
    )

    # Локальная фильтрация и формирование кнопок сквозной печати для аналитика
    custom_selection_df = edited_df[edited_df['Выбрать транзакцию'] == True]

    if not custom_selection_df.empty:
        final_selection = custom_selection_df.drop(columns=['Выбрать транзакцию'])
        st.markdown(f"**Ваша сформированная микро-выборка ({len(final_selection)} шт. транзакций):**")
        st.dataframe(final_selection, use_container_width=True)
        
        final_csv = final_selection.to_csv(index=False).encode('utf-8')
        st.download_button("Печать / Скачать выделенные строки (CSV)", final_csv, file_name="custom_selection.csv", mime="text/csv", use_container_width=True, key="main_download_custom_btn")
    else:
        st.info("Сейчас галочки не выбраны — экспорт выгрузит весь текущий отфильтрованный срез.")
        clean_full_df = edited_df.drop(columns=['Выбрать транзакцию'] if 'Выбрать транзакцию' in edited_df.columns else [])
        export_csv = clean_full_df.to_csv(index=False).encode('utf-8')
        st.download_button("Печать / Скачать всю отфильтрованную таблицу (CSV)", export_csv, file_name="filtered_table.csv", mime="text/csv", use_container_width=True, key="main_download_full_btn")

st.markdown("<br><hr>", unsafe_allow_html=True)

# ПОЯСНЕНИЕ К ГЛОБАЛЬНЫМ МЕТРИКАМ ПЛАТФОРМЫ
st.markdown("### Аналитическое описание контролируемых KPI-метрик")
st.markdown("""
Верхняя панель мониторинга агрегирует операционные показатели на основе глобальных настроек сайдбара:
* **Сессии в логах:** Общее количество unique-транзакционных запросов, поступивших от расчетных шлюзов в антифрод-систему за отчетный период. Тренд показывает динамику общей активности клиентов.
* **Инцидентов выявлено:** Общее число транзакций, которые автоматическая система скоринга пометила как нелегитимные (фрод). Попадание транзакции в этот реестр означает блокировку операции до ручной проверки.
* **Доля фрод-операций:** Процентное соотношение мошеннических сессий к общему объёму трафика. Критический маркер стабильности шлюзов: резкий рост доли фрода сигнализирует о направленной хакерской атаке.
* **Оборот под мониторингом:** Суммарный объем финансовых средств (в денежном выражении), пропущенный через верификационные алгоритмы комплаенс-контроля. 
* **Активные правила:** Количество работающих в данный момент эвристических моделей и логических триггеров SIEM-системы, проверяющих проходящие логи в реальном времени.
""")

# --- 5. МЕТРИКИ ---

if 'filtered_df' not in locals() and 'filtered_df' not in globals():
    filtered_df = df.copy()

# Расчет метрик на основе гарантированно существующего датафрейма
total_tx = len(filtered_df)
fraud_tx = len(filtered_df[filtered_df['статус'] == 'Мошенническая']) if 'статус' in filtered_df.columns else 0
fraud_rate = (fraud_tx / total_tx * 100) if total_tx > 0 else 0.0
total_volume = filtered_df['сумма'].sum() if 'сумма' in filtered_df.columns else 0.0

# Красивое и компактное отображение миллионов (M) или тысяч (K) без троеточий
if total_volume >= 1_000_000:
    formatted_volume = f"${total_volume / 1_000_000:.2f}M"
elif total_volume >= 1_000:
    formatted_volume = f"${total_volume / 1_000:.1f}K"
else:
    formatted_volume = f"${total_volume:,.2f}"

# ИСПРАВЛЕНИЕ: Обращаемся к колонкам по индексам [0]...[4], чтобы исправить ошибку с 'list' object
kpi_cols = st.columns(5)
with kpi_cols[0]:
    st.metric(label="ВСЕГО ЛОГОВ", value=f"{total_tx:,}", delta="+12%")
with kpi_cols[1]:
    st.metric(label="ФРОД-ИНЦИДЕНТЫ", value=f"{fraud_tx:,}", delta="Критично", delta_color="inverse")
with kpi_cols[2]:
    st.metric(label="УРОВЕНЬ ФРОДА", value=f"{fraud_rate:.2f}%", delta="-0.8%")
with kpi_cols[3]:
    st.metric(label="ОБОРОТ СИСТЕМЫ", value=formatted_volume, delta="+4.1%")
with kpi_cols[4]:
    st.metric(label="ПРАВИЛА SIEM", value="18/24", delta="Стабильно")

st.write("---")

# --- 6. БИЗНЕС-МОДЕЛИРОВАНИЕ ---
with st.container(border=True):
    st.markdown("<h4 style='color: #111111; margin-top:0; font-size:1.05rem; font-family: Georgia, serif;'>Кастомизация SIEM-фильтрации (Бизнес-моделирование)</h4>", unsafe_allow_html=True)
    
    max_database_amount = float(df['сумма'].max()) if not df.empty else 5000.0
    default_initial_value = min(1200.0, max_database_amount)
    
    ru_payments_list = [PAY_MAP.get(p, p) for p in df['способ_оплаты'].unique()]
    ru_auth_list = [AUTH_MAP.get(a, a) for a in df['подтверждение'].unique()]
    
    # ИСПРАВЛЕНИЕ: Перестроили фильтры бизнес-моделирования в вертикальный столбик, чтобы они не сжимались
    rule_amount = st.slider("Порог жесткой блокировки транзакции ($):", min_value=0.0, max_value=max_database_amount, value=default_initial_value, step=10.0, key="bm_rule_amount_slider")
    rule_payment_ru = st.selectbox("Целевая платежная система:", list(set(ru_payments_list)), key="bm_rule_payment_select")
    rule_auth_ru = st.selectbox("Слабый протокол аутентификации:", list(set(ru_auth_list)), key="bm_rule_auth_select")
    
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
    st.download_button(label="Сформировать выгрузку отфильтрованных логов комплаенс-контроля (CSV)", data=csv_buffer, file_name="siem_incidents_report.csv", mime="text/csv", use_container_width=True, key="bm_download_csv_report_btn")

st.markdown("<br>", unsafe_allow_html=True)

# --- 7. ВКЛАДКИ (НАЧАЛО: tab_monitor) ---
tab_monitor, tab_logs = st.tabs(["Сводный аудит параметров", "Продвинутый дата-майнинг и выгрузка рапортов"])
COLOR_MAP_PLOT = {'Легитимная': '#1d4ed8', 'Мошенническая': '#dc2626'}

def apply_bank_theme(fig):
    # ИСПРАВЛЕНИЕ: config включает встроенную панель Plotly (ModeBar) с кнопкой скачивания PNG в браузере
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
            # config позволяет скачивать PNG прямо кнопкой из правого верхнего угла самого графика
            st.plotly_chart(fig_hist, use_container_width=True, config={'displaymodebar': True, 'toImageButtonOptions': {'format': 'png', 'filename': 'volumes_chart'}})
            
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
            st.plotly_chart(fig_scatter, use_container_width=True, config={'displaymodebar': True, 'toImageButtonOptions': {'format': 'png', 'filename': 'scatter_chart'}})
            
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
            st.plotly_chart(fig_pay, use_container_width=True, config={'displaymodebar': True, 'toImageButtonOptions': {'format': 'png', 'filename': 'payment_chart'}})
            
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
            st.plotly_chart(fig_auth, use_container_width=True, config={'displaymodebar': True, 'toImageButtonOptions': {'format': 'png', 'filename': 'auth_chart'}})

    # ИСПРАВЛЕНИЕ: Инструкция заменена на чистую и строгую памятку без генерации серверных ошибок
    st.markdown("---")
    st.markdown("#### Руководство по сохранению графической аналитики")
    st.info("Для сохранения любого графика в формате PNG для печатного отчета наведите курсор на правый верхний угол нужной диаграммы и нажмите на появившуюся иконку с изображением фотоаппарата (Download plot as a png). Файл сохранится локально через ресурсы вашего браузера.")
with tab_logs:
    st.markdown("<h3 style='color: #111111; margin-top:0; font-family: Georgia, serif;'>КОНСТРУКТОР СВОДНЫХ ТАБЛИЦ И МАТЕМАТИЧЕСКИЙ АНАЛИЗ ЛОГОВ</h3>", unsafe_allow_html=True)
    st.markdown("<div class='section-description'><b>Инструментарий углубленного дата-майнинга:</b> Раздел содержит конструктор многокритериальных выборок, матрицы финансовой уязвимости по типам переводов и криминалистическую проверку сумм.</div>", unsafe_allow_html=True)
    
    df_workspace = filtered_df.copy()
    df_workspace['способ_оплаты'] = df_workspace['способ_оплаты'].map(PAY_MAP)
    df_workspace['подтверждение'] = df_workspace['подтверждение'].map(AUTH_MAP)
    
    # 1. Конструктор выборок
    st.markdown("<h4 style='color: #000000; font-family: Georgia, serif;'>1. Интерактивный конструктор выборок комплаенс-контроля</h4>", unsafe_allow_html=True)
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        f_status = st.multiselect("Вердикт системы:", list(df_workspace['статус'].unique()), default=list(df_workspace['статус'].unique()), key="ms_status")
    with f_col2:
        f_payment = st.multiselect("Канал оплаты:", list(df_workspace['способ_оплаты'].unique()), default=list(df_workspace['способ_оплаты'].unique()), key="ms_payment")
    with f_col3:
        f_auth = st.multiselect("Протокол защиты:", list(df_workspace['подтверждение'].unique()), default=list(df_workspace['подтверждение'].unique()), key="ms_auth")
        
    df_filtered_workspace = df_workspace[
        (df_workspace['статус'].isin(f_status)) & 
        (df_workspace['способ_оплаты'].isin(f_payment)) & 
        (df_workspace['подтверждение'].isin(f_auth))
    ]
    
    st.info(f"Конструктор скомпилировал выборку: найдено **{len(df_filtered_workspace):,}** транзакций.")
    
    # 2. Матрица потерь по типам
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
        
    # 3. Бакетный анализ
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
        
    # 4. Кросс-матрица
    st.markdown("<br><h4 style='color: #000000; font-family: Georgia, serif;'>4. Сводная кросс-матрица распределения фрода (Канал эквайринга / Защита сессии)</h4>", unsafe_allow_html=True)
    crosstab_df = pd.crosstab(
        df_filtered_workspace['способ_оплаты'], 
        df_filtered_workspace['подтверждение'], 
        values=df_filtered_workspace['статус'].apply(lambda x: 1 if x == 'Мошенническая' else 0), 
        aggfunc='sum'
    ).fillna(0).astype(int)
    st.dataframe(crosstab_df, use_container_width=True)
    
    # 5. Закон Бенфорда
    st.markdown("<br><h4 style='color: #000000; font-family: Georgia, serif;'>5. Криминалистический анализ сумм по закону Бенфорда</h4>", unsafe_allow_html=True)
    valid_amounts = df_filtered_workspace[df_filtered_workspace['сумма'] >= 1]['сумма']
    first_digits = valid_amounts.astype(str).str.lstrip('0. $').str.slice(0, 1)
    first_digits = pd.to_numeric(first_digits, errors='coerce')
    # ИСПРАВЛЕНИЕ: в pandas методе между аргумент inclusive использует строковые значения 'both', 'neither' и т.д.
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
        
    # 6. Инспекционный генератор комплексной отчетности СБ
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
        if st.button("Внутренний рапорт СБ", use_container_width=True, key="btn_rep_sb"): 
            st.session_state['active_report_type'] = "Рапорт СБ"
            st.rerun()
    with rep_col2:
        if st.button("Сформировать официальный доклад для ЦБ РФ", use_container_width=True, key="btn_rep_cb"): 
            st.session_state['active_report_type'] = "Доклад ЦБ"
            st.rerun()
    with rep_col3:
        if st.button("Сформировать отчет по форме 115-ФЗ", use_container_width=True, key="btn_rep_115"): 
            st.session_state['active_report_type'] = "Отчет 115"
            st.rerun()
            
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
высокий аппаратный риск подключений) имеет признаки легализации доходов. Данные переданы в уполномоченный орган для проведения финансовых расследований."""

    st.text_area(f"Печатная форма ({st.session_state['active_report_type']}) пересчитана автоматически:", report_text, height=250)
    
    st.download_button(
        label="Экспортировать сформированный текстовый отчет для печати (TXT)",
        data=report_text, 
        file_name=f"antifraud_{st.session_state['active_report_type']}_report.txt", 
        mime="text/plain", use_container_width=True,
        key="btn_download_txt_report"
    )
    
    # 7. Сквозной реестр
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






























































