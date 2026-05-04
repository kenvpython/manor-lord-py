# Manor Lord

A turn-based medieval strategy game inspired by Crusader Kings, written in Python with pygame.

This repository currently contains the **project scaffold** — directory structure, module placeholders, and a runnable pygame main loop with main menu and a placeholder map view. Real game logic (character generation, events, diplomacy, warfare, …) lives behind empty interfaces and will be filled in incrementally.

## Requirements

- Python 3.11+
- pygame >= 2.6

## Run

```bash
pip install -r requirements.txt
python main.py
```

You should see a 1280×720 window. From the main menu click **New Game** to enter the placeholder map view; **End Turn** advances the turn counter.

## Test

```bash
python -m pytest tests/
```

## Layout

```
src/manorlord/
├── app.py                 # pygame init + main loop + scene manager
├── config.py              # screen size / FPS / colors
├── core/                  # GameState, TurnManager, EventBus
├── entities/              # Character, Realm, Province, Title (dataclasses)
├── systems/               # Economy, Diplomacy, Warfare, Lifecycle, EventSystem
├── ui/                    # Scene base + scenes (main_menu, map_view)
├── data/                  # JSON: traits, events, names
└── persistence/           # save/load
```

## Roadmap

- [x] Project scaffold, runnable main loop, end-turn pipeline
- [ ] Character lifecycle (birth / death / inheritance)
- [ ] Economy: taxes, expenses, treasury
- [ ] Diplomacy & relations
- [ ] Warfare: levies, battles, sieges
- [ ] Event chains driven by `data/events.json`
- [ ] Real map: provinces, terrain, rendering

## License

MIT
