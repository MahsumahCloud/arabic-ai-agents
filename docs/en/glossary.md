<p align="center"><b>English</b> · <a href="../glossary.md">العربية</a></p>

<p align="center"><img src="../../assets/headers/glossary-en.svg" alt="Glossary" width="100%"></p>

# Glossary

Terms are listed in the order they appear in the lessons. The [Arabic glossary](../glossary.md) gives the Arabic term for each one.

| Term | Definition | Lesson |
|---|---|---|
| Virtual Environment | An isolated folder that holds one project's libraries so they don't clash with others | 00 |
| Environment Variable | A value set by the operating system outside the code; the API key is read from one | 00 |
| API Key | A secret that proves your identity to the API; treat it like a password | 00 |
| Token | A piece of text; the unit the model measures and prices by | 00 |
| Effort | A setting that controls how much the model thinks and how many tokens it uses | 00 |
| Sandbox | An isolated space that tools cannot escape | 00 |
| Least Privilege | Giving any component the smallest set of permissions it needs to do its job | 00 |
| Mock Client | A stand-in for the real client that returns pre-written responses, for testing | 00 |
| Large Language Model | A model trained on a large body of text that generates text appropriate to its input | 01 |
| Agent | A system that uses a model to decide its own steps inside a loop, using tools, until the goal is reached or a stopping limit is hit | 01 |
| Workflow | A sequence of steps fixed in advance by the code, where the model may be used in some of them | 01 |
| Loop | Repetition of perceive, think, act, until the stopping condition | 01 |
| Perceive | What the agent knows right now: the request and the tool results | 01 |
| Think | Choosing the next step | 01 |
| Act | Carrying out the step in the environment | 01 |
| Environment | The world that is affected by the agent's actions and returns results | 01 |
| Stopping Condition | A rule that ends the loop: a goal reached or a limit hit | 01 |
| System Prompt | General instructions that set the model's role and rules in the conversation | 01 |
| Content Block | A typed part of a response: text, thinking or a tool request | 01 |
| Stop Reason | The `stop_reason` field that tells you why the model stopped | 01 |
| Adaptive Thinking | Thinking whose amount the model decides according to how hard the request is | 01 |
| Tool | A capability you describe to the model and your code runs when the model asks for it | 02 |
| Tool Use | The mechanism by which the model asks for a tool to be run and receives its result | 02 |
| JSON Schema | A structured description of the data a tool accepts as input | 02 |
| Tool Result | The `tool_result` block that carries a tool's result or error back to the model | 02 |
| Parallel Tool Use | Asking for several tools in a single response | 02 |
| Allowlist | Naming what is allowed explicitly and rejecting everything else | 02 |
| Abstract Syntax Tree | A tree representation of an expression that can be inspected before it is evaluated, instead of `eval` | 02 |
| Human Approval | Requiring a person to approve before a dangerous action runs | 02 |
| Prompt Injection | Text planted in data the model reads that tries to change its behaviour | 02 |
| Tool Runner | A helper in the official library that runs the tool loop for you (beta) | 02 |
| Planning | Writing down the steps before acting, in a form that can be inspected | 03 |
| Conversation Memory | The list of messages your code sends in full with every request | 03 |
| Append-only History | The rule that the conversation is only added to; earlier turns are never edited | 03 |
| Normalization | Unifying letter forms and removing diacritics before comparing text | 03 |
| Stop Words | Very frequent words that are left out of a search | 03 |
| Citation | A pointer to the document and line a piece of information came from | 03 |
| Grounding | Tying an answer to real sources instead of the model's general knowledge | 03 |
| Max Steps | The maximum number of rounds the loop may run | 03 |
| Cost Budget | The maximum amount that may be spent on a single question | 03 |
| Loop Detection | Noticing that the agent keeps repeating the same call without making progress | 03 |
| Usage | The input, output and cache token counts in each response | 03 |
| Prompt Caching | Reusing a repeated request prefix at a lower price | 03 |
| Compaction | Automatically summarizing the start of a long conversation so it stays within the context | 03 |
| Spec-Driven Development | A way of working where decisions are written first in plain language and reviewed by a person, and the code is then built from them | 04 |
| Constitution | A short file of project rules that must not be broken, including what must not be touched, read before every feature | 04 |
| Specification | A description of what we're building, for whom and why, with numbered requirements and acceptance scenarios, and no technology | 04 |
| Requirement | One numbered sentence that says one testable thing | 04 |
| Acceptance Scenario | An example with real numbers: given this, when that happens, the result is this | 04 |
| Out of Scope | What we explicitly decided not to build in this feature | 04 |
| Technical Plan | How the feature will be built: stack, files and decisions, each decision naming the requirement it serves | 04 |
| Task List | Small, ordered steps, each pointing at a requirement and checked off when done | 04 |
| Traceability | Tying every line of code to a task and a requirement, and every requirement to a test | 04 |
| Convergence | Comparing the code against the spec after implementing, and adding tasks for what is missing until nothing is | 04 |
| Review Gate | A point after which implementation doesn't start until a person has read and approved the spec and the tasks | 04 |
| Verification Verdict | The result of the bug-fixing path: verified, partial or failed | 04 |
| Idea Assessment | Questions asked before building that end in a decision: go, clarify or stop | 04 |
| Agent Skill | A folder with an instructions file for one job, which the agent loads only when it needs it | 05 |
| SKILL.md | The required file in a skill: a header with the name and description, then the instructions | 05 |
| Front Matter | The lines between two `---` markers at the top of a file, holding fields such as the name and description | 05 |
| Skill Description | A sentence saying what a skill does and when to use it; the agent decides from it alone whether to open the skill | 05 |
| Progressive Loading | The description always, the instructions on a match, scripts and resources only on demand | 05 |
| Skill Catalogue | A list of skills available to install, with where each one lives and its trust signals | 05 |
| Trust Signals | What suggests a skill is sound, such as a verified source and the install count | 05 |
| Verified Source | A source reviewed by the catalogue's publisher; the strongest trust signal | 05 |
| Held-back Skill | A skill that matches the request but has low trust, so it is never recommended | 05 |
| Install Preview | What is shown before installing: name, description, source, files and warnings | 05 |
| Explicit Consent | A clear yes from the user; silence or "maybe" is not consent | 05 |
| Path Traversal | An attempt to read or write outside the allowed folder with a path such as `../` | 05 |
| Symbolic Link | A file that points at another file, possibly outside the folder it appears to be in | 05 |

---

<p align="center"><a href="../../README.en.md#course-map">Course map</a> · <a href="00-setup/README.md">Start with Lesson 00</a></p>
