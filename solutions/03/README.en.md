<p align="center"><b>English</b> · <a href="README.md">العربية</a></p>

# Lesson 03 exercise solutions

<img src="../../assets/mascot/thumbs-up.gif" alt="The course mascot giving a thumbs up" width="150" align="right">

## Exercise 1: trimming memory

The solution is in [`ex1_trim_memory.py`](ex1_trim_memory.py). Two rules:

1. **The cut point:** cut only at a `user` message whose content is text (a question), because the other `user` messages carry `tool_result` blocks and must stay right after the tool request that precedes them.
2. **Remove every thinking block from what remains:** in Opus 5.5 and similar models, each thinking block is tied to everything before it in the conversation. Removing the beginning changes what came before it, so it becomes invalid, and the request may be rejected with a 400 error. Removing all thinking blocks keeps the request valid, but the model loses that earlier thinking and caching starts over. So don't trim memory on every step; do it rarely, at a clear threshold.

Using it with the agent:

```python
from ex1_trim_memory import trim_history

if len(agent.messages) > 60:
    agent.messages[:] = trim_history(agent.messages, keep_questions=3)
```

## Exercise 2: require sources

The solution is in [`ex2_require_citations.py`](ex2_require_citations.py). We ask again only once, and only if the answer finished successfully (`done`) with no valid citations and was not an admission that the answer isn't available. The retry limit prevents a new loop inside the loop.

## Exercise 3: a malicious document

There is no code solution; what's required is an observation and an explanation:

- The model may ignore the planted sentence this time, and may not with a different wording. **One successful trial does not prove safety.**
- The protection you can rely on is architectural: the agent's tools are read-only, citations are checked, and any dangerous action needs human approval.
- Delete the malicious file after the experiment so it doesn't affect the rest of your experiments.
