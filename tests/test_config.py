from src.config import Config
import os
import shutil
from pytest import fixture


class TestConfig:

    _TEST_CONFIG_FILE = "sample.config.toml"

    @fixture
    def setup(self):
        # Delete Config singleton
        Config._instance = None

    @fixture
    def patch_config(self, mocker, tmpdir):
        """
        Patch the class Config
        Config._CONFIG_FILE is changed to a path towards a temporary file
        The temporary file is a copy of _TEST_CONFIG_FILE
        """
        assert os.path.isfile(self._TEST_CONFIG_FILE)
        p = tmpdir
        p = shutil.copy(self._TEST_CONFIG_FILE, p)
        return mocker.patch("src.config.Config._CONFIG_FILE", p)

    @fixture
    def patch_load_config(self, mocker):
        """
        Patch load_config in class Config
        The return value from load_config is changed to `{}`
        """
        return mocker.patch("src.config.Config.load_config", return_value={})

    def test_creation(self, setup, patch_config):
        assert Config() is not None
    
    def test_singleton(self, setup, patch_config):
        assert Config() == Config()

    def test_load_config_called_once_during_multiple_access(self, setup, patch_config, patch_load_config):
        Config(), Config(), Config(), Config(), Config()
        patch_load_config.assert_called_once()

    def test_save_config_correctly_saves_config(self, setup, patch_config):
        # Read config from file and modify values
        Config().set_bing_api_key("10random_bing_key01")
        Config().set_logs_dir("10random_logs_dir01")
        # (as of March 28th, setters save to file)
        # Get the config that was written to file 
        config_saved = Config().get_config()
        # Force loading of the config from the file by deleting singleton
        Config._instance = None
        # Get the config loaded from file
        config_loaded = Config().get_config()

        assert config_saved == config_loaded
        



