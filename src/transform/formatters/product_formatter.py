"""
Product formatter module for ETL transformation process.

This module handles formatting of product data following SOLID principles
and PEP 8 standards.
"""

import logging
from typing import Any
from formatters.base_formatter import BaseFormatter

logger = logging.getLogger(__name__)


class ProductFormatter(BaseFormatter):
    """
    Formatter for product data model.
    
    Handles formatting of product data to different output formats
    while maintaining data integrity and structure.
    
    Follows Single Responsibility Principle (SRP) - only handles
    product model formatting.
    """
    
    def __init__(self) -> None:
        """Initialize ProductFormatter with product model configuration."""
        super().__init__("ProductModel")
    
    def format_to_json(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Format product data to JSON structure.
        
        Creates a complete JSON structure with metadata and product list
        suitable for API responses and data interchange.
        
        Args:
            data: List of product dictionaries from transformation result
            
        Returns:
            Dictionary with formatted product data and metadata
        """
        if not self.validate_data(data):
            logger.warning("Invalid data provided to ProductFormatter.format_to_json")
            return {
                "model": self.model_name,
                "total_products": 0,
                "products": [],
                "metadata": {
                    "format": "json",
                    "version": "1.0"
                }
            }
        
        return {
            "model": self.model_name,
            "total_products": len(data),
            "products": data,
            "metadata": {
                "format": "json",
                "version": "1.0",
                "fields": self._get_product_fields()
            }
        }
    
    def format_to_csv(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Format product data to CSV-compatible structure.
        
        Removes complex nested fields and prepares data for CSV export
        suitable for data analysis and reporting.
        
        Args:
            data: List of product dictionaries from transformation result
            
        Returns:
            List of dictionaries ready for CSV conversion
        """
        if not self.validate_data(data):
            logger.warning("Invalid data provided to ProductFormatter.format_to_csv")
            return []
        
        csv_data = []
        for product in data:
            # Remove raw_data for CSV (too complex for spreadsheet analysis)
            csv_product = {k: v for k, v in product.items() if k != 'raw_data'}
            csv_data.append(csv_product)
        
        logger.info(f"Formatted {len(csv_data)} products for CSV export")
        return csv_data
    
    def get_formatter_name(self) -> str:
        """
        Get the name identifier for this formatter.
        
        Returns:
            String identifier for ProductFormatter
        """
        return "ProductFormatter"
    
    def _get_product_fields(self) -> list[str]:
        """
        Get list of standard product fields.
        
        Private method that defines the expected fields for product model.
        
        Returns:
            List of field names for product model
        """
        return [
            "source",
            "product_id", 
            "name",
            "category",
            "price",
            "brand",
            "image_url",
            "is_promotion",
            "family",
            "is_visible",
            "address",
            "phone",
            "price_type",
            "created_at"
        ]