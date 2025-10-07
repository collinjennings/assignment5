"""
Comprehensive pytest test suite for Calculator class - 100% coverage
"""

import logging
import os
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, PropertyMock

import pandas as pd
import pytest

from app.calculation import Calculation
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.exceptions import OperationError, ValidationError
from app.history import HistoryObserver
from app.operations import Operation


@pytest.fixture
def temp_config(tmp_path):
    """Create a temporary configuration for testing."""
    config = CalculatorConfig(base_dir=tmp_path)
    # Ensure history file doesn't exist initially
    if config.history_file.exists():
        config.history_file.unlink()
    return config


@pytest.fixture
def calculator(temp_config):
    """Create a calculator instance with temporary configuration."""
    # Delete history file if it exists
    if temp_config.history_file.exists():
        temp_config.history_file.unlink()
    calc = Calculator(config=temp_config)
    calc.history.clear()  # Ensure clean state
    calc.undo_stack.clear()
    calc.redo_stack.clear()
    return calc


@pytest.fixture
def mock_operation():
    """Create a mock operation for testing."""
    operation = Mock(spec=Operation)
    operation.execute.return_value = Decimal('15')
    operation.__str__ = Mock(return_value="add")
    return operation


@pytest.fixture
def sample_calculation():
    """Create a sample calculation for testing."""
    calc = Calculation(
        operation="Addition",
        operand1=Decimal('5'),
        operand2=Decimal('10')
    )
    return calc


class TestCalculatorInitialization:
    """Tests for Calculator initialization."""

    def test_init_with_config(self, temp_config):
        """Test initialization with provided config."""
        if temp_config.history_file.exists():
            temp_config.history_file.unlink()
        calc = Calculator(config=temp_config)
        calc.history.clear()
        assert calc.config == temp_config
        assert calc.history == []
        assert calc.operation_strategy is None
        assert calc.observers == []
        assert calc.undo_stack == []
        assert calc.redo_stack == []

    def test_init_without_config(self):
        """Test initialization without config (uses default)."""
        with patch('app.calculator.Path') as mock_path:
            mock_file = Mock()
            mock_file.parent.parent = Path('/mock/project/root')
            mock_path.return_value = mock_file
            
            with patch.object(Calculator, 'load_history'):
                calc = Calculator()
                assert calc.config is not None
                assert isinstance(calc.history, list)

    def test_init_creates_log_directory(self, temp_config):
        """Test that initialization creates log directory."""
        if temp_config.history_file.exists():
            temp_config.history_file.unlink()
        calc = Calculator(config=temp_config)
        assert temp_config.log_dir.exists()

    def test_init_validates_config(self, temp_config):
        """Test that config validation is called during init."""
        with patch.object(temp_config, 'validate') as mock_validate:
            if temp_config.history_file.exists():
                temp_config.history_file.unlink()
            calc = Calculator(config=temp_config)
            mock_validate.assert_called_once()

    def test_init_loads_existing_history(self, temp_config):
        """Test that initialization loads existing history."""
        # Create history file manually
        history_data = [{
            'operation': 'Addition',
            'operand1': '5',
            'operand2': '10',
            'result': '15',
            'timestamp': '2024-01-01T00:00:00'
        }]
        df = pd.DataFrame(history_data)
        temp_config.history_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(temp_config.history_file, index=False)
        
        # Create new calculator instance
        calc2 = Calculator(config=temp_config)
        assert len(calc2.history) == 1

    def test_init_handles_history_load_failure(self, temp_config):
        """Test that initialization handles history load failures gracefully."""
        with patch.object(Calculator, 'load_history', side_effect=Exception("Load error")):
            calc = Calculator(config=temp_config)
            # Should not raise, just log warning


class TestLoggingSetup:
    """Tests for logging configuration."""

    def test_setup_logging_creates_directory(self, temp_config):
        """Test that logging setup creates log directory."""
        if temp_config.history_file.exists():
            temp_config.history_file.unlink()
        calc = Calculator(config=temp_config)
        assert temp_config.log_dir.exists()

    def test_setup_logging_creates_log_file(self, temp_config):
        """Test that logging creates log file."""
        if temp_config.history_file.exists():
            temp_config.history_file.unlink()
        calc = Calculator(config=temp_config)
        logging.info("Test message")
        assert temp_config.log_file.exists()

    def test_setup_logging_failure(self, temp_config):
        """Test handling of logging setup failure."""
        with patch('app.calculator.logging.basicConfig', side_effect=Exception("Logging error")):
            with pytest.raises(Exception):
                Calculator(config=temp_config)


class TestDirectorySetup:
    """Tests for directory creation."""

    def test_setup_directories_creates_history_dir(self, temp_config):
        """Test that directory setup creates history directory."""
        if temp_config.history_file.exists():
            temp_config.history_file.unlink()
        calc = Calculator(config=temp_config)
        assert temp_config.history_dir.exists()


class TestObserverPattern:
    """Tests for Observer pattern implementation."""

    def test_add_observer(self, calculator):
        """Test adding an observer."""
        observer = Mock(spec=HistoryObserver)
        calculator.add_observer(observer)
        assert observer in calculator.observers

    def test_add_multiple_observers(self, calculator):
        """Test adding multiple observers."""
        observer1 = Mock(spec=HistoryObserver)
        observer2 = Mock(spec=HistoryObserver)
        calculator.add_observer(observer1)
        calculator.add_observer(observer2)
        assert len(calculator.observers) == 2

    def test_remove_observer(self, calculator):
        """Test removing an observer."""
        observer = Mock(spec=HistoryObserver)
        calculator.add_observer(observer)
        calculator.remove_observer(observer)
        assert observer not in calculator.observers

    def test_notify_observers(self, calculator):
        """Test that observers are notified of new calculations."""
        observer1 = Mock(spec=HistoryObserver)
        observer2 = Mock(spec=HistoryObserver)
        calculator.add_observer(observer1)
        calculator.add_observer(observer2)
        
        # Create a proper calculation
        calc = Calculation(
            operation="Addition",
            operand1=Decimal('5'),
            operand2=Decimal('10')
        )
        
        calculator.notify_observers(calc)
        
        observer1.update.assert_called_once_with(calc)
        observer2.update.assert_called_once_with(calc)


class TestOperationStrategy:
    """Tests for operation strategy pattern."""

    def test_set_operation(self, calculator, mock_operation):
        """Test setting an operation strategy."""
        calculator.set_operation(mock_operation)
        assert calculator.operation_strategy == mock_operation

    def test_perform_operation_without_strategy(self, calculator):
        """Test that performing operation without strategy raises error."""
        with pytest.raises(OperationError, match="No operation set"):
            calculator.perform_operation(5, 10)

    def test_perform_operation_success(self, calculator, mock_operation):
        """Test successful operation execution."""
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            mock_calc_instance = Mock()
            MockCalc.return_value = mock_calc_instance
            
            result = calculator.perform_operation(5, 10)
            
            assert result == Decimal('15')
            assert len(calculator.history) == 1
            assert len(calculator.undo_stack) == 1
            assert len(calculator.redo_stack) == 0

    def test_perform_operation_with_string_inputs(self, calculator, mock_operation):
        """Test operation with string inputs."""
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            mock_calc_instance = Mock()
            MockCalc.return_value = mock_calc_instance
            
            result = calculator.perform_operation("5", "10")
            assert result == Decimal('15')

    def test_perform_operation_validation_error(self, calculator, mock_operation):
        """Test that validation errors are raised and logged."""
        calculator.set_operation(mock_operation)
        with pytest.raises(ValidationError):
            calculator.perform_operation("invalid", "10")

    def test_perform_operation_execution_error(self, calculator, mock_operation):
        """Test that operation execution errors are handled."""
        mock_operation.execute.side_effect = Exception("Calculation error")
        calculator.set_operation(mock_operation)
        
        with pytest.raises(OperationError, match="Operation failed"):
            calculator.perform_operation(5, 10)

    def test_perform_operation_notifies_observers(self, calculator, mock_operation):
        """Test that observers are notified after operation."""
        observer = Mock(spec=HistoryObserver)
        calculator.add_observer(observer)
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            mock_calc_instance = Mock()
            MockCalc.return_value = mock_calc_instance
            
            calculator.perform_operation(5, 10)
            
            observer.update.assert_called_once()

    def test_perform_operation_respects_max_history(self, calculator, mock_operation):
        """Test that history respects maximum size."""
        calculator.config.max_history_size = 2
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            # Create different mock instances for each call
            mock_instances = [Mock(), Mock(), Mock()]
            mock_instances[0].operand1 = Decimal('1')
            mock_instances[1].operand1 = Decimal('2')
            mock_instances[2].operand1 = Decimal('3')
            MockCalc.side_effect = mock_instances
            
            calculator.perform_operation(1, 1)
            calculator.perform_operation(2, 2)
            calculator.perform_operation(3, 3)
            
            assert len(calculator.history) == 2
            # First calculation should be removed
            assert calculator.history[0].operand1 == Decimal('2')


class TestHistoryManagement:
    """Tests for history management."""

    def test_show_history_empty(self, calculator):
        """Test showing empty history."""
        assert calculator.show_history() == []

    def test_show_history_with_calculations(self, calculator, mock_operation):
        """Test showing history with calculations."""
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            mock_calc_instance = Mock()
            MockCalc.return_value = mock_calc_instance
            
            calculator.perform_operation(5, 10)
        
        history = calculator.show_history()
        assert len(history) == 1

    def test_clear_history(self, calculator, mock_operation):
        """Test clearing history."""
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            mock_calc_instance = Mock()
            MockCalc.return_value = mock_calc_instance
            
            calculator.perform_operation(5, 10)
        
        calculator.undo_stack.append(Mock())
        calculator.redo_stack.append(Mock())
        
        calculator.clear_history()
        
        assert len(calculator.history) == 0
        assert len(calculator.undo_stack) == 0
        assert len(calculator.redo_stack) == 0

    def test_get_history_dataframe_empty(self, calculator):
        """Test getting empty history as DataFrame."""
        df = calculator.get_history_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_get_history_dataframe_with_data(self, calculator, mock_operation):
        """Test getting history as DataFrame with data."""
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            mock_calc_instance = Mock()
            MockCalc.return_value = mock_calc_instance
            
            calculator.perform_operation(5, 10)
        
        df = calculator.get_history_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert 'operation' in df.columns
        assert 'operand1' in df.columns
        assert 'operand2' in df.columns
        assert 'result' in df.columns
        assert 'timestamp' in df.columns


class TestHistoryPersistence:
    """Tests for saving and loading history."""

    def test_save_history_success(self, calculator, mock_operation):
        """Test saving history to file."""
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            mock_calc_instance = Mock()
            MockCalc.return_value = mock_calc_instance
            
            calculator.perform_operation(5, 10)
        
        calculator.save_history()
        
        assert calculator.config.history_file.exists()

    def test_save_empty_history(self, calculator):
        """Test saving empty history creates file with headers."""
        calculator.save_history()
        
        assert calculator.config.history_file.exists()
        df = pd.read_csv(calculator.config.history_file)
        assert len(df) == 0
        assert list(df.columns) == ['operation', 'operand1', 'operand2', 'result', 'timestamp']

    def test_save_history_creates_directory(self, temp_config):
        """Test that save_history creates directory if it doesn't exist."""
        if temp_config.history_file.exists():
            temp_config.history_file.unlink()
        
        calc = Calculator(config=temp_config)
        calc.history.clear()
        
        # Remove the directory
        import shutil
        if temp_config.history_dir.exists():
            shutil.rmtree(temp_config.history_dir)
        
        calc.save_history()
        assert temp_config.history_dir.exists()

    def test_save_history_failure(self, calculator, mock_operation):
        """Test handling of save history failure."""
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            mock_calc_instance = Mock()
            MockCalc.return_value = mock_calc_instance
            
            calculator.perform_operation(5, 10)
        
        with patch('pandas.DataFrame.to_csv', side_effect=Exception("Write error")):
            with pytest.raises(OperationError, match="Failed to save history"):
                calculator.save_history()

    def test_load_history_success(self, calculator, mock_operation):
        """Test loading history from file."""
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            mock_calc_instance = Mock()
            mock_calc_instance.operation = "add"
            mock_calc_instance.operand1 = Decimal('5')
            mock_calc_instance.operand2 = Decimal('10')
            mock_calc_instance.result = Decimal('15')
            mock_calc_instance.timestamp = Mock()
            mock_calc_instance.timestamp.isoformat.return_value = '2024-01-01T00:00:00'
            MockCalc.return_value = mock_calc_instance
            
            calculator.perform_operation(5, 10)
            calculator.save_history()
        
        calculator.history.clear()
        
        # Patch Calculation.from_dict for loading
        with patch('app.calculation.Calculation.from_dict') as mock_from_dict:
            mock_loaded_calc = Mock()
            mock_from_dict.return_value = mock_loaded_calc
            calculator.load_history()
        
        assert len(calculator.history) == 1

    def test_load_history_no_file(self, calculator):
        """Test loading history when file doesn't exist."""
        # Ensure file doesn't exist
        if calculator.config.history_file.exists():
            calculator.config.history_file.unlink()
        
        calculator.history.clear()
        calculator.load_history()
        assert calculator.history == []

    def test_load_history_empty_file(self, calculator):
        """Test loading empty history file."""
        calculator.history.clear()
        calculator.save_history()  # Creates empty file
        calculator.load_history()
        assert calculator.history == []

    def test_load_history_failure(self, calculator):
        """Test handling of load history failure."""
        # Create a file so that the load will actually try to read it
        calculator.save_history()
        
        with patch('pandas.read_csv', side_effect=Exception("Read error")):
            with pytest.raises(OperationError, match="Failed to load history"):
                calculator.load_history()


class TestUndoRedo:
    """Tests for undo/redo functionality."""

    def test_undo_with_empty_stack(self, calculator):
        """Test undo with no operations to undo."""
        assert calculator.undo() is False

    def test_undo_success(self, calculator, mock_operation):
        """Test successful undo."""
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            mock_calc_instance = Mock()
            MockCalc.return_value = mock_calc_instance
            
            calculator.perform_operation(5, 10)
        
        assert len(calculator.history) == 1
        result = calculator.undo()
        
        assert result is True
        assert len(calculator.history) == 0
        assert len(calculator.redo_stack) == 1

    def test_undo_multiple_operations(self, calculator, mock_operation):
        """Test undoing multiple operations."""
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            MockCalc.return_value = Mock()
            
            calculator.perform_operation(1, 1)
            calculator.perform_operation(2, 2)
            calculator.perform_operation(3, 3)
        
        calculator.undo()
        assert len(calculator.history) == 2
        calculator.undo()
        assert len(calculator.history) == 1

    def test_redo_with_empty_stack(self, calculator):
        """Test redo with no operations to redo."""
        assert calculator.redo() is False

    def test_redo_success(self, calculator, mock_operation):
        """Test successful redo."""
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            mock_calc_instance = Mock()
            MockCalc.return_value = mock_calc_instance
            
            calculator.perform_operation(5, 10)
        
        calculator.undo()
        
        result = calculator.redo()
        
        assert result is True
        assert len(calculator.history) == 1
        assert len(calculator.undo_stack) == 1  # Changed from 2 to 1

    def test_redo_after_new_operation_clears_stack(self, calculator, mock_operation):
        """Test that new operation clears redo stack."""
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            MockCalc.return_value = Mock()
            
            calculator.perform_operation(5, 10)
            calculator.undo()
            
            assert len(calculator.redo_stack) == 1
            
            calculator.perform_operation(3, 3)
            
            assert len(calculator.redo_stack) == 0

    def test_undo_redo_chain(self, calculator, mock_operation):
        """Test chaining undo and redo operations."""
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            MockCalc.return_value = Mock()
            
            calculator.perform_operation(1, 1)
            calculator.perform_operation(2, 2)
        
        assert len(calculator.history) == 2
        
        calculator.undo()
        calculator.undo()
        assert len(calculator.history) == 0
        
        calculator.redo()
        assert len(calculator.history) == 1
        
        calculator.redo()
        assert len(calculator.history) == 2


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_operation_with_decimal_inputs(self, calculator, mock_operation):
        """Test operation with Decimal inputs."""
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            mock_calc_instance = Mock()
            MockCalc.return_value = mock_calc_instance
            
            result = calculator.perform_operation(Decimal('5.5'), Decimal('10.5'))
            assert result == Decimal('15')

    def test_operation_with_float_inputs(self, calculator, mock_operation):
        """Test operation with float inputs."""
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            mock_calc_instance = Mock()
            MockCalc.return_value = mock_calc_instance
            
            result = calculator.perform_operation(5.5, 10.5)
            assert result == Decimal('15')

    def test_operation_with_int_inputs(self, calculator, mock_operation):
        """Test operation with integer inputs."""
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            mock_calc_instance = Mock()
            MockCalc.return_value = mock_calc_instance
            
            result = calculator.perform_operation(5, 10)
            assert result == Decimal('15')

    def test_history_at_max_size(self, calculator, mock_operation):
        """Test behavior when history reaches maximum size."""
        calculator.config.max_history_size = 3
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            MockCalc.return_value = Mock()
            
            for i in range(5):
                calculator.perform_operation(i, i)
        
        assert len(calculator.history) == 3

    def test_multiple_observer_notifications(self, calculator, mock_operation):
        """Test that multiple observers all receive notifications."""
        observers = [Mock(spec=HistoryObserver) for _ in range(3)]
        for observer in observers:
            calculator.add_observer(observer)
        
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            mock_calc_instance = Mock()
            MockCalc.return_value = mock_calc_instance
            
            calculator.perform_operation(5, 10)
        
        for observer in observers:
            assert observer.update.call_count == 1


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_complete_calculation_workflow(self, calculator, mock_operation):
        """Test complete workflow from operation to history save."""
        observer = Mock(spec=HistoryObserver)
        calculator.add_observer(observer)
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            mock_calc_instance = Mock()
            mock_calc_instance.operation = "add"
            mock_calc_instance.operand1 = Decimal('5')
            mock_calc_instance.operand2 = Decimal('10')
            mock_calc_instance.result = Decimal('15')
            mock_calc_instance.timestamp = Mock()
            mock_calc_instance.timestamp.isoformat.return_value = '2024-01-01T00:00:00'
            MockCalc.return_value = mock_calc_instance
            
            # Perform calculation
            result = calculator.perform_operation(5, 10)
            assert result == Decimal('15')
        
        # Check history
        assert len(calculator.history) == 1
        
        # Check observer notified
        observer.update.assert_called_once()
        
        # Save history
        calculator.save_history()
        assert calculator.config.history_file.exists()
        
        # Clear and reload
        calculator.history.clear()
        
        # Patch Calculation.from_dict for loading
        with patch('app.calculation.Calculation.from_dict') as mock_from_dict:
            mock_loaded_calc = Mock()
            mock_from_dict.return_value = mock_loaded_calc
            calculator.load_history()
        
        assert len(calculator.history) == 1

    def test_undo_redo_with_save_load(self, calculator, mock_operation):
        """Test undo/redo with history persistence."""
        calculator.set_operation(mock_operation)
        
        with patch('app.calculator.Calculation') as MockCalc:
            MockCalc.return_value = Mock()
            
            calculator.perform_operation(1, 1)
            calculator.perform_operation(2, 2)
        
        calculator.save_history()
        
        calculator.undo()
        assert len(calculator.history) == 1
        
        calculator.redo()
        assert len(calculator.history) == 2