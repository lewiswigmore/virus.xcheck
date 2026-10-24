"""Tests for the check_hash function in virusxcheck."""

from unittest.mock import Mock
from virusxcheck import check_hash


# Example hashes for each type (valid hex, correct length)
SHA256 = "a" * 64
MD5 = "b" * 32
SHA1 = "c" * 40


def _make_api(get_result=None, fallback_result=None, get_side_effect=None):
    """Build a mock VX API with configurable behavior."""
    api = Mock()
    if get_side_effect:
        api.get_sample_details.side_effect = get_side_effect
    else:
        api.get_sample_details.return_value = get_result or {}
    api.fallback_check.return_value = fallback_result or {
        "status": "Not Found",
        "virustotal_url": None,
    }
    return api


def _make_vt_api(scan_results=None):
    """Build a mock VirusTotal API."""
    vt = Mock()
    vt.get_file_report.return_value = {"raw": "data"}
    vt.extract_scan_results.return_value = scan_results or {
        "last_analysis_stats": {"malicious": 5, "suspicious": 0, "undetected": 60},
    }
    return vt


# -- 1. Invalid hash returns early ----------------------------------------

def test_invalid_hash_returns_error():
    api = Mock()
    result = check_hash("not_a_valid_hash!", api)
    assert result["status"] == "Invalid hash format"
    assert result["virustotal_url"] is None
    api.get_sample_details.assert_not_called()


# -- 2. SHA-256 found in VX, no VT ----------------------------------------

def test_sha256_vx_found_no_vt():
    vx_result = {
        "status": "Found",
        "virustotal_url": f"https://www.virustotal.com/gui/file/{SHA256}",
    }
    api = _make_api(get_result=vx_result)

    result = check_hash(SHA256, api)

    assert result["status"] == "Found"
    assert "vt_data" not in result
    api.get_sample_details.assert_called_once_with(SHA256)
    api.fallback_check.assert_not_called()


# -- 3. SHA-256 not found in VX, no VT ------------------------------------

def test_sha256_vx_not_found_no_vt():
    vx_result = {"status": "Not Found", "virustotal_url": None}
    api = _make_api(get_result=vx_result)

    result = check_hash(SHA256, api)

    assert result["status"] == "Not Found"
    assert "vt_data" not in result


# -- 4. SHA-256 VX error triggers fallback ---------------------------------

def test_sha256_vx_error_triggers_fallback():
    vx_result = {"status": "Error: API unavailable"}
    fallback = {"status": "Found via fallback", "virustotal_url": "https://example.com"}
    api = _make_api(get_result=vx_result, fallback_result=fallback)

    result = check_hash(SHA256, api)

    api.fallback_check.assert_called_once_with(SHA256)
    assert result["status"] == "Found via fallback"


# -- 5. SHA-256 with VT API includes vt_data ------------------------------

def test_sha256_with_vt_api():
    vx_result = {"status": "Found", "virustotal_url": "https://example.com"}
    api = _make_api(get_result=vx_result)
    vt_api = _make_vt_api(scan_results={"malicious": 3})

    result = check_hash(SHA256, api, vt_api=vt_api)

    assert result["status"] == "Found"
    assert result["vt_data"] == {"malicious": 3}
    vt_api.get_file_report.assert_called_once_with(SHA256)
    vt_api.extract_scan_results.assert_called_once()


# -- 6. MD5 hash -> not supported in VX, queries VT if available ----------

def test_md5_without_vt():
    api = Mock()
    result = check_hash(MD5, api)

    assert result["status"] == "Hash type not supported in VX database"
    assert MD5 in result["virustotal_url"]
    assert "vt_data" not in result
    api.get_sample_details.assert_not_called()


def test_md5_with_vt():
    api = Mock()
    vt_api = _make_vt_api(scan_results={"malicious": 1})

    result = check_hash(MD5, api, vt_api=vt_api)

    assert result["status"] == "Hash type not supported in VX database"
    assert result["vt_data"] == {"malicious": 1}
    vt_api.get_file_report.assert_called_once_with(MD5)


# -- 7. SHA-1 hash -> same behavior as MD5 --------------------------------

def test_sha1_without_vt():
    api = Mock()
    result = check_hash(SHA1, api)

    assert result["status"] == "Hash type not supported in VX database"
    assert SHA1 in result["virustotal_url"]
    assert "vt_data" not in result


def test_sha1_with_vt():
    api = Mock()
    vt_api = _make_vt_api(scan_results={"malicious": 2})

    result = check_hash(SHA1, api, vt_api=vt_api)

    assert result["vt_data"] == {"malicious": 2}


# -- 8. Exception in VX API triggers fallback -----------------------------

def test_exception_in_vx_triggers_fallback():
    fallback = {"status": "Fallback result", "virustotal_url": None}
    api = _make_api(
        get_side_effect=ConnectionError("network down"),
        fallback_result=fallback,
    )

    result = check_hash(SHA256, api)

    api.fallback_check.assert_called_once_with(SHA256)
    assert result["status"] == "Fallback result"


def test_exception_in_vx_with_vt_still_queries_vt():
    fallback = {"status": "Fallback result", "virustotal_url": None}
    api = _make_api(
        get_side_effect=RuntimeError("boom"),
        fallback_result=fallback,
    )
    vt_api = _make_vt_api(scan_results={"malicious": 7})

    result = check_hash(SHA256, api, vt_api=vt_api)

    assert result["status"] == "Fallback result"
    assert result["vt_data"] == {"malicious": 7}
    vt_api.get_file_report.assert_called_once_with(SHA256)


# -- 9. VX disabled (backend shut down) -----------------------------------

def test_vx_disabled_no_vt_returns_unavailable():
    api = _make_api()
    result = check_hash(SHA256, api, vx_enabled=False)

    assert result["status"] == "Virus Exchange lookup unavailable (service shut down)"
    assert SHA256 in result["virustotal_url"]
    assert "vt_data" not in result
    api.get_sample_details.assert_not_called()
    api.fallback_check.assert_not_called()


def test_vx_disabled_with_vt_queries_vt_only():
    api = _make_api()
    vt_api = _make_vt_api(scan_results={"malicious": 4})

    result = check_hash(SHA256, api, vt_api=vt_api, vx_enabled=False)

    assert result["status"] == "Virus Exchange lookup unavailable (service shut down)"
    assert result["vt_data"] == {"malicious": 4}
    vt_api.get_file_report.assert_called_once_with(SHA256)


def test_vx_disabled_invalid_hash_still_invalid():
    api = _make_api()
    result = check_hash("nothex!", api, vx_enabled=False)

    assert result["status"] == "Invalid hash format"
    api.get_sample_details.assert_not_called()
