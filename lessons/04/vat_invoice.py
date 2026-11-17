"""Lesson 04: a small VAT invoice calculator, built from a written spec.

This file is the *result* of the five steps in lessons/04/example/:
constitution.md -> spec.md -> plan.md -> tasks.md -> this code.
Each function names the requirement in spec.md (م-1 ... م-6) that it serves.

Run:
    python lessons/04/vat_invoice.py "قهوة=١٥" "كعكة=٢٢٫٥"
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

VAT_RATE = Decimal("0.15")  # Saudi VAT rate; one constant, one place (constitution)
HALALA = Decimal("0.01")
RIYAL_SIGN = "⃁"  # the official Saudi Riyal sign (constitution: amounts use it)

# Arabic-Indic and Eastern Arabic-Indic digits, Arabic decimal and thousands separators.
_DIGITS = str.maketrans(
    "٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹٫٬",
    "01234567890123456789.,",
)


def to_halala(amount: Decimal) -> Decimal:
    """م-3: round half up to the nearest halala (two decimal places)."""
    return amount.quantize(HALALA, rounding=ROUND_HALF_UP)


def parse_amount(text: str) -> Decimal:
    """م-1: accept '١٥', '22.5', '٢٢٫٥', '1,250'; reject empty, negative or non-numbers."""
    cleaned = (text or "").strip().translate(_DIGITS).replace(",", "")
    if not cleaned:
        raise ValueError("المبلغ فارغ")
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        raise ValueError(f"ليس مبلغاً صحيحاً: {text}") from None
    if not value.is_finite():
        raise ValueError(f"ليس مبلغاً صحيحاً: {text}")
    if value < 0:
        raise ValueError("المبلغ لا يكون سالباً")
    return value


@dataclass(frozen=True)
class Line:
    name: str
    amount: Decimal  # price before VAT


@dataclass(frozen=True)
class Totals:
    subtotal: Decimal
    vat: Decimal
    total: Decimal


def parse_line(text: str) -> Line:
    """م-1: one item per argument, written as  name=amount."""
    name, sep, amount = (text or "").partition("=")
    if not sep or not name.strip():
        raise ValueError(f"اكتب البند بالصيغة: الاسم=المبلغ ({text})")
    return Line(name.strip(), parse_amount(amount))


def totals(lines: list[Line]) -> Totals:
    """م-2, م-3: VAT is computed once, on the subtotal, then rounded to the halala."""
    if not lines:
        raise ValueError("الفاتورة بلا بنود")
    subtotal = to_halala(sum((line.amount for line in lines), Decimal("0")))
    vat = to_halala(subtotal * VAT_RATE)
    return Totals(subtotal, vat, subtotal + vat)


def split_inclusive(total: Decimal) -> Totals:
    """م-4: split a VAT-inclusive price into net and VAT; net + vat always equals total."""
    total = to_halala(total)
    net = to_halala(total / (1 + VAT_RATE))
    return Totals(net, total - net, total)


def format_amount(amount: Decimal) -> str:
    """م-5: thousands separator, two decimals, then the riyal sign."""
    return f"{to_halala(amount):,.2f} {RIYAL_SIGN}"


def render(lines: list[Line]) -> str:
    """م-5: a short Arabic invoice, one line per item, then the three totals."""
    result = totals(lines)
    rows = [f"{line.name}: {format_amount(line.amount)}" for line in lines]
    rows += [
        "—",
        f"المجموع قبل الضريبة: {format_amount(result.subtotal)}",
        f"ضريبة القيمة المضافة 15٪: {format_amount(result.vat)}",
        f"الإجمالي: {format_amount(result.total)}",
    ]
    return "\n".join(rows)


def main(argv: list[str]) -> int:
    if not argv:
        print('مثال: python lessons/04/vat_invoice.py "قهوة=١٥" "كعكة=٢٢٫٥"')
        return 2
    try:
        print(render([parse_line(arg) for arg in argv]))
    except ValueError as error:  # م-6: a clear Arabic message, never a traceback
        print(f"خطأ: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
