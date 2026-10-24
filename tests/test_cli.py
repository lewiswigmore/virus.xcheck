"""Tests for CLI argument parsing and the main() entry point."""

import sys
import pytest
from unittest.mock import patch, MagicMock

import virusxcheck


VALID_SHA256 = "a" * 64


class TestNoArguments:
    """When no arguments are provided, help is printed and exit code is 1."""

    def test_no_args_exits_with_code_1(self):
        with patch.object(sys, "argv", ["virusxcheck"]):
            with pytest.raises(SystemExit) as exc_info:
                virusxcheck.main()
            assert exc_info.value.code == 1


class TestSaveConfig:
    """--save-config with no hash/file prompts for input then exits."""

    def test_save_config_prompts_and_exits(self):
        with patch.object(sys, "argv", ["virusxcheck", "--save-config"]):
            with patch("builtins.input", side_effect=EOFError):
                with pytest.raises(SystemExit) as exc_info:
                    virusxcheck.main()
                assert exc_info.value.code == 0

    def test_save_config_saves_keys(self):
        with patch.object(sys, "argv", ["virusxcheck", "--save-config"]):
            with patch("builtins.input", side_effect=["fake-vx-key", "fake-vt-key"]):
                with patch("virusxcheck.update_env_file_multiple") as mock_update:
                    with pytest.raises(SystemExit) as exc_info:
                        virusxcheck.main()
                    assert exc_info.value.code == 0
                    mock_update.assert_called_once_with({
                        "VIRUSXCHECK_API_KEY": "fake-vx-key",
                        "VIRUSTOTAL_API_KEY": "fake-vt-key",
                    })


class TestSingleHash:
    """Tests for -s / --single hash processing."""

    def test_valid_hash_processes(self):
        mock_result = {"status": "found"}
        with patch.object(sys, "argv", ["virusxcheck", "-s", VALID_SHA256]):
            with patch("virusxcheck.DEFAULT_API_KEY", "test-key"), \
                 patch("virusxcheck.DEFAULT_VT_API_KEY", "vt-test-key"), \
                 patch("virusxcheck.VirusExchangeAPI") as mock_vx_cls, \
                 patch("virusxcheck.VirusTotalAPI") as mock_vt_cls, \
                 patch("virusxcheck.check_hash", return_value=mock_result) as mock_check, \
                 patch("virusxcheck.pretty_print_results"):
                virusxcheck.main()
                mock_check.assert_called_once_with(
                    VALID_SHA256, mock_vx_cls.return_value, mock_vt_cls.return_value, False
                )

    def test_invalid_hash_exits_with_code_1(self):
        with patch.object(sys, "argv", ["virusxcheck", "-s", "not-a-hash"]):
            with patch("virusxcheck.DEFAULT_API_KEY", "test-key"), \
                 patch("virusxcheck.DEFAULT_VT_API_KEY", "vt-test-key"):
                with pytest.raises(SystemExit) as exc_info:
                    virusxcheck.main()
                assert exc_info.value.code == 1


class TestFileInput:
    """-f with a CSV file processes hashes via thread pool."""

    def test_file_processes_hashes(self):
        hashes = [VALID_SHA256]
        mock_result = {"status": "found"}
        with patch.object(sys, "argv", ["virusxcheck", "-f", "hashes.csv"]):
            with patch("virusxcheck.DEFAULT_API_KEY", "test-key"), \
                 patch("virusxcheck.DEFAULT_VT_API_KEY", "vt-test-key"), \
                 patch("virusxcheck.VirusExchangeAPI"), \
                 patch("virusxcheck.read_csv", return_value=hashes), \
                 patch("virusxcheck.check_hash", return_value=mock_result), \
                 patch("virusxcheck.pretty_print_results"):
                virusxcheck.main()


class TestNoColorFlag:
    """--no-color disables colorama."""

    def test_no_color_calls_deinit(self):
        with patch.object(sys, "argv", ["virusxcheck", "--no-color", "-s", VALID_SHA256]):
            with patch("virusxcheck.DEFAULT_API_KEY", "test-key"), \
                 patch("virusxcheck.DEFAULT_VT_API_KEY", "vt-test-key"), \
                 patch("virusxcheck.VirusExchangeAPI"), \
                 patch("virusxcheck.check_hash", return_value={}), \
                 patch("virusxcheck.pretty_print_results"), \
                 patch("virusxcheck.colorama") as mock_colorama:
                virusxcheck.main()
                mock_colorama.deinit.assert_called_once()


class TestOutputFlag:
    """--output writes results to the specified format."""

    def _run_with_output(self, output_path):
        """Helper to run main() with -s and --output."""
        with patch.object(sys, "argv", ["virusxcheck", "-s", VALID_SHA256, "-o", output_path]):
            with patch("virusxcheck.DEFAULT_API_KEY", "test-key"), \
                 patch("virusxcheck.DEFAULT_VT_API_KEY", "vt-test-key"), \
                 patch("virusxcheck.VirusExchangeAPI"), \
                 patch("virusxcheck.check_hash", return_value={}), \
                 patch("virusxcheck.write_to_csv") as mock_csv, \
                 patch("virusxcheck.write_to_json") as mock_json:
                virusxcheck.main()
        return mock_csv, mock_json

    def test_csv_output(self):
        mock_csv, mock_json = self._run_with_output("results.csv")
        mock_csv.assert_called_once()
        mock_json.assert_not_called()

    def test_json_output(self):
        mock_csv, mock_json = self._run_with_output("results.json")
        mock_json.assert_called_once()
        mock_csv.assert_not_called()

    def test_invalid_extension_exits_with_code_1(self):
        with patch.object(sys, "argv", ["virusxcheck", "-s", VALID_SHA256, "-o", "results.txt"]):
            with patch("virusxcheck.DEFAULT_API_KEY", "test-key"), \
                 patch("virusxcheck.DEFAULT_VT_API_KEY", "vt-test-key"), \
                 patch("virusxcheck.VirusExchangeAPI"), \
                 patch("virusxcheck.check_hash", return_value={}):
                with pytest.raises(SystemExit) as exc_info:
                    virusxcheck.main()
                assert exc_info.value.code == 1


class TestMissingApiKey:
    """Missing API key prints error and exits with code 1."""

    def test_no_api_key_exits_with_code_1(self):
        with patch.object(sys, "argv", ["virusxcheck", "-s", VALID_SHA256]):
            with patch("virusxcheck.DEFAULT_API_KEY", ""), \
                 patch("virusxcheck.DEFAULT_VT_API_KEY", ""):
                with pytest.raises(SystemExit) as exc_info:
                    virusxcheck.main()
                assert exc_info.value.code == 1
