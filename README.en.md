<p align="center"><b>English</b> · <a href="README.md">العربية</a></p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-en-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/banner-en-light.svg">
    <img src="assets/banner-en-dark.svg" alt="AI Agents in Arabic: from zero to production. A terminal runs the research assistant: a plan, then tool calls, then an answer with its source" width="100%">
  </picture>
</p>

<h1 align="center">AI Agents in Arabic: from zero to production</h1>

<p align="center"><b>Learn to build AI agents step by step, with runnable code and tests that pass without an API key.</b></p>

<p align="center"><sub>An original course written in Arabic, with a complete English edition of every lesson.</sub></p>

<p align="center">
  <img alt="Python 3.10+" src="https://img.shields.io/badge/Python-3.10%2B-22D3EE?style=for-the-badge&logo=python&logoColor=white&labelColor=0B1020">
  <img alt="Tests run offline, no API key" src="https://img.shields.io/badge/tests-offline%20%C2%B7%20no%20API%20key-34D399?style=for-the-badge&logo=pytest&logoColor=white&labelColor=0B1020">
  <img alt="Lessons: 4 of 12" src="https://img.shields.io/badge/lessons-4%20of%2012-A78BFA?style=for-the-badge&labelColor=0B1020">
  <img alt="Code: MIT" src="https://img.shields.io/badge/code-MIT-8B5CF6?style=for-the-badge&labelColor=0B1020">
  <img alt="Content: CC BY 4.0" src="https://img.shields.io/badge/content-CC%20BY%204.0-6366F1?style=for-the-badge&labelColor=0B1020">
</p>

<p align="center"><a href="docs/en/00-setup/README.md"><b>Start Lesson 00</b></a> · <a href="#course-map">Course map</a> · <a href="docs/en/glossary.md">Glossary</a> · <a href="README.md">النسخة العربية</a></p>

## What makes this course different

There are plenty of agent courses, and almost all of them are in English, built on English text. This one is Arabic-first, built on the problems Arabic itself raises:

<table>
<tr>
<td width="33%" valign="top"><img src="assets/icons/research.svg" width="36" height="36" alt=""><br><b>Real Arabic documents</b><br><sub>A search that understands Arabic: it unifies alef and taa marbuta forms, strips diacritics, and reads Arabic-Indic digits.</sub></td>
<td width="33%" valign="top"><img src="assets/icons/capstone.svg" width="36" height="36" alt=""><br><b>Examples from the region</b><br><sub>Date palms and the stages of the fruit, the Hijri calendar and Ramadan, the time in Riyadh, and a calculator that accepts Arabic-Indic digits (٠١٢٣).</sub></td>
<td width="33%" valign="top"><img src="assets/icons/eval.svg" width="36" height="36" alt=""><br><b>Cost discipline</b><br><sub>A cost budget checked before every call, the cost of each question printed in front of you, and one dated price table.</sub></td>
</tr>
<tr>
<td width="33%" valign="top"><img src="assets/icons/security.svg" width="36" height="36" alt=""><br><b>Citations checked, not trusted</b><br><sub>Every source in an answer is classified: valid, nonexistent, or never actually read by the agent.</sub></td>
<td width="33%" valign="top"><img src="assets/icons/tools.svg" width="36" height="36" alt=""><br><b>From scratch, no framework</b><br><sub>You write the tool loop by hand, build safe tools without eval, and deletion only happens with your approval.</sub></td>
<td width="33%" valign="top"><img src="assets/icons/setup.svg" width="36" height="36" alt=""><br><b>Tests with no API key</b><br><sub>Every example has a test that runs offline with a mock client, so you can learn without paying anything.</sub></td>
</tr>
</table>

## What you'll build

In Lesson 03 you run a research assistant that reads local Arabic documents, makes a plan, calls its search and read tools, then answers and cites the source of every claim:

```console
$ python lessons/03/research_agent.py
Research assistant. Documents:
calligraphy.txt (9 lines): الخط العربي: فنّ الحرف
hijri.txt (8 lines): التقويم الهجري
palm.txt (9 lines): النخلة: شجرة الصحراء الكريمة
solar.txt (8 lines): الطاقة الشمسية: أساسيات
Ask in Arabic. Empty line to quit.

> ما مراحل ثمرة النخلة؟
plan: ابحث عن مراحل الثمرة / اقرأ الأسطر / أجب مع المصادر
تمرّ ثمرة النخلة بمراحل متتابعة، أشهرها في الخليج: الخلال ثم الرطب ثم التمر [palm.txt:5].
[stop: done | steps: 4 | citations: valid 1 | this question: $0.0xxx]
[session: 4 calls | in ... | out ... | cache w/r 0/0 | $0.0xxx]
```

<sub>Illustrative output shape, not a real run; your text and numbers will differ. The question asks for the stages of the date palm's fruit; the answer names them (khalal, rutab, tamr) and cites line 5 of <code>palm.txt</code>.</sub>

On the way there, you build by hand:

- **An agent loop with no AI at all**, so you understand the structure before a model enters it.
- **Safe tools from scratch:** a calculator without `eval`, date and time, a sandboxed file reader, and a delete tool that only runs with your approval.
- **The tool-use loop, written by hand**, line by line.
- **A research assistant** that reads local Arabic documents, plans, remembers the conversation, stops safely, tracks its own cost, and has every citation in its answer checked.

## Course map

| | # | Lesson | What you'll learn | Status |
|:---:|:---:|---|---|:---:|
| <img src="assets/icons/setup.svg" width="32" height="32" alt=""> | 00 | [Setting up your workspace](docs/en/00-setup/README.md) | Python, keeping your API key safe, cost, and safety rules | **available** |
| <img src="assets/icons/agent.svg" width="32" height="32" alt=""> | 01 | [What is an agent?](docs/en/01-what-is-an-agent/README.md) | Model vs. workflow vs. agent, the perceive, think, act loop, when not to build an agent, and your first request | **available** |
| <img src="assets/icons/tools.svg" width="32" height="32" alt=""> | 02 | [Tools from scratch](docs/en/02-tools/README.md) | Defining tools with JSON Schema, the hand-written loop, error handling, and guarding dangerous tools | **available** |
| <img src="assets/icons/research.svg" width="32" height="32" alt=""> | 03 | [A first real agent: research assistant](docs/en/03-first-agent/README.md) | Planning, memory, stopping conditions, cost tracking, and citation checks | **available** |
| <img src="assets/icons/mcp-soon.svg" width="32" height="32" alt=""> | 04 | MCP: build a tool server | Connecting an agent to external tools through an open standard | coming soon |
| <img src="assets/icons/skills-soon.svg" width="32" height="32" alt=""> | 05 | Agent skills | Bundles of instructions and resources an agent loads when it needs them | coming soon |
| <img src="assets/icons/memory-soon.svg" width="32" height="32" alt=""> | 06 | Long-term memory and retrieval (RAG) | Embeddings, semantic search, and managing long context | coming soon |
| <img src="assets/icons/eval-soon.svg" width="32" height="32" alt=""> | 07 | Evaluating agents | Measuring an agent's quality with numbers, not impressions | coming soon |
| <img src="assets/icons/security-soon.svg" width="32" height="32" alt=""> | 08 | Agent security | Permissions, prompt injection, approvals, and logs | coming soon |
| <img src="assets/icons/multi-soon.svg" width="32" height="32" alt=""> | 09 | Multi-agent systems | When to split work across several agents, and how | coming soon |
| <img src="assets/icons/deploy-soon.svg" width="32" height="32" alt=""> | 10 | Deployment and monitoring | Running an agent for real, and watching its cost and errors | coming soon |
| <img src="assets/icons/capstone-soon.svg" width="32" height="32" alt=""> | 11 | Capstone project | A complete agent, from idea to production | coming soon |

Every lesson has: a clear explanation, diagrams, runnable code, "common mistakes", a "check yourself" quiz, exercises with separate solutions, and key terms collected in the [glossary](docs/en/glossary.md). The original Arabic edition of each lesson is one click away at the top of every page.

## Get started in five minutes

```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: see docs/00-setup
pip install -r requirements-dev.txt

python -m pytest                          # all lessons, offline, no API key
python lessons/01/agent_loop_toy.py       # the agent loop, no API key

export ANTHROPIC_API_KEY="..."            # never write it in code
python lessons/02/tool_loop.py "كم يساوي ١٥٪ من ٢٤٨٠؟"
python lessons/03/research_agent.py
```

The Arabic prompt above asks "what is 15% of 2480?" (written with Arabic-Indic digits, which the calculator tool accepts). Details, the Windows steps, and how cost is calculated are all in [Lesson 00](docs/en/00-setup/README.md).

## Who is this course for?

- **Programmers who know basic Python** and want to understand agents from the inside, rather than copy a ready-made framework.
- **Computer science students** looking for precise explanations of the terminology. The Arabic edition gives each English term once, so moving between Arabic and English references is easy.
- **Team leads** who need to decide when an agent is worth its cost, and when a single request is enough.

You don't need any prior AI experience. You need to be able to write a Python function and run a command in a terminal.

## How to study this course

1. Read the lesson, run the code, then change something and predict the result before you run it again.
2. Answer "check yourself" without opening the answers.
3. Solve the exercises, then compare with the solutions.
4. Run `python -m pytest` after every change.

> [!NOTE]
> **About the examples:** we use the official Anthropic Python library and Claude models. The default model is `claude-opus-5-5`, and you can change it with the `AGENT_MODEL` environment variable. The concepts themselves (the loop, tools, stopping conditions, cost) are general, and you'll find them with any other model provider under slightly different names.

## Repository layout

```text
docs/        lesson texts (Arabic) and the glossary
docs/en/     the full English edition, same structure
lessons/     runnable code for each lesson
solutions/   exercise solutions (try first!)
tests/       offline tests with a fake client
assets/      original diagrams, banners and icons (SVG)
```

## If the course helped you

If you found the course useful, a ⭐ on the repository helps other developers find it, and tells us the next lessons are worth speeding up. That's all we ask, and nothing is offered in return.

## Contributing

Corrections, new exercises and questions are welcome. Please read the [contributing guide](CONTRIBUTING.en.md) and the [code of conduct](CODE_OF_CONDUCT.en.md) before you start.

### Contributors

Contributor avatars will appear here once the repository is public. Be the first to fix a mistake or add an exercise.

<!--
After the repository is public, replace MahsumahCloud/arabic-ai-agents and uncomment:
<a href="https://github.com/MahsumahCloud/arabic-ai-agents/graphs/contributors"><img src="https://contrib.rocks/image?repo=MahsumahCloud/arabic-ai-agents" alt="Contributors"></a>
-->

## Original content

Every text, diagram, example and exercise in this course was written from scratch for it. It is not a translation of, or copied from, any other course. The sample documents in `lessons/03/corpus/` were also written for the course. If you see anything that suggests otherwise, please tell us.

## License

- **Code** (`lessons/`, `solutions/`, `tests/`): [MIT](LICENSE).
- **Written content and diagrams**: [CC BY 4.0](LICENSE-content). You may copy, adapt and use them, as long as you credit the source.

## About Mahsumah

This course was prepared by the team at [Mahsumah](https://mahsumaah.sa). We build cloud and software products, and we share what we learn in the open, Arabic first.

---

<p align="center"><sub><a href="DISCLAIMER.en.md">Disclaimer</a> · <a href="NOTICE.en.md">Trademarks</a> · <a href="SECURITY.en.md">Security</a> · <a href="PRIVACY.en.md">Privacy</a> · <a href="LICENSE">License</a></sub></p>
<p align="center"><sub>© Mahsumah · <a href="https://mahsumaah.sa">mahsumaah.sa</a></sub></p>
