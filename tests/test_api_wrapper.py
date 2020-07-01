import sys, unittest, logging, asyncio, time, toml, os, shutil

sys.path.append("../")
import cryptocom

logging.basicConfig(level=logging.INFO)


class Config:
    def __init__(self, file_name, template_name):
        config_file = self.extract_config(file_name, template_name)
        self.load_config(config_file)

    def get_path(self, name):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), name)

    def extract_config(self, file_name, template_name):
        config_file = self.get_path(file_name)
        if not os.path.isfile(config_file):
            logging.info("config file doesn't exist, copying template!")
            shutil.copyfile(self.get_path(template_name), config_file)
        return config_file

    def load_config(self, config_file):
        config = toml.load(config_file)

        binance = config["cryptocom"]
        self.api_key = binance["api_key"]
        self.api_secret = binance["api_secret"]


class TestQueries(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        config = Config("config.toml", "config.template.toml")
        self.client = cryptocom.Client(config.api_key, config.api_secret)

    async def test_load(self):
        await self.client.load()

if __name__ == "__main__":
    unittest.main()
