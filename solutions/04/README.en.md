<p align="center"><b>English</b> · <a href="README.md">العربية</a></p>

# Lesson 04 exercise solutions

<img src="../../assets/mascot/thumbs-up.gif" alt="The course mascot giving a thumbs up" width="150" align="right">

## Exercise 1: add a requirement the right way

The order is the solution: spec first, then tasks, then the check, then the code.

**In the spec**, one line settles both questions before anyone guesses:

> - Requirement 7: the discount comes off the subtotal **before** VAT is computed; a discount larger than the subtotal, or negative, is refused.

Add an acceptance scenario with numbers: "given coffee at 15, cake at 22.5 and a discount of 7.5, the taxable amount is 30.00, VAT is 4.50 and the total is 34.50".

**In the task list**, at least two tasks, both pointing at the new requirement: one for the calculation and its scenario test, one for refusing a discount larger than the subtotal. Run `spec_check.py` before and after: before you add the tasks it reports the requirement as uncovered.

**The code** is in [`ex1_discount.py`](ex1_discount.py). It reuses `parse_amount` and `to_halala` from the lesson, so the discount accepts Arabic digits and a negative one is refused with the same message, without a single extra line.

## Exercise 2: catch the vague words

The solution is in [`ex2_vague_words.py`](ex2_vague_words.py). Three points:

1. **Diacritics** are removed before comparing, so a word with case endings still matches.
2. **Prefixes:** the word is tried as it is, then without a leading conjunction, preposition or definite article, as long as at least three letters remain, so short words are not turned into something else.
3. **The list itself is a decision.** No list is complete. Start short, and add every word that has caused a misunderstanding in your own project.

Try it on the example spec before it reached its final form: it contained the Arabic term for "QR code", literally "quick response code", which is not vague at all. The tool doesn't understand meaning; it suggests, and you decide. So we reworded that line and added a test that keeps the spec free of vague words.

## Exercise 3: a bug path on paper

There is no code solution. This is a model of what to write:

**Assess**

- **Symptom:** the input `طاولة=١٥٫٠٠٠` (a table) produces an item of 15.00 while the user meant fifteen thousand.
- **Reproduce:** `python lessons/04/vat_invoice.py "طاولة=١٥٫٠٠٠"`.
- **Cause:** not a calculation bug. The code does exactly what the spec says: `٫` is a decimal separator (requirement 1). The cause is **a gap in the spec**: it says nothing about an amount with more than two decimal places, which makes no sense in riyals, because the smallest unit is the halala.
- **Scope:** change requirement 1 so that any amount with more than two decimal places is refused with an Arabic message, and nothing else.

**Fix:** it starts in the spec, not in the code: "requirement 1: ... an amount with more than two decimal places is refused". Then the test that fails before the fix: `parse_amount("١٥٫٠٠٠")` must raise `ValueError`. Then the change in `parse_amount`.

**Test:** run the original command again. Does it now show a clear message instead of an invoice for 15.00? Do the other tests still pass? If so, the verdict is **verified**.

The lesson: half the bugs you see in code started as a missing sentence in the spec. Fix the sentence first, and the bug doesn't come back in the next feature.
