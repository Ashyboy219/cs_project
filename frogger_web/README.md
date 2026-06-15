# Frogger — Web (WASM) build

This folder holds the browser-playable version of the game that is embedded as
the live demo in the presentation (`/index.html`, slide 10) and served at
`/game/` on the deployment.

It is the same game as the desktop `frogger.py`, with the main loop made
`async` so it can run in the browser via [pygbag](https://github.com/pygame-web/pygbag)
(pygame compiled to WebAssembly).

## Files

- `main.py` — the async, browser-compatible game (pygbag entry point).
- `local.tmpl` — the pygbag 0.9.3 HTML template, vendored so the build does not
  need to reach the pygbag CDN at build time.

## Rebuilding

```bash
pip install pygbag==0.9.3
python3 -m pygbag --build \
  --template frogger_web/local.tmpl \
  --icon <some.png> \
  frogger_web/main.py
# then copy the result into the served directory:
cp -r frogger_web/build/web game
```

The generated page loads the Python WASM runtime from the pygbag CDN
(`https://pygame-web.github.io/cdn/0.9.3/`) in the visitor's browser, and loads
the game code from the local `frogger_web.apk` next to it.
