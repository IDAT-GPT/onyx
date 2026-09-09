from typing import Any

from onyx.llm.multi_llm import _fill_missing_message_content


def test_assistant_tool_call_message_gets_empty_content() -> None:
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": "hi"},
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "c1",
                    "type": "function",
                    "function": {"name": "f", "arguments": "{}"},
                }
            ],
        },
        {"role": "tool", "tool_call_id": "c1", "content": "res"},
    ]

    filled = _fill_missing_message_content(messages)

    assert filled[1]["content"] == ""
    # Non-content fields survive untouched.
    assert filled[1]["tool_calls"][0]["id"] == "c1"
    # Messages that already carry content are unchanged.
    assert filled[0] == {"role": "user", "content": "hi"}
    assert filled[2]["content"] == "res"


def test_null_content_is_replaced_with_empty_string() -> None:
    filled = _fill_missing_message_content(
        [{"role": "assistant", "content": None, "tool_calls": []}]
    )
    assert filled[0]["content"] == ""


def test_existing_content_values_are_preserved() -> None:
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": [{"type": "text", "text": "hello"}]},
        {"role": "assistant", "content": ""},
    ]
    assert _fill_missing_message_content(messages) == messages


def test_input_list_is_not_mutated() -> None:
    original: dict[str, Any] = {"role": "assistant", "tool_calls": []}
    _fill_missing_message_content([original])
    assert "content" not in original
