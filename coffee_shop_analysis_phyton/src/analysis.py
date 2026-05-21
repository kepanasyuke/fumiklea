import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import matplotlib.font_manager as fm
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def setup_russian_font(font_path=None):
    """Настраивает русский шрифт для matplotlib с обработкой ошибок."""
    try:
        if font_path and Path(font_path).exists():
            fm.fontManager.addfont(str(font_path))
            plt.rcParams['font.family'] = 'DejaVu Sans'
            logger.info(f"Русский шрифт загружен из {font_path}")
            return True

        # Пробуем системные шрифты с кириллицей
        available_fonts = [f.name for f in fm.fontManager.ttflist
                           if 'DejaVu' in f.name or 'Arial' in f.name]
        if available_fonts:
            plt.rcParams['font.family'] = available_fonts[0]
            logger.info(f"Используется системный шрифт: {available_fonts[0]}")
            return True

        # Поддержка кириллицы через sans-serif
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Liberation Sans']
        plt.rcParams['axes.unicode_minus'] = False
        logger.warning("Русский шрифт явно не найден, используем стандартные настройки")
        return False
    except Exception as e:
        logger.warning(f"Ошибка настройки шрифта: {e}")
        return False


def load_data_from_csv(csv_path: str) -> pd.DataFrame:
    """Загружает данные из CSV файла. Ожидает колонки: date, hour, category, revenue."""
    try:
        df = pd.read_csv(csv_path)
        required_columns = ['date', 'hour', 'category', 'revenue']
        if not all(col in df.columns for col in required_columns):
            logger.error(f"CSV должен содержать колонки: {required_columns}")
            return None
        
        df['date'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date'].dt.day_name()
        df['weekday'] = df['date'].dt.weekday
        logger.info(f"Загружено {len(df)} записей из {csv_path}")
        return df
    except Exception as e:
        logger.error(f"Ошибка при загрузке CSV: {e}")
        return None


def generate_data(n_transactions=10000):
    """Генерирует синтетический датасет с продажами."""
    logger.info(f"Генерация {n_transactions} транзакций...")
    np.random.seed(42)

    start_date = datetime(2024, 6, 1)
    end_date = datetime(2024, 8, 31)
    dates = pd.date_range(start_date, end_date).to_list()

    probs_days = [0.18 if d.weekday() < 5 else 0.14 for d in dates]
    probs_days = np.array(probs_days) / sum(probs_days)
    chosen_dates = np.random.choice(dates, size=n_transactions, p=probs_days)

    hours = []
    hour_weights = [0.5,0.5,0.5,0.5,1,2,4,6,7,9,8,5,6,7,5,3,4,3,2,1,1,0.5,0.5,0.5]
    hour_weights = np.array(hour_weights) / sum(hour_weights)
    for _ in range(n_transactions):
        hours.append(np.random.choice(range(24), p=hour_weights))

    categories = {
        'Кофе': ['Эспрессо', 'Американо', 'Капучино', 'Латте', 'Раф'],
        'Чай': ['Чёрный чай', 'Зелёный чай', 'Матча латте', 'Травяной'],
        'Выпечка': ['Круассан', 'Маффин', 'Синнабон', 'Печенье'],
        'Сэндвичи': ['Сэндвич с курицей', 'Сэндвич с лососем', 'Веганский ролл']
    }
    items, prices, cats = [], [], []
    for _ in range(n_transactions):
        cat = np.random.choice(list(categories.keys()), p=[0.45, 0.15, 0.25, 0.15])
        item = np.random.choice(categories[cat])
        cats.append(cat)
        items.append(item)
        if cat == 'Кофе':
            prices.append(np.random.choice([150, 180, 220, 250, 280]))
        elif cat == 'Чай':
            prices.append(np.random.choice([130, 150, 200, 170]))
        elif cat == 'Выпечка':
            prices.append(np.random.choice([120, 140, 180, 90]))
        else:
            prices.append(np.random.choice([250, 290, 270]))

    quantity = np.random.choice([1,2,3], size=n_transactions, p=[0.8, 0.15, 0.05])
    revenue = np.array(prices) * quantity
    payment = np.random.choice(['Наличные', 'Карта', 'QR-код'], size=n_transactions, p=[0.3, 0.6, 0.1])

    df = pd.DataFrame({
        'date': chosen_dates,
        'hour': hours,
        'category': cats,
        'item': items,
        'price': prices,
        'quantity': quantity,
        'revenue': revenue,
        'payment_method': payment
    })
    df['day_of_week'] = df['date'].dt.day_name()
    df['weekday'] = df['date'].dt.weekday
    return df


def analyze_and_get_figures(df, font_path=None):
    """Анализирует данные, строит графики и возвращает метрики."""
    logger.info("Анализ данных и построение графиков...")
    sns.set_style("whitegrid")
    
    # УВЕЛИЧИВАЕМ размеры графиков для лучшей читаемости
    plt.rcParams['figure.figsize'] = (16, 8)
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.labelsize'] = 13
    plt.rcParams['axes.titlesize'] = 15
    plt.rcParams['xtick.labelsize'] = 11
    plt.rcParams['ytick.labelsize'] = 11
    plt.rcParams['legend.fontsize'] = 11

    # Настройка русского шрифта
    setup_russian_font(font_path)

    figures = {}
    try:
        # 1. Выручка по часам (УЛУЧШЕННО)
        hourly_revenue = df.groupby('hour')['revenue'].sum().reset_index()
        fig1, ax1 = plt.subplots(figsize=(16, 7))
        bars = ax1.bar(hourly_revenue['hour'], hourly_revenue['revenue'], 
                       color=plt.cm.viridis(np.linspace(0, 1, len(hourly_revenue))), 
                       edgecolor='black', linewidth=1.2)
        ax1.set_title('📊 Выручка по часам дня', fontsize=17, fontweight='bold', pad=20)
        ax1.set_xlabel('Час дня', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Выручка, рублей', fontsize=14, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Добавляем значения на столбцы
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}'.replace(',', ' '),
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax1.set_xticks(range(0, 24))
        figures['hourly'] = fig1

        # 2. Выручка по дням недели (УЛУЧШЕННО)
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_labels_ru = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        daily_revenue = df.groupby('day_of_week')['revenue'].sum().reindex(day_order)
        
        fig2, ax2 = plt.subplots(figsize=(14, 7))
        colors = ['#1f77b4', '#1f77b4', '#1f77b4', '#1f77b4', '#1f77b4', '#ff7f0e', '#ff7f0e']
        bars = ax2.bar(day_labels_ru, daily_revenue.values, color=colors, edgecolor='black', linewidth=1.2)
        ax2.set_title('📅 Выручка по дням недели', fontsize=17, fontweight='bold', pad=20)
        ax2.set_xlabel('День недели', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Выручка, рублей', fontsize=14, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Добавляем значения на столбцы
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}'.replace(',', ' '),
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        figures['daily'] = fig2

        # 3. Доля категорий (УЛУЧШЕННО)
        cat_revenue = df.groupby('category')['revenue'].sum().sort_values(ascending=False)
        fig3, ax3 = plt.subplots(figsize=(14, 8))
        colors_pie = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
        wedges, texts, autotexts = ax3.pie(cat_revenue, labels=cat_revenue.index, autopct='%1.1f%%', 
                                            startangle=140, colors=colors_pie, textprops={'fontsize': 13})
        ax3.set_title('🍰 Доля категорий в выручке', fontsize=17, fontweight='bold', pad=20)
        
        # Улучшаем текст процентов
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(12)
        
        figures['categories'] = fig3

        # 4. Средний чек по времени суток (УЛУЧШЕННО)
        def time_of_day(hour):
            if 7 <= hour < 12: return 'Утро\n(7-12)'
            elif 12 <= hour < 17: return 'День\n(12-17)'
            else: return 'Вечер\n(17-23)'
        
        df['time_period'] = df['hour'].apply(time_of_day)
        avg_check = df.groupby('time_period')['revenue'].mean()
        
        fig4, ax4 = plt.subplots(figsize=(14, 7))
        time_order = ['Утро\n(7-12)', 'День\n(12-17)', 'Вечер\n(17-23)']
        avg_check_ordered = avg_check.reindex(time_order)
        bars = ax4.bar(range(len(time_order)), avg_check_ordered.values, 
                       color=['#FFD700', '#FF8C00', '#4B0082'], 
                       edgecolor='black', linewidth=1.5, width=0.6)
        ax4.set_title('💰 Средний чек по времени суток', fontsize=17, fontweight='bold', pad=20)
        ax4.set_ylabel('Средний чек, рублей', fontsize=14, fontweight='bold')
        ax4.set_xticks(range(len(time_order)))
        ax4.set_xticklabels(time_order, fontsize=13, fontweight='bold')
        ax4.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Добавляем значения на столбцы
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)} ₽',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        figures['avg_check'] = fig4

        # 5. Тепловая карта (УЛУЧШЕННО)
        pivot = df.pivot_table(values='revenue', index='day_of_week',
                               columns='hour', aggfunc='sum', fill_value=0)
        pivot = pivot.reindex(day_order)
        pivot.index = day_labels_ru
        
        fig5, ax5 = plt.subplots(figsize=(18, 7))
        sns.heatmap(pivot, cmap='YlOrRd', annot=True, fmt='.0f', linewidths=0.5, 
                   cbar_kws={'label': 'Выручка (₽)'}, ax=ax5, annot_kws={'fontsize': 9})
        ax5.set_title('🔥 Тепловая карта выручки (день недели × час)', fontsize=17, fontweight='bold', pad=20)
        ax5.set_xlabel('Час дня', fontsize=14, fontweight='bold')
        ax5.set_ylabel('День недели', fontsize=14, fontweight='bold')
        figures['heatmap'] = fig5

        # Текстовые выводы
        peak_hour_row = hourly_revenue.loc[hourly_revenue['revenue'].idxmax()]
        peak_hour_val = int(peak_hour_row['hour'])
        peak_hour_rev = int(peak_hour_row['revenue'])
        best_day = daily_revenue.idxmax()
        best_day_ru = day_labels_ru[day_order.index(best_day)]
        top_cat = cat_revenue.idxmax()
        top_cat_share = cat_revenue.max() / cat_revenue.sum() * 100

        insights = {
            'peak_hour': f"{peak_hour_val}:00 ({peak_hour_rev:,} ₽)".replace(',', ' '),
            'best_day': best_day_ru,
            'top_cat': f"{top_cat} ({top_cat_share:.1f}%)",
            'avg_check_morning': f"{avg_check.get('Утро\n(7-12)', 0):.0f} ₽",
            'avg_check_day': f"{avg_check.get('День\n(12-17)', 0):.0f} ₽",
            'avg_check_evening': f"{avg_check.get('Вечер\n(17-23)', 0):.0f} ₽",
        }

        return figures, insights

    except Exception as e:
        logger.error(f"Ошибка при построении графиков или анализе: {e}")
        return {}, {}
