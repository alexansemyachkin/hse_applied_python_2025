import pandas as pd
from joblib import Parallel, delayed
import plotly.express as px
import plotly.graph_objects as go


def add_rolling_features(df, window=30):

    df = df.sort_values("timestamp").copy()

    df["rolling_mean"] = (
        df.groupby("city")["temperature"]
        .transform(lambda x: x.rolling(window, min_periods=1).mean())
    )

    df["rolling_std"] = (
        df.groupby("city")["temperature"]
        .transform(lambda x: x.rolling(window, min_periods=1).std())
    )

    return df


def detect_anomalies(df):
   
    df = df.copy()

    df["upper"] = df["rolling_mean"] + 2 * df["rolling_std"]
    df["lower"] = df["rolling_mean"] - 2 * df["rolling_std"]

    df["is_anomaly"] = (
        (df["temperature"] > df["upper"]) |
        (df["temperature"] < df["lower"])
    )

    return df


def seasonal_statistics(df):

    return (
        df.groupby(["city", "season"])
        .agg(
            mean_temp=("temperature", "mean"),
            std_temp=("temperature", "std")
        )
        .reset_index()
    )


def process_city(df):

    df_city = df.copy()

    df_city = add_rolling_features(df_city)
    df_city = detect_anomalies(df_city)

    return df_city


def analyze_sequential(df):
   
    results = []
    for city in df["city"].unique():
        df_city = df[df["city"] == city]
        results.append(process_city(df_city))

    return pd.concat(results)


def analyze_parallel(df, n_jobs=-1):
    
    cities = df["city"].unique()

    results = Parallel(n_jobs=n_jobs)(
        delayed(process_city)(df[df["city"] == city])
        for city in cities
    )

    return pd.concat(results)


def is_temperature_anomalous(
    current_temp,
    mean_temp,
    std_temp
):
    
    lower = mean_temp - 2 * std_temp
    upper = mean_temp + 2 * std_temp

    return not (lower <= current_temp <= upper)


def plot_seasonal_boxplot(df_city):
    fig = px.box(
        df_city,
        x="season",
        y="temperature",
        points="outliers",
        title="Распределение температуры по сезонам"
    )
    return fig


def plot_season_year_heatmap(df_city):
    df_tmp = df_city.copy()
    df_tmp["year"] = df_tmp["timestamp"].dt.year

    pivot = (
        df_tmp
        .groupby(["year", "season"])["temperature"]
        .mean()
        .reset_index()
        .pivot(index="year", columns="season", values="temperature")
    )

    fig = px.imshow(
        pivot,
        aspect="auto",
        title="Средняя температура: сезон × год",
        labels=dict(color="Температура")
    )

    return fig


def plot_anomaly_rate_by_season(df_city):
    stats = (
        df_city
        .groupby("season")["is_anomaly"]
        .mean()
        .reset_index()
        .rename(columns={"is_anomaly": "anomaly_rate"})
    )

    fig = px.bar(
        stats,
        x="season",
        y="anomaly_rate",
        title="Доля аномалий по сезонам"
    )

    return fig
