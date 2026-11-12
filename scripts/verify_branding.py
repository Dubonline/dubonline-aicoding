"""验证品牌信息与仓库选择，不调用模型，不写入个人运行数据。"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    from agent import env_utils

    with TemporaryDirectory(prefix="dubonline-branding-") as directory:
        env_utils.LOCAL_ENV = Path(directory) / ".env"
        with patch.dict(os.environ, {
            "DUBONLINE_AICODING_DATA_DIR": directory,
            "DUBONLINE_AICODING_LOG_DIR": directory,
            "AI_WORKSPACE_ROOT": directory,
            "CHECKPOINT_DB_PATH": str(Path(directory) / "checkpoints.sqlite"),
            "STORE_DB_PATH": str(Path(directory) / "store.sqlite"),
            "DUBONLINE_AICODING_DEFAULT_REPO": "",
        }):
            from fastapi import BackgroundTasks, HTTPException
            from fastapi.testclient import TestClient

            from agent.api import dashboard_routes as routes
            from agent.app import app

            client = TestClient(app)
            assert app.title == "dubonline AI Coding API"
            assert client.get("/dashboard/api/me").json()["login"] == "dubonline"
            assert client.get("/dashboard/api/profile").json()["default_repo"] is None
            assert client.get("/dashboard/api/repos").json()["repositories"] == []
            with patch.object(routes, "initialize_task_record") as initialize:
                response = client.post("/dashboard/api/threads", json={"prompt": "分析项目"})
                assert response.status_code == 400, response.text
                initialize.assert_not_called()
            os.environ["DUBONLINE_AICODING_DEFAULT_REPO"] = "https://gitee.com/example-owner/sample"
            assert client.get("/dashboard/api/profile").json()["default_repo"].endswith("/sample")
            assert len(client.get("/dashboard/api/repos").json()["repositories"]) == 1
            for body in [
                routes.DashboardThreadCreateRequest(prompt="分析", repo="https://github.com/example/sample"),
                routes.DashboardThreadCreateRequest(prompt="分析", repo_explicitly_none=True),
            ]:
                with patch.object(routes, "initialize_task_record") as initialize:
                    try:
                        asyncio.run(routes.dashboard_create_thread(body, BackgroundTasks()))
                    except HTTPException as exc:
                        assert exc.status_code == 400
                    else:
                        raise AssertionError("invalid or missing repository accepted")
                    initialize.assert_not_called()
            for repo in [None, "https://gitee.com/example-owner/explicit"]:
                background = BackgroundTasks()
                record = {"thread_id": "branding-test"}
                with patch.object(routes, "initialize_task_record", return_value="branding-test") as initialize, \
                     patch.object(routes, "get_task", return_value=record), \
                     patch.object(routes, "_thread_payload", return_value=record):
                    asyncio.run(routes.dashboard_create_thread(
                        routes.DashboardThreadCreateRequest(prompt="分析", repo=repo), background,
                    ))
                    assert initialize.call_args.kwargs["repo_url"] == (repo or os.environ["DUBONLINE_AICODING_DEFAULT_REPO"])
                    assert len(background.tasks) == 1
    print("branding and repository selection verification passed")


if __name__ == "__main__":
    main()
