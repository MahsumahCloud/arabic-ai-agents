from conftest import load

setup = load("lessons/00/check_setup.py")


def test_python_version_check():
    assert setup.check_python((3, 12, 0))[0] is True
    assert setup.check_python((3, 9, 18))[0] is False


def test_api_key_check_never_prints_the_key():
    ok, message = setup.check_api_key({"ANTHROPIC_API_KEY": "sk-secret-value"})
    assert ok
    assert "sk-secret-value" not in message and "sk-" not in message


def test_api_key_missing_or_blank():
    assert setup.check_api_key({})[0] is False
    assert setup.check_api_key({"ANTHROPIC_API_KEY": "   "})[0] is False
