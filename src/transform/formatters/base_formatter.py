"""
Base formatter module following SOLID principles and PEP 8 standards.

This module provides the abstract base class for all data formatters
in the ETL transformation process.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseFormatter(ABC):
    """
    Abstract base class for all data formatters.
    
    Follows Single Responsibility Principle (SRP) - each formatter
    handles formatting for a specific model type.
    
    Attributes:
        model_name (str): Name of the target model for formatting
    """
    
    def __init__(self, model_name: str) -> None:
        """
        Initialize the formatter with target model name.
        
        Args:
            model_name: Name of the target model for formatting
        """
        self.model_name = model_name
    
    @abstractmethod
    def format_to_json(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Format data to JSON structure for the target model.
        
        Args:
            data: List of dictionaries containing raw data
            
        Returns:
            Formatted data as dictionary ready for JSON serialization
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass
    
    @abstractmethod
    def format_to_csv(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Format data to CSV-compatible structure for the target model.
        
        Args:
            data: List of dictionaries containing raw data
            
        Returns:
            List of dictionaries ready for CSV conversion
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass
    
    @abstractmethod
    def get_formatter_name(self) -> str:
        """
        Get the name of this formatter.
        
        Returns:
            String identifier for this formatter
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass
    
    def validate_data(self, data: list[dict[str, Any]]) -> bool:
        """
        Validate input data structure.
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        return isinstance(data, list) and len(data) > 0
    
    def get_model_name(self) -> str:
        """
        Get the target model name for this formatter.
        
        Returns:
            Target model name
        """
        return self.model_name