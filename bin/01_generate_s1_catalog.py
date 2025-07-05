#!/usr/bin/env python3
"""
SAR Ship Detection - Ireland: Sentinel-1 Data Catalog Generation

This script generates a catalog of Sentinel-1 scenes covering Irish waters
for ship detection analysis. It utilizes the Sentinel-1-Coherence Pipeline
package for data discovery and catalog generation.

Usage:
    python bin/01_generate_s1_catalog.py [--start-date YYYY-MM-DD] [--end-date YYYY-MM-DD]

Author: SAR Ship Detection Team
Date: 2025
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add src to path for local imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    # Import from Sentinel-1-Coherence Pipeline package
    from sentinel1_coherence_pipeline import catalog_generator
    from sentinel1_coherence_pipeline.utils import setup_logging
except ImportError as e:
    print(f"Error importing Sentinel-1-Coherence Pipeline: {e}")
    print("Please ensure the package is installed: pip install sentinel1-coherence-pipeline")
    sys.exit(1)

from config import IRISH_WATERS_CONFIG

def setup_arguments():
    """Setup command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate Sentinel-1 catalog for Irish waters ship detection'
    )
    
    # Default to last 30 days if no dates specified
    default_end = datetime.now()
    default_start = default_end - timedelta(days=30)
    
    parser.add_argument(
        '--start-date',
        type=str,
        default=default_start.strftime('%Y-%m-%d'),
        help='Start date for catalog generation (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--end-date',
        type=str,
        default=default_end.strftime('%Y-%m-%d'),
        help='End date for catalog generation (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/catalogs',
        help='Output directory for catalog files'
    )
    
    parser.add_argument(
        '--max-scenes',
        type=int,
        default=100,
        help='Maximum number of scenes to include in catalog'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()

def main():
    """Main execution function."""
    args = setup_arguments()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Sentinel-1 catalog generation for Irish waters")
    logger.info(f"Date range: {args.start_date} to {args.end_date}")
    logger.info(f"Output directory: {args.output_dir}")
    
    # Create output directory
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Configure catalog generation parameters
        catalog_config = {
            'aoi_bounds': IRISH_WATERS_CONFIG['bbox'],  # (west, south, east, north)
            'start_date': args.start_date,
            'end_date': args.end_date,
            'platform': 'Sentinel-1',
            'product_type': ['GRD', 'SLC'],  # Both GRD and SLC for flexibility
            'beam_mode': 'IW',  # Interferometric Wide swath
            'polarization': ['VV', 'VH', 'VV+VH'],  # Dual-pol preferred
            'orbit_direction': ['ASCENDING', 'DESCENDING'],
            'max_results': args.max_scenes,
            'output_format': 'geoparquet'
        }
        
        # Generate catalog using the pipeline package
        logger.info("Generating Sentinel-1 scene catalog...")
        catalog_results = catalog_generator.generate_catalog(
            config=catalog_config,
            output_dir=output_path
        )
        
        # Log results
        logger.info(f"Catalog generation completed successfully")
        logger.info(f"Total scenes found: {catalog_results.get('total_scenes', 0)}")
        logger.info(f"Catalog saved to: {catalog_results.get('catalog_path', 'Unknown')}")
        
        # Additional filtering for ship detection optimization
        if catalog_results.get('total_scenes', 0) > 0:
            logger.info("Applying ship detection specific filtering...")
            
            # Filter for optimal conditions (low wind, clear weather)
            # This would be implemented based on the pipeline's filtering capabilities
            filtered_catalog = apply_ship_detection_filters(
                catalog_results['catalog_path'],
                output_path
            )
            
            logger.info(f"Filtered catalog contains {filtered_catalog['scene_count']} optimal scenes")
        
    except Exception as e:
        logger.error(f"Error during catalog generation: {e}")
        sys.exit(1)
    
    logger.info("Catalog generation completed successfully")

def apply_ship_detection_filters(catalog_path, output_dir):
    """
    Apply additional filtering specific to ship detection requirements.
    
    Args:
        catalog_path: Path to the generated catalog
        output_dir: Output directory for filtered catalog
        
    Returns:
        dict: Results of filtering operation
    """
    logger = logging.getLogger(__name__)
    
    # This function would implement ship detection specific filtering
    # such as:
    # - Prioritize scenes with low wind conditions
    # - Filter by time of day for optimal detection
    # - Remove scenes with excessive cloud cover over water
    # - Prioritize dual-polarization scenes
    
    logger.info("Ship detection filtering not yet implemented")
    logger.info("Using full catalog for now")
    
    return {
        'scene_count': 0,  # Placeholder
        'filtered_catalog_path': catalog_path
    }

if __name__ == '__main__':
    main()
