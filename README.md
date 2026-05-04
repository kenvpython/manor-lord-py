# Manor Lord

A turn-based medieval strategy game inspired by Crusader Kings, written in Python with pygame.

**v0.2.0 — Eight Realms.** The world is now seeded with eight rival counties, each with its own lord, treasury, and territory rendered as a polygon overlaid on an oil-painting style map. Real diplomacy, warfare, and event chains still live behind placeholder systems and will be filled in incrementally.

## Requirements

- Python 3.11+
- pygame >= 2.6

## Run

```bash
pip install -r requirements.txt
python main.py
```

A **1920×1080** window opens. From the main menu click **New Game** to reach the realm-select screen; click any of the eight realms on the map and press **Begin** to play that lord. **End Turn** advances the turn counter and runs all systems.

## Custom map art

Drop an oil-painting style image at `assets/images/map.png` (recommended 1500×970 to fit the map area). It will replace the parchment placeholder. The eight realm polygons are rendered semi-transparently on top, so any background art shows through.

## Test

```bash
python -m pytest tests/
```

## Layout

```
src/manorlord/
├── app.py                 # pygame init + main loop + scene manager
├── config.py              # screen size / FPS / palette / 8 realm colors
├── core/                  # GameState, TurnManager, EventBus, new_game (create_world / set_player)
├── entities/              # Character, Realm (with color), Province (with polygon), Title
├── systems/               # Economy, Diplomacy, Warfare, Lifecycle, EventSystem
├── ui/                    # Scene base, theme, widgets, world_map renderer
│   └── scenes/            #   main_menu, realm_select, map_view
├── data/                  # JSON: traits, events, names, realms, provinces
└── persistence/           # save/load
```

## Roadmap

- [x] Project scaffold, runnable main loop, end-turn pipeline
- [x] Eight rival realms with per-realm lords, colors, descriptions
- [x] Realm-select screen with map polygons and hover/select feedback
- [ ] Character lifecycle (birth / death / inheritance)
- [ ] Economy: real expenses, building/upgrade decisions
- [ ] Diplomacy & relations between the eight realms
- [ ] Warfare: levies, battles, sieges
- [ ] Event chains driven by `data/events.json`
- [ ] Replace placeholder map with rendered oil-painting art

## License

MIT
