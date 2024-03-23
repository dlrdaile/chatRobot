from datetime import datetime


def time_string_to_timestamp(time_str, format_str="%H:%M"):
    current_date = datetime.now().date()
    time_obj = datetime.strptime(time_str, format_str).time()
    combined_datetime = datetime.combine(current_date, time_obj)
    timestamp = int(combined_datetime.timestamp())
    return timestamp
