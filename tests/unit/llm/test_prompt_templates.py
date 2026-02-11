from src.llm.prompt_templates import build_system_prompt, SYSTEM_PROMPT_TEMPLATE


class TestBuildSystemPrompt:
    """Tests for system prompt construction."""

    def test_context_injection(self):
        """コンテキストがシステムプロンプトに注入されること"""
        context = "データセット: sales_data\nカラム: date, amount, region"
        prompt = build_system_prompt(context)
        assert "sales_data" in prompt
        assert "date, amount, region" in prompt

    def test_contains_role_definition(self):
        """プロンプトにロール定義が含まれること"""
        prompt = build_system_prompt("test context")
        assert "データ分析" in prompt or "アシスタント" in prompt

    def test_contains_code_rules(self):
        """プロンプトにコード生成ルールが含まれること"""
        prompt = build_system_prompt("test context")
        assert "result" in prompt
        assert "df" in prompt

    def test_contains_japanese_instruction(self):
        """日本語回答指示が含まれること"""
        prompt = build_system_prompt("test context")
        assert "日本語" in prompt

    def test_template_is_string(self):
        """テンプレート定数が文字列であること"""
        assert isinstance(SYSTEM_PROMPT_TEMPLATE, str)
        assert "{context}" in SYSTEM_PROMPT_TEMPLATE

    def test_empty_context(self):
        """空のコンテキストでもエラーにならないこと"""
        prompt = build_system_prompt("")
        assert isinstance(prompt, str)
        assert len(prompt) > 0
