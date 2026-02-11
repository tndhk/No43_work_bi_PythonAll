"""Tests for GeminiClient."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from src.llm.client import GeminiClient


class TestGeminiClient:
    """Tests for GeminiClient."""

    def test_init_with_api_key(self):
        """APIキーで初期化できること"""
        with patch("src.llm.client.genai") as mock_genai:
            client = GeminiClient(api_key="test-key", model_name="gemini-2.0-flash")
            assert client.model_name == "gemini-2.0-flash"

    def test_init_configures_client(self):
        """初期化時にgenaiクライアントが設定されること"""
        with patch("src.llm.client.genai") as mock_genai:
            client = GeminiClient(api_key="test-key", model_name="gemini-2.0-flash")
            mock_genai.Client.assert_called_once_with(api_key="test-key")

    def test_send_message(self):
        """メッセージ送信が動作すること"""
        with patch("src.llm.client.genai") as mock_genai:
            mock_client_instance = MagicMock()
            mock_genai.Client.return_value = mock_client_instance

            mock_response = MagicMock()
            mock_response.text = "テスト回答です。"
            mock_client_instance.models.generate_content.return_value = mock_response

            client = GeminiClient(api_key="test-key", model_name="gemini-2.0-flash")
            result = client.send_message(
                user_message="テスト質問",
                history=[],
                system_prompt="あなたはアシスタントです",
            )
            assert result == "テスト回答です。"

    def test_send_message_with_history(self):
        """会話履歴付きメッセージが動作すること"""
        with patch("src.llm.client.genai") as mock_genai:
            mock_client_instance = MagicMock()
            mock_genai.Client.return_value = mock_client_instance

            mock_response = MagicMock()
            mock_response.text = "履歴ありの回答"
            mock_client_instance.models.generate_content.return_value = mock_response

            client = GeminiClient(api_key="test-key", model_name="gemini-2.0-flash")
            history = [
                {"role": "user", "content": "前の質問"},
                {"role": "assistant", "content": "前の回答"},
            ]
            result = client.send_message(
                user_message="追加の質問",
                history=history,
                system_prompt="テスト",
            )
            assert result == "履歴ありの回答"
            # generate_content が呼ばれたことを確認
            mock_client_instance.models.generate_content.assert_called_once()

    def test_send_message_api_error(self):
        """API呼び出しエラー時にLLMErrorが送出されること"""
        with patch("src.llm.client.genai") as mock_genai:
            mock_client_instance = MagicMock()
            mock_genai.Client.return_value = mock_client_instance

            mock_client_instance.models.generate_content.side_effect = Exception(
                "API Error"
            )

            client = GeminiClient(api_key="test-key", model_name="gemini-2.0-flash")
            from src.llm.exceptions import LLMError

            with pytest.raises(LLMError, match="API"):
                client.send_message(
                    user_message="テスト",
                    history=[],
                    system_prompt="テスト",
                )

    def test_send_message_no_api_key(self):
        """APIキーが空の場合エラーになること"""
        with patch("src.llm.client.genai") as mock_genai:
            from src.llm.exceptions import LLMError

            with pytest.raises(LLMError):
                GeminiClient(api_key="", model_name="gemini-2.0-flash")
