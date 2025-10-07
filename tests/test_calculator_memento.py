"""
Comprehensive pytest test suite for CalculatorMemento class - 100% coverage
"""

import datetime
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from app.calculation import Calculation
from app.calculator_memento import CalculatorMemento


@pytest.fixture
def sample_calculation():
    """Create a sample calculation for testing."""
    return Calculation(
        operation="Addition",
        operand1=Decimal('5'),
        operand2=Decimal('10')
    )


@pytest.fixture
def sample_calculations():
    """Create a list of sample calculations for testing."""
    return [
        Calculation(
            operation="Addition",
            operand1=Decimal('5'),
            operand2=Decimal('10')
        ),
        Calculation(
            operation="Subtraction",
            operand1=Decimal('20'),
            operand2=Decimal('8')
        ),
        Calculation(
            operation="Multiplication",
            operand1=Decimal('3'),
            operand2=Decimal('7')
        )
    ]


@pytest.fixture
def fixed_timestamp():
    """Create a fixed timestamp for testing."""
    return datetime.datetime(2024, 1, 15, 10, 30, 45)


class TestCalculatorMementoInitialization:
    """Tests for CalculatorMemento initialization."""

    def test_init_with_empty_history(self):
        """Test initialization with empty history."""
        memento = CalculatorMemento(history=[])
        assert memento.history == []
        assert isinstance(memento.timestamp, datetime.datetime)

    def test_init_with_calculations(self, sample_calculations):
        """Test initialization with calculation history."""
        memento = CalculatorMemento(history=sample_calculations)
        assert len(memento.history) == 3
        assert memento.history == sample_calculations
        assert isinstance(memento.timestamp, datetime.datetime)

    def test_init_with_single_calculation(self, sample_calculation):
        """Test initialization with a single calculation."""
        memento = CalculatorMemento(history=[sample_calculation])
        assert len(memento.history) == 1
        assert memento.history[0] == sample_calculation

    def test_init_with_custom_timestamp(self, sample_calculations, fixed_timestamp):
        """Test initialization with a custom timestamp."""
        memento = CalculatorMemento(
            history=sample_calculations,
            timestamp=fixed_timestamp
        )
        assert memento.timestamp == fixed_timestamp
        assert memento.history == sample_calculations

    def test_init_timestamp_auto_generated(self, sample_calculation):
        """Test that timestamp is automatically generated if not provided."""
        before = datetime.datetime.now()
        memento = CalculatorMemento(history=[sample_calculation])
        after = datetime.datetime.now()
        
        assert before <= memento.timestamp <= after

    def test_init_preserves_calculation_order(self, sample_calculations):
        """Test that initialization preserves the order of calculations."""
        memento = CalculatorMemento(history=sample_calculations)
        
        for i, calc in enumerate(sample_calculations):
            assert memento.history[i] == calc


class TestToDict:
    """Tests for to_dict method."""

    def test_to_dict_empty_history(self, fixed_timestamp):
        """Test to_dict with empty history."""
        memento = CalculatorMemento(history=[], timestamp=fixed_timestamp)
        result = memento.to_dict()
        
        assert result == {
            'history': [],
            'timestamp': '2024-01-15T10:30:45'
        }

    def test_to_dict_with_single_calculation(self, sample_calculation, fixed_timestamp):
        """Test to_dict with a single calculation."""
        memento = CalculatorMemento(
            history=[sample_calculation],
            timestamp=fixed_timestamp
        )
        result = memento.to_dict()
        
        assert 'history' in result
        assert 'timestamp' in result
        assert len(result['history']) == 1
        assert result['timestamp'] == '2024-01-15T10:30:45'

    def test_to_dict_with_multiple_calculations(self, sample_calculations, fixed_timestamp):
        """Test to_dict with multiple calculations."""
        memento = CalculatorMemento(
            history=sample_calculations,
            timestamp=fixed_timestamp
        )
        result = memento.to_dict()
        
        assert 'history' in result
        assert 'timestamp' in result
        assert len(result['history']) == 3
        assert result['timestamp'] == '2024-01-15T10:30:45'

    def test_to_dict_calls_calculation_to_dict(self, sample_calculation, fixed_timestamp):
        """Test that to_dict calls to_dict on each calculation."""
        with patch.object(sample_calculation, 'to_dict', return_value={'test': 'data'}) as mock_to_dict:
            memento = CalculatorMemento(
                history=[sample_calculation],
                timestamp=fixed_timestamp
            )
            result = memento.to_dict()
            
            mock_to_dict.assert_called_once()
            assert result['history'][0] == {'test': 'data'}

    def test_to_dict_timestamp_format(self, sample_calculation):
        """Test that timestamp is properly formatted as ISO string."""
        timestamp = datetime.datetime(2024, 6, 15, 14, 30, 0, 123456)
        memento = CalculatorMemento(history=[sample_calculation], timestamp=timestamp)
        result = memento.to_dict()
        
        assert result['timestamp'] == '2024-06-15T14:30:00.123456'

    def test_to_dict_returns_new_dict(self, sample_calculation, fixed_timestamp):
        """Test that to_dict returns a new dictionary each time."""
        memento = CalculatorMemento(
            history=[sample_calculation],
            timestamp=fixed_timestamp
        )
        
        result1 = memento.to_dict()
        result2 = memento.to_dict()
        
        assert result1 is not result2
        assert result1 == result2


class TestFromDict:
    """Tests for from_dict class method."""

    def test_from_dict_empty_history(self, fixed_timestamp):
        """Test from_dict with empty history."""
        data = {
            'history': [],
            'timestamp': '2024-01-15T10:30:45'
        }
        
        memento = CalculatorMemento.from_dict(data)
        
        assert memento.history == []
        assert memento.timestamp == fixed_timestamp

    def test_from_dict_with_single_calculation(self):
        """Test from_dict with a single calculation."""
        data = {
            'history': [
                {
                    'operation': 'Addition',
                    'operand1': '5',
                    'operand2': '10',
                    'result': '15',
                    'timestamp': '2024-01-15T10:30:45'
                }
            ],
            'timestamp': '2024-01-15T10:30:45'
        }
        
        with patch('app.calculation.Calculation.from_dict') as mock_from_dict:
            mock_calc = Mock()
            mock_from_dict.return_value = mock_calc
            
            memento = CalculatorMemento.from_dict(data)
            
            assert len(memento.history) == 1
            assert memento.history[0] == mock_calc
            mock_from_dict.assert_called_once()

    def test_from_dict_with_multiple_calculations(self):
        """Test from_dict with multiple calculations."""
        data = {
            'history': [
                {
                    'operation': 'Addition',
                    'operand1': '5',
                    'operand2': '10',
                    'result': '15',
                    'timestamp': '2024-01-15T10:30:45'
                },
                {
                    'operation': 'Subtraction',
                    'operand1': '20',
                    'operand2': '8',
                    'result': '12',
                    'timestamp': '2024-01-15T10:31:00'
                }
            ],
            'timestamp': '2024-01-15T10:30:45'
        }
        
        with patch('app.calculation.Calculation.from_dict') as mock_from_dict:
            mock_calc1 = Mock()
            mock_calc2 = Mock()
            mock_from_dict.side_effect = [mock_calc1, mock_calc2]
            
            memento = CalculatorMemento.from_dict(data)
            
            assert len(memento.history) == 2
            assert memento.history[0] == mock_calc1
            assert memento.history[1] == mock_calc2
            assert mock_from_dict.call_count == 2

    def test_from_dict_calls_calculation_from_dict(self):
        """Test that from_dict calls Calculation.from_dict for each calculation."""
        calc_data = {
            'operation': 'Multiplication',
            'operand1': '3',
            'operand2': '7',
            'result': '21',
            'timestamp': '2024-01-15T10:30:45'
        }
        
        data = {
            'history': [calc_data],
            'timestamp': '2024-01-15T10:30:45'
        }
        
        with patch('app.calculation.Calculation.from_dict') as mock_from_dict:
            mock_calc = Mock()
            mock_from_dict.return_value = mock_calc
            
            memento = CalculatorMemento.from_dict(data)
            
            mock_from_dict.assert_called_once_with(calc_data)

    def test_from_dict_parses_timestamp(self):
        """Test that from_dict correctly parses ISO timestamp string."""
        data = {
            'history': [],
            'timestamp': '2024-06-15T14:30:00.123456'
        }
        
        memento = CalculatorMemento.from_dict(data)
        
        expected_timestamp = datetime.datetime(2024, 6, 15, 14, 30, 0, 123456)
        assert memento.timestamp == expected_timestamp

    def test_from_dict_preserves_calculation_order(self):
        """Test that from_dict preserves the order of calculations."""
        data = {
            'history': [
                {'operation': 'Addition', 'operand1': '1', 'operand2': '1', 'result': '2', 'timestamp': '2024-01-15T10:30:45'},
                {'operation': 'Subtraction', 'operand1': '5', 'operand2': '3', 'result': '2', 'timestamp': '2024-01-15T10:31:00'},
                {'operation': 'Multiplication', 'operand1': '2', 'operand2': '4', 'result': '8', 'timestamp': '2024-01-15T10:32:00'}
            ],
            'timestamp': '2024-01-15T10:30:45'
        }
        
        with patch('app.calculation.Calculation.from_dict') as mock_from_dict:
            mock_calcs = [Mock(), Mock(), Mock()]
            mock_from_dict.side_effect = mock_calcs
            
            memento = CalculatorMemento.from_dict(data)
            
            for i, mock_calc in enumerate(mock_calcs):
                assert memento.history[i] == mock_calc


class TestRoundTrip:
    """Tests for serialization/deserialization round-trip."""

    def test_round_trip_empty_history(self, fixed_timestamp):
        """Test round-trip conversion with empty history."""
        original = CalculatorMemento(history=[], timestamp=fixed_timestamp)
        
        data = original.to_dict()
        restored = CalculatorMemento.from_dict(data)
        
        assert restored.timestamp == original.timestamp
        assert len(restored.history) == 0

    def test_round_trip_with_calculations(self, sample_calculations, fixed_timestamp):
        """Test round-trip conversion with calculations."""
        original = CalculatorMemento(
            history=sample_calculations,
            timestamp=fixed_timestamp
        )
        
        data = original.to_dict()
        
        with patch('app.calculation.Calculation.from_dict') as mock_from_dict:
            mock_from_dict.side_effect = sample_calculations
            restored = CalculatorMemento.from_dict(data)
            
            assert restored.timestamp == original.timestamp
            assert len(restored.history) == len(original.history)

    def test_round_trip_preserves_timestamp_precision(self):
        """Test that round-trip preserves timestamp microsecond precision."""
        timestamp = datetime.datetime(2024, 6, 15, 14, 30, 0, 999999)
        original = CalculatorMemento(history=[], timestamp=timestamp)
        
        data = original.to_dict()
        restored = CalculatorMemento.from_dict(data)
        
        assert restored.timestamp == original.timestamp
        assert restored.timestamp.microsecond == 999999


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_memento_with_very_old_timestamp(self):
        """Test memento with very old timestamp."""
        old_timestamp = datetime.datetime(1900, 1, 1, 0, 0, 0)
        memento = CalculatorMemento(history=[], timestamp=old_timestamp)
        
        assert memento.timestamp == old_timestamp
        
        data = memento.to_dict()
        assert data['timestamp'] == '1900-01-01T00:00:00'

    def test_memento_with_future_timestamp(self):
        """Test memento with future timestamp."""
        future_timestamp = datetime.datetime(2099, 12, 31, 23, 59, 59)
        memento = CalculatorMemento(history=[], timestamp=future_timestamp)
        
        assert memento.timestamp == future_timestamp
        
        data = memento.to_dict()
        restored = CalculatorMemento.from_dict(data)
        assert restored.timestamp == future_timestamp

    def test_memento_history_is_list_reference(self, sample_calculations):
        """Test that memento stores reference to history list."""
        history = sample_calculations.copy()
        memento = CalculatorMemento(history=history)
        
        # Both should reference the same list object
        assert memento.history is history

    def test_multiple_mementos_independent(self, sample_calculation):
        """Test that multiple mementos are independent."""
        memento1 = CalculatorMemento(history=[sample_calculation])
        memento2 = CalculatorMemento(history=[])
        
        assert len(memento1.history) == 1
        assert len(memento2.history) == 0
        assert memento1.history is not memento2.history
        assert memento1.timestamp != memento2.timestamp

    def test_to_dict_with_large_history(self):
        """Test to_dict with a large number of calculations."""
        # Create a large history
        large_history = []
        for i in range(100):
            calc = Calculation(
                operation="Addition",
                operand1=Decimal(str(i)),
                operand2=Decimal(str(i + 1))
            )
            large_history.append(calc)
        
        memento = CalculatorMemento(history=large_history)
        result = memento.to_dict()
        
        assert len(result['history']) == 100

    def test_from_dict_with_large_history(self):
        """Test from_dict with a large number of calculations."""
        # Create large history data
        history_data = []
        for i in range(100):
            history_data.append({
                'operation': 'Addition',
                'operand1': str(i),
                'operand2': str(i + 1),
                'result': str(i + i + 1),
                'timestamp': '2024-01-15T10:30:45'
            })
        
        data = {
            'history': history_data,
            'timestamp': '2024-01-15T10:30:45'
        }
        
        with patch('app.calculation.Calculation.from_dict') as mock_from_dict:
            mock_from_dict.return_value = Mock()
            memento = CalculatorMemento.from_dict(data)
            
            assert len(memento.history) == 100
            assert mock_from_dict.call_count == 100


class TestDataclassFeatures:
    """Tests for dataclass-specific features."""

    def test_memento_has_dataclass_fields(self):
        """Test that memento has expected dataclass fields."""
        memento = CalculatorMemento(history=[])
        
        assert hasattr(memento, 'history')
        assert hasattr(memento, 'timestamp')

    def test_memento_equality(self, sample_calculation, fixed_timestamp):
        """Test memento equality comparison."""
        memento1 = CalculatorMemento(
            history=[sample_calculation],
            timestamp=fixed_timestamp
        )
        memento2 = CalculatorMemento(
            history=[sample_calculation],
            timestamp=fixed_timestamp
        )
        
        # Dataclasses with same values should be equal
        assert memento1 == memento2

    def test_memento_inequality_different_history(self, sample_calculations, fixed_timestamp):
        """Test memento inequality with different history."""
        memento1 = CalculatorMemento(
            history=[sample_calculations[0]],
            timestamp=fixed_timestamp
        )
        memento2 = CalculatorMemento(
            history=[sample_calculations[1]],
            timestamp=fixed_timestamp
        )
        
        assert memento1 != memento2

    def test_memento_inequality_different_timestamp(self, sample_calculation):
        """Test memento inequality with different timestamps."""
        timestamp1 = datetime.datetime(2024, 1, 1, 0, 0, 0)
        timestamp2 = datetime.datetime(2024, 1, 2, 0, 0, 0)
        
        memento1 = CalculatorMemento(
            history=[sample_calculation],
            timestamp=timestamp1
        )
        memento2 = CalculatorMemento(
            history=[sample_calculation],
            timestamp=timestamp2
        )
        
        assert memento1 != memento2

    def test_memento_repr(self, sample_calculation, fixed_timestamp):
        """Test memento string representation."""
        memento = CalculatorMemento(
            history=[sample_calculation],
            timestamp=fixed_timestamp
        )
        
        repr_str = repr(memento)
        assert 'CalculatorMemento' in repr_str
        assert 'history' in repr_str
        assert 'timestamp' in repr_str