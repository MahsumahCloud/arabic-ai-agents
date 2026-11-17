from decimal import Decimal as D

import pytest
from conftest import ROOT, load

vat = load("lessons/04/vat_invoice.py")
spec = load("lessons/04/spec_check.py")

EXAMPLE = ROOT / "lessons/04/example"


# ---- the feature built from the spec (one test per requirement) -------------

@pytest.mark.parametrize(
    "text,expected",
    [("١٥", "15"), ("22.5", "22.5"), ("٢٢٫٥", "22.5"), ("1,250", "1250"), ("١٬٢٥٠٫٧٥", "1250.75"), (" 0 ", "0")],
)
def test_r1_parse_amount_accepts_arabic_and_latin_digits(text, expected):
    assert vat.parse_amount(text) == D(expected)


@pytest.mark.parametrize("text", ["", "   ", "-٥", "abc", "NaN", "Infinity", "1.2.3"])
def test_r6_parse_amount_rejects_bad_input_in_arabic(text):
    with pytest.raises(ValueError) as error:
        vat.parse_amount(text)
    assert any("؀" <= ch <= "ۿ" for ch in str(error.value))


def test_r1_r6_parse_line():
    assert vat.parse_line("قهوة=١٥") == vat.Line("قهوة", D("15"))
    for bad in ["قهوة ١٥", "=١٥", "قهوة="]:
        with pytest.raises(ValueError):
            vat.parse_line(bad)


def test_r2_r3_vat_on_subtotal_rounded_half_up():
    result = vat.totals([vat.Line("قهوة", D("15")), vat.Line("كعكة", D("22.5"))])
    assert (result.subtotal, result.vat, result.total) == (D("37.50"), D("5.63"), D("43.13"))


def test_r2_vat_is_computed_once_not_per_line():
    # three lines of 0.10: per-line VAT would be 3 x 0.02 = 0.06; on the subtotal it is 0.05
    result = vat.totals([vat.Line(str(i), D("0.10")) for i in range(3)])
    assert result.vat == D("0.05")


def test_r3_rounding():
    assert vat.to_halala(D("0.005")) == D("0.01")
    assert vat.to_halala(D("0.004")) == D("0.00")


def test_r4_split_inclusive_always_adds_up():
    assert vat.split_inclusive(D("115")) == vat.Totals(D("100.00"), D("15.00"), D("115.00"))
    assert vat.split_inclusive(D("10")) == vat.Totals(D("8.70"), D("1.30"), D("10.00"))
    for cents in range(1, 100_001, 7):
        total = D(cents) / 100
        part = vat.split_inclusive(total)
        assert part.subtotal + part.vat == total


def test_r5_render_in_arabic_with_riyal_sign():
    text = vat.render([vat.Line("قهوة", D("1250"))])
    assert "قهوة: 1,250.00 " + vat.RIYAL_SIGN in text
    assert "الإجمالي: 1,437.50 " + vat.RIYAL_SIGN in text
    assert vat.RIYAL_SIGN == "⃁"


def test_r6_cli_prints_arabic_error_and_no_invoice(capsys):
    assert vat.main(["شاي=-٥"]) == 1
    out, err = capsys.readouterr()
    assert out == "" and "سالب" in err
    assert vat.main(["قهوة=١٥"]) == 0


def test_no_float_in_money_code():
    source = (ROOT / "lessons/04/vat_invoice.py").read_text(encoding="utf-8")
    assert "float(" not in source  # constitution, principle 1


# ---- reading the spec before building ---------------------------------------

def test_example_folder_is_ready_and_done():
    report = spec.check_folder(EXAMPLE)
    assert report.requirements == [f"م-{n}" for n in range(1, 7)]
    assert len(report.tasks) == 8
    assert report.ready_to_build and report.done


def test_example_has_the_five_files():
    for name in ["constitution.md", "spec.md", "plan.md", "tasks.md"]:
        assert (EXAMPLE / name).read_text(encoding="utf-8").strip()


SPEC = """
- م-1: الأول
- **م-2**: الثاني
- م-3: الثالث [يحتاج توضيحاً]
"""

TASKS = """
- [x] ت-1 (م-1): أنجزت
- [ ] ت-2 (م-1، م-9): تشير إلى متطلب غير موجود
- [ ] ت-3: بلا متطلب
"""


def test_check_finds_every_gap():
    report = spec.check(SPEC, TASKS)
    assert report.requirements == ["م-1", "م-2", "م-3"]
    assert report.uncovered == ["م-2", "م-3"]
    assert report.unknown_refs == [("ت-2", "م-9")]
    assert report.orphan_tasks == ["ت-3"]
    assert [n for n, _ in report.open_questions] == [4]
    assert report.unchecked == ["ت-2", "ت-3"]
    assert not report.ready_to_build and not report.done


def test_ready_but_not_done():
    report = spec.check("- م-1: واحد\n", "- [ ] ت-1 (م-1): لم تُنجز\n")
    assert report.ready_to_build and not report.done


def test_empty_spec_is_never_ready():
    assert not spec.check("", "").ready_to_build


@pytest.mark.parametrize(
    "answers,decision",
    [
        ({k: True for k in spec.ASSESS_QUESTIONS}, "go"),
        ({**{k: True for k in spec.ASSESS_QUESTIONS}, "can_measure": None}, "clarify"),
        ({"real_problem": True}, "clarify"),
        ({**{k: True for k in spec.ASSESS_QUESTIONS}, "worth_cost": False}, "stop"),
        ({"real_problem": False}, "stop"),
    ],
)
def test_assess(answers, decision):
    assert spec.assess(answers) == decision


def test_spec_check_cli(capsys):
    assert spec.main([str(EXAMPLE)]) == 0
    assert "ready to build: yes" in capsys.readouterr().out
