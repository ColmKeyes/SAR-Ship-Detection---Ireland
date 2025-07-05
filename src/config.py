"""
SAR Ship Detection - Ireland: Configuration Settings

This module contains configuration parameters for the SAR ship detection
pipeline over Irish waters.

Author: SAR Ship Detection Team
Date: 2025
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Irish Waters Configuration
IRISH_WATERS_CONFIG = {
    # Bounding box for Irish coastal waters and EEZ
    # Format: (west, south, east, north) in WGS84 decimal degrees
    'bbox': (-11.0, 51.0, -5.0, 56.0),
    
    # Coordinate reference systems
    'input_crs': 'EPSG:4326',  # WGS84
    'output_crs': 'EPSG:2157',  # Irish Grid
    
    # Geographic metadata
    'region_name': 'Irish Waters',
    'country_code': 'IE',
    'timezone': 'Europe/Dublin',
    
    # Key maritime areas
    'major_ports': [
        {'name': 'Dublin Port', 'lat': 53.3498, 'lon': -6.2603},
        {'name': 'Cork Port', 'lat': 51.8985, 'lon': -8.2944},
        {'name': 'Shannon Foynes Port', 'lat': 52.6110, 'lon': -9.0983},
        {'name': 'Waterford Port', 'lat': 52.2593, 'lon': -7.1101},
        {'name': 'Galway Port', 'lat': 53.2707, 'lon': -9.0568},
        {'name': 'Rosslare Port', 'lat': 52.2518, 'lon': -6.3386}
    ],
    
    # Shipping lanes (approximate corridors)
    'shipping_lanes': [
        {'name': 'Dublin-Liverpool', 'priority': 'high'},
        {'name': 'Cork-France', 'priority': 'high'},
        {'name': 'Rosslare-Wales', 'priority': 'medium'},
        {'name': 'Atlantic Approaches', 'priority': 'medium'}
    ]
}

# SAR Processing Configuration
SAR_PROCESSING_CONFIG = {
    # Sentinel-1 specific parameters
    'platform': 'Sentinel-1',
    'preferred_modes': ['IW'],  # Interferometric Wide swath
    'preferred_polarizations': ['VV+VH', 'VV', 'VH'],
    'preferred_product_types': ['GRD', 'SLC'],
    
    # Processing parameters
    'resolution': {
        'grd': 10,  # meters
        'slc': 5    # meters (range x azimuth: ~2.3 x 14 m)
    },
    
    # SNAP processing settings
    'snap_config': {
        'memory_gb': 16,
        'jvm_flags': ['-Xmx16G', '-XX:+UseG1GC'],
        'batch_size': 5,  # scenes per batch
        'num_threads': 4
    },
    
    # Speckle filtering
    'speckle_filter': {
        'type': 'Lee',
        'window_size': 5,
        'num_looks': 1
    },
    
    # Terrain correction
    'terrain_correction': {
        'dem': 'SRTM 1Sec HGT',  # or 'ASTER 1sec GDEM'
        'pixel_spacing': 10,  # meters
        'resampling_method': 'BILINEAR_INTERPOLATION'
    }
}

# Ship Detection Configuration
SHIP_DETECTION_CONFIG = {
    # CFAR detection parameters
    'cfar': {
        'window_sizes': [50, 100, 150, 200],  # pixels
        'guard_cells': 10,
        'false_alarm_rate': 1e-6,
        'threshold_factor': 3.0
    },
    
    # Target filtering
    'target_filtering': {
        'min_size_pixels': 25,
        'max_size_pixels': 1000,
        'min_aspect_ratio': 0.2,
        'max_aspect_ratio': 5.0,
        'min_intensity_db': -15
    },
    
    # Morphological operations
    'morphology': {
        'opening_kernel_size': 3,
        'closing_kernel_size': 5,
        'erosion_iterations': 1,
        'dilation_iterations': 2
    },
    
    # Ship wake detection (optional enhancement)
    'wake_detection': {
        'enabled': False,  # Set to True to enable
        'wake_length_ratio': 5.0,  # wake length to ship length ratio
        'wake_angle_tolerance': 15  # degrees
    }
}

# AIS Validation Configuration
AIS_CONFIG = {
    # Data sources
    'data_sources': [
        'Irish Coast Guard',
        'Marine Institute',
        'MarineTraffic API',
        'AISHub'
    ],
    
    # Matching parameters
    'spatial_tolerance_m': 500,  # meters
    'temporal_tolerance_min': 30,  # minutes
    
    # Vessel type filtering
    'vessel_types': {
        'cargo': [70, 71, 72, 73, 74, 75, 76, 77, 78, 79],
        'tanker': [80, 81, 82, 83, 84, 85, 86, 87, 88, 89],
        'passenger': [60, 61, 62, 63, 64, 65, 66, 67, 68, 69],
        'fishing': [30],
        'other': [90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
    }
}

# Output Configuration
OUTPUT_CONFIG = {
    # Directory structure
    'base_dir': PROJECT_ROOT / 'data',
    'catalogs_dir': PROJECT_ROOT / 'data' / 'catalogs',
    'raw_data_dir': PROJECT_ROOT / 'data' / 'raw',
    'processed_dir': PROJECT_ROOT / 'data' / 'processed',
    'results_dir': PROJECT_ROOT / 'data' / 'results',
    'logs_dir': PROJECT_ROOT / 'logs',
    
    # File formats
    'catalog_format': 'geoparquet',
    'detection_format': 'geotiff',
    'metadata_format': 'json',
    
    # Geoparquet partitioning
    'partitioning': {
        'spatial': True,
        'temporal': True,
        'by_orbit': True
    },
    
    # Metadata fields
    'detection_fields': [
        'detection_id',
        'timestamp',
        'latitude',
        'longitude',
        'size_pixels',
        'size_m2',
        'orientation_deg',
        'confidence_score',
        'rcs_db',
        'polarization',
        'orbit_direction',
        'processing_uuid'
    ]
}

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'detailed',
            'class': 'logging.FileHandler',
            'filename': str(PROJECT_ROOT / 'logs' / 'sar_ship_detection.log'),
            'mode': 'a'
        }
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

# Environment-specific overrides
if os.getenv('SAR_SHIP_DETECTION_ENV') == 'development':
    # Development settings
    SAR_PROCESSING_CONFIG['snap_config']['memory_gb'] = 8
    SAR_PROCESSING_CONFIG['snap_config']['batch_size'] = 2
    LOGGING_CONFIG['handlers']['default']['level'] = 'DEBUG'

elif os.getenv('SAR_SHIP_DETECTION_ENV') == 'production':
    # Production settings
    SAR_PROCESSING_CONFIG['snap_config']['memory_gb'] = 32
    SAR_PROCESSING_CONFIG['snap_config']['batch_size'] = 10
    LOGGING_CONFIG['handlers']['default']['level'] = 'INFO'
