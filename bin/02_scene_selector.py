#!/usr/bin/env python3
"""
SAR Ship Detection - Ireland: Scene Selection

This script selects optimal Sentinel-1 scenes from the generated catalog
for ship detection analysis. It prioritizes scenes with favorable conditions
for maritime target detection.

Usage:
    python bin/02_scene_selector.py --catalog data/catalogs/s1_catalog.parquet

Author: SAR Ship Detection Team
Date: 2025
"""

import argparse
import sys
from pathlib import Path
import logging
import pandas as pd
import geopandas as gpd

# Add src to path for local imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    # Import from Sentinel-1-Coherence Pipeline package
    from sentinel1_coherence_pipeline import scene_selector
    from sentinel1_coherence_pipeline.utils import setup_logging
except ImportError as e:
    print(f"Error importing Sentinel-1-Coherence Pipeline: {e}")
    print("Please ensure the package is installed: pip install sentinel1-coherence-pipeline")
    sys.exit(1)

from config import IRISH_WATERS_CONFIG, SAR_PROCESSING_CONFIG, OUTPUT_CONFIG

def setup_arguments():
    """Setup command line arguments."""
    parser = argparse.ArgumentParser(
        description='Select optimal Sentinel-1 scenes for ship detection'
    )
    
    parser.add_argument(
        '--catalog',
        type=str,
        required=True,
        help='Path to input catalog file (parquet format)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/selected_scenes',
        help='Output directory for selected scenes catalog'
    )
    
    parser.add_argument(
        '--max-scenes',
        type=int,
        default=50,
        help='Maximum number of scenes to select'
    )
    
    parser.add_argument(
        '--min-coverage',
        type=float,
        default=0.8,
        help='Minimum coverage of AOI required (0.0-1.0)'
    )
    
    parser.add_argument(
        '--max-wind-speed',
        type=float,
        default=15.0,
        help='Maximum wind speed for optimal detection (m/s)'
    )
    
    parser.add_argument(
        '--prefer-dual-pol',
        action='store_true',
        help='Prefer dual-polarization scenes'
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
    
    logger.info("Starting scene selection for ship detection")
    logger.info(f"Input catalog: {args.catalog}")
    logger.info(f"Output directory: {args.output_dir}")
    
    # Create output directory
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load catalog
        logger.info("Loading scene catalog...")
        if not Path(args.catalog).exists():
            raise FileNotFoundError(f"Catalog file not found: {args.catalog}")
        
        catalog_df = pd.read_parquet(args.catalog)
        logger.info(f"Loaded {len(catalog_df)} scenes from catalog")
        
        # Configure selection criteria for ship detection
        selection_config = {
            'aoi_bounds': IRISH_WATERS_CONFIG['bbox'],
            'max_scenes': args.max_scenes,
            'min_coverage': args.min_coverage,
            'selection_criteria': {
                # Prioritize conditions favorable for ship detection
                'wind_speed_max': args.max_wind_speed,
                'sea_state_max': 4,  # Beaufort scale
                'cloud_cover_max': 0.3,  # Over water areas
                'time_of_day': ['day', 'night'],  # SAR works day/night
                'orbit_direction': ['ASCENDING', 'DESCENDING'],
                'polarization_preference': ['VV+VH', 'VV', 'VH'] if args.prefer_dual_pol else None
            },
            'quality_filters': {
                'min_incidence_angle': 20,  # degrees
                'max_incidence_angle': 45,  # degrees
                'exclude_border_scenes': True,
                'min_data_quality': 0.8
            },
            'temporal_distribution': {
                'spread_evenly': True,
                'max_scenes_per_day': 2,
                'prefer_recent': True
            }
        }
        
        # Apply ship detection specific filtering
        logger.info("Applying ship detection specific filters...")
        filtered_catalog = apply_ship_detection_filters(catalog_df, selection_config)
        
        # Use pipeline scene selector for final selection
        logger.info("Running scene selection algorithm...")
        selected_scenes = scene_selector.select_optimal_scenes(
            catalog=filtered_catalog,
            config=selection_config
        )
        
        # Log selection results
        logger.info(f"Selected {len(selected_scenes)} scenes from {len(catalog_df)} candidates")
        
        # Save selected scenes catalog
        output_file = output_path / 'selected_scenes.parquet'
        selected_scenes.to_parquet(output_file)
        logger.info(f"Selected scenes saved to: {output_file}")
        
        # Generate selection summary
        generate_selection_summary(selected_scenes, output_path, logger)
        
        # Create download list for next processing step
        create_download_list(selected_scenes, output_path, logger)
        
    except Exception as e:
        logger.error(f"Error during scene selection: {e}")
        sys.exit(1)
    
    logger.info("Scene selection completed successfully")

def apply_ship_detection_filters(catalog_df, config):
    """
    Apply ship detection specific filtering to the catalog.
    
    Args:
        catalog_df: Input catalog DataFrame
        config: Selection configuration
        
    Returns:
        pd.DataFrame: Filtered catalog
    """
    logger = logging.getLogger(__name__)
    
    filtered_df = catalog_df.copy()
    initial_count = len(filtered_df)
    
    # Filter by wind speed if available
    if 'wind_speed' in filtered_df.columns:
        max_wind = config['selection_criteria']['wind_speed_max']
        filtered_df = filtered_df[filtered_df['wind_speed'] <= max_wind]
        logger.info(f"Wind speed filter: {len(filtered_df)}/{initial_count} scenes remaining")
    
    # Filter by sea state if available
    if 'sea_state' in filtered_df.columns:
        max_sea_state = config['selection_criteria']['sea_state_max']
        filtered_df = filtered_df[filtered_df['sea_state'] <= max_sea_state]
        logger.info(f"Sea state filter: {len(filtered_df)}/{initial_count} scenes remaining")
    
    # Prioritize dual-polarization scenes
    if 'polarization' in filtered_df.columns:
        dual_pol_scenes = filtered_df[filtered_df['polarization'].str.contains('\+')]
        if len(dual_pol_scenes) > 0:
            # Add priority score for dual-pol
            filtered_df['dual_pol_priority'] = filtered_df['polarization'].str.contains('\+').astype(int)
            logger.info(f"Found {len(dual_pol_scenes)} dual-polarization scenes")
    
    # Filter by incidence angle for optimal ship detection
    if 'incidence_angle' in filtered_df.columns:
        min_angle = config['quality_filters']['min_incidence_angle']
        max_angle = config['quality_filters']['max_incidence_angle']
        filtered_df = filtered_df[
            (filtered_df['incidence_angle'] >= min_angle) &
            (filtered_df['incidence_angle'] <= max_angle)
        ]
        logger.info(f"Incidence angle filter: {len(filtered_df)}/{initial_count} scenes remaining")
    
    # Prioritize scenes over shipping lanes
    filtered_df = add_shipping_lane_priority(filtered_df)
    
    logger.info(f"Final filtered catalog: {len(filtered_df)} scenes")
    return filtered_df

def add_shipping_lane_priority(catalog_df):
    """
    Add priority scores based on proximity to major shipping lanes.
    
    Args:
        catalog_df: Input catalog DataFrame
        
    Returns:
        pd.DataFrame: Catalog with shipping lane priority scores
    """
    logger = logging.getLogger(__name__)
    
    # This is a simplified implementation
    # In practice, you would use actual shipping lane geometries
    
    catalog_df['shipping_lane_priority'] = 0
    
    # High priority areas (approximate)
    high_priority_areas = [
        {'name': 'Dublin Bay', 'lat': 53.35, 'lon': -6.26, 'radius': 0.5},
        {'name': 'Cork Harbor', 'lat': 51.90, 'lon': -8.29, 'radius': 0.3},
        {'name': 'Irish Sea', 'lat': 53.0, 'lon': -5.5, 'radius': 1.0}
    ]
    
    for area in high_priority_areas:
        # Simple distance-based priority (would be more sophisticated in practice)
        if 'center_lat' in catalog_df.columns and 'center_lon' in catalog_df.columns:
            distance = ((catalog_df['center_lat'] - area['lat'])**2 + 
                       (catalog_df['center_lon'] - area['lon'])**2)**0.5
            
            in_area = distance <= area['radius']
            catalog_df.loc[in_area, 'shipping_lane_priority'] += 1
    
    logger.info(f"Added shipping lane priorities to {len(catalog_df)} scenes")
    return catalog_df

def generate_selection_summary(selected_scenes, output_path, logger):
    """Generate a summary of the scene selection."""
    
    summary = {
        'total_scenes': len(selected_scenes),
        'date_range': {
            'start': selected_scenes['acquisition_date'].min() if 'acquisition_date' in selected_scenes.columns else 'Unknown',
            'end': selected_scenes['acquisition_date'].max() if 'acquisition_date' in selected_scenes.columns else 'Unknown'
        },
        'polarizations': selected_scenes['polarization'].value_counts().to_dict() if 'polarization' in selected_scenes.columns else {},
        'orbit_directions': selected_scenes['orbit_direction'].value_counts().to_dict() if 'orbit_direction' in selected_scenes.columns else {},
        'coverage_stats': {
            'mean_coverage': selected_scenes['aoi_coverage'].mean() if 'aoi_coverage' in selected_scenes.columns else 'Unknown',
            'min_coverage': selected_scenes['aoi_coverage'].min() if 'aoi_coverage' in selected_scenes.columns else 'Unknown'
        }
    }
    
    # Save summary
    import json
    summary_file = output_path / 'selection_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    logger.info(f"Selection summary saved to: {summary_file}")

def create_download_list(selected_scenes, output_path, logger):
    """Create a download list for the next processing step."""
    
    if 'download_url' in selected_scenes.columns:
        download_list = selected_scenes[['scene_id', 'download_url', 'file_size']].copy()
        download_file = output_path / 'download_list.csv'
        download_list.to_csv(download_file, index=False)
        logger.info(f"Download list saved to: {download_file}")
    else:
        logger.warning("No download URLs found in catalog")

if __name__ == '__main__':
    main()
