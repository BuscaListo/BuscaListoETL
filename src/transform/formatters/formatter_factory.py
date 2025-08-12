"""
Formatter factory module implementing Factory Pattern.

This module provides centralized creation of formatter instances
following SOLID principles and PEP 8 standards.
"""

import logging
from typing import Type
from formatters.base_formatter import BaseFormatter
from formatters.product_formatter import ProductFormatter

logger = logging.getLogger(__name__)


class FormatterFactory:
    """
    Factory class for creating formatter instances.
    
    Implements Factory Pattern to provide centralized formatter creation
    and management. Follows Open/Closed Principle (OCP) - open for
    extension, closed for modification.
    
    Class Attributes:
        _formatters: Dictionary mapping model names to formatter classes
    """
    
    _formatters: dict[str, Type[BaseFormatter]] = {
        "product": ProductFormatter,
        "productmodel": ProductFormatter,  # Alternative naming
    }
    
    @classmethod
    def create_formatter(cls, model_type: str) -> BaseFormatter:
        """
        Create formatter instance for specified model type.
        
        Args:
            model_type: Type of model to format (e.g., 'product')
            
        Returns:
            Formatter instance for the specified model type
            
        Raises:
            ValueError: If model_type is not supported
            
        Example:
            >>> formatter = FormatterFactory.create_formatter('product')
            >>> json_data = formatter.format_to_json(data)
        """
        model_key = model_type.lower().strip()
        formatter_class = cls._formatters.get(model_key)
        
        if not formatter_class:
            available_models = ', '.join(cls._formatters.keys())
            error_msg = (
                f"Formatter for model '{model_type}' not found. "
                f"Available models: {available_models}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Creating formatter for model: {model_type}")
        return formatter_class()
    
    @classmethod
    def get_available_models(cls) -> list[str]:
        """
        Get list of available model types for formatting.
        
        Returns:
            List of supported model type identifiers
        """
        return list(cls._formatters.keys())
    
    @classmethod
    def create_all_formatters(cls) -> dict[str, BaseFormatter]:
        """
        Create instances of all available formatters.
        
        Useful for batch processing or initialization scenarios.
        
        Returns:
            Dictionary mapping model names to formatter instances
        """
        formatters = {}
        for model_name in cls._formatters.keys():
            try:
                formatters[model_name] = cls.create_formatter(model_name)
                logger.info(f"Successfully created formatter for: {model_name}")
            except ValueError as e:
                logger.error(f"Failed to create formatter for {model_name}: {e}")
        
        return formatters
    
    @classmethod
    def register_formatter(
        cls, 
        model_type: str, 
        formatter_class: Type[BaseFormatter]
    ) -> None:
        """
        Register new formatter class for a model type.
        
        Allows dynamic registration of new formatters without modifying
        the factory class (Open/Closed Principle).
        
        Args:
            model_type: Model type identifier
            formatter_class: Formatter class to register
            
        Raises:
            TypeError: If formatter_class is not a BaseFormatter subclass
            
        Example:
            >>> FormatterFactory.register_formatter('inventory', InventoryFormatter)
        """
        if not issubclass(formatter_class, BaseFormatter):
            raise TypeError(
                f"Formatter class must inherit from BaseFormatter, "
                f"got: {formatter_class.__name__}"
            )
        
        model_key = model_type.lower().strip()
        cls._formatters[model_key] = formatter_class
        logger.info(f"Registered formatter for model: {model_type}")
    
    @classmethod
    def is_model_supported(cls, model_type: str) -> bool:
        """
        Check if a model type is supported by the factory.
        
        Args:
            model_type: Model type to check
            
        Returns:
            True if model is supported, False otherwise
        """
        return model_type.lower().strip() in cls._formatters