"""
ETL Utility Functions

Common helper functions for ETL operations:
- File loading (CSV, JSON)
- Data transformation
- Logging setup
- Configuration management
"""
import json
import csv
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path


def load_json(file_path: str) -> List[Dict[str, Any]]:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        List of dictionaries
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Ensure it's a list
    if not isinstance(data, list):
        data = [data]
    
    return data


def load_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Load data from a CSV file.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        List of dictionaries
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    return data


def save_json(data: List[Dict[str, Any]], file_path: str, indent: int = 2):
    """
    Save data to a JSON file.
    
    Args:
        data: List of dictionaries to save
        file_path: Output file path
        indent: JSON indentation (default: 2)
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def save_csv(data: List[Dict[str, Any]], file_path: str):
    """
    Save data to a CSV file.
    
    Args:
        data: List of dictionaries to save
        file_path: Output file path
    """
    if not data:
        raise ValueError("Cannot save empty data to CSV")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def setup_file_logger(
    name: str,
    log_file: str,
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup a logger that writes to both console and file.
    
    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level
        format_string: Optional custom format string
        
    Returns:
        Configured logger
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Format
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format_string, datefmt='%Y-%m-%d %H:%M:%S')
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_neo4j_config(
    uri: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None
) -> Dict[str, str]:
    """
    Get Neo4j configuration from environment variables or parameters.
    
    Args:
        uri: Neo4j URI (overrides env var)
        user: Neo4j username (overrides env var)
        password: Neo4j password (overrides env var)
        
    Returns:
        Dictionary with uri, user, password
        
    Raises:
        ValueError: If required credentials are missing
    """
    config = {
        'uri': uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        'user': user or os.getenv('NEO4J_USER', 'neo4j'),
        'password': password or os.getenv('NEO4J_PASSWORD')
    }
    
    if not config['password']:
        raise ValueError(
            "Neo4j password not provided. "
            "Set NEO4J_PASSWORD environment variable or pass as parameter."
        )
    
    return config


def chunk_list(data: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.
    
    Args:
        data: List to split
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


def clean_string(value: Any) -> Optional[str]:
    """
    Clean a string value for Neo4j.
    
    Args:
        value: Value to clean
        
    Returns:
        Cleaned string or None
    """
    if value is None or value == '':
        return None
    
    if not isinstance(value, str):
        value = str(value)
    
    return value.strip()


def parse_date(date_string: str, format: str = '%Y-%m-%d') -> Optional[str]:
    """
    Parse and validate a date string.
    
    Args:
        date_string: Date string to parse
        format: Date format (default: YYYY-MM-DD)
        
    Returns:
        Validated date string in ISO format or None
    """
    if not date_string:
        return None
    
    try:
        dt = datetime.strptime(date_string, format)
        return dt.date().isoformat()
    except ValueError:
        return None


def sanitize_for_cypher(value: Any) -> Any:
    """
    Sanitize a value for use in Cypher queries.
    
    Args:
        value: Value to sanitize
        
    Returns:
        Sanitized value
    """
    if value is None:
        return None
    
    if isinstance(value, str):
        # Remove or escape problematic characters
        value = value.strip()
        # Neo4j handles escaping in parameterized queries
        return value
    
    if isinstance(value, (int, float, bool)):
        return value
    
    # Convert other types to string
    return str(value)


def validate_required_fields(
    record: Dict[str, Any],
    required_fields: List[str]
) -> tuple[bool, List[str]]:
    """
    Validate that a record has all required fields.
    
    Args:
        record: Data record to validate
        required_fields: List of required field names
        
    Returns:
        Tuple of (is_valid, missing_fields)
    """
    missing = []
    
    for field in required_fields:
        if field not in record or record[field] is None or record[field] == '':
            missing.append(field)
    
    return len(missing) == 0, missing


def print_progress_bar(
    current: int,
    total: int,
    prefix: str = 'Progress',
    suffix: str = 'Complete',
    length: int = 50
):
    """
    Print a progress bar to console.
    
    Args:
        current: Current progress value
        total: Total value (100%)
        prefix: Prefix text
        suffix: Suffix text
        length: Length of progress bar
    """
    percent = 100 * (current / float(total))
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    
    print(f'\r{prefix} |{bar}| {percent:.1f}% {suffix}', end='', flush=True)
    
    # Print newline on completion
    if current == total:
        print()


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "2m 30s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    
    if minutes < 60:
        return f"{minutes}m {remaining_seconds}s"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{hours}h {remaining_minutes}m {remaining_seconds}s"


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path to project root
    """
    # Assume this file is in etl/ directory
    return Path(__file__).parent.parent


def ensure_directory_exists(directory: str):
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        directory: Directory path
    """
    os.makedirs(directory, exist_ok=True)


def merge_dicts(*dicts: Dict) -> Dict:
    """
    Merge multiple dictionaries.
    
    Args:
        *dicts: Variable number of dictionaries
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def count_records_by_field(data: List[Dict], field: str) -> Dict[str, int]:
    """
    Count records grouped by a field value.
    
    Args:
        data: List of records
        field: Field name to group by
        
    Returns:
        Dictionary of {field_value: count}
    """
    counts = {}
    for record in data:
        value = record.get(field, 'Unknown')
        counts[value] = counts.get(value, 0) + 1
    return counts


class ProgressTracker:
    """Simple progress tracker for ETL operations"""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
    
    def update(self, count: int = 1):
        """Update progress by count"""
        self.current += count
        self._print_progress()
    
    def _print_progress(self):
        """Print current progress"""
        elapsed = time.time() - self.start_time
        percent = 100 * (self.current / self.total) if self.total > 0 else 0
        
        # Estimate time remaining
        if self.current > 0:
            avg_time_per_item = elapsed / self.current
            remaining_items = self.total - self.current
            eta = avg_time_per_item * remaining_items
            eta_str = format_duration(eta)
        else:
            eta_str = "calculating..."
        
        print(
            f"\r{self.description}: {self.current}/{self.total} "
            f"({percent:.1f}%) - ETA: {eta_str}",
            end='',
            flush=True
        )
        
        if self.current >= self.total:
            print()  # New line on completion
    
    def complete(self):
        """Mark as complete"""
        self.current = self.total
        self._print_progress()


# Import time for ProgressTracker
import time
