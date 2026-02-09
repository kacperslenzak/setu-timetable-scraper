from datetime import datetime, timedelta


def merge_timetables(tt1, tt2):
    merged = {}

    for d in [tt1, tt2]:
        for group, days in d.items():
            merged.setdefault(group, {})
            for day, lessons in days.items():
                merged.setdefault(group, {}).setdefault(day, [])
                for lesson in lessons:
                    # Only add if not already in list
                    if lesson not in merged[group][day]:
                        merged[group][day].append(lesson)

    return merged


def get_timetable_week_number(date=None):
    """
    Calculate the week number for the timetable scraper.

    Args:
        date: datetime object or None. If None, uses current date.

    Returns:
        int: The week number to use as parameter (e.g., 24 for week starting 09-FEB-26)

    Example:
        >>> get_timetable_week_number(datetime(2026, 2, 9))
        24
    """
    if date is None:
        date = datetime.now()

    # Reference point: Week 24 starts on Monday, February 9, 2026
    reference_date = datetime(2026, 2, 9)  # Monday of week 24
    reference_week = 24

    # Calculate the difference in days
    days_diff = (date - reference_date).days

    # Calculate week difference (each week is 7 days)
    weeks_diff = days_diff // 7

    # Calculate the week number
    week_number = reference_week + weeks_diff

    return week_number


def get_week_for_param(date=None):
    """
    Get the week number formatted for the CboWeeks parameter.

    Args:
        date: datetime object or None. If None, uses current date.

    Returns:
        str: The week number as a string (e.g., "24")

    Example:
        >>> get_week_for_param(datetime(2026, 2, 9))
        '24'
    """
    week_num = get_timetable_week_number(date)
    return str(week_num)
