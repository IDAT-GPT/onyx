from typing import Any
from unittest.mock import MagicMock, patch

from onyx.connectors.clickup.connector import CLICKUP_API_BASE_URL, ClickupConnector
from onyx.connectors.models import Document


def _mock_response(json_response: dict[str, Any]) -> MagicMock:
    response = MagicMock()
    response.json.return_value = json_response
    return response


def _task(task_id: str, parent: str | None = None) -> dict[str, Any]:
    return {
        "id": task_id,
        "name": f"Task {task_id}",
        "url": f"https://app.clickup.com/t/{task_id}",
        "date_updated": "1700000000000",
        "date_created": "1690000000000",
        "creator": {"username": "creator", "email": "creator@example.com"},
        "assignees": [],
        "markdown_description": "body",
        "status": {"status": "open"},
        "list": {"name": "list"},
        "project": {"name": "project"},
        "folder": {"name": "folder"},
        "space": {"id": "space-1"},
        "tags": [],
        "parent": parent,
    }


def test_get_all_tasks_filtered_uses_relative_endpoint() -> None:
    connector = ClickupConnector(api_token="test-token", team_id="123")
    response = _mock_response({"tasks": []})

    with patch("onyx.connectors.clickup.connector.requests.get") as mock_get:
        mock_get.return_value = response

        list(connector._get_all_tasks_filtered())

    mock_get.assert_called_once()
    assert mock_get.call_args.args[0] == f"{CLICKUP_API_BASE_URL}/team/123/task"


def test_get_all_tasks_filtered_requests_subtasks_by_default() -> None:
    connector = ClickupConnector(api_token="test-token", team_id="123")
    response = _mock_response({"tasks": []})

    with patch("onyx.connectors.clickup.connector.requests.get") as mock_get:
        mock_get.return_value = response

        list(connector._get_all_tasks_filtered())

    params = mock_get.call_args.kwargs["params"]
    assert params["subtasks"] == "true"


def test_get_all_tasks_filtered_can_exclude_subtasks() -> None:
    connector = ClickupConnector(
        api_token="test-token", team_id="123", include_subtasks=False
    )
    response = _mock_response({"tasks": []})

    with patch("onyx.connectors.clickup.connector.requests.get") as mock_get:
        mock_get.return_value = response

        list(connector._get_all_tasks_filtered())

    params = mock_get.call_args.kwargs["params"]
    assert "subtasks" not in params


def test_subtask_documents_record_parent_task_id() -> None:
    connector = ClickupConnector(
        api_token="test-token", team_id="123", retrieve_task_comments=False
    )
    response = _mock_response(
        {
            "tasks": [_task("parent-1"), _task("child-1", parent="parent-1")],
            "last_page": True,
        }
    )

    with patch("onyx.connectors.clickup.connector.requests.get") as mock_get:
        mock_get.return_value = response

        batches = list(connector._get_all_tasks_filtered())

    documents = [doc for batch in batches for doc in batch]
    assert [doc.id for doc in documents] == ["parent-1", "child-1"]

    parent_doc, child_doc = documents
    assert isinstance(parent_doc, Document)
    assert isinstance(child_doc, Document)
    assert "parent_task_id" not in parent_doc.metadata
    assert child_doc.metadata["parent_task_id"] == "parent-1"


def test_get_task_comments_uses_relative_endpoint() -> None:
    connector = ClickupConnector(api_token="test-token")
    response = _mock_response(
        {
            "comments": [
                {
                    "id": "comment-1",
                    "comment_text": "Looks good",
                }
            ]
        }
    )

    with patch("onyx.connectors.clickup.connector.requests.get") as mock_get:
        mock_get.return_value = response

        sections = connector._get_task_comments("task-1")

    mock_get.assert_called_once()
    assert mock_get.call_args.args[0] == f"{CLICKUP_API_BASE_URL}/task/task-1/comment"
    assert sections[0].text == "Looks good"
