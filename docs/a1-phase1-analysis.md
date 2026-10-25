# Bambu Lab A1 support: Phase 1 analysis

Read-only analysis of where the Bambu Lab X2D is hard-wired, and the proposed
changes for an A1 (0.4 mm nozzle, AMS lite, Textured PEI Plate). Nothing in
`src/` was changed. Baseline: `pytest -q` → 77 passed, 9 skipped.

## Hard-wired X2D spots

| File | Lines | What |
|---|---|---|
| `paths.py` | 19 | `default_profiles_dir()` fixed to `profiles/x2d-0.4`. Used by `pipeline.py`, `cli.py` (`status`, `plan`, `flatten`), `handoff.py`. |
| `flatten.py` | 19–22, 29–44, 225 | `DEFAULT_MACHINE/PROCESS/FILAMENT/BED_TYPE`, `flatten_x2d()`. `detect_profiles_root()` only knows macOS paths (`BAMBU_PROFILES_ROOT` env already works as an escape hatch). The flatten logic itself (inherits/include, `cli_config` overlay, extruder count from `nozzle_diameter`) is printer-agnostic. |
| `dfm.py` | 11, 127, 134 | `X2D_BED_MM = (256, 256, 260)`, message "exceeds X2D bed". `check_mesh()` already takes `bed_mm=`; `pipeline.py:267` does not pass it. |
| `filaments.py` | 5, 37 | `NOZZLES = 2`, docstring about two nozzles. |
| `pipeline.py` | 22, 285–293 | > `NOZZLES` colours → `note` "Fine with an AMS". No error path. |
| `studio.py` | 33, 40–57 | `bed_type` default "Textured PEI Plate" (pipeline never overrides it). `find_studio()` only knows macOS/Homebrew paths; Linux relies on `BAMBU_STUDIO_BIN` or `bambu-studio` on PATH. |
| `handoff.py` | 85, 315 | `_cost_per_kg()` reads the default profile dir. Header text hard-codes "Bambu Lab X2D, 0.4 mm nozzle, 0.20 mm layers, Bambu PLA Basic, textured PEI, supports off". |
| `mcp_server.py` | 32 | Agent instructions name the X2D. |
| `cli.py` | 266, 396 | Parser description and `flatten` help name the X2D. |
| `__init__.py` | 1 | Docstring. |
| `printability.py` | 10 | Comment on `enable_support = 0`. That value comes from the Bambu profile itself; `flatten` does not force it. |
| `setup.py` | 126 | `claude mcp add` is called without `env`. |
| Skill | `SKILL.md` 3, 8, 81, 136–139; `modelling.md` 1; `parts-and-fits.md` 45 | X2D, bed size, "two nozzles". |
| Tests | `test_studio_it.py` | Asserts real slice values (e.g. 15 layers). Golden fixture `tests/fixtures/cube_20mm.gcode.3mf`. Unit tests do not reference X2D constants. |

Notes:

- The pinned X2D machine profile has `printable_height = 261`; `dfm.py` uses 260. Keep that for the X2D; for the A1 take the bed from the flattened profile.
- `fits.py`, `THIN_PART_MM = 1.2` and the "0.4 mm nozzle in PLA" texts still hold for the A1.

## Proposed changes

1. New `printers.py`: frozen `Printer` dataclass (`id`, `display`, `profiles_dir`, `bed_mm`, `nozzles`, `max_filaments`, `bed_type`, `machine`, `process`, `filament`, `slicer="bambu-studio"`) and a registry dict with `x2d-0.4` and `a1-0.4`.
2. `active_printer()`: `--printer` → `PRINT3D_PRINTER` → `x2d-0.4`; unknown id is an error with a fix. Keep `default_profiles_dir()` as a thin wrapper to keep the upstream diff small.
3. `dfm.py`: keep `X2D_BED_MM` as an alias; pipeline passes `bed_mm=printer.bed_mm`; message uses `printer.display`.
4. Colours: keep `NOZZLES` for upstream; pipeline uses `printer.nozzles` / `printer.max_filaments`. More than `max_filaments` → `error` with fix; more than `nozzles` → purge `note`. A1 with AMS lite: 1 nozzle, up to 4 colours.
5. `flatten_printer(printer, ...)`, with `flatten_x2d` kept as a wrapper. Add Linux sources (`~/.config/BambuStudio/system`, Flatpak `~/.var/app/com.bambulab.BambuStudio/config/BambuStudio/system`, extracted AppImage `resources/profiles`) and `--source`. Force `enable_support = 0`. Record the Studio version in provenance.
6. `find_studio()`: add Linux candidates (`/usr/bin/bambu-studio`, Flatpak export, AppImage).
7. Texts from `printer.display`: handoff header, MCP instructions, CLI help, `status` (also shows the active printer). `_cost_per_kg` reads the active printer's profiles.
8. Skill: short A1 section in `SKILL.md` and `parts-and-fits.md` (one nozzle, purge per colour change, bed size from the profile).
9. `setup.py`: optionally pass `-e KEY=VAL` to `claude mcp add`; otherwise document it in `docs/fork-local-setup.md`.
10. Tests: registry, selection via env and CLI, A1 bed check, colour logic with 1 nozzle (1 and 4 filaments), `flatten` against a small fixture BBL tree.

## Open until Bambu Studio is available

- Exact A1 machine/process/filament profile names (X2D filament names end in "0.4 nozzle"; check the A1 naming).
- A1 `printable_area` / `printable_height`.
- `enable_support` in the A1 process.
- Golden slice `cube_20mm_a1.gcode.3mf` (time, grams, layers).

## Likely upstream merge conflicts

`pipeline.py` (colour block), `handoff.py` (header), `cli.py` (parser), skill
texts. The wrapper approach keeps the rest small.
