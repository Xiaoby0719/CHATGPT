#!/usr/bin/env python3
"""Yi Huan (異環) Daily Assistant - runnable template.

This project is a downloadable/run-ready assistant for daily-task workflows.
It intentionally avoids process injection or anti-cheat bypass.
Use only where game ToS allows automation.
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class Rule:
    name: str
    when_all: Dict[str, Any]
    do: List[str]
    cooldown_sec: float = 0.0


class YiHuanStateProvider:
    """Read current game state snapshot from JSON.

    The downloaded software can run immediately by updating state.json from
    any detector layer (OCR/screenshot parser/external tool).
    """

    def __init__(self, state_file: Path):
        self.state_file = state_file

    def get_state(self) -> Dict[str, Any]:
        if not self.state_file.exists():
            return {}
        try:
            data = json.loads(self.state_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
        return {}


class ActionExecutor:
    """Action layer for Yi Huan daily tasks.

    Default mode is dry-run for customer safety. In --live mode this template
    still only prints action mapping; users can plug real macro libraries.
    """

    ACTION_MAP = {
        "focus_game_window": "切換到異環視窗",
        "open_daily_panel": "開啟每日面板",
        "claim_sign_in_reward": "領取簽到獎勵",
        "claim_mail_reward": "領取郵件獎勵",
        "open_bounty_board": "開啟委託面板",
        "start_quick_bounty": "執行快速委託",
        "collect_bounty_reward": "領取委託獎勵",
        "open_stamina_shop": "開啟體力商店",
        "buy_stamina_once": "購買一次體力",
        "close_panel": "關閉目前面板",
    }

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run

    def execute(self, action_name: str) -> None:
        desc = self.ACTION_MAP.get(action_name, f"未定義動作: {action_name}")
        mode = "DRY-RUN" if self.dry_run else "LIVE"
        print(f"[{mode}] {action_name} -> {desc}")


class RuleEngine:
    def __init__(self, rules: List[Rule]):
        self.rules = rules
        self._last_run: Dict[str, float] = {}

    @staticmethod
    def _match(when_all: Dict[str, Any], state: Dict[str, Any]) -> bool:
        return all(state.get(k) == v for k, v in when_all.items())

    def evaluate(self, state: Dict[str, Any]) -> List[Rule]:
        now = time.time()
        matched: List[Rule] = []
        for rule in self.rules:
            if not self._match(rule.when_all, state):
                continue
            last = self._last_run.get(rule.name, 0.0)
            if now - last < rule.cooldown_sec:
                continue
            matched.append(rule)
            self._last_run[rule.name] = now
        return matched


def load_rules(path: Path) -> List[Rule]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [
        Rule(
            name=item["name"],
            when_all=item.get("when_all", {}),
            do=item.get("do", []),
            cooldown_sec=float(item.get("cooldown_sec", 0)),
        )
        for item in raw.get("rules", [])
    ]


def run_loop(provider: YiHuanStateProvider, engine: RuleEngine, executor: ActionExecutor, interval: float) -> None:
    print("Yi Huan Daily Assistant started. Press Ctrl+C to stop.")
    while True:
        state = provider.get_state()
        if state:
            print(f"[STATE] {state}")
        for rule in engine.evaluate(state):
            print(f"[RULE] matched: {rule.name}")
            for action in rule.do:
                executor.execute(action)
        time.sleep(interval)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Yi Huan daily assistant")
    parser.add_argument("--rules", default="rules.example.json", help="Path to rules JSON")
    parser.add_argument("--state", default="state.json", help="Path to state JSON")
    parser.add_argument("--interval", type=float, default=1.0, help="Polling interval in seconds")
    parser.add_argument("--live", action="store_true", help="Enable live mode")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    rules_path = Path(args.rules)
    if not rules_path.exists():
        print(f"Rules file not found: {rules_path}")
        return 1

    rules = load_rules(rules_path)
    provider = YiHuanStateProvider(Path(args.state))
    engine = RuleEngine(rules)
    executor = ActionExecutor(dry_run=not args.live)

    try:
        run_loop(provider, engine, executor, args.interval)
    except KeyboardInterrupt:
        print("Stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
