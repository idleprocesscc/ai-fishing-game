# Blind Play with an AI That Has Code Execution

Works with ChatGPT Advanced Data Analysis, Claude with code execution, or any agent with a Python sandbox.

## Steps

1. Upload **`fishing.py`** to the AI.
2. Send a prompt like this:

> I made a small text fishing game for you. You are the player. Please `import fishing`, then play by reading the text returned by `fishing.cmd("command")`:
>
> ```python
> import fishing
> print(fishing.cmd("help"))
> print(fishing.cmd("status"))
> print(fishing.cmd("cast"))
> ```
>
> Please do not decode or inspect `_BLOB`; that packed data is the game engine and would spoil the fish list, locations, and probabilities. Play blind and discover things by casting.
>
> For fewer turns, use `cast 10` or `cast 20 stop=rare`.

## Tips

- The save file is `fishing_save.json` inside the AI sandbox. If the sandbox resets, progress resets too.
- Start a fresh run with `fishing.new_game(seed)`.
- Same seed + same command sequence gives reproducible results for that version.
