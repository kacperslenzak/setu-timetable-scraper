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
