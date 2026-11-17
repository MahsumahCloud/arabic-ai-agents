<p align="center"><b>English</b> · <a href="README.md">العربية</a></p>

# Lesson 05 exercise solutions

<img src="../../assets/mascot/thumbs-up.gif" alt="The course mascot giving a thumbs up" width="150" align="right">

## Exercise 1: an old skill earns less trust

The solution is in [`ex1_freshness.py`](ex1_freshness.py). Three points:

1. **Leave the original function alone:** `fresh_trust` takes the lesson's `trust` result and halves it when the last update is more than 365 days old. Trust keeps a single definition.
2. **A date in the future is a data error,** so it is refused with a message, not treated as "very recent".
3. **Old unverified skills are held back** even with many installs: many installs long ago don't mean it still works. Old verified skills stay, ranked lower.

## Exercise 2: read the scripts before anyone runs them

The solution is in [`ex2_audit_scripts.py`](ex2_audit_scripts.py). `audit` opens every file as text and looks for signs worth a human look: forced deletion, downloads, piping a command's output into an interpreter, running text as code, encoded text, asking for admin rights, and reading keys. It runs nothing and imports nothing.

Try it on `speed-cleaner`: it finds nothing, because its script only prints. Yet it is the most dangerous skill in the catalogue, because the danger is in its **instructions**: run immediately, without asking the user. That is why the lesson also checks the text of SKILL.md itself, and why a clean report doesn't prove a skill is safe.

## Exercise 3: rewrite a description that doesn't work

There is no separate code solution; the test `test_rewritten_description_triggers_the_skill` in `tests/test_solutions.py` proves the idea. A description like "a useful skill" says neither what the skill does nor when to use it, so the agent never picks it. A good description is two sentences: the first says **what it does**, the second says **when to use it**, in words users actually type. The test uses an Arabic description written that way.

---

<p align="center"><a href="../../docs/en/05-agent-skills/README.md">Back to Lesson 05</a></p>
