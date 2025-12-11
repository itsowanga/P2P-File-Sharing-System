import hashlib
import os


def compute_file_hash(filename, algorithm='sha256'):
    """
    Compute the hash of a file using the specified algorithm.
    
    Args:
        filename (str): Path to the file to hash
        algorithm (str): Hashing algorithm to use (default: 'sha256')
    
    Returns:
        str: Hexadecimal hash string of the file, or None if file doesn't exist
    """
    if not os.path.exists(filename):
        return None
    
    hash_obj = hashlib.new(algorithm)
    
    try:
        with open(filename, 'rb') as f:
            # Read file in chunks to handle large files
            while chunk := f.read(8192):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        print(f'\033[31m'f"Error computing hash for {filename}: {e}"+'\033[0m')
        return None


def verify_file_integrity(filename, expected_hash, algorithm='sha256'):
    """
    Verify the integrity of a downloaded file by comparing its hash with the expected hash.
    
    Args:
        filename (str): Path to the file to verify
        expected_hash (str): Expected hash value (hexadecimal string)
        algorithm (str): Hashing algorithm used (default: 'sha256')
    
    Returns:
        bool: True if hashes match (file is intact), False otherwise
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
    Get file information including name, size, and hash.
    
    Args:
        filename (str): Path to the file
    
    Returns:
        dict: Dictionary containing filename, size, and hash, or None if file doesn't exist
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
