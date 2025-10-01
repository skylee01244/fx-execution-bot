from datetime import datetime

def format_datetime(dt_str):
    """Convert Saxo's ISO datetime into a cleaner format"""
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M UTC")
