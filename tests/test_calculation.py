"""
Comprehensive test suite for the Calculation class.

Tests all methods including initialization, calculations, serialization,
and utility methods.
"""

import pytest
import datetime
from decimal import Decimal, InvalidOperation
from app.calculation import Calculation
from app.exceptions import OperationError


class TestCalculationInitialization:
    """Tests for Calculation initialization and __post_init__."""

    def test_addition_initialization(self):
        """Test calculation is properly initialized with addition."""
        calc = Calculation(operation="Addition", operand1=Decimal("5"), operand2=Decimal("3"))
        assert calc.operation == "Addition"
        assert calc.operand1 == Decimal("5")
        assert calc.operand2 == Decimal("3")
        assert calc.result == Decimal("8")
        assert isinstance(calc.timestamp, datetime.datetime)

    def test_initialization_auto_calculates_result(self):
        """Test that result is automatically calculated on initialization."""
        calc = Calculation(operation="Multiplication", operand1=Decimal("4"), operand2=Decimal("7"))
        assert calc.result == Decimal("28")

    def test_timestamp_default_factory(self):
        """Test that timestamp is automatically set to current time."""
        before = datetime.datetime.now()
        calc = Calculation(operation="Addition", operand1=Decimal("1"), operand2=Decimal("1"))
        after = datetime.datetime.now()
        assert before <= calc.timestamp <= after


class TestCalculateMethod:
    """Tests for the calculate() method and all supported operations."""

    def test_addition(self):
        """Test addition operation."""
        calc = Calculation(operation="Addition", operand1=Decimal("10"), operand2=Decimal("5"))
        assert calc.result == Decimal("15")

    def test_addition_with_negatives(self):
        """Test addition with negative numbers."""
        calc = Calculation(operation="Addition", operand1=Decimal("-10"), operand2=Decimal("5"))
        assert calc.result == Decimal("-5")

    def test_subtraction(self):
        """Test subtraction operation."""
        calc = Calculation(operation="Subtraction", operand1=Decimal("10"), operand2=Decimal("5"))
        assert calc.result == Decimal("5")

    def test_subtraction_negative_result(self):
        """Test subtraction resulting in negative number."""
        calc = Calculation(operation="Subtraction", operand1=Decimal("5"), operand2=Decimal("10"))
        assert calc.result == Decimal("-5")

    def test_multiplication(self):
        """Test multiplication operation."""
        calc = Calculation(operation="Multiplication", operand1=Decimal("6"), operand2=Decimal("7"))
        assert calc.result == Decimal("42")

    def test_multiplication_by_zero(self):
        """Test multiplication by zero."""
        calc = Calculation(operation="Multiplication", operand1=Decimal("100"), operand2=Decimal("0"))
        assert calc.result == Decimal("0")

    def test_division(self):
        """Test division operation."""
        calc = Calculation(operation="Division", operand1=Decimal("10"), operand2=Decimal("2"))
        assert calc.result == Decimal("5")

    def test_division_with_decimal_result(self):
        """Test division with decimal result."""
        calc = Calculation(operation="Division", operand1=Decimal("10"), operand2=Decimal("3"))
        # Result will be a Decimal with precision
        assert calc.result > Decimal("3.33") and calc.result < Decimal("3.34")

    def test_division_by_zero_raises_error(self):
        """Test that division by zero raises OperationError."""
        with pytest.raises(OperationError, match="Division by zero is not allowed"):
            Calculation(operation="Division", operand1=Decimal("10"), operand2=Decimal("0"))

    def test_power_operation(self):
        """Test power operation."""
        calc = Calculation(operation="Power", operand1=Decimal("2"), operand2=Decimal("3"))
        assert calc.result == Decimal("8")

    def test_power_with_zero_exponent(self):
        """Test power with zero exponent."""
        calc = Calculation(operation="Power", operand1=Decimal("5"), operand2=Decimal("0"))
        assert calc.result == Decimal("1")

    def test_power_with_negative_exponent_raises_error(self):
        """Test that negative exponent raises OperationError."""
        with pytest.raises(OperationError, match="Negative exponents are not supported"):
            Calculation(operation="Power", operand1=Decimal("2"), operand2=Decimal("-1"))

    def test_root_operation(self):
        """Test root operation (square root)."""
        calc = Calculation(operation="Root", operand1=Decimal("9"), operand2=Decimal("2"))
        assert calc.result == Decimal("3")

    def test_root_operation_cube_root(self):
        """Test cube root operation."""
        calc = Calculation(operation="Root", operand1=Decimal("27"), operand2=Decimal("3"))
        assert calc.result == Decimal("3")

    def test_root_of_negative_number_raises_error(self):
        """Test that root of negative number raises OperationError."""
        with pytest.raises(OperationError, match="Cannot calculate root of negative number"):
            Calculation(operation="Root", operand1=Decimal("-9"), operand2=Decimal("2"))

    def test_root_with_zero_degree_raises_error(self):
        """Test that zero root raises OperationError."""
        with pytest.raises(OperationError, match="Zero root is undefined"):
            Calculation(operation="Root", operand1=Decimal("9"), operand2=Decimal("0"))

    def test_unknown_operation_raises_error(self):
        """Test that unknown operation raises OperationError."""
        with pytest.raises(OperationError, match="Unknown operation: InvalidOp"):
            Calculation(operation="InvalidOp", operand1=Decimal("5"), operand2=Decimal("3"))

    def test_calculate_handles_arithmetic_errors(self):
        """Test that calculate() properly handles arithmetic errors during calculation."""
    # Create a calculation that will cause an arithmetic error
    # Using extremely large exponents can cause overflow/arithmetic errors
        with pytest.raises(OperationError, match="Calculation failed"):
        # This should trigger an ArithmeticError/OverflowError during the pow() operation
            Calculation(
                operation="Power",
                operand1=Decimal("10"),
                operand2=Decimal("999999999")
            )
            
    def test_calculate_arithmetic_error_with_overflow(self):
        """Test that calculate() catches arithmetic errors from overflow."""
    # Using Power with very large exponents causes overflow
        with pytest.raises(OperationError, match="Calculation failed"):
            Calculation(
                operation="Power",
                operand1=Decimal("999999"),
                operand2=Decimal("999999")
            )

class TestToDictMethod:
    """Tests for the to_dict() serialization method."""

    def test_to_dict_returns_correct_structure(self):
        """Test that to_dict returns properly formatted dictionary."""
        calc = Calculation(operation="Addition", operand1=Decimal("5"), operand2=Decimal("3"))
        result_dict = calc.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict['operation'] == 'Addition'
        assert result_dict['operand1'] == '5'
        assert result_dict['operand2'] == '3'
        assert result_dict['result'] == '8'
        assert 'timestamp' in result_dict

    def test_to_dict_timestamp_is_isoformat(self):
        """Test that timestamp is serialized in ISO format."""
        calc = Calculation(operation="Subtraction", operand1=Decimal("10"), operand2=Decimal("4"))
        result_dict = calc.to_dict()
        
        # Should be able to parse it back
        parsed_timestamp = datetime.datetime.fromisoformat(result_dict['timestamp'])
        assert isinstance(parsed_timestamp, datetime.datetime)

    def test_to_dict_with_decimal_result(self):
        """Test to_dict with decimal result."""
        calc = Calculation(operation="Division", operand1=Decimal("10"), operand2=Decimal("4"))
        result_dict = calc.to_dict()
        
        assert isinstance(result_dict['result'], str)
        assert Decimal(result_dict['result']) == calc.result


class TestFromDictMethod:
    """Tests for the from_dict() deserialization method."""

    def test_from_dict_creates_calculation(self):
        """Test that from_dict creates a valid Calculation instance."""
        data = {
            'operation': 'Addition',
            'operand1': '5',
            'operand2': '3',
            'result': '8',
            'timestamp': '2024-01-15T10:30:00'
        }
        calc = Calculation.from_dict(data)
        
        assert calc.operation == 'Addition'
        assert calc.operand1 == Decimal('5')
        assert calc.operand2 == Decimal('3')
        assert calc.result == Decimal('8')
        assert calc.timestamp == datetime.datetime(2024, 1, 15, 10, 30, 0)

    def test_from_dict_recalculates_result(self):
        """Test that from_dict recalculates and verifies result."""
        data = {
            'operation': 'Multiplication',
            'operand1': '4',
            'operand2': '5',
            'result': '20',
            'timestamp': '2024-01-15T10:30:00'
        }
        calc = Calculation.from_dict(data)
        assert calc.result == Decimal('20')

    def test_from_dict_missing_operation_raises_error(self):
        """Test that missing operation field raises OperationError."""
        data = {
            'operand1': '5',
            'operand2': '3',
            'result': '8',
            'timestamp': '2024-01-15T10:30:00'
        }
        with pytest.raises(OperationError, match="Invalid calculation data"):
            Calculation.from_dict(data)

    def test_from_dict_missing_operand1_raises_error(self):
        """Test that missing operand1 raises OperationError."""
        data = {
            'operation': 'Addition',
            'operand2': '3',
            'result': '8',
            'timestamp': '2024-01-15T10:30:00'
        }
        with pytest.raises(OperationError, match="Invalid calculation data"):
            Calculation.from_dict(data)

    def test_from_dict_invalid_decimal_raises_error(self):
        """Test that invalid decimal value raises OperationError."""
        data = {
            'operation': 'Addition',
            'operand1': 'invalid',
            'operand2': '3',
            'result': '8',
            'timestamp': '2024-01-15T10:30:00'
        }
        with pytest.raises(OperationError, match="Invalid calculation data"):
            Calculation.from_dict(data)

    def test_from_dict_invalid_timestamp_raises_error(self):
        """Test that invalid timestamp raises OperationError."""
        data = {
            'operation': 'Addition',
            'operand1': '5',
            'operand2': '3',
            'result': '8',
            'timestamp': 'invalid-timestamp'
        }
        with pytest.raises(OperationError, match="Invalid calculation data"):
            Calculation.from_dict(data)


class TestStringRepresentation:
    """Tests for __str__ and __repr__ methods."""

    def test_str_representation(self):
        """Test string representation of calculation."""
        calc = Calculation(operation="Addition", operand1=Decimal("5"), operand2=Decimal("3"))
        assert str(calc) == "Addition(5, 3) = 8"

    def test_str_with_division(self):
        """Test string representation with division."""
        calc = Calculation(operation="Division", operand1=Decimal("10"), operand2=Decimal("2"))
        assert str(calc) == "Division(10, 2) = 5"

    def test_repr_representation(self):
        """Test detailed repr representation."""
        calc = Calculation(operation="Multiplication", operand1=Decimal("4"), operand2=Decimal("5"))
        repr_str = repr(calc)
        
        assert "Calculation(" in repr_str
        assert "operation='Multiplication'" in repr_str
        assert "operand1=4" in repr_str
        assert "operand2=5" in repr_str
        assert "result=20" in repr_str
        assert "timestamp=" in repr_str


class TestEqualityMethod:
    """Tests for __eq__ equality comparison method."""

    def test_equal_calculations(self):
        """Test that identical calculations are equal."""
        calc1 = Calculation(operation="Addition", operand1=Decimal("5"), operand2=Decimal("3"))
        calc2 = Calculation(operation="Addition", operand1=Decimal("5"), operand2=Decimal("3"))
        assert calc1 == calc2

    def test_different_operations_not_equal(self):
        """Test that calculations with different operations are not equal."""
        calc1 = Calculation(operation="Addition", operand1=Decimal("5"), operand2=Decimal("3"))
        calc2 = Calculation(operation="Subtraction", operand1=Decimal("5"), operand2=Decimal("3"))
        assert calc1 != calc2

    def test_different_operands_not_equal(self):
        """Test that calculations with different operands are not equal."""
        calc1 = Calculation(operation="Addition", operand1=Decimal("5"), operand2=Decimal("3"))
        calc2 = Calculation(operation="Addition", operand1=Decimal("5"), operand2=Decimal("4"))
        assert calc1 != calc2

    def test_equality_with_non_calculation_returns_not_implemented(self):
        """Test equality comparison with non-Calculation object."""
        calc = Calculation(operation="Addition", operand1=Decimal("5"), operand2=Decimal("3"))
        assert calc.__eq__("not a calculation") == NotImplemented

    def test_equality_ignores_timestamp(self):
        """Test that equality comparison ignores timestamp differences."""
        calc1 = Calculation(operation="Addition", operand1=Decimal("5"), operand2=Decimal("3"))
        # Create second calculation with different timestamp
        import time
        time.sleep(0.01)
        calc2 = Calculation(operation="Addition", operand1=Decimal("5"), operand2=Decimal("3"))
        # Should still be equal despite different timestamps
        assert calc1 == calc2


class TestFormatResultMethod:
    """Tests for the format_result() method."""

    def test_format_result_default_precision(self):
        """Test format_result with default precision."""
        calc = Calculation(operation="Division", operand1=Decimal("10"), operand2=Decimal("3"))
        formatted = calc.format_result()
        assert isinstance(formatted, str)

    def test_format_result_custom_precision(self):
        """Test format_result with custom precision."""
        calc = Calculation(operation="Division", operand1=Decimal("1"), operand2=Decimal("3"))
        formatted = calc.format_result(precision=2)
        assert isinstance(formatted, str)

    def test_format_result_removes_trailing_zeros(self):
        """Test that format_result removes trailing zeros."""
        calc = Calculation(operation="Division", operand1=Decimal("10"), operand2=Decimal("2"))
        formatted = calc.format_result()
        assert formatted == "5"

    def test_format_result_with_integer_result(self):
        """Test format_result with integer result."""
        calc = Calculation(operation="Addition", operand1=Decimal("5"), operand2=Decimal("3"))
        formatted = calc.format_result()
        assert formatted == "8"

    def test_format_result_with_zero_precision(self):
        """Test format_result with zero precision."""
        calc = Calculation(operation="Addition", operand1=Decimal("5.7"), operand2=Decimal("3.2"))
        formatted = calc.format_result(precision=0)
        assert isinstance(formatted, str)


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_large_numbers(self):
        """Test calculations with very large numbers."""
        calc = Calculation(
            operation="Addition",
            operand1=Decimal("999999999999999999"),
            operand2=Decimal("1")
        )
        assert calc.result == Decimal("1000000000000000000")

    def test_very_small_decimals(self):
        """Test calculations with very small decimal numbers."""
        calc = Calculation(
            operation="Addition",
            operand1=Decimal("0.0000000001"),
            operand2=Decimal("0.0000000001")
        )
        assert calc.result == Decimal("0.0000000002")

    def test_negative_numbers_multiplication(self):
        """Test multiplication with negative numbers."""
        calc = Calculation(
            operation="Multiplication",
            operand1=Decimal("-5"),
            operand2=Decimal("-3")
        )
        assert calc.result == Decimal("15")

    def test_zero_operands(self):
        """Test calculations with zero operands."""
        calc = Calculation(operation="Addition", operand1=Decimal("0"), operand2=Decimal("0"))
        assert calc.result == Decimal("0")

    def test_serialization_deserialization_round_trip(self):
        """Test that serialization and deserialization preserve data."""
        original = Calculation(operation="Division", operand1=Decimal("22"), operand2=Decimal("7"))
        data = original.to_dict()
        restored = Calculation.from_dict(data)
        
        assert original == restored
        assert original.timestamp == restored.timestamp