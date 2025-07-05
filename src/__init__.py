"""
SAR Ship Detection - Ireland

A comprehensive pipeline for detecting and cataloging ships in Irish coastal waters
using Sentinel-1 SAR data.

Author: SAR Ship Detection Team
Date: 2025
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "SAR Ship Detection Team"
__email__ = "contact@sar-ship-detection.ie"
__description__ = "SAR Ship Detection pipeline for Irish waters"

# Import main configuration
from .config import (
    IRISH_WATERS_CONFIG,
    SAR_PROCESSING_CONFIG,
    SHIP_DETECTION_CONFIG,
    AIS_CONFIG,
    OUTPUT_CONFIG,
    LOGGING_CONFIG
)

__all__ = [
    'IRISH_WATERS_CONFIG',
    'SAR_PROCESSING_CONFIG', 
    'SHIP_DETECTION_CONFIG',
    'AIS_CONFIG',
    'OUTPUT_CONFIG',
    'LOGGING_CONFIG'
]
