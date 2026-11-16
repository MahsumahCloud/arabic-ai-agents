<p align="center"><b>English</b> · <a href="CONTRIBUTING.md">العربية</a></p>

# Contributing guide

Thank you for your interest. Our goal is for this course to be the most accurate Arabic reference on building agents, and every small correction brings us closer.

## Ways to contribute

- **Report a mistake:** inaccurate information, code that doesn't run, or a broken link. Open an issue and name the file, the line, and what you expected.
- **Improve the wording:** an unclear sentence or a poorly chosen term.
- **A new exercise:** with its solution and a test.
- **Propose a lesson:** open an issue for discussion first, before writing a whole lesson.

## Content rules

1. **Originality:** write in your own words. Don't copy or translate from other courses, books or articles, and don't bring in other people's diagrams. A short quotation with its source is fine when needed.
2. **Accuracy:** every statement about an API, a price or a model's behaviour must be verifiable against the official documentation. Name the source you checked in your pull request.
3. **No unsupported claims:** no invented performance numbers, no unmeasured comparisons, no marketing language.
4. **One language per file:** lesson files in `docs/` are written in Modern Standard Arabic. The English term is given in parentheses **once**, at its first appearance. Variable names and code comments are in English.
5. **The English edition:** every Arabic lesson has a counterpart in `docs/en/` with the same structure. If you change a lesson, update its counterpart in the same pull request, and keep the code byte-identical in both versions.
6. **Terminology:** use the terms in the [glossary](docs/en/glossary.md). If you introduce a new term, add it to both glossaries in the same pull request.
7. **Human review:** every text that gets merged is read and checked by a person before merging, however it was written.

## Code rules

1. **Every example has a test** in `tests/` that runs offline with the mock client in `tests/fakes.py`. No test sends a real request.
2. **No secrets:** no keys, no access tokens, no internal addresses, no real data about people or companies.
3. **Safety first:** any tool that writes, deletes or sends needs a sandbox and human approval.
4. **Simplicity:** the code is for teaching. Prefer clarity over clever shortcuts.

## Pull request steps

```bash
pip install -r requirements-dev.txt
python -m pytest            # must pass before you open the PR
```

Checklist:

- [ ] The tests pass locally.
- [ ] Every new technical claim has its source in the pull request description.
- [ ] New terms are added to the glossary.
- [ ] No text is copied or translated from other sources.
- [ ] I added a line to [CHANGELOG.md](CHANGELOG.md) if the change is visible to learners.

## License

By contributing, you agree that your code is published under the MIT license and your written content under CC BY 4.0, as in [LICENSE](LICENSE) and [LICENSE-content](LICENSE-content).
