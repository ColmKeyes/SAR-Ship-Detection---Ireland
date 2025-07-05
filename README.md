# SAR Ship Detection - Ireland

A comprehensive pipeline for detecting and cataloging ships in Irish coastal waters using Sentinel-1 SAR (Synthetic Aperture Radar) data. This project leverages amplitude-based detection techniques including CFAR (Constant False Alarm Rate) algorithms to identify maritime vessels across major shipping lanes, fishing areas, and offshore installations around Ireland.

## 🚢 Overview

This project implements a complete SAR ship detection workflow specifically designed for Irish waters, covering:

- **Geographic Coverage**: Irish coastal waters and Exclusive Economic Zone (EEZ)
- **Data Source**: Sentinel-1 SAR imagery (GRD/SLC products)
- **Detection Method**: CFAR algorithms with morphological filtering
- **Validation**: AIS (Automatic Identification System) cross-reference
- **Output**: Geoparquet catalogs with comprehensive metadata

## 🏗️ Project Structure

```
SAR Ship Detection - Ireland/
├── bin/                          # Executable scripts
│   ├── 01_generate_s1_catalog.py   # Scene catalog generation
│   ├── 02_scene_selector.py        # Optimal scene selection
│   └── 03_data_downloader.py       # Data download management
├── src/                          # Source code modules
│   └── config.py                   # Configuration settings
├── data/                         # Data directories
│   ├── catalogs/                   # Scene catalogs
│   ├── raw/                        # Downloaded SAR data
│   ├── processed/                  # Processed SAR products
│   └── results/                    # Detection results
├── docs/                         # Documentation
├── tests/                        # Unit tests
├── logs/                         # Log files
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🛠️ Installation

### Prerequisites

1. **Python 3.8+** with pip
2. **ESA SNAP** (Sentinel Application Platform) - Required for SAR processing
3. **Sentinel-1-Coherence Pipeline** package - Core dependency for data handling

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd "SAR Ship Detection - Ireland"
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install SNAP and SNAPPY

1. Download and install [ESA SNAP](https://step.esa.int/main/download/snap-download/)
2. Configure SNAPPY (SNAP Python API):
   ```bash
   # Navigate to SNAP installation directory
   cd $SNAP_HOME/bin
   ./snappy-conf <path-to-your-python>
   ```

### Step 5: Install Sentinel-1-Coherence Pipeline

```bash
# Install from your package source
pip install sentinel1-coherence-pipeline
```

## 🚀 Quick Start

### 1. Generate Scene Catalog

Create a catalog of available Sentinel-1 scenes over Irish waters:

```bash
python bin/01_generate_s1_catalog.py --start-date 2024-12-01 --end-date 2025-01-31 --verbose
```

### 2. Select Optimal Scenes

Select scenes with favorable conditions for ship detection:

```bash
python bin/02_scene_selector.py --catalog data/catalogs/s1_catalog.parquet --max-scenes 50 --prefer-dual-pol
```

### 3. Download Selected Scenes

Download the selected scenes for processing:

```bash
python bin/03_data_downloader.py --scene-list data/selected_scenes/download_list.csv --max-workers 3 --resume
```

## ⚙️ Configuration

The project uses a centralized configuration system in `src/config.py`. Key configuration sections include:

### Irish Waters Configuration
- **Bounding Box**: (-11.0, 51.0, -5.0, 56.0) - Irish coastal waters and EEZ
- **Coordinate Systems**: WGS84 input, Irish Grid (EPSG:2157) output
- **Major Ports**: Dublin, Cork, Shannon Foynes, Waterford, Galway, Rosslare

### SAR Processing Configuration
- **Platform**: Sentinel-1 (IW mode preferred)
- **Polarizations**: VV+VH (dual-pol preferred), VV, VH
- **Resolution**: 10m (GRD), 5m (SLC)
- **SNAP Settings**: 16GB memory, batch processing

### Ship Detection Configuration
- **CFAR Parameters**: Adaptive window sizing, 1e-6 false alarm rate
- **Target Filtering**: 25-1000 pixel size range, aspect ratio constraints
- **Morphological Operations**: Opening/closing for noise reduction

## 📊 Data Processing Workflow

1. **Scene Discovery**: Query Sentinel-1 archive for Irish waters coverage
2. **Scene Selection**: Filter for optimal detection conditions (low wind, clear weather)
3. **Data Download**: Concurrent download with resume capability
4. **SAR Preprocessing**: Calibration, speckle filtering, terrain correction
5. **Ship Detection**: CFAR algorithms with adaptive thresholding
6. **False Alarm Mitigation**: Morphological filtering and contextual analysis
7. **AIS Validation**: Cross-reference with vessel tracking data
8. **Catalog Generation**: Geoparquet output with spatial partitioning

## 🎯 Detection Methodology

### CFAR Detection
- **Algorithm**: Constant False Alarm Rate with sliding window
- **Window Sizes**: 50x50 to 200x200 pixels (adaptive)
- **Guard Cells**: 10-pixel buffer around test cell
- **Threshold**: 3σ above local background

### Target Filtering
- **Size Constraints**: 25-1000 pixels (ship-like targets)
- **Aspect Ratio**: 0.2-5.0 (elongated objects)
- **Intensity Threshold**: >-15 dB above background

### Validation
- **AIS Matching**: ±500m spatial, ±30min temporal tolerance
- **Performance Targets**: >85% detection rate, <15% false alarms

## 📈 Expected Outputs

### Detection Products
- **GeoTIFF Masks**: Binary ship detection masks
- **Confidence Scores**: Detection confidence (0-1)
- **Attribute Data**: Size, orientation, radar cross-section

### Geoparquet Catalog
Comprehensive database with fields:
- `detection_id`: Unique detection identifier
- `timestamp`: Acquisition timestamp
- `latitude`, `longitude`: Detection coordinates
- `size_pixels`, `size_m2`: Target size measurements
- `orientation_deg`: Target orientation
- `confidence_score`: Detection confidence
- `rcs_db`: Radar cross-section estimate
- `processing_uuid`: Processing batch identifier

## 🔧 Advanced Usage

### Environment Variables
```bash
export SAR_SHIP_DETECTION_ENV=production  # or development
export SNAP_HOME=/path/to/snap
```

### Custom Configuration
Modify `src/config.py` for:
- Different geographic areas
- Alternative processing parameters
- Custom output formats

### Batch Processing
```bash
# Process multiple date ranges
for month in {01..12}; do
    python bin/01_generate_s1_catalog.py --start-date 2024-${month}-01 --end-date 2024-${month}-31
done
```

## 📋 Requirements

### System Requirements
- **RAM**: 16GB minimum (32GB recommended for large scenes)
- **Storage**: 100GB+ for raw data, 50GB+ for processed results
- **CPU**: Multi-core processor (4+ cores recommended)

### Software Dependencies
- Python 3.8+
- ESA SNAP 8.0+
- GDAL 3.3+
- See `requirements.txt` for complete list

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **ESA Copernicus Programme** for Sentinel-1 data
- **Irish Marine Institute** for maritime domain expertise
- **Sentinel-1-Coherence Pipeline** package developers
- **SNAP Development Team** for SAR processing tools

## 📞 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation in the `docs/` directory

## 🔗 Related Projects

- [Sentinel-1-Coherence Pipeline](https://github.com/your-org/sentinel1-coherence-pipeline)
- [ESA SNAP](https://step.esa.int/main/toolboxes/snap/)
- [Copernicus Open Access Hub](https://scihub.copernicus.eu/)

---

**Note**: This project is designed for research and maritime surveillance applications. Ensure compliance with local regulations and data usage policies when deploying in operational environments.
