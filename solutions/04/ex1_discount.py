"""Solution 04-1: a discount line, added the spec-driven way.

The spec gained one requirement (م-7) and the task list two tasks before any
code was written. The rule the spec settled: the discount comes off the
subtotal BEFORE VAT, and it can never be larger than the subtotal.
"""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lessons" / "04"))

from vat_invoice import VAT_RATE, Line, Totals, parse_amount, to_halala  # noqa: E402


def totals_with_discount(lines: list[Line], discount: str | Decimal) -> Totals:
    """م-7: subtotal - discount, then VAT on what remains."""
    if not lines:
        raise ValueError("الفاتورة بلا بنود")
    discount = to_halala(parse_amount(discount) if isinstance(discount, str) else discount)
    subtotal = to_halala(sum((line.amount for line in lines), Decimal("0")))
    if discount > subtotal:
        raise ValueError("الخصم أكبر من المجموع")
    taxable = subtotal - discount
    vat = to_halala(taxable * VAT_RATE)
    return Totals(taxable, vat, taxable + vat)
