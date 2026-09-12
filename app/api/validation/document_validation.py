from pathlib import Path
from fastapi import UploadFile


class DocumentValidator:

    def __init__(self, config):
        self.allowed_extensions = config.extensions
        self.max_size_mb = config.max_size_mb
        self.max_size_bytes = self.max_size_mb * 1024 * 1024

    def validate_extension(self, filename: str) -> tuple[bool, str | None]:
        """Check whether the file extension is allowed."""

        extension = Path(filename).suffix.lower()

        if extension not in self.allowed_extensions:
            return False, f"File type '{extension}' not allowed"

        return True, None

    def validate_size(self, contents: bytes) -> tuple[bool, str | None]:
        """Check whether the file size is within the configured limit."""

        if len(contents) > self.max_size_bytes:
            return False, f"File too large. Max {self.max_size_mb}MB"

        return True, None

    def validate_filename(self, filename: str) -> tuple[bool, str | None]:
        """Check that a filename exists."""

        if not filename or not filename.strip():
            return False, "Filename is missing"

        return True, None

    def validate(
        self,
        filename: str,
        contents: bytes
    ) -> tuple[bool, str | None]:

        is_valid, error = self.validate_filename(filename)

        if not is_valid:
            return False, error

        is_valid, error = self.validate_extension(filename)

        if not is_valid:
            return False, error

        is_valid, error = self.validate_size(contents)

        if not is_valid:
            return False, error

        return True, None