<p align="center"><b>English</b> · <a href="README.md">العربية</a></p>

# Lesson 02 exercise solutions

## Exercise 1: a unit converter tool

The solution is in [`ex1_unit_converter.py`](ex1_unit_converter.py). The idea: subclass `ToolBox`, add the definition to `definitions` and the schema to `_schemas`, then override `_dispatch` for the new tool and leave everything else to the parent class. That way `tools.py` stays unchanged, and validation and guarding still apply to the new tool.

Notice that we check the units inside the implementation even though the schema has an `enum`, because the simplified `validate_input` doesn't check `enum`. The rule: never assume another layer validated for you.

## Exercise 2: approval with an audit log

The solution is in [`ex2_audit_approver.py`](ex2_audit_approver.py). The approval function is a callable object that keeps a list of decisions. The fixed policy (protecting `.md` files) is applied before asking the human, so the human is never asked about something that is always forbidden. Usage:

```python
from tools import ToolBox, ask_in_terminal
from ex2_audit_approver import AuditApprover

approver = AuditApprover(ask_human=ask_in_terminal)
toolbox = ToolBox(approver=approver)
```

## Exercise 3: think about it

- **An ID that matches no request:** the API rejects the request, because every `tool_result` must answer a `tool_use` present in the model's previous response, and every `tool_use` needs a result.
- **Why is `is_error` better than stopping?** Because many errors can be fixed: a wrong file name, or an invalid arithmetic expression. When the model sees the error message, it can try another name or ask the user. Stopping the loop throws away the work done so far and denies the model the chance to correct itself. Errors that can't be fixed (such as running out of credit) end the loop through the stopping conditions, not by crashing the program.
