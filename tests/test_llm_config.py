import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.llm_config import get_default_model, has_llm_config, openai_client_kwargs


class LLMConfigTests(unittest.TestCase):
    def test_model_name_comes_from_environment_and_allows_cli_override(self):
        with patch.dict(os.environ, {"DEFAULT_MODEL": "Qwen/local-model"}, clear=False):
            self.assertEqual(get_default_model(), "Qwen/local-model")
            self.assertEqual(get_default_model("Qwen/cli-override"), "Qwen/cli-override")

    def test_vllm_configuration_uses_openai_compatible_url_and_api_key(self):
        with patch.dict(os.environ, {
            "OPENAI_BASE_URL": "http://127.0.0.1:8000/v1",
            "OPENAI_API_KEY": "EMPTY",
        }, clear=False):
            self.assertEqual(openai_client_kwargs(), {
                "api_key": "EMPTY",
                "base_url": "http://127.0.0.1:8000/v1",
            })
            self.assertTrue(has_llm_config())

    def test_vllm_url_supplies_placeholder_key_when_key_is_omitted(self):
        with patch.dict(os.environ, {
            "OPENAI_BASE_URL": "http://127.0.0.1:8000/v1",
            "OPENAI_API_KEY": "",
        }, clear=True):
            self.assertEqual(openai_client_kwargs(), {
                "api_key": "EMPTY",
                "base_url": "http://127.0.0.1:8000/v1",
            })
            self.assertTrue(has_llm_config())


if __name__ == "__main__":
    unittest.main()
