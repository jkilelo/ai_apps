from core.actions import parse_actions, Nav, Click, Type, Wait, Extract

SCRIPT = """
# comment
NAV https://example.com
CLICK .btn-login
TYPE input[name=email] => user@example.com
WAIT 250
EXTRACT h1.title
""".strip()


def test_parse_actions_basic():
    acts = parse_actions(SCRIPT)
    assert len(acts) == 5
    assert isinstance(acts[0], Nav) and acts[0].url.endswith("example.com")
    assert isinstance(acts[1], Click)
    assert isinstance(acts[2], Type) and acts[2].text == "user@example.com"
    assert isinstance(acts[3], Wait) and acts[3].ms == 250
    assert isinstance(acts[4], Extract)


def test_parse_unknown_action():
    bad = "BAD something"
    try:
        parse_actions(bad)
    except ValueError as e:
        assert "Unknown action" in str(e)
    else:
        assert False, "Expected ValueError"
