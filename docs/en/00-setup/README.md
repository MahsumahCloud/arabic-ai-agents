<p align="center"><b>English</b> · <a href="../../00-setup/README.md">العربية</a></p>

<p align="center"><img src="../../../assets/headers/lesson-00-en.svg" alt="Lesson 00: Setting up your workspace" width="100%"></p>

<p align="center"><img src="../../../assets/mascot/welcome-hand-on-chest.gif" alt="The course mascot, hand on chest in welcome" width="170"></p>

# Lesson 00: Setting up your workspace

> [!NOTE]
> **What you'll learn**
>
> - Install Python and the official Anthropic library in a virtual environment.
> - Keep your API key in an environment variable, never in your code.
> - Understand how cost is calculated, and how to set limits for yourself.
> - Run the course tests with no key and no internet connection.
>
> **Time:** about 20 minutes · **You'll leave with:** a working Python environment, an API key stored safely, and a clear picture of cost and risk before you write your first agent.

## Run it

<img src="../../../assets/mascot/coding.gif" alt="The course mascot typing on a laptop" width="150" align="right">

```console
$ python3 -m venv .venv && source .venv/bin/activate
$ pip install -r requirements-dev.txt
$ python -m pytest                      # offline, no API key
$ python lessons/00/check_setup.py      # tells you if the key is set, never prints it
```

## 1. Requirements

| Requirement | Details |
|---|---|
| Python | 3.10 or newer. Version 1.x of the `anthropic` library requires it. |
| A terminal | Any terminal: Terminal on macOS, PowerShell on Windows, or a Linux shell. |
| A developer account | An account on the Claude developer platform (platform.claude.com) to create an API key. You don't need it to run the tests. |

Check your Python version:

```bash
python3 --version
```

## 2. Virtual environment and dependencies

A virtual environment is an isolated folder that holds this project's libraries only, so they never clash with your other projects. Run these commands from the repository root:

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
py -m venv .venv
.venv\Scripts\Activate.ps1

# both
pip install -r requirements-dev.txt
```

`requirements-dev.txt` installs the `anthropic` library (version 1.x) and `pytest` for the tests.

## 3. The API key: keep it in the environment, not in the code

An API key works like a password: whoever holds it can spend your credit.

> [!WARNING]
> **The rule in this course, no exceptions:** the key is never written in any code file and never pushed to any repository.

The official library reads the key automatically from the `ANTHROPIC_API_KEY` environment variable, so your code never needs to mention it:

```bash
# macOS / Linux (current terminal session only)
export ANTHROPIC_API_KEY="paste-your-key-here"

# Windows PowerShell (current session only)
$env:ANTHROPIC_API_KEY = "paste-your-key-here"
```

Then check that everything is ready. This script tells you whether the key is present without printing it:

```bash
python lessons/00/check_setup.py
```

> [!TIP]
> **Alternative:** if you install the official `ant` command-line tool and sign in with `ant auth login`, the library reads the saved profile automatically, with no environment variable.

### Rules for protecting your key

1. Don't write it in code, or in config files that get pushed to Git. `.env` is listed in `.gitignore`, and `.env.example` is only an empty template.
2. Don't paste it into a chat, a screenshot, or a forum question.
3. Create a separate key for each project, so you can revoke one without breaking the rest.
4. If the key leaks, revoke it immediately in the console and create a new one. Removing it from Git history is not enough, because old copies may already have been cloned somewhere else.
5. Set a spending limit on the Limits page of the console before you experiment with loops.

## 4. Cost: how is it calculated?

Cost is measured in tokens. A token is a piece of text: a word, or part of one. There are two prices: one for input tokens (what you send), and a higher one for output tokens (what the model generates).

Published Claude API prices in November 2026, in US dollars per million tokens:

| Model | Model ID | Input | Output |
|---|---|---|---|
| Claude Opus 5.5 | `claude-opus-5-5` | 4.00 | 20.00 |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | 2.00 | 10.00 |
| Claude Haiku 5.5 | `claude-haiku-5-5` | 0.10 | 0.50 |

> [!IMPORTANT]
> Prices change. Check the official pricing page before any serious estimate. The Haiku 5.5 price above applies to requests of up to 100 thousand input tokens.

**Three facts that shape your bill:**

1. **Thinking tokens are billed as output.** Modern models think before they answer, and those tokens are charged at the output price even when you never see them as text. That's why the lessons set the effort level to `low` for experiments.
2. **A loop resends the whole conversation on every step.** An agent that takes 5 steps sends the growing history 5 times. That is what makes a step limit and a cost budget a necessity, not a luxury (Lesson 03).
3. **The token count of Arabic text can differ from English** for the same meaning. Don't guess: the `count_tokens` endpoint counts tokens before you send anything.

**A worked example** (made-up numbers, not a real measurement): a Lesson 02 run with 3 requests, each about 1,500 input tokens and 300 output tokens on Opus 5.5:

```text
input:  3 x 1,500 = 4,500 tokens  x $4  / 1,000,000 = $0.018
output: 3 x   300 =   900 tokens  x $20 / 1,000,000 = $0.018
total ≈ $0.036
```

### Choosing the model and the effort level

The lessons use `claude-opus-5-5` by default, and you can switch without touching the code:

```bash
export AGENT_MODEL="claude-sonnet-5-5"   # model id
export AGENT_EFFORT="low"                # low | medium | high | xhigh | max
```

## 5. Safety notes before you start

An agent is not just a chat; it is a program that **takes actions**. So:

- **Run tools in a sandbox.** The file tools in this course can only reach one specific folder.
- **Grant the least privilege that works.** Never give an experimental agent the power to delete, send, or pay.
- **Make dangerous actions require human approval.** You'll build that yourself in Lesson 02.
- **Don't experiment on real data or production systems.** Use the sample files that ship with the course.
- **Tool output is data, not instructions.** Text an agent reads from a file may contain planted instructions (prompt injection). We deal with that in Lesson 03.

## 6. Running the tests (no key, no internet)

Every example in the course has a test that uses a mock client returning pre-written responses, so no real request is ever sent:

```bash
python -m pytest
```

If the tests pass, your environment is ready. To see how an agent can be tested without a real model, read `tests/fakes.py`.

## Common mistakes

<img src="../../../assets/mascot/tip.gif" alt="The course mascot giving a tip" width="150" align="right">

| Mistake | What happens | Do this instead |
|---|---|---|
| Writing the key inside `client = anthropic.Anthropic(api_key="...")` | It leaks with your first push | Call `anthropic.Anthropic()` with no arguments and let the library read the environment |
| Installing packages outside the virtual environment | Version clashes between projects | Activate `.venv` before `pip install` |
| Using Python 3.9 or older | Installing `anthropic` 1.x fails | Upgrade to 3.10 or newer |
| Exporting the variable in one terminal and running the code in another | `ANTHROPIC_API_KEY is not set` | An `export` only lives in the current session |

## Check yourself

<img src="../../../assets/mascot/thinking.gif" alt="The course mascot thinking" width="150" align="right">

1. Where should your API key be stored?
2. Why can an agent cost far more than a single question?
3. Are thinking tokens billed?
4. What do you do if you accidentally push your key to a public repository?

<details>
<summary><b>Answers</b></summary>

1. In the `ANTHROPIC_API_KEY` environment variable (or an `ant` profile), never in a code file.
2. Because the loop resends the growing conversation on every step, and every step generates output and thinking tokens.
3. Yes, at the output price, even when they don't appear as text.
4. Revoke it immediately in the console and create a new key. Removing it from Git history alone is not enough.

</details>

## Key terms

Virtual Environment · Environment Variable · API Key · Token · Effort · Sandbox · Least Privilege · Prompt Injection · Mock Client

Full definitions in the [glossary](../glossary.md).


<p align="center"><img src="../../../assets/mascot/celebrate.gif" alt="The course mascot celebrating the end of the lesson" width="170"></p>

---

<p align="center"><a href="../../../README.en.md#course-map">Course map</a> · <b>Next:</b> <a href="../01-what-is-an-agent/README.md">Lesson 01: What is an agent?</a></p>
