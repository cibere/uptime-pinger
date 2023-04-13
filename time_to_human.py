"""
This file is licensed under MPL-2.0

This code was taken from https://github.com/Rapptz/RoboDanny
specifically a combination of https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/utils/formats.py
and https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/utils/time.py
"""

from __future__ import annotations

import datetime
from typing import Sequence

from dateutil.relativedelta import relativedelta

__all__ = ("plural", "human_join", "human_timedelta")


class plural:
    def __init__(self, value: int):
        self.value: int = value

    def __format__(self, format_spec: str) -> str:
        v = self.value
        singular, sep, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"
        if abs(v) != 1:
            return f"{v} {plural}"
        return f"{v} {singular}"


def human_join(seq: Sequence[str], delim: str = ", ", final: str = "or") -> str:
    size = len(seq)
    if size == 0:
        return ""

    if size == 1:
        return seq[0]

    if size == 2:
        return f"{seq[0]} {final} {seq[1]}"

    return delim.join(seq[:-1]) + f" {final} {seq[-1]}"


def human_timedelta(dt: datetime.datetime) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)

    if now.tzinfo is None:
        now = now.replace(tzinfo=datetime.timezone.utc)

    now = now.replace(microsecond=0)
    dt = dt.replace(microsecond=0)

    if dt > now:
        delta = relativedelta(dt, now)
    else:
        delta = relativedelta(now, dt)
    output_suffix = ""

    attrs = [
        ("year", "y"),
        ("month", "mo"),
        ("day", "d"),
        ("hour", "h"),
        ("minute", "m"),
        ("second", "s"),
    ]

    output = []
    for attr, _ in attrs:
        elem = getattr(delta, attr + "s")
        if not elem:
            continue

        if attr == "day":
            weeks = delta.weeks
            if weeks:
                elem -= weeks * 7
                output.append(format(plural(weeks), "week"))

        if elem <= 0:
            continue

        output.append(format(plural(elem), attr))

    if len(output) == 0:
        return "now"
    else:
        return human_join(output, final="and") + output_suffix
