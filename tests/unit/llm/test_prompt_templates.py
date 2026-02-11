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

    def test_contains_kpi_reference_guidance(self):
        """KPI参照ガイダンスがテンプレートに含まれること"""
        prompt = build_system_prompt("test context")
        assert "現在のKPI値" in prompt
        assert "計算条件" in prompt

    def test_contains_code_mandatory_for_calculations(self):
        """数値計算にはコード生成が必須であることを示す指示がプロンプトに含まれること"""
        prompt = build_system_prompt("test context")
        assert "定量的" in prompt
        assert "必ずPythonコードを生成" in prompt

    def test_contains_no_approximation_rule(self):
        """概算・推測の禁止指示が含まれること"""
        prompt = build_system_prompt("test context")
        assert "概算" in prompt
        assert "禁止" in prompt

    def test_contains_statistics_purpose_clarification(self):
        """統計情報はデータ構造理解用であるという説明が含まれること"""
        prompt = build_system_prompt("test context")
        assert "統計情報" in prompt
        assert "参考情報" in prompt
