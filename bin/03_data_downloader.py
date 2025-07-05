#!/usr/bin/env python3
"""
SAR Ship Detection - Ireland: Data Downloader

This script downloads selected Sentinel-1 scenes using the Sentinel-1-Coherence
Pipeline package. It handles authentication, download management, and data
organization for the ship detection pipeline.

Usage:
    python bin/03_data_downloader.py --scene-list data/selected_scenes/download_list.csv

Author: SAR Ship Detection Team
Date: 2025
"""

import argparse
import sys
from pathlib import Path
import logging
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Add src to path for local imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    # Import from Sentinel-1-Coherence Pipeline package
    from sentinel1_coherence_pipeline import data_downloader
    from sentinel1_coherence_pipeline.utils import setup_logging
    from sentinel1_coherence_pipeline.auth import setup_authentication
except ImportError as e:
    print(f"Error importing Sentinel-1-Coherence Pipeline: {e}")
    print("Please ensure the package is installed: pip install sentinel1-coherence-pipeline")
    sys.exit(1)

from config import OUTPUT_CONFIG, SAR_PROCESSING_CONFIG

def setup_arguments():
    """Setup command line arguments."""
    parser = argparse.ArgumentParser(
        description='Download selected Sentinel-1 scenes for ship detection'
    )
    
    parser.add_argument(
        '--scene-list',
        type=str,
        required=True,
        help='Path to scene list file (CSV format)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/raw',
        help='Output directory for downloaded scenes'
    )
    
    parser.add_argument(
        '--max-workers',
        type=int,
        default=3,
        help='Maximum number of concurrent downloads'
    )
    
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume interrupted downloads'
    )
    
    parser.add_argument(
        '--verify-checksums',
        action='store_true',
        help='Verify file checksums after download'
    )
    
    parser.add_argument(
        '--organize-by-date',
        action='store_true',
        help='Organize downloaded files by acquisition date'
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
    
    logger.info("Starting Sentinel-1 data download for ship detection")
    logger.info(f"Scene list: {args.scene_list}")
    logger.info(f"Output directory: {args.output_dir}")
    
    # Create output directory
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load scene list
        logger.info("Loading scene list...")
        if not Path(args.scene_list).exists():
            raise FileNotFoundError(f"Scene list file not found: {args.scene_list}")
        
        scene_list = pd.read_csv(args.scene_list)
        logger.info(f"Loaded {len(scene_list)} scenes for download")
        
        # Setup authentication
        logger.info("Setting up authentication...")
        auth_config = setup_authentication()
        
        # Configure download parameters
        download_config = {
            'output_dir': output_path,
            'max_workers': args.max_workers,
            'resume_downloads': args.resume,
            'verify_checksums': args.verify_checksums,
            'organize_by_date': args.organize_by_date,
            'auth_config': auth_config,
            'retry_attempts': 3,
            'retry_delay': 30,  # seconds
            'timeout': 3600,    # 1 hour per file
        }
        
        # Filter existing downloads if resuming
        if args.resume:
            scene_list = filter_existing_downloads(scene_list, output_path, logger)
            logger.info(f"After filtering existing files: {len(scene_list)} scenes to download")
        
        if len(scene_list) == 0:
            logger.info("No scenes to download")
            return
        
        # Start downloads
        logger.info(f"Starting download of {len(scene_list)} scenes...")
        download_results = download_scenes(scene_list, download_config, logger)
        
        # Generate download report
        generate_download_report(download_results, output_path, logger)
        
        # Organize downloaded files
        if args.organize_by_date:
            organize_files_by_date(output_path, logger)
        
        # Verify downloads
        if args.verify_checksums:
            verify_downloaded_files(download_results, logger)
        
    except Exception as e:
        logger.error(f"Error during data download: {e}")
        sys.exit(1)
    
    logger.info("Data download completed successfully")

def filter_existing_downloads(scene_list, output_dir, logger):
    """Filter out scenes that have already been downloaded."""
    
    filtered_scenes = []
    
    for _, scene in scene_list.iterrows():
        scene_id = scene['scene_id']
        
        # Check for existing files (various possible extensions)
        existing_files = list(output_dir.glob(f"{scene_id}*"))
        
        if existing_files:
            logger.debug(f"Scene {scene_id} already exists, skipping")
        else:
            filtered_scenes.append(scene)
    
    return pd.DataFrame(filtered_scenes)

def download_scenes(scene_list, config, logger):
    """Download scenes using the pipeline package."""
    
    download_results = []
    
    # Use ThreadPoolExecutor for concurrent downloads
    with ThreadPoolExecutor(max_workers=config['max_workers']) as executor:
        # Submit download tasks
        future_to_scene = {}
        
        for _, scene in scene_list.iterrows():
            future = executor.submit(
                download_single_scene,
                scene,
                config
            )
            future_to_scene[future] = scene
        
        # Process completed downloads
        for future in as_completed(future_to_scene):
            scene = future_to_scene[future]
            
            try:
                result = future.result()
                download_results.append(result)
                
                if result['success']:
                    logger.info(f"Successfully downloaded: {result['scene_id']}")
                else:
                    logger.error(f"Failed to download: {result['scene_id']} - {result['error']}")
                    
            except Exception as e:
                logger.error(f"Download task failed for {scene['scene_id']}: {e}")
                download_results.append({
                    'scene_id': scene['scene_id'],
                    'success': False,
                    'error': str(e),
                    'file_path': None,
                    'file_size': 0,
                    'download_time': 0
                })
    
    return download_results

def download_single_scene(scene, config):
    """Download a single scene using the pipeline package."""
    
    start_time = time.time()
    
    try:
        # Use the pipeline's download functionality
        download_result = data_downloader.download_scene(
            scene_id=scene['scene_id'],
            download_url=scene['download_url'],
            output_dir=config['output_dir'],
            auth_config=config['auth_config'],
            verify_checksum=config['verify_checksums'],
            timeout=config['timeout']
        )
        
        download_time = time.time() - start_time
        
        return {
            'scene_id': scene['scene_id'],
            'success': download_result['success'],
            'error': download_result.get('error', None),
            'file_path': download_result.get('file_path', None),
            'file_size': download_result.get('file_size', 0),
            'download_time': download_time
        }
        
    except Exception as e:
        download_time = time.time() - start_time
        
        return {
            'scene_id': scene['scene_id'],
            'success': False,
            'error': str(e),
            'file_path': None,
            'file_size': 0,
            'download_time': download_time
        }

def generate_download_report(download_results, output_dir, logger):
    """Generate a report of download results."""
    
    # Convert to DataFrame for analysis
    results_df = pd.DataFrame(download_results)
    
    # Calculate statistics
    total_scenes = len(results_df)
    successful_downloads = len(results_df[results_df['success'] == True])
    failed_downloads = total_scenes - successful_downloads
    total_size_gb = results_df['file_size'].sum() / (1024**3)
    total_time_hours = results_df['download_time'].sum() / 3600
    
    # Create report
    report = {
        'download_summary': {
            'total_scenes': total_scenes,
            'successful_downloads': successful_downloads,
            'failed_downloads': failed_downloads,
            'success_rate': successful_downloads / total_scenes if total_scenes > 0 else 0,
            'total_size_gb': round(total_size_gb, 2),
            'total_time_hours': round(total_time_hours, 2),
            'average_speed_mbps': round((total_size_gb * 8 * 1024) / (total_time_hours * 3600), 2) if total_time_hours > 0 else 0
        },
        'failed_scenes': results_df[results_df['success'] == False][['scene_id', 'error']].to_dict('records'),
        'successful_scenes': results_df[results_df['success'] == True]['scene_id'].tolist()
    }
    
    # Save report
    import json
    report_file = output_dir / 'download_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    logger.info(f"Download report saved to: {report_file}")
    logger.info(f"Download summary: {successful_downloads}/{total_scenes} successful ({report['download_summary']['success_rate']:.1%})")
    logger.info(f"Total data downloaded: {total_size_gb:.2f} GB in {total_time_hours:.2f} hours")

def organize_files_by_date(output_dir, logger):
    """Organize downloaded files by acquisition date."""
    
    logger.info("Organizing files by acquisition date...")
    
    # This would parse scene IDs to extract dates and organize accordingly
    # Implementation depends on the specific file naming convention
    
    # For now, just log that organization would happen here
    logger.info("File organization by date not yet implemented")

def verify_downloaded_files(download_results, logger):
    """Verify the integrity of downloaded files."""
    
    logger.info("Verifying downloaded files...")
    
    successful_results = [r for r in download_results if r['success']]
    
    for result in successful_results:
        file_path = Path(result['file_path'])
        
        if file_path.exists():
            actual_size = file_path.stat().st_size
            expected_size = result['file_size']
            
            if actual_size != expected_size:
                logger.warning(f"Size mismatch for {result['scene_id']}: expected {expected_size}, got {actual_size}")
            else:
                logger.debug(f"File verification passed for {result['scene_id']}")
        else:
            logger.error(f"Downloaded file not found: {file_path}")

if __name__ == '__main__':
    main()
