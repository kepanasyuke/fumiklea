import pandas as pd
import matplotlib.pyplot as plt
from coffee_analysis import generate_data

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("Библиотека Prophet не установлена. Прогноз будет пропущен. Установите: pip install prophet")

def prepare_daily_revenue(df):
    daily = df.groupby('date')['revenue'].sum().reset_index()
    daily.columns = ['ds', 'y']
    daily['ds'] = pd.to_datetime(daily['ds'])
    return daily

def forecast_demand(daily_df, periods=30):
    if not PROPHET_AVAILABLE:
        return None, None
    model = Prophet(daily_seasonality=True, weekly_seasonality=True)
    model.fit(daily_df)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return model, forecast

def plot_forecast(model, forecast, save_path='forecast_plot.png'):
    if model is None:
        print("Прогноз не построен из-за отсутствия Prophet.")
        return
    fig = model.plot(forecast, xlabel='Дата', ylabel='Выручка, руб.')
    plt.title('Прогноз ежедневной выручки кофейни')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    fig2 = model.plot_components(forecast)
    plt.tight_layout()
    plt.savefig('forecast_components.png')
    plt.close()

if __name__ == '__main__':
    df = generate_data(10000)
    daily = prepare_daily_revenue(df)
    model, forecast = forecast_demand(daily, periods=30)
    plot_forecast(model, forecast)
    if PROPHET_AVAILABLE:
        print("Прогноз сохранён: forecast_plot.png, forecast_components.png")
    else:
        print("Прогноз пропущен. Установите prophet для возможности прогнозирования.")