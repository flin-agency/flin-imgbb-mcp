"""Tests for flin-imgbb-mcp server."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from flin_imgbb_mcp.server import list_images, upload_all_images, upload_image


class TestListImages:
    def test_returns_message_when_empty(self, tmp_path):
        result = list_images(str(tmp_path))
        assert "No images found" in result

    def test_finds_image_files(self, tmp_path):
        (tmp_path / "photo.jpg").touch()
        (tmp_path / "diagram.png").touch()
        (tmp_path / "notes.txt").touch()

        result = list_images(str(tmp_path))

        assert "2 image(s)" in result
        assert "photo.jpg" in result
        assert "diagram.png" in result
        assert "notes.txt" not in result

    def test_all_supported_extensions(self, tmp_path):
        for name in ["a.png", "b.jpg", "c.jpeg", "d.gif", "e.webp", "f.bmp"]:
            (tmp_path / name).touch()

        result = list_images(str(tmp_path))
        assert "6 image(s)" in result

    def test_case_insensitive_extensions(self, tmp_path):
        (tmp_path / "PHOTO.JPG").touch()
        (tmp_path / "image.PNG").touch()

        result = list_images(str(tmp_path))
        assert "2 image(s)" in result

    def test_raises_for_missing_folder(self):
        with pytest.raises(FileNotFoundError):
            list_images("/nonexistent/folder/path")

    def test_raises_if_path_is_file(self, tmp_path):
        f = tmp_path / "file.txt"
        f.touch()
        with pytest.raises(ValueError):
            list_images(str(f))


class TestUploadImage:
    async def test_raises_file_not_found(self, monkeypatch):
        monkeypatch.setenv("IMGBB_API_KEY", "test-key")
        with pytest.raises(FileNotFoundError):
            await upload_image("/nonexistent/image.jpg")

    async def test_raises_when_api_key_missing(self, tmp_path, monkeypatch):
        img = tmp_path / "test.jpg"
        img.write_bytes(b"fake")
        monkeypatch.delenv("IMGBB_API_KEY", raising=False)

        with pytest.raises(ValueError, match="IMGBB_API_KEY"):
            await upload_image(str(img))

    async def test_successful_upload(self, tmp_path, monkeypatch):
        img = tmp_path / "test.jpg"
        img.write_bytes(b"fake-image-data")
        monkeypatch.setenv("IMGBB_API_KEY", "test-key")

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "url": "https://i.ibb.co/abc/test.jpg",
                "display_url": "https://i.ibb.co/abc/test.jpg",
                "delete_url": "https://ibb.co/abc/test",
                "title": "test",
            },
        }

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("flin_imgbb_mcp.server.httpx.AsyncClient", return_value=mock_client):
            result = await upload_image(str(img))

        assert "https://i.ibb.co/abc/test.jpg" in result

    async def test_raises_if_path_is_directory(self, tmp_path, monkeypatch):
        monkeypatch.setenv("IMGBB_API_KEY", "test-key")
        with pytest.raises(ValueError):
            await upload_image(str(tmp_path))


class TestUploadAllImages:
    async def test_returns_message_when_empty(self, tmp_path, monkeypatch):
        monkeypatch.setenv("IMGBB_API_KEY", "test-key")
        result = await upload_all_images(str(tmp_path))
        assert "No images found" in result

    async def test_raises_for_missing_folder(self, monkeypatch):
        monkeypatch.setenv("IMGBB_API_KEY", "test-key")
        with pytest.raises(FileNotFoundError):
            await upload_all_images("/nonexistent/folder")

    async def test_reports_results(self, tmp_path, monkeypatch):
        (tmp_path / "a.jpg").write_bytes(b"fake")
        (tmp_path / "b.png").write_bytes(b"fake")
        monkeypatch.setenv("IMGBB_API_KEY", "test-key")

        call_count = 0

        async def mock_upload(file_path, name=None, expiration=None):
            nonlocal call_count
            call_count += 1
            return {
                "url": f"https://i.ibb.co/{file_path.name}",
                "display_url": f"https://i.ibb.co/{file_path.name}",
                "delete_url": f"https://ibb.co/{file_path.stem}",
                "title": file_path.stem,
            }

        with patch("flin_imgbb_mcp.server._upload_to_imgbb", side_effect=mock_upload):
            result = await upload_all_images(str(tmp_path))

        assert "2 files" in result
        assert call_count == 2
        assert "OK" in result
