from src.llm.prompt_templates import (
    build_system_prompt,
    build_summarize_prompt,
    SYSTEM_PROMPT_TEMPLATE,
    SUMMARIZE_RESULT_TEMPLATE,
)


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


class TestBuildSummarizePrompt:
    """Tests for summarize prompt construction."""

    def test_all_fields_injected(self):
        """全フィールドがプロンプトに注入されること"""
        # Given: user question, code, and result
        # When: build_summarize_prompt is called
        # Then: All fields are present in the prompt
        prompt = build_summarize_prompt(
            user_question="言語別に集計して",
            code="result = df.groupby('language').size()",
            result="Japanese    15\nKorean       9",
        )
        assert "言語別に集計して" in prompt
        assert "df.groupby('language').size()" in prompt
        assert "Japanese    15" in prompt
        assert "Korean       9" in prompt

    def test_contains_japanese_instruction(self):
        """日本語回答指示が含まれること"""
        # Given: any input
        # When: build_summarize_prompt is called
        # Then: Japanese instruction is present
        prompt = build_summarize_prompt("test", "code", "result")
        assert "日本語" in prompt

    def test_contains_no_code_block_rule(self):
        """Pythonコード禁止ルールが含まれること"""
        # Given: any input
        # When: build_summarize_prompt is called
        # Then: No code block rule is present
        prompt = build_summarize_prompt("test", "code", "result")
        assert "```python" in prompt
        assert "禁止" in prompt

    def test_contains_accuracy_instruction(self):
        """数値の正確性指示が含まれること"""
        # Given: any input
        # When: build_summarize_prompt is called
        # Then: Accuracy instruction is present
        prompt = build_summarize_prompt("test", "code", "result")
        assert "正確" in prompt

    def test_template_is_string(self):
        """テンプレート定数が文字列であること"""
        # Given: the template constant
        # When: checking its type
        # Then: It should be a string with placeholders
        assert isinstance(SUMMARIZE_RESULT_TEMPLATE, str)
        assert "{user_question}" in SUMMARIZE_RESULT_TEMPLATE
        assert "{code}" in SUMMARIZE_RESULT_TEMPLATE
        assert "{result}" in SUMMARIZE_RESULT_TEMPLATE

    def test_empty_result(self):
        """空の結果でもエラーにならないこと"""
        # Given: empty result
        # When: build_summarize_prompt is called
        # Then: No error occurs
        prompt = build_summarize_prompt("question", "code", "")
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_multiline_result(self):
        """複数行の結果が正しく含まれること"""
        # Given: multiline result
        # When: build_summarize_prompt is called
        # Then: All lines are preserved
        result = """original_language_name
Japanese    15
Korean       9
dtype: int64"""
        prompt = build_summarize_prompt("質問", "result = df.groupby('x').size()", result)
        assert "original_language_name" in prompt
        assert "Japanese    15" in prompt
        assert "dtype: int64" in prompt
