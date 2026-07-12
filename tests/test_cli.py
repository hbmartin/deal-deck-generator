"""Tests for command-line orchestration and failure reporting."""

from pathlib import Path
from types import SimpleNamespace

from src import cli, goldens
from src.compare import contact_sheet
from src.raster import base as raster_base
from src.raster import fontsetup
from src.svg.cards import base as card_base


def test_cmd_render_lists_themes(monkeypatch, capsys):
    monkeypatch.setattr(cli, "available_themes", lambda: ["chicago", "classic"])

    assert cli.cmd_render(SimpleNamespace(list_themes=True)) == 0
    assert capsys.readouterr().out == "chicago\nclassic\n"


def test_cmd_render_reports_unknown_theme(monkeypatch, capsys):
    def reject_theme(_name: str) -> Path:
        raise ValueError("unknown theme 'missing'")

    monkeypatch.setattr(cli, "theme_cards_path", reject_theme)

    assert cli.cmd_render(SimpleNamespace(list_themes=False, theme="missing")) == 2
    assert "unknown theme 'missing'" in capsys.readouterr().err


def test_cmd_render_passes_filters_to_pipeline(monkeypatch, tmp_path, capsys):
    deck = object()
    tokens = object()
    cards_path = tmp_path / "cards.yaml"
    calls = {}

    monkeypatch.setattr(cli, "theme_cards_path", lambda _name: cards_path)
    monkeypatch.setattr(cli, "load_deck", lambda _path: deck)
    monkeypatch.setattr(cli, "load_theme_tokens", lambda _name: tokens)

    def fake_render_deck(deck_arg, out_arg, **kwargs) -> dict:
        calls.update(deck=deck_arg, out=out_arg, **kwargs)
        return {"cards": {"one": {}}, "total_physical_cards": 2}

    monkeypatch.setattr(cli, "render_deck", fake_render_deck)
    args = SimpleNamespace(
        list_themes=False,
        theme="classic",
        out=tmp_path / "rendered",
        types=["money"],
        cards=["money-1m"],
        renderer="inkscape",
        fonts="bundled",
        no_previews=True,
    )

    assert cli.cmd_render(args) == 0
    assert calls == {
        "deck": deck,
        "out": args.out,
        "types": ["money"],
        "card_ids": ["money-1m"],
        "renderer": "inkscape",
        "fonts_mode": "bundled",
        "previews": False,
        "tokens": tokens,
    }
    assert "rendered 1 designs (2 physical cards)" in capsys.readouterr().out


class BlankDocument:
    def to_bytes(self) -> bytes:
        return b"<svg />"


class FakeRasterizer:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error

    def rasterize(self, *_args) -> None:
        if self.error is not None:
            raise self.error


def _patch_smoke_dependencies(monkeypatch, tmp_path, failures) -> None:
    monkeypatch.setattr(card_base, "blank_card", BlankDocument)
    monkeypatch.setattr(
        fontsetup,
        "write_fonts_conf",
        lambda _out, _fonts: tmp_path / "fonts.conf",
    )
    monkeypatch.setattr(
        raster_base,
        "get_rasterizer",
        lambda name: FakeRasterizer(failures.get(name)),
    )


def test_cmd_smoke_allows_optional_inkscape_failure(monkeypatch, tmp_path, capsys):
    _patch_smoke_dependencies(
        monkeypatch,
        tmp_path,
        {"inkscape": RuntimeError("not installed")},
    )

    assert cli.cmd_smoke(SimpleNamespace(out=tmp_path, fonts="bundled")) == 0
    captured = capsys.readouterr().out
    assert "ok:" in captured
    assert "warn: optional rasterizer inkscape unavailable" in captured
    assert (tmp_path / "smoke" / "blank.svg").read_bytes() == b"<svg />"


def test_cmd_smoke_fails_when_rsvg_fails(monkeypatch, tmp_path, capsys):
    _patch_smoke_dependencies(
        monkeypatch,
        tmp_path,
        {"rsvg": RuntimeError("broken")},
    )

    assert cli.cmd_smoke(SimpleNamespace(out=tmp_path, fonts="system")) == 1
    assert "FAIL rsvg: broken" in capsys.readouterr().out


def test_cmd_compare_prints_generated_sheets(monkeypatch, tmp_path, capsys):
    sheets = [tmp_path / "compare" / "compare-money.png"]
    monkeypatch.setattr(contact_sheet, "build_contact_sheets", lambda **_kwargs: sheets)

    args = SimpleNamespace(out=tmp_path, types=["money"])
    assert cli.cmd_compare(args) == 0
    assert capsys.readouterr().out == f"sheet: {sheets[0]}\n"


def test_cmd_goldens_requires_update(monkeypatch, capsys):
    args = SimpleNamespace(update=False, env=None, renderer="rsvg")

    assert cli.cmd_goldens(args) == 2
    assert "nothing to do" in capsys.readouterr().err


def test_cmd_goldens_updates_selected_environment(monkeypatch, capsys):
    monkeypatch.setattr(goldens, "update_goldens", lambda **_kwargs: "ci")
    args = SimpleNamespace(update=True, env="ci", renderer="inkscape")

    assert cli.cmd_goldens(args) == 0
    assert capsys.readouterr().out == "updated goldens for env 'ci'\n"


def test_main_builds_parser_and_dispatches(monkeypatch, capsys):
    monkeypatch.setattr(cli, "available_themes", lambda: ["classic"])

    assert cli.main(["render", "--list-themes"]) == 0
    assert capsys.readouterr().out == "classic\n"
