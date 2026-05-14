"""输入校验单元测试。"""


from agent.guardrails.validator import InputValidator


class TestInputValidator:
    def test_valid_query(self):
        ok, err = InputValidator.validate_query("扫地机器人怎么选？")
        assert ok is True
        assert err is None

    def test_empty_query(self):
        ok, err = InputValidator.validate_query("")
        assert ok is False
        assert err is not None

    def test_whitespace_query(self):
        ok, err = InputValidator.validate_query("   ")
        assert ok is False

    def test_script_tag_blocked(self):
        ok, err = InputValidator.validate_query("<script>alert(1)</script>")
        assert ok is False

    def test_sql_injection_blocked(self):
        ok, err = InputValidator.validate_query("DROP TABLE users")
        assert ok is False

    def test_max_length(self):
        ok, err = InputValidator.validate_query("a" * 2001)
        assert ok is False

    def test_boundary_length(self):
        ok, err = InputValidator.validate_query("a" * 2000)
        assert ok is True
