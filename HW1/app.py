import streamlit as st
import pandas as pd
import plotly.express as px
import time

from analysis import (
    analyze_sequential,
    analyze_parallel,
    seasonal_statistics,
    is_temperature_anomalous,
    plot_seasonal_boxplot,
    plot_season_year_heatmap,
    plot_anomaly_rate_by_season
)
from api import get_weather_sync, get_weather_async


st.set_page_config(page_title="Мониторинг температуры")
st.title("Мониторинг и анализ температуры")

uploaded_file = st.file_uploader("Загрузите файл temperature_data.csv", type="csv")

if uploaded_file is None:
    st.info("Для начала работы загрузите файл temperature_data.csv")
    st.stop()

df = pd.read_csv(uploaded_file, parse_dates=["timestamp"])

city = st.selectbox("Выберите город", sorted(df["city"].unique()))

st.subheader("Анализ исторических данных")

run_parallel = st.checkbox("Использовать параллеллизацию", value=True)

start = time.time()
if run_parallel:
    df_processed = analyze_parallel(df)
else:
    df_processed = analyze_sequential(df)
elapsed = time.time() - start

st.caption(f"Время выполнения анализа: {elapsed:.2f} секунд")

df_city = df_processed[df_processed["city"] == city]

fig_ts = px.line(
    df_city,
    x="timestamp",
    y="temperature",
    title="Временной ряд температуры"
)

fig_ts.add_scatter(
    x=df_city[df_city["is_anomaly"]]["timestamp"],
    y=df_city[df_city["is_anomaly"]]["temperature"],
    mode="markers",
    name="Аномалия"
)

fig_rm = px.line(
    df_city,
    x="timestamp",
    y="rolling_mean",
    title=f"Скользящее среднее температуры за 30 дней"
)

st.plotly_chart(fig_ts)

st.plotly_chart(fig_rm)

st.plotly_chart(
    plot_seasonal_boxplot(df_city)
)

st.plotly_chart(
    plot_anomaly_rate_by_season(df_city)
)

st.plotly_chart(
    plot_season_year_heatmap(df_city)
)

season_stats = seasonal_statistics(df)
season_city = season_stats[season_stats["city"] == city]

fig_season = px.bar(
    season_city,
    x="season",
    y="mean_temp",
    error_y="std_temp",
    title="Сезонный профиль температуры"
)

st.plotly_chart(fig_season)

st.subheader("Текущая погода")

api_key = st.text_input("API-ключ OpenWeatherMap", type="password")

if api_key:
    weather = get_weather_sync(city, api_key)

    if weather.get("cod") == 401:
        st.error(weather["message"])
    elif weather.get("main"):
        current_temp = weather["main"]["temp"]
        st.metric("Текущая температура", f"{current_temp:.1f} °C")

        current_season = (
            df_city
            .sort_values("timestamp")
            .iloc[-1]["season"]
        )

        row = season_city[season_city["season"] == current_season].iloc[0]

        anomaly = is_temperature_anomalous(
            current_temp,
            row["mean_temp"],
            row["std_temp"]
        )

        if anomaly:
            st.warning("Температура является аномальной для данного сезона")
        else:
            st.success("Температура находится в пределах нормы для данного сезона")
