import json
from pathlib import Path

import pytest
from conftest import ascii_stl_cube

from print3d import cli
from print3d.dfm import check_mesh
from print3d.flatten import flatten_printer
from print3d.paths import default_profiles_dir
from print3d.pipeline import colour_advice
from print3d.printers import (
    PRINTER_ENV,
    PRINTERS,
    Printer,
    PrinterError,
    active_printer,
    get_printer,
)


def test_default_is_x2d(monkeypatch):
    monkeypatch.delenv(PRINTER_ENV, raising=False)
    assert active_printer().id == "x2d-0.4"
    assert default_profiles_dir().name == "x2d-0.4"


def test_env_selects_a1(monkeypatch):
    monkeypatch.setenv(PRINTER_ENV, "a1-0.4")
    printer = active_printer()
    assert printer.display == "Bambu Lab A1"
    assert printer.bed_mm == (256.0, 256.0, 256.0)
    assert default_profiles_dir().name == "a1-0.4"


def test_unknown_printer_names_the_fix(monkeypatch):
    monkeypatch.setenv(PRINTER_ENV, "ender3")
    with pytest.raises(PrinterError, match="a1-0.4"):
        active_printer()


@pytest.mark.parametrize("printer", PRINTERS.values(), ids=list(PRINTERS))
def test_pinned_profiles_match_the_registry(printer: Printer):
    folder = printer.profiles_dir
    machine = json.loads((folder / "machine.json").read_text(encoding="utf-8"))
    process = json.loads((folder / "process.json").read_text(encoding="utf-8"))
    filament = json.loads((folder / "filament.json").read_text(encoding="utf-8"))
    assert machine["name"] == printer.machine
    assert process["name"] == printer.process
    assert filament["name"] == printer.filament
    assert process["enable_support"] == "0"
    assert len(machine["nozzle_diameter"]) == printer.nozzles
    xs = [float(p.split("x")[0]) for p in machine["printable_area"]]
    ys = [float(p.split("x")[1]) for p in machine["printable_area"]]
    assert (max(xs) - min(xs), max(ys) - min(ys)) == printer.bed_mm[:2]
    # The DFM check stays at or under the profile's height.
    assert printer.bed_mm[2] <= float(machine["printable_height"])


def test_a1_bed_is_lower_than_x2d(tmp_path: Path):
    path = tmp_path / "tall.stl"
    path.write_text(ascii_stl_cube(258), encoding="ascii")  # fits 260 mm, not 256 mm
    a1 = get_printer("a1-0.4")
    report = check_mesh(path, bed_mm=(300.0, 300.0, a1.bed_mm[2]), printer=a1.display)
    assert not report.ok
    assert any("Bambu Lab A1 bed" in error for error in report.errors)
    assert check_mesh(path, bed_mm=(300.0, 300.0, 260.0)).ok


def test_colours_on_one_nozzle():
    a1 = get_printer("a1-0.4")
    assert colour_advice(1, a1) == []
    [note] = colour_advice(4, a1)
    assert note.severity == "note"
    assert "one nozzle" in note.message
    [error] = colour_advice(5, a1)
    assert error.severity == "error"
    assert "at most 4" in error.message


def test_colours_on_two_nozzles():
    x2d = get_printer("x2d-0.4")
    assert colour_advice(2, x2d) == []
    [note] = colour_advice(3, x2d)
    assert note.severity == "note"


def test_flatten_printer_into_a_folder(tmp_path: Path):
    root = tmp_path / "profiles"
    for kind, data in {
        "machine": {"name": "M", "type": "machine", "nozzle_diameter": ["0.4"], "printer_model": "PM"},
        "process": {"name": "P", "type": "process", "enable_support": "1"},
        "filament": {"name": "F", "type": "filament"},
    }.items():
        (root / "BBL" / kind).mkdir(parents=True)
        (root / "BBL" / kind / f"{data['name']}.json").write_text(json.dumps(data), encoding="utf-8")
    (root / "BBL.json").write_text('{"name":"Bambu Lab","version":"01.02.03.04"}', encoding="utf-8")
    printer = Printer(
        id="test", display="Test", bed_mm=(100.0, 100.0, 100.0), nozzles=1, max_filaments=1,
        bed_type="Textured PEI Plate", machine="M", process="P", filament="F",
    )
    out = tmp_path / "out"
    result = flatten_printer(printer, output_dir=out, profiles_root=root)
    assert result["provenance"]["profiles_version"] == "01.02.03.04"
    process = json.loads((out / "process.json").read_text(encoding="utf-8"))
    assert process["enable_support"] == "0"
    assert process["curr_bed_type"] == "Textured PEI Plate"
    assert "M" in process["compatible_printers"]


def test_cli_printer_flag_sets_env(monkeypatch, capsys):
    # Set first so monkeypatch restores it after cli.main overwrites it.
    monkeypatch.setenv(PRINTER_ENV, "x2d-0.4")
    monkeypatch.setattr(cli, "find_studio", lambda: Path("/bin/true"))
    assert cli.main(["--printer", "a1-0.4", "status"]) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["printer"] == "a1-0.4"
    assert status["profiles_present"]
    assert status["bed_mm"] == [256.0, 256.0, 256.0]
