import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class DecisionLogger:
    def __init__(self, log_path: Path, quality_path: Path):
        self.log_path = log_path
        self.quality_path = quality_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, payload: Dict[str, Any]) -> None:
        payload = dict(payload)
        payload["logged_at"] = datetime.now(timezone.utc).isoformat()

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

        self._refresh_quality_summary()

    def _read_log_rows(self) -> List[Dict[str, Any]]:
        if not self.log_path.exists():
            return []
        rows: List[Dict[str, Any]] = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return rows

    def _refresh_quality_summary(self) -> None:
        rows = self._read_log_rows()
        if not rows:
            summary = {
                "total_decisions": 0,
                "avg_confidence": 0.0,
                "grounded_rate": 0.0,
                "status_distribution": {},
            }
        else:
            total = len(rows)
            confidences = [float(r.get("response", {}).get("confidence_score", 0.0)) for r in rows]
            grounded_count = sum(1 for r in rows if r.get("response", {}).get("grounded", False))
            status_distribution: Dict[str, int] = {}
            for row in rows:
                status = row.get("response", {}).get("eligibility_status", "UNKNOWN")
                status_distribution[status] = status_distribution.get(status, 0) + 1

            summary = {
                "total_decisions": total,
                "avg_confidence": round(sum(confidences) / total, 3),
                "grounded_rate": round(grounded_count / total, 3),
                "status_distribution": status_distribution,
            }

        with open(self.quality_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
