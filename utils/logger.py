from datetime import datetime
from typing import List, Dict

class Logger:
    def __init__(self):
        self.logs: List[Dict] = []

    def log(self, entry: Dict):
        entry["start_time"] = entry.get("start_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
        entry["end_time"] = entry.get("end_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
        self.logs.append(entry)

    def get_logs(self) -> List[Dict]:
        return self.logs
