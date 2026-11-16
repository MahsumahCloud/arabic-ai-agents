<p align="center"><b>English</b> · <a href="README.md">العربية</a></p>

# Lesson 01 exercise solutions

> Try the exercise yourself first. A solution teaches you more after you've made an attempt.

## Exercise 1: the minimum number of steps

Binary search halves the range on every step. A range of n numbers needs, in the worst case:

```text
ceil(log2(n + 1))   ->   n = 1000  ->  ceil(log2(1001)) = 10
```

The solution in [`ex1_min_steps.py`](ex1_min_steps.py) computes the value in theory, then tries every number from 1 to 1000 and measures the actual worst-case step count. Both values are 10.

## Exercise 2: a brief answer

The solution is in [`ex2_ask_brief.py`](ex2_ask_brief.py). Notice that it returns the stop reason along with the text, so the caller knows whether the answer is complete.

## Exercise 3: classify the tasks

| Task | Choice | Why |
|---|---|---|
| (a) Translate a tweet | Single call | One known step |
| (b) Find the cause of an unknown bug in a repository | Agent | You can't know in advance which files to inspect, and the tests reveal the bug |
| (c) A weekly report with fixed sections | Workflow | The steps are fixed, and the code knows what to fetch |
| (d) Answer from a long user manual, citing the page | Agent, or a search-then-answer workflow | If one search is enough, the workflow is simpler; if the question needs repeated searching, an agent fits better |
