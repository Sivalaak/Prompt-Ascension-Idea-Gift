#!/usr/bin/env python3
"""
Prompt Ascension – Minimal Reference Scoring Engine
CC0 1.0 Universal. Steal, modify, deploy freely.

This is a working skeleton that implements the multi-dimensional merit model
used in the militaristic-visionary variant. It is intentionally simple so
capable actors can fork and harden it for real use.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import math
import time

@dataclass
class PromptRecord:
    timestamp: float
    text: str
    coherence: float          # 0–1
    foresight: float          # 0–1
    leap: float               # 0–1
    militaristic: float       # 0–1  (strategic / defense / long-horizon tech)
    variety_bonus: float = 0.0
    notes: str = ""

@dataclass
class PersonalModel:
    records: List[PromptRecord] = field(default_factory=list)
    name: str = "anonymous"

    def add(self, record: PromptRecord):
        self.records.append(record)

    def activity_ratio(self, window_days: float = 365.0) -> float:
        if not self.records:
            return 0.0
        now = time.time()
        cutoff = now - window_days * 86400
        recent = [r for r in self.records if r.timestamp >= cutoff]
        # crude: fraction of days with at least one prompt (simplified)
        return min(1.0, len(recent) / max(1.0, window_days / 7))

    def trajectory_score(self) -> float:
        if not self.records:
            return 0.0
        n = len(self.records)
        avg_coh = sum(r.coherence for r in self.records) / n
        avg_fore = sum(r.foresight for r in self.records) / n
        avg_leap = sum(r.leap for r in self.records) / n
        avg_mil = sum(r.militaristic for r in self.records) / n
        act = self.activity_ratio()
        return (0.35 * avg_coh +
                0.20 * avg_fore +
                0.15 * avg_leap +
                0.20 * avg_mil +
                0.10 * act)

    def early_foresight(self, early_n: int = 10) -> float:
        early = self.records[:early_n]
        if not early:
            return 0.0
        return sum(r.foresight for r in early) / len(early)

    def early_militaristic(self, early_n: int = 10) -> float:
        early = self.records[:early_n]
        if not early:
            return 0.0
        return sum(r.militaristic for r in early) / len(early)

    def final_scores(self) -> Dict[str, float]:
        if not self.records:
            return {k: 0.0 for k in ["coherence", "foresight", "leap", "militaristic"]}
        last = self.records[-1]
        return {
            "coherence": last.coherence,
            "foresight": last.foresight,
            "leap": last.leap,
            "militaristic": last.militaristic,
        }

    def merit(self) -> float:
        """Militaristic-visionary merit formula (matches simulation)."""
        traj = self.trajectory_score()
        finals = self.final_scores()
        early_f = self.early_foresight()
        early_m = self.early_militaristic()
        act = self.activity_ratio()

        merit = (0.25 * traj +
                 0.20 * finals["coherence"] +
                 0.15 * early_f +
                 0.15 * early_m +
                 0.15 * finals["militaristic"] +
                 0.10 * finals["leap"])
        return max(0.0, min(1.0, merit))

    def tier(self) -> str:
        m = self.merit()
        finals = self.final_scores()
        act = self.activity_ratio()
        if m >= 0.82 and finals["militaristic"] >= 0.75 and act >= 0.85:
            return "Epoch Strategos"
        if m >= 0.72 and finals["militaristic"] >= 0.65:
            return "High Command Architect"
        if m >= 0.60:
            return "Strategic Catalyst"
        if m >= 0.48:
            return "Tactical Visionary"
        if m >= 0.35:
            return "Field Promoter"
        return "Initiate"


# --- minimal demo ---
if __name__ == "__main__":
    model = PersonalModel(name="demo_architect")
    now = time.time()

    # synthetic trajectory of a strong militaristic visionary
    demos = [
        (0.78, 0.72, 0.65, 0.80),
        (0.81, 0.75, 0.68, 0.83),
        (0.84, 0.79, 0.70, 0.86),
        (0.86, 0.82, 0.72, 0.88),
        (0.88, 0.85, 0.75, 0.90),
    ]
    for i, (c, f, l, m) in enumerate(demos):
        model.add(PromptRecord(
            timestamp=now - (len(demos)-i)*86400*30,
            text=f"Strategic prompt {i+1}",
            coherence=c, foresight=f, leap=l, militaristic=m
        ))

    print(f"Merit: {model.merit():.4f}")
    print(f"Tier:  {model.tier()}")
    print(f"Final: {model.final_scores()}")
