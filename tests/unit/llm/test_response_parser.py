from src.llm.response_parser import parse_response, ParsedResponse


class TestParseResponse:
    """Tests for LLM response parsing."""

    def test_text_only(self):
        """テキストのみの応答を正しくパースすること"""
        raw = "これはテスト回答です。"
        result = parse_response(raw)
        assert isinstance(result, ParsedResponse)
        assert result.text == "これはテスト回答です。"
        assert result.code is None

    def test_text_with_python_code_block(self):
        """テキストとPythonコードブロックを分離すること"""
        raw = """分析結果を表示します。

```python
result = df['age'].mean()
```

以上が平均年齢です。"""
        result = parse_response(raw)
        assert "分析結果を表示します。" in result.text
        assert "以上が平均年齢です。" in result.text
        assert result.code == "result = df['age'].mean()"

    def test_code_block_without_language(self):
        """言語指定のないコードブロックはコードとして抽出しないこと"""
        raw = """説明:

```
これはテキストです
```"""
        result = parse_response(raw)
        assert result.code is None

    def test_multiple_code_blocks_takes_first(self):
        """複数のpythonコードブロックがある場合、最初のものを使うこと"""
        raw = """まず:

```python
result = df.head()
```

次に:

```python
result = df.tail()
```"""
        result = parse_response(raw)
        assert result.code == "result = df.head()"

    def test_empty_response(self):
        """空の応答を処理すること"""
        result = parse_response("")
        assert result.text == ""
        assert result.code is None

    def test_code_block_with_multiline(self):
        """複数行のコードブロックを正しく抽出すること"""
        raw = """結果:

```python
filtered = df[df['age'] > 30]
grouped = filtered.groupby('name')['salary'].mean()
result = grouped.to_dict()
```"""
        result = parse_response(raw)
        expected_code = (
            "filtered = df[df['age'] > 30]\n"
            "grouped = filtered.groupby('name')['salary'].mean()\n"
            "result = grouped.to_dict()"
        )
        assert result.code == expected_code

    def test_text_around_code_preserved(self):
        """コードブロック前後のテキストが保持されること"""
        raw = "前のテキスト\n\n```python\nresult = 42\n```\n\n後のテキスト"
        result = parse_response(raw)
        assert "前のテキスト" in result.text
        assert "後のテキスト" in result.text
        assert "```" not in result.text

    def test_whitespace_handling(self):
        """コードの前後の空白がトリムされること"""
        raw = """テスト:

```python

  result = df.describe()

```"""
        result = parse_response(raw)
        assert result.code == "result = df.describe()"

    def test_non_python_code_blocks_remain_in_text(self):
        """sql/json/言語なしのfencedコードブロックがtextに残ること"""
        raw = """SQLの例:

```sql
SELECT * FROM users WHERE age > 30;
```

JSONの例:

```json
{"key": "value"}
```

言語指定なし:

```
plain text block
```"""
        result = parse_response(raw)
        assert result.code is None
        assert "```sql" in result.text
        assert "SELECT * FROM users" in result.text
        assert "```json" in result.text
        assert '{"key": "value"}' in result.text
        assert "plain text block" in result.text

    def test_only_first_python_block_extracted_rest_stays(self):
        """2つ目のpythonブロックがtextに残ること"""
        raw = """最初の分析:

```python
result = df.head()
```

追加の分析:

```python
result = df.tail()
```"""
        result = parse_response(raw)
        assert result.code == "result = df.head()"
        # First python block should be removed from text
        assert "result = df.head()" not in result.text
        # Second python block should remain in text
        assert "```python" in result.text
        assert "result = df.tail()" in result.text

    def test_mixed_code_blocks(self):
        """pythonは抽出、sql等はtext内に保持される混合パターン"""
        raw = """データ分析の手順:

まずSQLで確認:

```sql
SELECT COUNT(*) FROM orders;
```

Pythonで集計:

```python
result = df.groupby('category').sum()
```

結果をJSON形式で:

```json
{"total": 100}
```"""
        result = parse_response(raw)
        assert result.code == "result = df.groupby('category').sum()"
        # SQL and JSON blocks should remain in text
        assert "```sql" in result.text
        assert "SELECT COUNT(*)" in result.text
        assert "```json" in result.text
        assert '{"total": 100}' in result.text
        # Python block should be removed from text
        assert "result = df.groupby('category').sum()" not in result.text
