from src.config import Config
import os
import shutil
from pytest import fixture


class TestConfig:

    _TEST_CONFIG_FILE = "sample.config.toml"

    @fixture
    def patch_config(self, mocker, tmpdir):
        """
        Patch the class Config
        Config._CONFIG_FILE is changed to point to the example config file
        """
        assert os.path.isfile(self._TEST_CONFIG_FILE)
        p = tmpdir
        p = shutil.copy(self._TEST_CONFIG_FILE, p)
        return mocker.patch("src.config.Config._CONFIG_FILE", p)

    @fixture
    def patch_toml_load(self, mocker):
        """
        Patch every use of toml.load in class Config
        The return value from toml.load is changed to `{}`
        """
        return mocker.patch("src.config.toml.load", return_value={})

    def test_creation(self, patch_config):
        assert Config() is not None
    
    def test_singleton(self, patch_config):
        assert Config() == Config()

    def test_toml_load_called_once_during_multiple_access(self, patch_toml_load):
        Config(), Config(), Config(), Config(), Config()
        patch_toml_load.assert_called_once()

    def test_save_config_correctly_saves_config(self, patch_config):
        # Read config from file and modify values
        Config().set_bing_api_key("10random_bing_key01")
        Config().set_logs_dir("10random_logs_dir01")
        # (as of March 28th, setters save to file)
        # Get the config that was written to file 
        config_saved = Config().get_config()
        # Force loading of the config from the file by deleting singleton
        Config()._instance = None
        # Get the config loaded from file
        config_loaded = Config().get_config()

        assert config_saved == config_loaded
        



