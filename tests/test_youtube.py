from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.youtube_service import YouTubeService

client = TestClient(app)

# 비동기 테스트 환경을 위해 pytest-asyncio를 사용
@pytest.mark.asyncio
async def test_save_video_id():
    video_id = "test_video_123"

    # MongoDBHandler의 insert 메소드를 모킹하여 MongoDB에 접근하지 않도록 설정
    with patch("app.services.youtube_service.MongoDBHandler.insert", new_callable=AsyncMock) as mock_insert:
        mock_insert.return_value = True  # 성공적인 저장을 가정

        response = client.post("/youtube/video/save", json={"video_id": video_id})

        # 예상 결과
        assert response.status_code == 200
        assert response.json()["video_id"] == video_id
        assert response.json()["message"] == "video_id saved successfully"

        # MongoDBHandler.insert가 한번 호출되었는지 확인
        mock_insert.assert_called_once_with({"_id": video_id})


@pytest.mark.asyncio
async def test_delete_video_id():
    video_id = "test_video_123"

    # MongoDBHandler의 delete 메소드를 모킹하여 MongoDB에 접근하지 않도록 설정
    with patch("app.services.youtube_service.MongoDBHandler.delete", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = 1  # 성공적인 삭제를 가정

        response = client.delete(f"/youtube/video/delete/{video_id}")

        # 예상 결과
        assert response.status_code == 200
        assert response.json()["video_id"] == video_id
        assert response.json()["message"] == "video_id deleted successfully"

        # MongoDBHandler.delete가 한번 호출되었는지 확인
        mock_delete.assert_called_once_with({"_id": video_id})


@pytest.mark.asyncio
async def test_update_video_id():
    old_video_id = "test_video_123"
    new_video_id = "test_video_456"

    # MongoDBHandler의 delete 및 insert 메소드를 모킹하여 MongoDB에 접근하지 않도록 설정
    with patch("app.services.youtube_service.MongoDBHandler.delete", new_callable=AsyncMock) as mock_delete, \
         patch("app.services.youtube_service.MongoDBHandler.insert", new_callable=AsyncMock) as mock_insert:

        mock_delete.return_value = 1  # 성공적인 삭제를 가정
        mock_insert.return_value = True  # 성공적인 삽입을 가정

        response = client.put("/youtube/video/update", json={"old_video_id": old_video_id, "new_video_id": new_video_id})

        # 예상 결과
        assert response.status_code == 200
        assert response.json()["new_video_id"] == new_video_id
        assert response.json()["message"] == "video_id updated successfully"

        # MongoDBHandler.delete와 insert가 각각 한번 호출되었는지 확인
        mock_delete.assert_called_once_with({"_id": old_video_id})
        mock_insert.assert_called_once_with({"_id": new_video_id})
