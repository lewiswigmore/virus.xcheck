```
██╗   ██╗██╗██████╗ ██╗   ██╗███████╗   ██╗  ██╗ ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗
██║   ██║██║██╔══██╗██║   ██║██╔════╝   ╚██╗██╔╝██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝
██║   ██║██║██████╔╝██║   ██║███████╗    ╚███╔╝ ██║     ███████║█████╗  ██║     █████╔╝ 
╚██╗ ██╔╝██║██╔══██╗██║   ██║╚════██║    ██╔██╗ ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ 
 ╚████╔╝ ██║██║  ██║╚██████╔╝███████║██╗██╔╝ ██╗╚██████╗██║  ██║███████╗╚██████╗██║  ██╗
  ╚═══╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝
```
<p align="left">
      <a href="https://github.com/lewiswigmore/virus.xcheck/releases"><img src="https://img.shields.io/github/v/release/lewiswigmore/virus.xcheck" alt="Version"></a>
      <a href="https://github.com/lewiswigmore/virus.xcheck"><img src="https://img.shields.io/badge/python-3.8%2B-blue" alt="Python 3.8+"></a>
      <a href="https://github.com/lewiswigmore/virus.xcheck/blob/main/LICENSE"><img src="https://img.shields.io/github/license/lewiswigmore/virus.xcheck" alt="License"></a>
      <a href="https://github.com/lewiswigmore/virus.xcheck"><img src="https://img.shields.io/badge/GitHub-Follow%20on%20GitHub-inactive.svg?logo=github"></a>
</p>

> **Service notice (October 2026):** Virus.Exchange (virus.exchange) has shut down: the domain now redirects to [vx-underground.org](https://vx-underground.org/) and its public sample bucket was removed. As of v0.2.3, virusxcheck runs in **VirusTotal-only mode**: VX lookups are disabled and a VirusTotal API key (VIRUSTOTAL_API_KEY) is required.

## Overview
Virus.xcheck is a Python tool that checks file hashes against VirusTotal. It was originally built to cross-check hashes against the Virus Exchange database; Virus.Exchange has since shut down (see the service notice above), and from v0.2.3 the tool runs in VirusTotal-only mode. The tool can read hashes from a CSV file or accept a single hash from the command line.

## Features
- Reads hashes from a CSV file or a single hash from the command line
- Checks each hash against the VirusTotal API (Virus Exchange lookups are disabled since the service shut down)
- Parallel processing for efficient handling of larger files
- Colorized, beautifully formatted output in the terminal
- Outputs the results in JSON or CSV format
- Command-line interface with multiple options
- API key management with .env file support
- Rate limiting to prevent API throttling
- Interactive HTML reports with visualisations

## Requirements
- Python 3.8+

## Installation

### From PyPI (Recommended)

```bash
pip install virusxcheck
```

### HTML Reports (Optional)

To generate interactive HTML reports, install with the report extra:

```bash
pip install virusxcheck[report]
```

This installs additional dependencies (plotly, pandas, jinja2) needed for HTML report generation.

### From Source

```bash
git clone https://github.com/lewiswigmore/virus.xcheck.git
cd virus.xcheck
pip install -r requirements.txt
```

### API Key Setup
1. Get an API key from [VirusTotal](https://www.virustotal.com/)
2. Create a `.env` file in the root directory with your API key:
   ```
   VIRUSTOTAL_API_KEY=your_api_key_here
   ```
   Alternatively, you can use the `--save-config` option to set your keys interactively:
   ```bash
   virusxcheck --save-config
   ```

## Quick Start

```bash
pip install virusxcheck
virusxcheck --save-config            # Set up your API key
virusxcheck -s "sha256_hash_value"   # Check a single hash
virusxcheck -f hashes.csv -o out.json --html report.html  # Batch check with report
```

## Usage

> **Note:** After installing via `pip install virusxcheck`, you can use the `virusxcheck` command directly. If running from source, use `python virusxcheck.py` instead.

Execute the script from the command line with the following options:

### Check a single hash
```bash
virusxcheck -s "hash_value"
```

### Process multiple hashes from a CSV file
```bash
virusxcheck -f /path/to/your/hashes.csv
```

### Save results to a file
```bash
virusxcheck -f /path/to/hashes.csv -o /path/to/results.csv
virusxcheck -s "hash_value" -o /path/to/results.json
```

### Generate HTML report
```bash
virusxcheck -f /path/to/hashes.csv --html report.html
```

### Disable colored output
```bash
virusxcheck -s "hash_value" --no-color
```

## Test Examples

### Sample Hashes for Testing
```
d00853e592bccd823027e7e685d88c5a1f76a5a36ec5b7073d49ee633b050cc8
3965811a37eded16030a1dd4ac57119ce774bed4fcd70a232011f8f86efbfd83
51919bdfd8bc0ebeec651efdd5d97dae7ad9532cb10f6efaa67c3dbc88ea7500
```

### Testing with Sample CSV
Create a file `test_hashes.csv` with the above hashes and run:
```bash
virusxcheck -f test_hashes.csv --html results/report.html -o results/output.csv
```

### Sample Output
When running the tool with the test hashes, you'll see output similar to:
```
VirusTotal API integration enabled
Processing: 100%|██████████████████████| 3/3 [00:00<00:00, 5.85it/s]
HTML report saved to results/report.html
Results saved to results/output.csv
```

The terminal will display detailed information about each hash, including:
- Detection status (found/not found)
- File metadata (size, type, first seen)
- Known filenames
- Tags associated with the sample
- VirusTotal detection statistics
- Download and reference links

## Command-Line Arguments
- `-s, --single`: Single hash string to check
- `-f, --file`: Path to CSV file containing hashes
- `-o, --output`: Path to output file (CSV or JSON format)
- `--html`: Generate HTML report with interactive charts
- `--save-config`: Interactively save API keys to .env file
- `--no-color`: Disable colored output

## Output Formats

### Terminal Output
The tool produces a colored output in the terminal:
- Red for malicious files found in the database
- Green for clean files not found
- Yellow for warnings and errors
- Metadata display with file information, names, tags, and links

### HTML Reports
The HTML reports include:
- Interactive charts showing detection rates and statistics
- File metadata and statistics
- Malware tag classification
- Detailed scan results from VirusTotal

### JSON Output
```json
{
    "dbd5e933fe023ee03953ed8a8997c58be05ba97c092b795647962cf111bcd540": {
        "status": "Found in VX database",
        "details": {
            "md5": "d51c19925a2ae853d3b19a1259f86de5",
            "size": 4042752,
            "type": "unknown",
            "names": [
                "csrss.exe",
                "app.exe"
            ],
            "sha1": "332a18521f2905e233bbab094a021cee44ac750e",
            "tags": [
                "spreader",
                "peexe",
                "executable",
                "windows"
            ],
            "first_seen": "2025-03-30T17:36:55Z",
            "download_link": "https://s3.us-east-1.wasabisys.com/vxugmwdb/dbd5e933fe023ee03953ed8a8997c58be05ba97c092b795647962cf111bcd540"
        },
        "virustotal_url": "https://www.virustotal.com/gui/file/dbd5e933fe023ee03953ed8a8997c58be05ba97c092b795647962cf111bcd540"
    }
}
```

### CSV Output
The CSV output includes columns for:
- Hash
- VX Status
- File Type
- Size
- First Seen
- Names
- VX URL
- Download Link
- VirusTotal URL
- VT Detection Rate
- VT Malicious
- VT Suspicious
- VT Clean
- VT Type
- VT First Seen
- VT Tags

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes.

## Security

For security concerns, please see [SECURITY.md](SECURITY.md).

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for informational purposes only. Ensure you have the right to access and check the hashes against the database and always comply with the terms of service of the Virus Exchange and VirusTotal APIs.
