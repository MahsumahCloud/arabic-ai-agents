"""Lesson 02: tools, written from scratch.

A tool has two halves:
  1. a *definition* the model reads (name, description, JSON Schema), and
  2. an *implementation* that YOUR code runs.

The model never runs anything. It only asks. Your code decides whether to run
the tool, runs it, and sends back the result.

Tools in this file:
  - calculator            safe arithmetic (no eval)
  - get_current_datetime  current date and time in a time zone
  - list_files            list files in the sandbox folder
  - read_file             read a text file, only inside the sandbox folder
  - delete_file           DANGEROUS: needs human approval every time
"""

from __future__ import annotations

import ast
import operator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

SANDBOX_DIR = Path(__file__).parent / "sandbox"
ALLOWED_SUFFIXES = {".txt", ".md"}
MAX_FILE_CHARS = 20_000
MAX_EXPRESSION_CHARS = 200
MAX_EXPONENT = 100
MAX_RESULT_BITS = 4096  # stops (9**99)**99**... style blow-ups

# --------------------------------------------------------------------------
# 1) Definitions: this is all the model sees. Descriptions say WHEN to call.
# --------------------------------------------------------------------------

TOOL_DEFINITIONS: list[dict] = [
    {
        "name": "calculator",
        "description": (
            "Evaluate an arithmetic expression exactly. Call this for ANY "
            "calculation instead of computing in your head. Supports + - * / "
            "// % ** and parentheses. Arabic-Indic digits are accepted."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The expression, e.g. '(1250 * 0.15) + 30'",
                }
            },
            "required": ["expression"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_current_datetime",
        "description": (
            "Return the current date, time and weekday. Call this whenever the "
            "answer depends on today's date or the current time."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "IANA time zone name, e.g. 'Asia/Riyadh'. Default: Asia/Riyadh.",
                }
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "list_files",
        "description": "List the text files available in the sandbox folder. Call this before read_file if you do not know the file name.",
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "read_file",
        "description": (
            "Read a .txt or .md file from the sandbox folder. Only relative "
            "paths inside the sandbox are allowed."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative path, e.g. 'notes.txt'"}
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "delete_file",
        "description": (
            "Delete a file from the sandbox folder. Only call this when the user "
            "explicitly asks to delete a specific file. A human must approve each call."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Relative path inside the sandbox"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
]

# --------------------------------------------------------------------------
# 2) Input validation: never trust tool input, even from a good model.
# --------------------------------------------------------------------------

_JSON_TYPES = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
}


def validate_input(schema: dict, data: object) -> str | None:
    """Return an error message, or None if `data` matches the (simple) schema."""
    if not isinstance(data, dict):
        return "input must be a JSON object"
    properties = schema.get("properties", {})
    for key in schema.get("required", []):
        if key not in data:
            return f"missing required field: {key}"
    if schema.get("additionalProperties") is False:
        extra = set(data) - set(properties)
        if extra:
            return f"unexpected field(s): {', '.join(sorted(extra))}"
    for key, value in data.items():
        expected = properties.get(key, {}).get("type")
        if expected is None:
            continue
        python_type = _JSON_TYPES[expected]
        # bool is a subclass of int in Python; do not accept True as a number.
        if isinstance(value, bool) and expected in ("integer", "number"):
            return f"field '{key}' must be {expected}"
        if not isinstance(value, python_type):
            return f"field '{key}' must be {expected}"
    return None


# --------------------------------------------------------------------------
# 3) Implementations
# --------------------------------------------------------------------------

_ARABIC_INDIC = str.maketrans("٠١٢٣٤٥٦٧٨٩٫", "0123456789.")

_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        left, right = _eval_node(node.left), _eval_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > MAX_EXPONENT:
            raise ValueError(f"exponent larger than {MAX_EXPONENT} is not allowed")
        result = _BIN_OPS[type(node.op)](left, right)
        if isinstance(result, int) and result.bit_length() > MAX_RESULT_BITS:
            raise ValueError("result is too large")
        return result
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("only numbers and + - * / // % ** ( ) are allowed")


def calculator(expression: str) -> str:
    expression = expression.translate(_ARABIC_INDIC).strip()
    if len(expression) > MAX_EXPRESSION_CHARS:
        raise ValueError("expression too long")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError("invalid expression") from exc
    try:
        result = _eval_node(tree.body)
    except ZeroDivisionError as exc:
        raise ValueError("division by zero") from exc
    if isinstance(result, float) and result.is_integer():
        result = int(result)
    return str(result)


def get_current_datetime(timezone: str = "Asia/Riyadh", now: Callable[[ZoneInfo], datetime] | None = None) -> str:
    try:
        tz = ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError(f"unknown time zone: {timezone}") from exc
    current = now(tz) if now else datetime.now(tz)
    return f"{current.isoformat(timespec='seconds')} ({current.strftime('%A')}, {timezone})"


def _safe_path(sandbox: Path, relative: str) -> Path:
    """Resolve `relative` inside `sandbox`, or raise. Blocks '../' and absolute paths."""
    root = sandbox.resolve()
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root):
        raise PermissionError("path is outside the sandbox")
    if candidate.suffix.lower() not in ALLOWED_SUFFIXES:
        raise PermissionError(f"only {sorted(ALLOWED_SUFFIXES)} files are allowed")
    return candidate


def list_files(sandbox: Path) -> str:
    root = sandbox.resolve()
    names = sorted(
        str(p.relative_to(root))
        for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in ALLOWED_SUFFIXES
    )
    return "\n".join(names) if names else "(no files)"


def read_file(sandbox: Path, path: str) -> str:
    target = _safe_path(sandbox, path)
    if not target.is_file():
        raise FileNotFoundError(f"no such file: {path}")
    text = target.read_text(encoding="utf-8")
    if len(text) > MAX_FILE_CHARS:
        return text[:MAX_FILE_CHARS] + f"\n[truncated: file has {len(text)} characters]"
    return text


# --------------------------------------------------------------------------
# 4) The toolbox: one place that validates, guards, runs and reports.
# --------------------------------------------------------------------------

Approver = Callable[[str, dict], bool]
DANGEROUS_TOOLS = {"delete_file"}


def deny_all(tool_name: str, tool_input: dict) -> bool:
    """Default approver: refuse every dangerous action."""
    return False


def ask_in_terminal(tool_name: str, tool_input: dict) -> bool:
    """Ask the human at the keyboard. Anything other than 'yes' means no."""
    answer = input(f"\nThe agent wants to run {tool_name}({tool_input}). Type 'yes' to allow: ")
    return answer.strip().lower() == "yes"


@dataclass
class ToolResult:
    content: str
    is_error: bool = False


class ToolBox:
    def __init__(
        self,
        sandbox_dir: Path = SANDBOX_DIR,
        approver: Approver = deny_all,
        now: Callable[[ZoneInfo], datetime] | None = None,
    ):
        self.sandbox_dir = Path(sandbox_dir)
        self.approver = approver
        self.now = now
        self.definitions = TOOL_DEFINITIONS
        self._schemas = {tool["name"]: tool["input_schema"] for tool in TOOL_DEFINITIONS}
        self.log: list[tuple[str, dict, ToolResult]] = []

    def _dispatch(self, name: str, args: dict) -> str:
        if name == "calculator":
            return calculator(args["expression"])
        if name == "get_current_datetime":
            return get_current_datetime(args.get("timezone", "Asia/Riyadh"), now=self.now)
        if name == "list_files":
            return list_files(self.sandbox_dir)
        if name == "read_file":
            return read_file(self.sandbox_dir, args["path"])
        if name == "delete_file":
            target = _safe_path(self.sandbox_dir, args["path"])
            if not target.is_file():
                raise FileNotFoundError(f"no such file: {args['path']}")
            target.unlink()
            return f"deleted {args['path']}"
        raise KeyError(name)

    def run(self, name: str, tool_input: object) -> ToolResult:
        result = self._run(name, tool_input)
        self.log.append((name, tool_input if isinstance(tool_input, dict) else {}, result))
        return result

    def _run(self, name: str, tool_input: object) -> ToolResult:
        if name not in self._schemas:
            return ToolResult(f"unknown tool: {name}", is_error=True)
        problem = validate_input(self._schemas[name], tool_input)
        if problem:
            return ToolResult(f"invalid input: {problem}", is_error=True)
        if name in DANGEROUS_TOOLS and not self.approver(name, tool_input):
            return ToolResult("the user did not approve this action", is_error=True)
        try:
            return ToolResult(self._dispatch(name, tool_input))
        except (ValueError, PermissionError, FileNotFoundError) as exc:
            # Expected failures: tell the model what went wrong so it can recover.
            return ToolResult(str(exc), is_error=True)
        except Exception as exc:  # noqa: BLE001 - never let a tool crash the loop
            return ToolResult(f"tool failed: {type(exc).__name__}", is_error=True)
