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


class TestSummarizeResult:
    """Tests for GeminiClient.summarize_result method."""

    def test_summarize_result_success(self):
        """要約が正常に動作すること"""
        # Given: A mock response with summary text
        # When: summarize_result is called
        # Then: The summary text is returned
        with patch("src.llm.client.genai") as mock_genai:
            mock_client_instance = MagicMock()
            mock_genai.Client.return_value = mock_client_instance

            mock_response = MagicMock()
            mock_response.text = "Japanese: 15件、Korean: 9件です。"
            mock_client_instance.models.generate_content.return_value = mock_response

            client = GeminiClient(api_key="test-key", model_name="gemini-2.0-flash")
            result = client.summarize_result("テスト要約プロンプト")

            assert result == "Japanese: 15件、Korean: 9件です。"

    def test_summarize_result_uses_low_temperature(self):
        """要約は低temperatureを使うこと"""
        # Given: A mock client
        # When: summarize_result is called
        # Then: temperature is 0.1
        with patch("src.llm.client.genai") as mock_genai:
            mock_client_instance = MagicMock()
            mock_genai.Client.return_value = mock_client_instance

            mock_response = MagicMock()
            mock_response.text = "要約テキスト"
            mock_client_instance.models.generate_content.return_value = mock_response

            client = GeminiClient(api_key="test-key", model_name="gemini-2.0-flash")
            client.summarize_result("プロンプト")

            # Check the config passed to generate_content
            call_args = mock_client_instance.models.generate_content.call_args
            assert call_args.kwargs["config"]["temperature"] == 0.1

    def test_summarize_result_uses_limited_tokens(self):
        """要約はmax_output_tokensを制限すること"""
        # Given: A mock client
        # When: summarize_result is called
        # Then: max_output_tokens is 1024
        with patch("src.llm.client.genai") as mock_genai:
            mock_client_instance = MagicMock()
            mock_genai.Client.return_value = mock_client_instance

            mock_response = MagicMock()
            mock_response.text = "要約テキスト"
            mock_client_instance.models.generate_content.return_value = mock_response

            client = GeminiClient(api_key="test-key", model_name="gemini-2.0-flash")
            client.summarize_result("プロンプト")

            call_args = mock_client_instance.models.generate_content.call_args
            assert call_args.kwargs["config"]["max_output_tokens"] == 1024

    def test_summarize_result_no_system_instruction(self):
        """要約はsystem_instructionを使わないこと"""
        # Given: A mock client
        # When: summarize_result is called
        # Then: No system_instruction in config
        with patch("src.llm.client.genai") as mock_genai:
            mock_client_instance = MagicMock()
            mock_genai.Client.return_value = mock_client_instance

            mock_response = MagicMock()
            mock_response.text = "要約テキスト"
            mock_client_instance.models.generate_content.return_value = mock_response

            client = GeminiClient(api_key="test-key", model_name="gemini-2.0-flash")
            client.summarize_result("プロンプト")

            call_args = mock_client_instance.models.generate_content.call_args
            assert "system_instruction" not in call_args.kwargs["config"]

    def test_summarize_result_api_error(self):
        """API呼び出しエラー時にLLMErrorが送出されること"""
        # Given: A mock client that raises an exception
        # When: summarize_result is called
        # Then: LLMError is raised with appropriate message
        with patch("src.llm.client.genai") as mock_genai:
            mock_client_instance = MagicMock()
            mock_genai.Client.return_value = mock_client_instance

            mock_client_instance.models.generate_content.side_effect = Exception(
                "API Error"
            )

            client = GeminiClient(api_key="test-key", model_name="gemini-2.0-flash")
            from src.llm.exceptions import LLMError

            with pytest.raises(LLMError, match="summarization"):
                client.summarize_result("プロンプト")

    def test_summarize_result_empty_response(self):
        """空の応答時にLLMErrorが送出されること"""
        # Given: A mock response with None text
        # When: summarize_result is called
        # Then: LLMError is raised
        with patch("src.llm.client.genai") as mock_genai:
            mock_client_instance = MagicMock()
            mock_genai.Client.return_value = mock_client_instance

            mock_response = MagicMock()
            mock_response.text = None
            mock_client_instance.models.generate_content.return_value = mock_response

            client = GeminiClient(api_key="test-key", model_name="gemini-2.0-flash")
            from src.llm.exceptions import LLMError

            with pytest.raises(LLMError, match="empty"):
                client.summarize_result("プロンプト")
