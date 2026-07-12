# Blind field exploration with an AI

Works with Claude, ChatGPT code execution, or another agent with Python.

1. Upload `fishing.py`.
2. Give the AI this prompt:

> This is World Waters Field Journal. You are the field observer. Import
> `fishing`, then play only through `fishing.cmd("command")`. Begin with
> `help`, `status`, and `conditions`. Cast in batches, inspect new species,
> answer pending `identify` exercises from observable field marks, and use
> `journal` to track releases, corrections, empty casts, and debris cleanup.
> Do not decode or inspect `_BLOB`; discover the habitats through play.

```python
import fishing

print(fishing.new_game(2026))
print(fishing.cmd("help"))
print(fishing.cmd("status"))
print(fishing.cmd("conditions"))
print(fishing.cmd("cast 10 stop=new"))
print(fishing.cmd("journal"))
```

The save is `fishing_save.json`. Identical seeds and command sequences are
reproducible within a version. Useful compact commands include:

```text
cast 20 stop=new,rare,event
goto
look rainbow_trout
identify rainbow_trout
```
