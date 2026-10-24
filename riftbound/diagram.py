"""Deterministic Graphviz DOT from the model's structured output (Visualization Generator).

The model never writes DOT. It returns plain data (steps, zones, objects, moves); this
module validates that data and draws it, so a malformed or invented structure is dropped
instead of being rendered as if it were game state.
"""

from __future__ import annotations

import textwrap

OWNER_COLORS = {"you": "#dbeafe", "opponent": "#fee2e2", "shared": "#f3f4f6"}


def _esc(text: str) -> str:
    return str(text).replace("\\", "\\\\").replace('"', '\\"')


def _cluster(node_id: str) -> str:
    return node_id.split("_")[0][1:]  # "z2_o0" -> "2"


def _wrap(text: str, width: int = 40) -> str:
    return "\\n".join(textwrap.wrap(_esc(text), width)) or " "


def sequence_dot(steps: list[dict], title: str = "") -> str | None:
    """Numbered left-to-right flow of the steps in the explanation."""
    steps = [s for s in steps if s.get("title") or s.get("detail")]
    if len(steps) < 2:
        return None
    lines = [
        "digraph sequence {",
        "  rankdir=TB; bgcolor=transparent; nodesep=0.3; ranksep=0.25;",
        '  node [shape=box style="rounded,filled" fillcolor="#eef2ff" color="#6366f1" fontname="Helvetica" fontsize=11];',
        '  edge [color="#6366f1"];',
        f'  labelloc=t; fontname="Helvetica"; fontsize=12; fontcolor="#9ca3af"; label="{_esc(title or "Sequence of events (illustration)")}";',
    ]
    for i, s in enumerate(steps, start=1):
        refs = ", ".join(c for c in s.get("citations", [])[:2])
        label = f"{i}. {s.get('title') or s.get('detail')[:40]}"
        body = _wrap(label) + (f"\\n({_esc(refs)})" if refs else "")
        lines.append(f'  s{i} [label="{body}"];')
    lines.append("  " + " -> ".join(f"s{i}" for i in range(1, len(steps) + 1)) + ";")
    lines.append("}")
    return "\n".join(lines)


def board_dot(board: dict | None) -> str | None:
    """Zones as boxed clusters, objects inside them, and arrows for moves between zones."""
    if not isinstance(board, dict):
        return None
    zones = [z for z in board.get("zones") or [] if isinstance(z, dict) and z.get("name")]
    if not zones:
        return None
    lines = [
        "digraph board {",
        "  rankdir=LR; bgcolor=transparent; compound=true; newrank=true;",
        '  node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=10];',
        '  labelloc=t; fontname="Helvetica"; fontsize=12; fontcolor="#9ca3af"; label="Board as described in your scenario (illustration, not an official ruling)";',
    ]
    anchor: dict[str, str] = {}  # zone name -> first node id inside that zone's cluster
    for zi, z in enumerate(zones):
        name = str(z["name"])
        fill = OWNER_COLORS.get(str(z.get("owner", "shared")).lower(), OWNER_COLORS["shared"])
        lines.append(f"  subgraph cluster_{zi} {{")
        lines.append(f'    label="{_esc(name)}"; style="rounded,filled"; fillcolor="{fill}"; color="#9ca3af";')
        objs = [o for o in z.get("objects") or [] if (isinstance(o, dict) and o.get("label")) or isinstance(o, str)]
        if not objs:
            lines.append(f'    z{zi}_empty [label="(empty)" shape=plaintext style=""];')
            anchor[name.lower()] = f"z{zi}_empty"
        for oi, o in enumerate(objs):
            label = o["label"] if isinstance(o, dict) else o
            owner = str(o.get("owner", "")).lower() if isinstance(o, dict) else ""
            color = "#2563eb" if owner == "you" else "#dc2626" if owner == "opponent" else "#6b7280"
            nid = f"z{zi}_o{oi}"
            lines.append(f'    {nid} [label="{_wrap(label, 24)}" fillcolor="white" color="{color}"];')
            anchor.setdefault(name.lower(), nid)
        lines.append("  }")
    for m in board.get("moves") or []:
        if not isinstance(m, dict):
            continue
        src, dst = anchor.get(str(m.get("from", "")).lower()), anchor.get(str(m.get("to", "")).lower())
        if not src or not dst or src == dst:
            continue  # ignore moves that reference zones the model did not define
        label = _esc(" ".join(str(m[k]) for k in ("object", "label") if m.get(k)))
        lines.append(
            f'  {src} -> {dst} [label="{label}" color="#16a34a" fontcolor="#166534" fontsize=9 '
            f"ltail=cluster_{_cluster(src)} lhead=cluster_{_cluster(dst)}];"
        )
    lines.append("}")
    return "\n".join(lines)
