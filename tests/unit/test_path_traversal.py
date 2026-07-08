"""Path traversal protection for storage (NFR-SEC-002)."""

import pytest

from api.app.services.storage import FilesystemStorage


def test_storage_rejects_traversal(tmp_path):
    storage = FilesystemStorage(str(tmp_path))
    with pytest.raises(ValueError):
        storage.get_object("bucket", "../outside.wav")
