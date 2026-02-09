import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from utils import merge_timetables

TIME_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")


class SETUTimetableScraper:
    def __init__(self):
        self.TIMETABLE_URL = "https://studentssp.setu.ie/timetables/StudentGroupTT.aspx"
        self.params = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",

            "hProgram": "",
            "hStudentcount": "",
            "txtStudentNo": "",
            "cboSchool": "%",
            "CboDept": "%",
            "txtProgTitleFilter": "computer science",
            "CboPOS": "KCMSC_B_Y1",
            "CboStudParentGrp": "kcmsc_b1-W_W3/W4",
            "CboWeeks": "23",
            "CboStartTime": "1",
            "CboEndTime": "9",
            "BtnRetrieve": "Generate Timetable"
        }

        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,pl;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://studentssp.setu.ie',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://studentssp.setu.ie/timetables/StudentGroupTT.aspx',
            'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'
        }

    def warmup_fetch(self):
        """
        This functions gathers fields that are needed for request vlidation by the SETU website
        """
        req = requests.get(self.TIMETABLE_URL, verify=False, headers=self.headers)
        soup = BeautifulSoup(req.text, "html.parser")
        for hidden in soup.select("input[type='hidden']"):
            name = hidden.get("name")
            value = hidden.get("value")

            if name in ["__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION"]:
                # print(f"{name} -> {value}")
                self.params[name] = value

    def fetch_timetable(self, class_group: str = None):
        if class_group:
            self.params["CboStudParentGrp"] = class_group

        req = requests.post(
            self.TIMETABLE_URL,
            headers=self.headers,
            data=self.params,
            verify=False
        )
        soup = BeautifulSoup(req.text, "html.parser")

        table = soup.find("table", attrs={"border": "1"})

        rows = table.find_all("tr")

        timetable = []
        for row in rows:
            cells = [c.get_text(strip=True) for c in row.find_all("td")]
            if cells:
                timetable.append(cells)

        return self._process_timetable(timetable)

    @staticmethod
    def _process_timetable(raw_data):
        """
        Converts raw timetable array into a nested dictionary:
        { group: { day: [classes_sorted_by_time] } }
        Handles multiple P/W groups per class.
        """
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

        # Initialize timetable with P2-P6 and W1-W4
        groups = [f'P{i}' for i in range(2, 7)] + [f'W{i}' for i in range(1, 5)]
        timetable = {g: {day: [] for day in days_order} for g in groups}

        current_day = None
        for row in raw_data[1:]:  # skip header
            if not row or not row[0]:
                continue

            # Detect day row
            if row[0] in days_order:
                current_day = row[0]
                continue

            if not current_day:
                continue  # skip rows before first day

            student_group_field = row[2] if len(row) > 2 else ''

            # Extract P groups
            p_groups = re.findall(r'P\d', student_group_field)
            # Extract W groups (handle multiple W groups separated by /)
            w_groups = []
            for part in re.findall(r'W[\d/]+', student_group_field):
                w_groups.extend(part.split('/'))

            # Combine all groups
            all_groups = set(p_groups + w_groups)

            for group in all_groups:
                if group in timetable:  # only valid groups
                    timetable[group][current_day].append(row)

        # Sort each day's classes by time
        for group in timetable:
            for day in timetable[group]:
                timetable[group][day].sort(
                    key=lambda x: datetime.strptime(x[0], "%H:%M") if x[0] else datetime.strptime("00:00", "%H:%M")
                )

        return timetable


if __name__ == '__main__':
    timetable_generator = SETUTimetableScraper()
    timetable_generator.warmup_fetch()

    timetable_W3_W4 = timetable_generator.fetch_timetable("kcmsc_b1-W_W3/W4")
    timetable_W1_W2 = timetable_generator.fetch_timetable("kcmsc_b1-W_W1/W2")
    merged = merge_timetables(timetable_W3_W4, timetable_W1_W2)
    print(dict(merged))
