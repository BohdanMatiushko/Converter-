"""Business logic for electrical unit conversion."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Dict, List


@dataclass(frozen=True)
class UnitDefinition:
    """Represents a unit and its relation to a base unit."""

    symbol: str
    category: str
    factor_to_base: Decimal


CURRENT = "current"
VOLTAGE = "voltage"


UNITS: Dict[str, UnitDefinition] = {
    "A": UnitDefinition(symbol="A", category=CURRENT, factor_to_base=Decimal("1")),
    "mA": UnitDefinition(symbol="mA", category=CURRENT, factor_to_base=Decimal("0.001")),
    "µA": UnitDefinition(symbol="µA", category=CURRENT, factor_to_base=Decimal("0.000001")),
    "V": UnitDefinition(symbol="V", category=VOLTAGE, factor_to_base=Decimal("1")),
    "mV": UnitDefinition(symbol="mV", category=VOLTAGE, factor_to_base=Decimal("0.001")),
}


DEFAULT_FROM_UNIT = "A"
DEFAULT_TO_UNIT = "mA"


class ConversionError(ValueError):
    """Raised when conversion cannot be performed."""


def get_available_units() -> List[str]:
    """Return units in display order."""
    return ["A", "mA", "µA", "V", "mV"]


def normalize_number_string(raw_value: str) -> str:
    """Normalize user input before parsing."""
    return raw_value.strip().replace(",", ".")


def parse_numeric_value(raw_value: str) -> Decimal:
    """
    Parse a numeric string into Decimal.

    Raises:
        ConversionError: if the value is empty or invalid.
    """
    prepared = normalize_number_string(raw_value)
    if not prepared:
        raise ConversionError("Помилка: введіть числове значення")

    try:
        return Decimal(prepared)
    except InvalidOperation as exc:
        raise ConversionError("Помилка: введіть числове значення") from exc


def validate_units(from_unit: str, to_unit: str) -> None:
    """
    Validate that both units exist and belong to the same physical category.

    Raises:
        ConversionError: if the units are missing or incompatible.
    """
    if from_unit not in UNITS or to_unit not in UNITS:
        raise ConversionError("Помилка: невідома одиниця вимірювання")

    if UNITS[from_unit].category != UNITS[to_unit].category:
        raise ConversionError("Помилка: одиниці несумісні")


def convert_value(value: Decimal, from_unit: str, to_unit: str) -> Decimal:
    """
    Convert a value between compatible units.

    Raises:
        ConversionError: if units are incompatible.
    """
    validate_units(from_unit, to_unit)

    from_def = UNITS[from_unit]
    to_def = UNITS[to_unit]

    value_in_base = value * from_def.factor_to_base
    converted_value = value_in_base / to_def.factor_to_base
    return converted_value


def format_decimal(value: Decimal) -> str:
    """
    Format Decimal without trailing zeros.

    Examples:
        1.000000 -> 1
        0.500000 -> 0.5
    """
    normalized = value.normalize()

    if normalized == normalized.to_integral():
        return format(normalized.quantize(Decimal("1")), "f")

    return format(normalized, "f").rstrip("0").rstrip(".")


def convert_raw_value(raw_value: str, from_unit: str, to_unit: str) -> str:
    """
    Convert raw string input and return formatted string result.

    Raises:
        ConversionError: if parsing or conversion fails.
    """
    numeric_value = parse_numeric_value(raw_value)
    converted = convert_value(numeric_value, from_unit, to_unit)
    return format_decimal(converted)