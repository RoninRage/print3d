"""The printers print3d knows, and which one is active.

Pick one with `--printer` on the CLI or `PRINT3D_PRINTER` in the environment.
The default is the X2D, so nothing changes for existing setups.
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PRINTER_ENV = "PRINT3D_PRINTER"
DEFAULT_PRINTER = "x2d-0.4"
PROFILES = Path(__file__).resolve().parent / "profiles"


@dataclass(frozen=True)
class Printer:
    id: str
    display: str
    bed_mm: tuple[float, float, float]
    # Colours that print without a filament change.
    nozzles: int
    # Colours one job may use at all (AMS slots).
    max_filaments: int
    bed_type: str
    machine: str
    process: str
    filament: str

    @property
    def profiles_dir(self) -> Path:
        return PROFILES / self.id

    def as_dict(self) -> dict[str, Any]:
        return {**asdict(self), "profiles_dir": str(self.profiles_dir)}


PRINTERS: dict[str, Printer] = {
    p.id: p
    for p in (
        Printer(
            id="x2d-0.4",
            display="Bambu Lab X2D",
            bed_mm=(256.0, 256.0, 260.0),
            nozzles=2,
            max_filaments=16,
            bed_type="Textured PEI Plate",
            machine="Bambu Lab X2D 0.4 nozzle",
            process="0.20mm Standard @BBL X2D",
            filament="Bambu PLA Basic @BBL X2D 0.4 nozzle",
        ),
        Printer(
            id="a1-0.4",
            display="Bambu Lab A1",
            bed_mm=(256.0, 256.0, 256.0),
            nozzles=1,
            max_filaments=4,
            bed_type="Textured PEI Plate",
            machine="Bambu Lab A1 0.4 nozzle",
            process="0.20mm Standard @BBL A1",
            filament="Bambu PLA Basic @BBL A1",
        ),
    )
}


class PrinterError(ValueError):
    """Raised for a printer id print3d does not know."""


def get_printer(printer_id: str) -> Printer:
    key = printer_id.strip().lower()
    if key not in PRINTERS:
        raise PrinterError(
            f"Unknown printer {printer_id!r}. Use one of: {', '.join(PRINTERS)} "
            f"(--printer or {PRINTER_ENV})."
        )
    return PRINTERS[key]


def active_printer() -> Printer:
    """`$PRINT3D_PRINTER`, else the X2D."""
    return get_printer(os.environ.get(PRINTER_ENV, "").strip() or DEFAULT_PRINTER)
