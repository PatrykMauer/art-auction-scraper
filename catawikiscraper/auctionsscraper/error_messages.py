"""Store error messages"""

import json

FILE_NOT_FOUND_ERROR = "The file 'auctions.json' was not found."
PERMISSION_ERROR = "Permission denied while trying to read 'auctions.json'."
IO_ERROR = "An I/O error occurred while accessing 'auctions.json': {error}"
JSON_DECODE_ERROR = "Failed to decode JSON. The file may be corrupted or is not in JSON format."

error_msg = {
    FileNotFoundError: FILE_NOT_FOUND_ERROR,
    PermissionError: PERMISSION_ERROR,
    json.JSONDecodeError: JSON_DECODE_ERROR,
    IOError: IO_ERROR
}
