from datetime import datetime, timedelta
import numpy as np


def clean(df, max_age_days=None):
    if df.empty:
        return df
    df = df.dropna(subset=['title', 'score', 'created_utc'])
    df = df[df['score'] >= 0]
    # Respect selected timeframe if provided
    if max_age_days is not None:
        current_time = datetime.now()
        df = df[(df['created_utc'] >= current_time - timedelta(days=max_age_days)) & (df['created_utc'] <= current_time)]
    df['selftext'] = df['selftext'].fillna('')
    df['virality'] = df['score'] * np.log1p(df['velocity'])
    df['hour'] = df['created_utc'].dt.hour
    df['day_of_week'] = df['created_utc'].dt.dayofweek
    df['month'] = df['created_utc'].dt.month
    return df


