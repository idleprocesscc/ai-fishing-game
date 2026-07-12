#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate the blind-play fishing.py from engine.py.

engine.py is the readable engine source. fishing.py packs it into base64 so
an AI player can use cmd()/new_game() without reading fish tables or odds.

Run this after changing engine.py:

    python build_blind.py

The generated file stays behaviorally identical to engine.py.
"""
import base64
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

# Header shown to AI players. The packed engine lives below it in _BLOB.
HEADER = '''"""🌍🎣 World Waters Field Journal · Blind-Play Build

Instructions for AI players:
You are a field observer, not the developer. Play by reading cmd() results:

    import fishing
    print(fishing.cmd("help"))      # rules
    print(fishing.cmd("language en")) # optional; Chinese is the default
    print(fishing.cmd("status"))    # current state
    print(fishing.cmd("cast"))      # cast once
    print(fishing.cmd("cast 10"))   # batch-cast 10 times
    # Then decide: conditions / cast / goto / identify / journal ...

Please do not decode or inspect _BLOB. It contains the engine and would spoil
species lists, locations, and probabilities. Play blind and learn by observing.
Use engine.py if you want to read or modify the source.

API: fishing.cmd("command") returns text; fishing.new_game(seed) starts over.
"""'''


def build():
    engine_src = (HERE / "engine.py").read_text(encoding="utf-8")
    data_src = (HERE / "real_world_data.py").read_text(encoding="utf-8")
    # Install the content module in memory so the blind build remains a single
    # distributable file even though readable development uses two files.
    bootstrap = (
        "import sys, types\n"
        "_rw = types.ModuleType('real_world_data')\n"
        "exec(" + repr(data_src) + ", _rw.__dict__)\n"
        "sys.modules['real_world_data'] = _rw\n"
    )
    bundled_src = bootstrap + engine_src
    b64 = base64.b64encode(bundled_src.encode("utf-8")).decode("ascii")
    chunks = "\n".join('    "%s"' % b64[i:i + 76] for i in range(0, len(b64), 76))
    out = (
        HEADER
        + "\nimport base64\n_BLOB = (\n"
        + chunks
        + "\n)\nexec(base64.b64decode(_BLOB).decode(\"utf-8\"), globals())\n\n"
        + "if __name__ == \"__main__\":\n    print(cmd(\"help\"))\n    print()\n    print(cmd(\"status\"))\n"
    )
    (HERE / "fishing.py").write_text(out, encoding="utf-8")
    print("✅ Regenerated fishing.py from engine.py (%d bytes)" % len(out))


if __name__ == "__main__":
    build()
