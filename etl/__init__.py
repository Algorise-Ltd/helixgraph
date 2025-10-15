"""
ETL module for HelixGraph data loading.

This module provides a generic ETL framework for loading data into Neo4j,
with domain-specific loaders for HR, Marketing, and Procurement data.

Main Components:
- BaseLoader: Abstract base class for all loaders
- HRLoader: HR-specific data loader
- utils: Common utility functions
"""

from etl.base_loader import BaseLoader, LoadStats
from etl.hr_loader import HRLoader
from etl.marketing_loader import MarketingLoader
from etl.procurement_csv_loader import ProcurementCSVLoader
from etl import utils

# Legacy import for backward compatibility
try:
    from etl.procurement_loader import ProcurementLoader as _LegacyProcurementLoader
    ProcurementLoader = _LegacyProcurementLoader
except ImportError:
    # If old loader doesn't exist, alias to new CSV loader
    ProcurementLoader = ProcurementCSVLoader

__all__ = [
    'BaseLoader',
    'LoadStats',
    'HRLoader',
    'MarketingLoader',
    'ProcurementCSVLoader',
    'ProcurementLoader',  # Legacy alias
    'utils'
]

__version__ = '0.1.0'
