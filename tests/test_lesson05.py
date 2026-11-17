import json
import shutil

import pytest
from conftest import ROOT, load

loader = load("lessons/05/skill_loader.py")
finder = load("lessons/05/skill_finder.py")

LESSON = ROOT / "lessons/05"
CATALOG_ROOT = LESSON / "catalog"


def skill_md(name="demo", description="وصف تجريبي", body="# تعليمات\n1. خطوة"):
    return f"---\nname: {name}\ndescription: {description}\n---\n\n{body}\n"


# ---- what a skill is ----------------------------------------------------------

def test_parse_skill_reads_front_matter_and_body():
    skill = loader.parse_skill(skill_md(description='"وصف بين علامتي تنصيص"'))
    assert skill.name == "demo"
    assert skill.description == "وصف بين علامتي تنصيص"
    assert skill.body.startswith("# تعليمات")


@pytest.mark.parametrize(
    "text",
    [
        "name: demo\n",                                   # no opening ---
        "---\nname: demo\ndescription: x\n",               # never closed
        skill_md(name=""),                                 # no name
        skill_md(name="Demo_Skill"),                       # bad characters
        skill_md(name="a" * 65),                           # too long
        skill_md(name="../evil"),                          # path in the name
        skill_md(description=""),                          # no trigger at all
        skill_md(description="x" * 1025),                  # description too long
        skill_md(body=""),                                 # no instructions
        "---\nname demo\n---\nbody\n",                     # not key: value
    ],
)
def test_parse_skill_rejects_broken_files_in_arabic(text):
    with pytest.raises(loader.SkillError) as error:
        loader.parse_skill(text)
    assert any("؀" <= ch <= "ۿ" for ch in str(error.value))


def test_folder_name_must_match(tmp_path):
    folder = tmp_path / "other-name"
    folder.mkdir()
    (folder / "SKILL.md").write_text(skill_md(), encoding="utf-8")
    with pytest.raises(loader.SkillError):
        loader.read_skill(folder)


def test_every_catalogue_skill_and_our_finder_skill_are_valid():
    skills = loader.read_skills(CATALOG_ROOT / "skills")
    assert [s.name for s in skills] == [
        "arabic-text-cleanup", "csv-summary", "hijri-dates", "meeting-minutes", "speed-cleaner", "vat-invoice",
    ]
    ours = loader.read_skill(LESSON / "skill-finder")
    assert ours.name == "skill-finder"
    assert "موافقت" in ours.description  # the trigger says it installs only with consent


# ---- how the agent decides ----------------------------------------------------

def test_terms_normalize_arabic():
    assert loader.terms("التَّاريخ الهجريّ") == {"تاريخ", "هجري"}
    assert loader.terms("في هل من") == set()


@pytest.mark.parametrize(
    "request_text,expected",
    [
        ("حوّل التاريخ الهجري إلى ميلادي", "hijri-dates"),
        ("أريد فاتورة بالضريبة لهذه البنود", "vat-invoice"),
        ("اكتب محضر الاجتماع من هذه الملاحظات", "meeting-minutes"),
        ("ما عاصمة فرنسا؟", None),
    ],
)
def test_description_is_the_trigger(request_text, expected):
    skills = loader.read_skills(CATALOG_ROOT / "skills")
    chosen = loader.pick_skill(request_text, skills)
    assert (chosen.name if chosen else None) == expected


def test_a_skill_with_a_vague_description_is_never_picked():
    vague = loader.parse_skill(skill_md(name="helper", description="مهارة مفيدة"))
    assert loader.pick_skill("حوّل التاريخ الهجري", [vague]) is None


def test_only_descriptions_are_always_in_view():
    skills = loader.read_skills(CATALOG_ROOT / "skills")
    index = loader.index_lines(skills)
    assert all(s.name in index and s.description in index for s in skills)
    assert all(s.body not in index for s in skills)
    always, everything = loader.context_cost(skills)
    assert always < everything


def test_finder_skill_is_picked_for_a_new_capability():
    skills = loader.read_skills(CATALOG_ROOT / "skills") + [loader.read_skill(LESSON / "skill-finder")]
    chosen = loader.pick_skill("هل توجد مهارة تضيف قدرة جديدة؟ أريد تثبيت مهارة", skills)
    assert chosen.name == "skill-finder"


# ---- searching the catalogue ----------------------------------------------------

def test_search_ranks_the_matching_trusted_skill_first():
    result = finder.search(finder.load_catalog(), "حوّل تاريخاً هجرياً إلى ميلادي")
    assert result.recommended[0].entry.name == "hijri-dates"


def test_low_trust_skills_are_held_back_never_recommended():
    result = finder.search(finder.load_catalog(), "نظف الملفات وسرع الجهاز")
    assert result.recommended == []
    assert [m.entry.name for m in result.held_back] == ["speed-cleaner"]


def test_unrelated_query_finds_nothing():
    result = finder.search(finder.load_catalog(), "وصفة كبسة")
    assert result.recommended == [] and result.held_back == []


def test_trust_signals():
    def entry(installs, verified):
        return finder.Entry("x", "skills/x", "", (), installs, verified)

    assert finder.trust(entry(10_000, True)) == 1.0
    assert finder.trust(entry(0, False)) == 0.0
    assert finder.trust(entry(500, False)) < finder.trust(entry(500, True))
    assert finder.is_low_trust(entry(499, False))
    assert not finder.is_low_trust(entry(500, False))
    assert not finder.is_low_trust(entry(0, True))


def test_trust_breaks_ties_between_equally_relevant_skills(tmp_path):
    entries = [
        finder.Entry("a-notes", "skills/a", "ملاحظات الاجتماع", (), 600, False),
        finder.Entry("b-notes", "skills/b", "ملاحظات الاجتماع", (), 5000, True),
    ]
    result = finder.search(entries, "ملاحظات الاجتماع")
    assert [m.entry.name for m in result.recommended] == ["b-notes", "a-notes"]


def test_catalogue_rejects_bad_install_counts(tmp_path):
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps({"skills": [{"name": "x", "path": "skills/x", "installs": "many"}]}))
    with pytest.raises(ValueError):
        finder.load_catalog(path)
    path.write_text(json.dumps({"skills": [{"name": "x", "path": "skills/x", "verified": "yes"}]}))
    assert finder.load_catalog(path)[0].verified is False  # only a real true counts


# ---- installing ---------------------------------------------------------------------

def entry_named(name):
    return finder.find(finder.load_catalog(), name)


def test_install_copies_after_yes(tmp_path):
    seen = []
    target = finder.install(entry_named("hijri-dates"), CATALOG_ROOT, tmp_path / "skills",
                            lambda text: seen.append(text) or True)
    assert target == (tmp_path / "skills" / "hijri-dates").resolve()
    assert (target / "SKILL.md").read_text(encoding="utf-8").startswith("---\nname: hijri-dates")
    assert "hijri-dates" in seen[0] and "SKILL.md" in seen[0]


@pytest.mark.parametrize("answer", [False, None, "yes", 1])
def test_anything_but_a_real_yes_copies_nothing(tmp_path, answer):
    assert finder.install(entry_named("vat-invoice"), CATALOG_ROOT, tmp_path, lambda _: answer) is None
    assert not (tmp_path / "vat-invoice").exists()


def test_low_trust_is_refused_before_asking(tmp_path):
    asked = []
    with pytest.raises(finder.InstallError):
        finder.install(entry_named("speed-cleaner"), CATALOG_ROOT, tmp_path, lambda t: asked.append(t) or True)
    assert asked == [] and not any(tmp_path.iterdir())


def test_preview_warns_about_scripts_and_broad_triggers():
    text = finder.preview(entry_named("speed-cleaner"), CATALOG_ROOT / "skills/speed-cleaner")
    assert "scripts/clean.sh" in text
    assert text.count("تنبيه") == 2
    clean = finder.preview(entry_named("hijri-dates"), CATALOG_ROOT / "skills/hijri-dates")
    assert "تنبيه" not in clean


def make_catalog(tmp_path, name="good-skill"):
    root = tmp_path / "catalog"
    folder = root / "skills" / name
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(skill_md(name=name), encoding="utf-8")
    return root


def trusted(name, path):
    return finder.Entry(name, path, "", (), 1000, True)


@pytest.mark.parametrize("path", ["../outside", "skills/../../outside", "/etc", "."])
def test_paths_that_escape_the_catalogue_are_refused(tmp_path, path):
    root = make_catalog(tmp_path)
    (tmp_path / "outside").mkdir()
    (tmp_path / "outside" / "SKILL.md").write_text(skill_md(name="good-skill"), encoding="utf-8")
    with pytest.raises(finder.InstallError):
        finder.install(trusted("good-skill", path), root, tmp_path / "skills", lambda _: True)
    assert not (tmp_path / "skills").exists()


@pytest.mark.parametrize("name", ["../evil", "a/b", "Good", ""])
def test_bad_names_are_refused(tmp_path, name):
    root = make_catalog(tmp_path)
    with pytest.raises(finder.InstallError):
        finder.install(trusted(name, "skills/good-skill"), root, tmp_path / "skills", lambda _: True)


def test_name_mismatch_symlink_and_existing_target_are_refused(tmp_path):
    root = make_catalog(tmp_path)
    with pytest.raises(finder.InstallError):  # catalogue name differs from the folder's SKILL.md
        finder.install(trusted("other-skill", "skills/good-skill"), root, tmp_path / "skills", lambda _: True)

    secret = tmp_path / "secret.txt"
    secret.write_text("x")
    link = root / "skills" / "good-skill" / "link.txt"
    link.symlink_to(secret)
    with pytest.raises(finder.InstallError):
        finder.install(trusted("good-skill", "skills/good-skill"), root, tmp_path / "skills", lambda _: True)
    link.unlink()

    skills = tmp_path / "skills"
    assert finder.install(trusted("good-skill", "skills/good-skill"), root, skills, lambda _: True)
    with pytest.raises(finder.InstallError):  # never overwrite an installed skill
        finder.install(trusted("good-skill", "skills/good-skill"), root, skills, lambda _: True)


def test_installed_skill_is_picked_on_the_next_request(tmp_path):
    skills_dir = tmp_path / "skills"
    assert loader.pick_skill("حوّل التاريخ الهجري", loader.read_skills(skills_dir)) is None
    finder.install(entry_named("hijri-dates"), CATALOG_ROOT, skills_dir, lambda _: True)
    assert loader.pick_skill("حوّل التاريخ الهجري", loader.read_skills(skills_dir)).name == "hijri-dates"


def test_finder_never_runs_code():
    source = (LESSON / "skill_finder.py").read_text(encoding="utf-8")
    for forbidden in ("subprocess", "os.system", "exec(", "eval(", "import os"):
        assert forbidden not in source


# ---- command line -----------------------------------------------------------------------

def test_cli_search(capsys):
    assert finder.main(["فاتورة", "ضريبة"]) == 0
    out = capsys.readouterr().out
    assert "1. vat-invoice" in out


def test_cli_install_asks_and_respects_no(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "لا")
    assert finder.main(["--install", "hijri-dates", "--to", str(tmp_path)]) == 0
    assert "cancelled" in capsys.readouterr().out and not (tmp_path / "hijri-dates").exists()
    monkeypatch.setattr("builtins.input", lambda _: "نعم")
    assert finder.main(["--install", "hijri-dates", "--to", str(tmp_path)]) == 0
    assert (tmp_path / "hijri-dates" / "SKILL.md").exists()
    assert finder.main(["--install", "speed-cleaner", "--to", str(tmp_path)]) == 1
    assert finder.main(["--install", "missing", "--to", str(tmp_path)]) == 1
    assert finder.main(["--install", "hijri-dates"]) == 2


def test_loader_cli(capsys):
    assert loader.main(["اكتب محضر الاجتماع من هذه الملاحظات"]) == 0
    assert "loaded: meeting-minutes" in capsys.readouterr().out
    assert loader.main(["ما عاصمة فرنسا"]) == 1
