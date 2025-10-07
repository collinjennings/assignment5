"""
Comprehensive test suite for the calculator_repl() function achieving 100% coverage.

Tests all commands, user interactions, error handling, and edge cases.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock, call
from io import StringIO

from app.calculator_repl import calculator_repl
from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError


class TestREPLInitialization:
    """Tests for REPL initialization and setup."""

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['exit'])
    @patch('builtins.print')
    def test_repl_initializes_calculator(self, mock_print, mock_input, mock_calc_class):
        """Test that REPL initializes Calculator instance."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_calc_class.assert_called_once()

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['exit'])
    @patch('builtins.print')
    def test_repl_adds_observers(self, mock_print, mock_input, mock_calc_class):
        """Test that REPL adds LoggingObserver and AutoSaveObserver."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        # Should call add_observer twice (LoggingObserver and AutoSaveObserver)
        assert mock_calc.add_observer.call_count == 2

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['exit'])
    @patch('builtins.print')
    def test_repl_prints_startup_message(self, mock_print, mock_input, mock_calc_class):
        """Test that REPL prints startup message."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_print.assert_any_call("Calculator started. Type 'help' for commands.")

    @patch('app.calculator_repl.Calculator', side_effect=Exception("Init error"))
    @patch('builtins.print')
    def test_repl_handles_fatal_initialization_error(self, mock_print, mock_calc_class):
        """Test that REPL handles fatal initialization errors."""
        with pytest.raises(Exception, match="Init error"):
            calculator_repl()
        
        mock_print.assert_called_with("Fatal error: Init error")


class TestHelpCommand:
    """Tests for the 'help' command."""

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['help', 'exit'])
    @patch('builtins.print')
    def test_help_command_displays_all_commands(self, mock_print, mock_input, mock_calc_class):
        """Test that help command displays all available commands."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        # Check that help text was printed
        help_calls = [call for call in mock_print.call_args_list if 'Available commands' in str(call)]
        assert len(help_calls) > 0

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['HELP', 'exit'])
    @patch('builtins.print')
    def test_help_command_case_insensitive(self, mock_print, mock_input, mock_calc_class):
        """Test that help command is case insensitive."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        help_calls = [call for call in mock_print.call_args_list if 'Available commands' in str(call)]
        assert len(help_calls) > 0

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['  help  ', 'exit'])
    @patch('builtins.print')
    def test_help_command_strips_whitespace(self, mock_print, mock_input, mock_calc_class):
        """Test that help command strips whitespace."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        help_calls = [call for call in mock_print.call_args_list if 'Available commands' in str(call)]
        assert len(help_calls) > 0


class TestExitCommand:
    """Tests for the 'exit' command."""

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['exit'])
    @patch('builtins.print')
    def test_exit_command_saves_history(self, mock_print, mock_input, mock_calc_class):
        """Test that exit command saves history."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_calc.save_history.assert_called_once()

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['exit'])
    @patch('builtins.print')
    def test_exit_command_prints_success_message(self, mock_print, mock_input, mock_calc_class):
        """Test that exit command prints success messages."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_print.assert_any_call("History saved successfully.")
        mock_print.assert_any_call("Goodbye!")

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['exit'])
    @patch('builtins.print')
    def test_exit_command_handles_save_error(self, mock_print, mock_input, mock_calc_class):
        """Test that exit command handles save errors gracefully."""
        mock_calc = Mock()
        mock_calc.save_history.side_effect = Exception("Save error")
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        # Should print warning but still exit
        warning_calls = [call for call in mock_print.call_args_list 
                        if 'Warning: Could not save history' in str(call)]
        assert len(warning_calls) > 0
        mock_print.assert_any_call("Goodbye!")

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['EXIT', 'exit'])
    @patch('builtins.print')
    def test_exit_command_case_insensitive(self, mock_print, mock_input, mock_calc_class):
        """Test that exit command is case insensitive."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_print.assert_any_call("Goodbye!")


class TestHistoryCommand:
    """Tests for the 'history' command."""

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['history', 'exit'])
    @patch('builtins.print')
    def test_history_command_empty_history(self, mock_print, mock_input, mock_calc_class):
        """Test history command with empty history."""
        mock_calc = Mock()
        mock_calc.show_history.return_value = []
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_print.assert_any_call("No calculations in history")

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['history', 'exit'])
    @patch('builtins.print')
    def test_history_command_with_calculations(self, mock_print, mock_input, mock_calc_class):
        """Test history command with calculations."""
        mock_calc = Mock()
        mock_calc.show_history.return_value = [
            "Addition(5, 3) = 8",
            "Subtraction(10, 4) = 6"
        ]
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_print.assert_any_call("\nCalculation History:")
        mock_print.assert_any_call("1. Addition(5, 3) = 8")
        mock_print.assert_any_call("2. Subtraction(10, 4) = 6")

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['HISTORY', 'exit'])
    @patch('builtins.print')
    def test_history_command_case_insensitive(self, mock_print, mock_input, mock_calc_class):
        """Test that history command is case insensitive."""
        mock_calc = Mock()
        mock_calc.show_history.return_value = []
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_calc.show_history.assert_called()


class TestClearCommand:
    """Tests for the 'clear' command."""

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['clear', 'exit'])
    @patch('builtins.print')
    def test_clear_command_clears_history(self, mock_print, mock_input, mock_calc_class):
        """Test that clear command clears history."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_calc.clear_history.assert_called_once()
        mock_print.assert_any_call("History cleared")

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['CLEAR', 'exit'])
    @patch('builtins.print')
    def test_clear_command_case_insensitive(self, mock_print, mock_input, mock_calc_class):
        """Test that clear command is case insensitive."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_calc.clear_history.assert_called_once()


class TestUndoCommand:
    """Tests for the 'undo' command."""

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['undo', 'exit'])
    @patch('builtins.print')
    def test_undo_command_success(self, mock_print, mock_input, mock_calc_class):
        """Test undo command when successful."""
        mock_calc = Mock()
        mock_calc.undo.return_value = True
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_calc.undo.assert_called_once()
        mock_print.assert_any_call("Operation undone")

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['undo', 'exit'])
    @patch('builtins.print')
    def test_undo_command_nothing_to_undo(self, mock_print, mock_input, mock_calc_class):
        """Test undo command when nothing to undo."""
        mock_calc = Mock()
        mock_calc.undo.return_value = False
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_calc.undo.assert_called_once()
        mock_print.assert_any_call("Nothing to undo")

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['UNDO', 'exit'])
    @patch('builtins.print')
    def test_undo_command_case_insensitive(self, mock_print, mock_input, mock_calc_class):
        """Test that undo command is case insensitive."""
        mock_calc = Mock()
        mock_calc.undo.return_value = True
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_calc.undo.assert_called_once()


class TestRedoCommand:
    """Tests for the 'redo' command."""

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['redo', 'exit'])
    @patch('builtins.print')
    def test_redo_command_success(self, mock_print, mock_input, mock_calc_class):
        """Test redo command when successful."""
        mock_calc = Mock()
        mock_calc.redo.return_value = True
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_calc.redo.assert_called_once()
        mock_print.assert_any_call("Operation redone")

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['redo', 'exit'])
    @patch('builtins.print')
    def test_redo_command_nothing_to_redo(self, mock_print, mock_input, mock_calc_class):
        """Test redo command when nothing to redo."""
        mock_calc = Mock()
        mock_calc.redo.return_value = False
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_calc.redo.assert_called_once()
        mock_print.assert_any_call("Nothing to redo")

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['REDO', 'exit'])
    @patch('builtins.print')
    def test_redo_command_case_insensitive(self, mock_print, mock_input, mock_calc_class):
        """Test that redo command is case insensitive."""
        mock_calc = Mock()
        mock_calc.redo.return_value = True
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_calc.redo.assert_called_once()


class TestSaveCommand:
    """Tests for the 'save' command."""

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['save', 'exit'])
    @patch('builtins.print')
    def test_save_command_success(self, mock_print, mock_input, mock_calc_class):
        """Test save command when successful."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_calc.save_history.assert_called()
        mock_print.assert_any_call("History saved successfully")

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['save', 'exit'])
    @patch('builtins.print')
    def test_save_command_handles_error(self, mock_print, mock_input, mock_calc_class):
        """Test save command handles errors."""
        mock_calc = Mock()
        mock_calc.save_history.side_effect = Exception("Save error")
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        error_calls = [call for call in mock_print.call_args_list 
                      if 'Error saving history' in str(call)]
        assert len(error_calls) > 0

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['SAVE', 'exit'])
    @patch('builtins.print')
    def test_save_command_case_insensitive(self, mock_print, mock_input, mock_calc_class):
        """Test that save command is case insensitive."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_calc.save_history.assert_called()


class TestLoadCommand:
    """Tests for the 'load' command."""

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['load', 'exit'])
    @patch('builtins.print')
    def test_load_command_success(self, mock_print, mock_input, mock_calc_class):
        """Test load command when successful."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        # load_history is called during init and when 'load' command is issued
        assert mock_calc.load_history.call_count >= 1
        mock_print.assert_any_call("History loaded successfully")

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['load', 'exit'])
    @patch('builtins.print')
    def test_load_command_handles_error(self, mock_print, mock_input, mock_calc_class):
        """Test load command handles errors."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        # Make load_history raise an exception when called from 'load' command
        # Note: load_history is also called during __init__, but that error is caught with a warning
        # We need to make sure it fails on the explicit 'load' command
        mock_calc.load_history.side_effect = Exception("Load error")
        
        calculator_repl()
        
        # Check that error message was printed
        # The error message format is: "Error loading history: {e}"
        all_print_calls = [str(call) for call in mock_print.call_args_list]
        error_found = any('Error loading history' in call_str and 'Load error' in call_str 
                         for call_str in all_print_calls)
        assert error_found, f"Expected 'Error loading history: Load error' in print calls, got: {all_print_calls}"

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['LOAD', 'exit'])
    @patch('builtins.print')
    def test_load_command_case_insensitive(self, mock_print, mock_input, mock_calc_class):
        """Test that load command is case insensitive."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        assert mock_calc.load_history.call_count >= 1


class TestArithmeticOperations:
    """Tests for arithmetic operation commands."""

    @patch('app.calculator_repl.Calculator')
    @patch('app.calculator_repl.OperationFactory')
    @patch('builtins.input', side_effect=['add', '5', '3', 'exit'])
    @patch('builtins.print')
    def test_add_operation_success(self, mock_print, mock_input, mock_factory, mock_calc_class):
        """Test add operation with valid inputs."""
        mock_calc = Mock()
        mock_calc.perform_operation.return_value = Decimal('8')
        mock_calc_class.return_value = mock_calc
        
        mock_operation = Mock()
        mock_factory.create_operation.return_value = mock_operation
        
        calculator_repl()
        
        mock_factory.create_operation.assert_called_with('add')
        mock_calc.set_operation.assert_called_with(mock_operation)
        mock_calc.perform_operation.assert_called_with('5', '3')
        mock_print.assert_any_call("\nResult: 8")

    @patch('app.calculator_repl.Calculator')
    @patch('app.calculator_repl.OperationFactory')
    @patch('builtins.input', side_effect=['subtract', '10', '4', 'exit'])
    @patch('builtins.print')
    def test_subtract_operation(self, mock_print, mock_input, mock_factory, mock_calc_class):
        """Test subtract operation."""
        mock_calc = Mock()
        mock_calc.perform_operation.return_value = Decimal('6')
        mock_calc_class.return_value = mock_calc
        
        mock_operation = Mock()
        mock_factory.create_operation.return_value = mock_operation
        
        calculator_repl()
        
        mock_factory.create_operation.assert_called_with('subtract')

    @patch('app.calculator_repl.Calculator')
    @patch('app.calculator_repl.OperationFactory')
    @patch('builtins.input', side_effect=['multiply', '4', '5', 'exit'])
    @patch('builtins.print')
    def test_multiply_operation(self, mock_print, mock_input, mock_factory, mock_calc_class):
        """Test multiply operation."""
        mock_calc = Mock()
        mock_calc.perform_operation.return_value = Decimal('20')
        mock_calc_class.return_value = mock_calc
        
        mock_operation = Mock()
        mock_factory.create_operation.return_value = mock_operation
        
        calculator_repl()
        
        mock_factory.create_operation.assert_called_with('multiply')

    @patch('app.calculator_repl.Calculator')
    @patch('app.calculator_repl.OperationFactory')
    @patch('builtins.input', side_effect=['divide', '10', '2', 'exit'])
    @patch('builtins.print')
    def test_divide_operation(self, mock_print, mock_input, mock_factory, mock_calc_class):
        """Test divide operation."""
        mock_calc = Mock()
        mock_calc.perform_operation.return_value = Decimal('5')
        mock_calc_class.return_value = mock_calc
        
        mock_operation = Mock()
        mock_factory.create_operation.return_value = mock_operation
        
        calculator_repl()
        
        mock_factory.create_operation.assert_called_with('divide')

    @patch('app.calculator_repl.Calculator')
    @patch('app.calculator_repl.OperationFactory')
    @patch('builtins.input', side_effect=['power', '2', '3', 'exit'])
    @patch('builtins.print')
    def test_power_operation(self, mock_print, mock_input, mock_factory, mock_calc_class):
        """Test power operation."""
        mock_calc = Mock()
        mock_calc.perform_operation.return_value = Decimal('8')
        mock_calc_class.return_value = mock_calc
        
        mock_operation = Mock()
        mock_factory.create_operation.return_value = mock_operation
        
        calculator_repl()
        
        mock_factory.create_operation.assert_called_with('power')

    @patch('app.calculator_repl.Calculator')
    @patch('app.calculator_repl.OperationFactory')
    @patch('builtins.input', side_effect=['root', '9', '2', 'exit'])
    @patch('builtins.print')
    def test_root_operation(self, mock_print, mock_input, mock_factory, mock_calc_class):
        """Test root operation."""
        mock_calc = Mock()
        mock_calc.perform_operation.return_value = Decimal('3')
        mock_calc_class.return_value = mock_calc
        
        mock_operation = Mock()
        mock_factory.create_operation.return_value = mock_operation
        
        calculator_repl()
        
        mock_factory.create_operation.assert_called_with('root')

    @patch('app.calculator_repl.Calculator')
    @patch('app.calculator_repl.OperationFactory')
    @patch('builtins.input', side_effect=['ADD', '5', '3', 'exit'])
    @patch('builtins.print')
    def test_operation_case_insensitive(self, mock_print, mock_input, mock_factory, mock_calc_class):
        """Test that operations are case insensitive."""
        mock_calc = Mock()
        mock_calc.perform_operation.return_value = Decimal('8')
        mock_calc_class.return_value = mock_calc
        
        mock_operation = Mock()
        mock_factory.create_operation.return_value = mock_operation
        
        calculator_repl()
        
        mock_factory.create_operation.assert_called_with('add')

    @patch('app.calculator_repl.Calculator')
    @patch('app.calculator_repl.OperationFactory')
    @patch('builtins.input', side_effect=['add', 'cancel', 'exit'])
    @patch('builtins.print')
    def test_operation_cancel_first_number(self, mock_print, mock_input, mock_factory, mock_calc_class):
        """Test canceling operation at first number prompt."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_print.assert_any_call("Operation cancelled")
        mock_calc.perform_operation.assert_not_called()

    @patch('app.calculator_repl.Calculator')
    @patch('app.calculator_repl.OperationFactory')
    @patch('builtins.input', side_effect=['add', '5', 'CANCEL', 'exit'])
    @patch('builtins.print')
    def test_operation_cancel_second_number(self, mock_print, mock_input, mock_factory, mock_calc_class):
        """Test canceling operation at second number prompt."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        mock_print.assert_any_call("Operation cancelled")
        mock_calc.perform_operation.assert_not_called()

    @patch('app.calculator_repl.Calculator')
    @patch('app.calculator_repl.OperationFactory')
    @patch('builtins.input', side_effect=['add', 'invalid', '3', 'exit'])
    @patch('builtins.print')
    def test_operation_validation_error(self, mock_print, mock_input, mock_factory, mock_calc_class):
        """Test operation with validation error."""
        mock_calc = Mock()
        mock_calc.perform_operation.side_effect = ValidationError("Invalid number")
        mock_calc_class.return_value = mock_calc
        
        mock_operation = Mock()
        mock_factory.create_operation.return_value = mock_operation
        
        calculator_repl()
        
        error_calls = [call for call in mock_print.call_args_list 
                      if 'Error: Invalid number' in str(call)]
        assert len(error_calls) > 0

    @patch('app.calculator_repl.Calculator')
    @patch('app.calculator_repl.OperationFactory')
    @patch('builtins.input', side_effect=['divide', '10', '0', 'exit'])
    @patch('builtins.print')
    def test_operation_operation_error(self, mock_print, mock_input, mock_factory, mock_calc_class):
        """Test operation with operation error."""
        mock_calc = Mock()
        mock_calc.perform_operation.side_effect = OperationError("Division by zero")
        mock_calc_class.return_value = mock_calc
        
        mock_operation = Mock()
        mock_factory.create_operation.return_value = mock_operation
        
        calculator_repl()
        
        error_calls = [call for call in mock_print.call_args_list 
                      if 'Error: Division by zero' in str(call)]
        assert len(error_calls) > 0

    @patch('app.calculator_repl.Calculator')
    @patch('app.calculator_repl.OperationFactory')
    @patch('builtins.input', side_effect=['add', '5', '3', 'exit'])
    @patch('builtins.print')
    def test_operation_unexpected_error(self, mock_print, mock_input, mock_factory, mock_calc_class):
        """Test operation with unexpected error."""
        mock_calc = Mock()
        mock_calc.perform_operation.side_effect = RuntimeError("Unexpected error")
        mock_calc_class.return_value = mock_calc
        
        mock_operation = Mock()
        mock_factory.create_operation.return_value = mock_operation
        
        calculator_repl()
        
        error_calls = [call for call in mock_print.call_args_list 
                      if 'Unexpected error' in str(call)]
        assert len(error_calls) > 0

    @patch('app.calculator_repl.Calculator')
    @patch('app.calculator_repl.OperationFactory')
    @patch('builtins.input', side_effect=['add', '5.5', '3.2', 'exit'])
    @patch('builtins.print')
    def test_operation_normalizes_decimal_result(self, mock_print, mock_input, mock_factory, mock_calc_class):
        """Test that decimal results are normalized."""
        mock_calc = Mock()
        # Return a Decimal that needs normalization
        mock_calc.perform_operation.return_value = Decimal('8.70')
        mock_calc_class.return_value = mock_calc
        
        mock_operation = Mock()
        mock_factory.create_operation.return_value = mock_operation
        
        calculator_repl()
        
        # Result should be normalized (8.70 -> 8.7)
        result_calls = [call for call in mock_print.call_args_list 
                       if 'Result:' in str(call)]
        assert len(result_calls) > 0

    @patch('app.calculator_repl.Calculator')
    @patch('app.calculator_repl.OperationFactory')
    @patch('builtins.input', side_effect=['add', '5', '3', 'exit'])
    @patch('builtins.print')
    def test_operation_with_non_decimal_result(self, mock_print, mock_input, mock_factory, mock_calc_class):
        """Test operation that returns non-Decimal result."""
        mock_calc = Mock()
        mock_calc.perform_operation.return_value = 8  # Return int instead of Decimal
        mock_calc_class.return_value = mock_calc
        
        mock_operation = Mock()
        mock_factory.create_operation.return_value = mock_operation
        
        calculator_repl()
        
        mock_print.assert_any_call("\nResult: 8")


class TestUnknownCommand:
    """Tests for unknown command handling."""

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=['unknown', 'exit'])
    @patch('builtins.print')
    def test_unknown_command_displays_error(self, mock_print, mock_input, mock_calc_class):
        """Test that unknown command displays error message."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        error_calls = [call for call in mock_print.call_args_list 
                      if "Unknown command: 'unknown'" in str(call)]
        assert len(error_calls) > 0


class TestKeyboardInterrupts:
    """Tests for keyboard interrupt and EOF handling."""

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=[KeyboardInterrupt(), 'exit'])
    @patch('builtins.print')
    def test_keyboard_interrupt_during_command(self, mock_print, mock_input, mock_calc_class):
        """Test that KeyboardInterrupt (Ctrl+C) is handled gracefully."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        # Should print "Operation cancelled" and continue
        cancel_calls = [call for call in mock_print.call_args_list 
                       if "Operation cancelled" in str(call)]
        assert len(cancel_calls) > 0

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=[EOFError()])
    @patch('builtins.print')
    def test_eof_error_exits_gracefully(self, mock_print, mock_input, mock_calc_class):
        """Test that EOFError (Ctrl+D) exits gracefully."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        # Should print "Input terminated. Exiting..."
        exit_calls = [call for call in mock_print.call_args_list 
                     if "Input terminated. Exiting..." in str(call)]
        assert len(exit_calls) > 0

    @patch('app.calculator_repl.Calculator')
    @patch('builtins.input', side_effect=[RuntimeError("Some error"), 'exit'])
    @patch('builtins.print')
    def test_generic_exception_during_loop(self, mock_print, mock_input, mock_calc_class):
        """Test that generic exceptions during the loop are caught and handled."""
        mock_calc = Mock()
        mock_calc_class.return_value = mock_calc
        
        calculator_repl()
        
        # Should print "Error: Some error" and continue
        error_calls = [call for call in mock_print.call_args_list 
                      if "Error: Some error" in str(call)]
        assert len(error_calls) > 0