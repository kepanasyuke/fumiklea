import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from io import BytesIO

def generate_data(n_transactions=10000):
    np.random.seed(42)
    start_date = datetime(2024, 6, 1)
    end_date = datetime(2024, 8, 31)
    dates = pd.date_range(start_date, end_date).to_list()

    probs_days = [0.18 if d.weekday() < 5 else 0.14 for d in dates]
    probs_days = np.array(probs_days) / sum(probs_days)
    chosen_dates = np.random.choice(dates, size=n_transactions, p=probs_days)

    hours = []
    hour_weights = [0.5,0.5,0.5,0.5,1,2,4,6,7, 9,8,5,6,7,5,3,4, 3,2,1,1,0.5,0.5,0.5]
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

def fig_to_bytes(fig):
    """Сохраняет matplotlib figure в BytesIO (PNG) и возвращает."""
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return buf

def analyze_and_get_figures(df):
    """Возвращает словарь с BytesIO графиков и текстовые выводы."""
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 6)

    # 1. Выручка по часам
    hourly_revenue = df.groupby('hour')['revenue'].sum().reset_index()
    fig1, ax1 = plt.subplots()
    sns.barplot(data=hourly_revenue, x='hour', y='revenue', hue='hour', palette='viridis', legend=False, ax=ax1)
    ax1.set_title('Общая выручка по часам')
    ax1.set_xlabel('Час')
    ax1.set_ylabel('Выручка, руб.')
    buf1 = fig_to_bytes(fig1)
    plt.close(fig1)

    # 2. Выручка по дням недели
    daily_revenue = df.groupby('day_of_week')['revenue'].sum().reindex(
        ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    )
    fig2, ax2 = plt.subplots()
    sns.barplot(x=daily_revenue.index, y=daily_revenue.values, hue=daily_revenue.index, palette='coolwarm', legend=False, ax=ax2)
    ax2.set_title('Выручка по дням недели')
    ax2.set_xlabel('День недели')
    ax2.set_ylabel('Выручка, руб.')
    ax2.tick_params(axis='x', rotation=45)
    buf2 = fig_to_bytes(fig2)
    plt.close(fig2)

    # 3. Доля категорий
    cat_revenue = df.groupby('category')['revenue'].sum().sort_values(ascending=False)
    fig3, ax3 = plt.subplots()
    ax3.pie(cat_revenue, labels=cat_revenue.index, autopct='%1.1f%%', startangle=140,
            colors=sns.color_palette('pastel'))
    ax3.set_title('Доля категорий в общей выручке')
    buf3 = fig_to_bytes(fig3)
    plt.close(fig3)

    # 4. Средний чек по времени суток
    def time_of_day(hour):
        if 7 <= hour < 12: return 'Утро'
        elif 12 <= hour < 17: return 'День'
        else: return 'Вечер'
    df['time_period'] = df['hour'].apply(time_of_day)
    avg_check = df.groupby('time_period')['revenue'].mean()
    fig4, ax4 = plt.subplots()
    sns.barplot(x=avg_check.index, y=avg_check.values, hue=avg_check.index, palette='Set2',
                order=['Утро','День','Вечер'], legend=False, ax=ax4)
    ax4.set_title('Средний чек по времени суток')
    ax4.set_xlabel('Период')
    ax4.set_ylabel('Средний чек, руб.')
    buf4 = fig_to_bytes(fig4)
    plt.close(fig4)

    # 5. Тепловая карта
    pivot = df.pivot_table(values='revenue', index='day_of_week',
                           columns='hour', aggfunc='sum', fill_value=0)
    pivot = pivot.reindex(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
    fig5, ax5 = plt.subplots(figsize=(14, 6))
    sns.heatmap(pivot, cmap='YlOrRd', annot=True, fmt='.0f', linewidths=.5, ax=ax5)
    ax5.set_title('Тепловая карта выручки (день недели × час)')
    ax5.set_xlabel('Час')
    ax5.set_ylabel('День недели')
    buf5 = fig_to_bytes(fig5)
    plt.close(fig5)

    # Текстовые выводы
    peak_hour_row = hourly_revenue.loc[hourly_revenue['revenue'].idxmax()]
    peak_hour_val = int(peak_hour_row['hour'])
    peak_hour_rev = int(peak_hour_row['revenue'])
    best_day = daily_revenue.idxmax()
    top_cat = cat_revenue.idxmax()
    top_cat_share = cat_revenue.max() / cat_revenue.sum() * 100

    insights = {
        'peak_hour': f"{peak_hour_val}:00 (выручка {peak_hour_rev} руб.)",
        'best_day': best_day,
        'top_cat': f"{top_cat} ({top_cat_share:.1f}%)",
        'avg_check_morning': f"{avg_check.get('Утро', 0):.0f} руб.",
        'avg_check_day': f"{avg_check.get('День', 0):.0f} руб.",
        'avg_check_evening': f"{avg_check.get('Вечер', 0):.0f} руб.",
    }

    figures = {
        'hourly': buf1,
        'daily': buf2,
        'categories': buf3,
        'avg_check': buf4,
        'heatmap': buf5
    }

    return figures, insights