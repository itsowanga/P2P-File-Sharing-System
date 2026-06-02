"""SHA256 hashing and integrity verification for shared files."""

import hashlib
import os


def compute_file_hash(filename, algorithm='sha256'):
    """
    Compute the hash of a file.

    Args:
        filename: Path to the file.
        algorithm: Hash algorithm name (default: sha256).

    Returns:
        Hex digest string, or None if the file does not exist.
    """
    if not os.path.exists(filename):
        return None
    
    hash_obj = hashlib.new(algorithm)
    
    try:
        with open(filename, 'rb') as f:
            # Read in chunks to limit memory use
            while chunk := f.read(8192):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        print(f'\033[31m'f"Error computing hash for {filename}: {e}"+'\033[0m')
        return None


def verify_file_integrity(filename, expected_hash, algorithm='sha256'):
    """
    Compare the file hash to the expected value.

    Args:
        filename: Path to the file.
        expected_hash: Expected hex digest.
        algorithm: Hash algorithm name (default: sha256).

    Returns:
        True if the hashes match, False otherwise.
    """
    if not os.path.exists(filename):
        print('\033[31m'+f"Error: File {filename} not found."+'\033[0m')
        return False
    
    computed_hash = compute_file_hash(filename, algorithm)
    
    if computed_hash is None:
        return False
    
    if computed_hash.lower() == expected_hash.lower():
        print('\033[32m'+f"✓ File integrity verified: {filename}"+'\033[0m')
        return True
    else:
        print('\033[31m'+f"✗ File integrity check FAILED: {filename}"+'\033[0m')
        print('\033[31m'+f"  Expected: {expected_hash}"+'\033[0m')
        print('\033[31m'+f"  Got:      {computed_hash}"+'\033[0m')
        return False


def get_file_info(filename):
    """
    Return filename, size, and hash for a file.

    Args:
        filename: Path to the file.

    Returns:
        Dict with filename, size, hash, and algorithm keys, or None if missing.
    """
    if not os.path.exists(filename):
        return None
    
    try:
        size = os.path.getsize(filename)
        file_hash = compute_file_hash(filename)
        
        return {
            'filename': filename,
            'size': size,
            'hash': file_hash,
            'algorithm': 'sha256'
        }
    except Exception as e:
        print(f'\033[31m'f"Error getting file info for {filename}: {e}"+'\033[0m')
        return None
