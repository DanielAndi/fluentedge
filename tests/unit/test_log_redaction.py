"""Logging redaction tests (FR-API-005, NFR-PRIV-002)."""

import logging

from api.app.main import RedactingFilter


def test_redacting_filter_blocks_sensitive_markers():
    filt = RedactingFilter()
    record = logging.LogRecord(
        name="api",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="payload contains access_token=secret",
        args=(),
        exc_info=None,
    )
    assert filt.filter(record) is False


def test_redacting_filter_allows_safe_messages():
    filt = RedactingFilter()
    record = logging.LogRecord(
        name="api",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="predict_complete request_id=req_abc label=pass",
        args=(),
        exc_info=None,
    )
    assert filt.filter(record) is True
