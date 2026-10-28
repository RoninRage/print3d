# Bambu Lab A1: offene Todos

Stand 28.10.2026, Branch `a1-support`, PR #2. Was erledigt ist, steht im PR und
in `docs/a1-phase1-analysis.md`. Hier steht nur, was noch fehlt.

## 1. Vor dem ersten echten Druck

- [ ] **PR #2 mergen** oder bewusst auf `a1-support` bleiben. Ein Agent, der
      print3d aus diesem Ordner startet, nutzt den Branch, der gerade
      ausgecheckt ist.
- [ ] **print3d beim Agent registrieren**, mit dem A1 als Drucker. Bisher ist es
      in Claude Code nicht eingetragen:
      ```bash
      claude mcp add print3d -e PRINT3D_PRINTER=a1-0.4 -- \
        uv run --directory /mnt/daten/Development/print3d python -m print3d mcp
      ```
      Danach eine neue Session starten.
- [ ] **Bambu Studio einrichten:** A1 als Drucker hinzufügen und verbinden,
      AMS lite erkannt, Textured-PEI-Platte ausgewählt.

## 2. Echte Drucke (Abgleich mit der Realität)

- [ ] **Passungs-Test** drucken (`print3d --printer a1-0.4 coupon`). Die Werte,
      die gepasst haben, mit `print3d fit set --slide ... --snug ...`
      speichern. Erst danach stimmen Passungen in Modellen.
- [ ] **Einfaches Teil** drucken, z. B. das Namensschild aus `examples/nameplate.py`.
      Maße mit dem Messschieber gegen den Report prüfen.
- [ ] **Mehrfarbiger Druck** (z. B. `tests/fixtures/lidded_box_inlay.py`):
  - [ ] Ordnet Studio die Filamente den richtigen AMS-lite-Slots zu?
  - [ ] Wie viel Material geht beim Purgen verloren, und steckt das in den
        14,03 g, die der Report angibt?
  - [ ] Setzt Studio einen Prime Tower? Stimmt die Zeitschätzung (44,5 min)
        ungefähr?
- [ ] **Schätzung gegen Realität:** Zeit und Gewicht von Studio gegen den
      echten Druck notieren. Bei großen Abweichungen braucht der Report einen
      Hinweis.

## 3. Code: offen aus dem Plan

- [ ] **`print3d setup` setzt `PRINT3D_PRINTER` nicht** (Schritt 9 der
      Analyse). Bisher steht nur in der README, wie man es von Hand setzt.
      Idee: `print3d setup --printer a1-0.4` gibt `-e PRINT3D_PRINTER=...` an
      jeden Agent weiter.
- [ ] **Drucker pro Aufruf im MCP-Tool:** `make` kennt den Drucker nur über die
      Umgebungsvariable. Ein optionales Argument `printer` würde Umschalten
      ohne Neustart erlauben.
- [ ] **Purge-Verlust im Report:** Beim A1 kostet jeder Farbwechsel Material.
      Die Advice nennt das nur als Hinweis, ohne Gramm. Prüfen, ob Studio den
      Purge in `slice_info` ausweist, und dann anzeigen.

## 4. Code: Aufräumen und Prüfen

- [ ] **Vier Integrationstests sind schon vorher kaputt.** Ihnen fehlen
      `examples/lidded_box.py`, `examples/pen_caddy.py` und
      `tests/test_tin_benchmark.py`; die Dateien wurden nie committet.
      Entweder aus dem Original-Repo (mfranzon) holen oder die Tests entfernen.
- [ ] **X2D-Farbgrenze von 16 ist geschätzt** (4 AMS × 4 Slots). Vorher gab es
      keine Grenze. Bestätigen oder anpassen.
- [ ] **X2D-Profile sind noch die von macOS** (Studio 02.08.02.61). Ein Slice
      unter Linux ergibt 13 min 47 s und 3,66 g statt 13 min 52 s und 3,63 g
      im Referenz-Slice. Das stört nicht, aber man könnte mit
      `print3d flatten` neu flatten und den Referenz-Slice erneuern.
- [ ] **Lint:** `ruff check` meldet 24 alte Fehler, keiner davon aus dem
      A1-Umbau (Import-Sortierung, `fit_coupon.py`). Optional.
- [ ] **Hinweis zu Blender 5.2:** Die Meldungen zu `cattrs` und
      `register_class` kommen vom Add-on `bl_pkg` und sind harmlos.
      Eventuell in der README erwähnen.

## 5. Nächstes Ziel: A1 mit anderen Düsen (0,2 / 0,6 / 0,8 mm)

Bisher gibt es nur `a1-0.4`. Bambu Studio liefert die Profile für alle drei
anderen Düsen mit (geprüft in `~/.config/BambuStudio/system/BBL`).

### Profile

| id | Machine | Process (Standard) | Filament |
|---|---|---|---|
| `a1-0.2` | `Bambu Lab A1 0.2 nozzle` | `0.10mm Standard @BBL A1 0.2 nozzle` | `Bambu PLA Basic @BBL A1 0.2 nozzle` |
| `a1-0.6` | `Bambu Lab A1 0.6 nozzle` | `0.30mm Standard @BBL A1 0.6 nozzle` | `Bambu PLA Basic @BBL A1` |
| `a1-0.8` | `Bambu Lab A1 0.8 nozzle` | `0.40mm Standard @BBL A1 0.8 nozzle` | `Bambu PLA Basic @BBL A1` |

- [ ] Für die 0,6er-Düse ist in Studio `0.30mm Strength` voreingestellt.
      Entscheiden, ob `Standard` oder `Strength` gepinnt wird.
- [ ] Die drei Einträge in `printers.py` anlegen und mit
      `print3d --printer a1-0.X flatten` die Ordner
      `src/print3d/profiles/a1-0.X/` erzeugen.

### Code, der heute 0,4 mm annimmt

- [ ] **`Printer` um `nozzle_mm` und `layer_mm` erweitern.** Die Texte und
      Grenzwerte unten sollen daraus rechnen statt fester Zahlen.
- [ ] **Druckblatt-Kopf** (`handoff.py`): „0.4 mm nozzle, 0.20 mm layers“ ist
      fest eingetragen.
- [ ] **Mindestdicke** (`printability.py`, `THIN_PART_MM = 1.2`): Das sind
      etwa 3 Perimeter bei 0,4 mm. Bei 0,8 mm sind 1,2 mm nur noch
      1,5 Perimeter, bei 0,2 mm ist der Wert zu streng. Etwa
      `3 × nozzle_mm` verwenden.
- [ ] **„Sticker“-Grenze** (`printability.py`, 0,6 mm = 3 Layer bei 0,2 mm):
      an `layer_mm` koppeln.
- [ ] **Passungen** (`fits.py`): Die Standardwerte gelten für 0,4 mm, und
      gespeichert wird global in `~/print3d/fits.json`. Das Spiel hängt von
      der Düse ab, also pro Drucker-id speichern (z. B. ein Schlüssel pro
      `a1-0.X`). Texte in `fits.py` und `handoff.py` anpassen.
- [ ] **Passungs-Test** (`coupons/fit_coupon.py`, 0,00–0,40 mm): Für 0,6
      und 0,8 mm den Bereich vergrößern, für 0,2 mm feiner stufen.
- [ ] **Skill-Texte:** Das Inlay mit „0.6 mm (three layers)“ und die
      Tabelle in `SKILL.md` (0,4 mm, 0,20 mm Layer) nach Düse beschreiben.
      `modelling.md` auf Details prüfen, die mit 0,2 mm nicht druckbar sind
      bzw. bei 0,8 mm verloren gehen (Text, kleine Löcher).
- [ ] **Studio-Ausgabe prüfen:** Steht in der `.3mf` die richtige Düse? Studio
      warnt beim Senden, wenn die eingebaute Düse nicht passt.

### Tests

- [ ] `test_pinned_profiles_match_the_registry` deckt neue Einträge
      automatisch ab. Dazu `nozzle_diameter` gegen `nozzle_mm` prüfen.
- [ ] Pro Düse ein Referenz-Slice des 20-mm-Würfels
      (`tests/fixtures/cube_20mm_a1-0.X.gcode.3mf`) und ein Live-Test.
- [ ] Unit-Tests für die Grenzwerte, die von der Düse abhängen
      (Mindestdicke, Sticker, Passungen).

### Echte Drucke

- [ ] Pro Düse einen eigenen Passungs-Test drucken und die Werte speichern.
- [ ] Bei 0,2 mm prüfen, ob die Zeitschätzung (sehr lange Drucke) und feine
      Details stimmen, bei 0,8 mm Maßhaltigkeit und Überhänge.
