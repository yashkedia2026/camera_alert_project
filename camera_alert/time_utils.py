from datetime import datetime, time as dtime

# Operating hours constants
START_TIME = dtime(20, 0)    # 8:00 PM
END_TIME   = dtime(9, 30)    # 9:30 AM


def get_timestamped_filename(prefix: str, ext: str) -> str:
    """
    Generate a filename with millisecond precision to avoid collisions.
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    return f"{prefix}_{ts}.{ext}"


# def is_within_operating_hours(now: dtime = None) -> bool:
#     """
#     Return True if current local time is within the operating window:
#     from START_TIME (8:00 PM) to END_TIME (9:30 AM), crossing midnight.
#     """
#     current = now or datetime.now().time()
#     return (current >= START_TIME) or (current <= END_TIME)
