"""文件上传 API 端点测试"""
import pytest
from fastapi import status
from httpx import AsyncClient
from pathlib import Path
import json
from io import BytesIO

from backend.models.user import User


class TestUploadAPI:
    """文件上传 API 测试类"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_upload_whatsapp_file(self, async_client: AsyncClient, auth_headers: dict, tmp_path: Path):
        """测试上传 WhatsApp 聊天文件"""
        # 创建测试文件
        chat_content = """[2025-07-01 10:00:00] Alice: Hello!
[2025-07-01 10:01:00] Bob: Hi there!
[2025-07-01 10:02:00] Alice: How's your day going?
[2025-07-01 10:03:00] Bob: Pretty good, thanks!"""
        
        test_file = tmp_path / "whatsapp_chat.txt"
        test_file.write_text(chat_content)
        
        # 上传文件
        with open(test_file, "rb") as f:
            files = {"file": ("whatsapp_chat.txt", f, "text/plain")}
            data = {"source_type": "whatsapp", "persona_name": "Test WhatsApp"}
            
            response = await async_client.post(
                "/api/upload",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        assert response.status_code == status.HTTP_201_CREATED
        result = response.json()
        assert result["persona"]["name"] == "Test WhatsApp"
        assert result["message_count"] == 4
        assert "persona_id" in result
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_upload_json_file(self, async_client: AsyncClient, auth_headers: dict, tmp_path: Path):
        """测试上传 JSON 聊天文件"""
        # 创建测试 JSON 文件
        chat_data = {
            "messages": [
                {
                    "sender": "Alice",
                    "content": "Hello from JSON!",
                    "timestamp": "2025-07-01T10:00:00Z"
                },
                {
                    "sender": "Bob",
                    "content": "Hi Alice!",
                    "timestamp": "2025-07-01T10:01:00Z"
                }
            ]
        }
        
        test_file = tmp_path / "chat.json"
        test_file.write_text(json.dumps(chat_data))
        
        # 上传文件
        with open(test_file, "rb") as f:
            files = {"file": ("chat.json", f, "application/json")}
            data = {"source_type": "json", "persona_name": "JSON Chat"}
            
            response = await async_client.post(
                "/api/upload",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        assert response.status_code == status.HTTP_201_CREATED
        result = response.json()
        assert result["persona"]["name"] == "JSON Chat"
        assert result["message_count"] == 2
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_upload_csv_file(self, async_client: AsyncClient, auth_headers: dict, tmp_path: Path):
        """测试上传 CSV 聊天文件"""
        # 创建测试 CSV 文件
        csv_content = """timestamp,sender,content
2025-07-01 10:00:00,Alice,Hello from CSV!
2025-07-01 10:01:00,Bob,Hi Alice!
2025-07-01 10:02:00,Alice,How are you?"""
        
        test_file = tmp_path / "chat.csv"
        test_file.write_text(csv_content)
        
        # 上传文件
        with open(test_file, "rb") as f:
            files = {"file": ("chat.csv", f, "text/csv")}
            data = {"source_type": "csv", "persona_name": "CSV Chat"}
            
            response = await async_client.post(
                "/api/upload",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        assert response.status_code == status.HTTP_201_CREATED
        result = response.json()
        assert result["persona"]["name"] == "CSV Chat"
        assert result["message_count"] == 3
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_upload_empty_file(self, async_client: AsyncClient, auth_headers: dict):
        """测试上传空文件"""
        # 创建空文件
        empty_file = BytesIO(b"")
        
        files = {"file": ("empty.txt", empty_file, "text/plain")}
        data = {"source_type": "whatsapp", "persona_name": "Empty"}
        
        response = await async_client.post(
            "/api/upload",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "empty" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_upload_invalid_format(self, async_client: AsyncClient, auth_headers: dict, tmp_path: Path):
        """测试上传无效格式的文件"""
        # 创建无法解析的文件
        test_file = tmp_path / "invalid.txt"
        test_file.write_text("This is not a valid chat format")
        
        with open(test_file, "rb") as f:
            files = {"file": ("invalid.txt", f, "text/plain")}
            data = {"source_type": "whatsapp", "persona_name": "Invalid"}
            
            response = await async_client.post(
                "/api/upload",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_upload_too_large_file(self, async_client: AsyncClient, auth_headers: dict):
        """测试上传过大的文件"""
        # 创建一个模拟的大文件（不实际创建大文件）
        large_content = "x" * (10 * 1024 * 1024 + 1)  # 10MB + 1 byte
        large_file = BytesIO(large_content.encode())
        
        files = {"file": ("large.txt", large_file, "text/plain")}
        data = {"source_type": "whatsapp", "persona_name": "Large"}
        
        response = await async_client.post(
            "/api/upload",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        # 文件大小限制应该在 API 层处理
        assert response.status_code in [status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, status.HTTP_400_BAD_REQUEST]
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_upload_without_auth(self, async_client: AsyncClient, tmp_path: Path):
        """测试未授权上传文件"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        with open(test_file, "rb") as f:
            files = {"file": ("test.txt", f, "text/plain")}
            data = {"source_type": "whatsapp", "persona_name": "Test"}
            
            response = await async_client.post(
                "/api/upload",
                files=files,
                data=data
            )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_upload_missing_required_fields(self, async_client: AsyncClient, auth_headers: dict, tmp_path: Path):
        """测试缺少必需字段的上传"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        # 缺少 source_type
        with open(test_file, "rb") as f:
            files = {"file": ("test.txt", f, "text/plain")}
            data = {"persona_name": "Test"}
            
            response = await async_client.post(
                "/api/upload",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_upload_duplicate_persona_name(self, async_client: AsyncClient, auth_headers: dict, tmp_path: Path, test_persona):
        """测试使用重复的人格名称上传"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("[2025-07-01 10:00:00] User: Test message")
        
        with open(test_file, "rb") as f:
            files = {"file": ("test.txt", f, "text/plain")}
            data = {"source_type": "whatsapp", "persona_name": test_persona.name}
            
            response = await async_client.post(
                "/api/upload",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        # 应该允许更新现有人格或创建新版本
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_upload_with_metadata(self, async_client: AsyncClient, auth_headers: dict, tmp_path: Path):
        """测试带元数据的上传"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("[2025-07-01 10:00:00] User: Test with metadata")
        
        metadata = {
            "platform": "whatsapp",
            "export_date": "2025-07-01",
            "chat_name": "Family Group"
        }
        
        with open(test_file, "rb") as f:
            files = {"file": ("test.txt", f, "text/plain")}
            data = {
                "source_type": "whatsapp",
                "persona_name": "Test Metadata",
                "metadata": json.dumps(metadata)
            }
            
            response = await async_client.post(
                "/api/upload",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        assert response.status_code == status.HTTP_201_CREATED
        result = response.json()
        assert result["persona"]["metadata"]["platform"] == "whatsapp"