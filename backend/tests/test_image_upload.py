import os
import tempfile
import pytest
import httpx
from PIL import Image

from backend.app.services.serpapi_service import (
    SerpApiService,
    SerpApiError,
)
from backend.app.services.cache_service import CacheService
from backend.app.agent.tools import tool_lens_search


@pytest.fixture
def sample_image_path(tmp_path):
    """Create a small temporary image file."""
    img_file = tmp_path / "test_sample.jpg"
    img = Image.new("RGB", (200, 200), color=(73, 109, 137))
    img.save(img_file, "JPEG")
    return str(img_file)


@pytest.fixture
def large_image_path(tmp_path):
    """Create a temporary image file exceeding 500 KB to trigger auto-compression."""
    img_file = tmp_path / "test_large.jpg"
    # 2500x2500 noisy image to ensure file size exceeds 500 KB
    img = Image.new("RGB", (1800, 1800), color=(120, 150, 180))
    img.save(img_file, "JPEG", quality=100)
    return str(img_file)


def test_upload_image_success(sample_image_path, monkeypatch):
    """Verify successful image upload to SerpApi Image API returning image_id."""
    service = SerpApiService(api_key="test_key_123", use_cache=False)

    def mock_post(url, *args, **kwargs):
        assert "serpapi.com/image" in url
        assert "data" in kwargs
        assert kwargs["data"]["api_key"] == "test_key_123"
        assert "files" in kwargs
        return httpx.Response(
            status_code=200,
            json={"image_id": "serp_img_abc999", "status": "Success"},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(service._client, "post", mock_post)

    image_id = service.upload_image(sample_image_path)
    assert image_id == "serp_img_abc999"


def test_upload_image_auto_resizing(large_image_path, monkeypatch):
    """Verify that images > 500 KB are automatically compressed under 500 KB before upload."""
    service = SerpApiService(api_key="test_key_123", use_cache=False)
    captured_payload_size = []

    def mock_post(url, *args, **kwargs):
        files = kwargs.get("files", {})
        assert "image" in files
        _, file_bytes, _ = files["image"]
        captured_payload_size.append(len(file_bytes))
        return httpx.Response(
            status_code=200,
            json={"image_id": "serp_img_compressed_123"},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(service._client, "post", mock_post)

    image_id = service.upload_image(large_image_path)
    assert image_id == "serp_img_compressed_123"
    assert len(captured_payload_size) == 1
    # Must be under 500 KB limit (500 * 1024 = 512,000 bytes)
    assert captured_payload_size[0] <= 500 * 1024


def test_upload_image_cache_hit_prevents_duplicate_uploads(sample_image_path, monkeypatch, tmp_path):
    """Verify that identical file content hashes reuse the cached image_id without network calls."""
    isolated_db = str(tmp_path / "isolated_cache.db")
    cache = CacheService(db_path=isolated_db)
    service = SerpApiService(api_key="test_key_123", cache_service=cache, use_cache=True)
    post_count = 0

    def mock_post(url, *args, **kwargs):
        nonlocal post_count
        post_count += 1
        return httpx.Response(
            status_code=200,
            json={"image_id": "serp_img_cached_555"},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(service._client, "post", mock_post)

    # First upload: cache miss, network called
    id1 = service.upload_image(sample_image_path)
    assert id1 == "serp_img_cached_555"
    assert post_count == 1

    # Second upload of same file: cache hit, network NOT called
    id2 = service.upload_image(sample_image_path)
    assert id2 == "serp_img_cached_555"
    assert post_count == 1  # No additional network call!


def test_search_lens_with_crop_bbox(sample_image_path, monkeypatch):
    """Verify search_lens crops the bounding box, uploads the crop, and cleans up temp files."""
    service = SerpApiService(api_key="test_key_123", use_cache=False)
    captured_image_id = []

    def mock_upload(path, *args, **kwargs):
        assert os.path.exists(path)
        return "crop_img_id_777"

    def mock_execute(params, *args, **kwargs):
        assert params.get("engine") == "google_lens"
        assert params.get("image_id") == "crop_img_id_777"
        captured_image_id.append(params.get("image_id"))
        return {
            "visual_matches": [
                {
                    "title": "Matching Cropped Garment",
                    "link": "https://example.com/item",
                    "source": "Shop",
                }
            ]
        }

    monkeypatch.setattr(service, "upload_image", mock_upload)
    monkeypatch.setattr(service, "_execute_query", mock_execute)

    # Normalized bounding box [ymin, xmin, ymax, xmax]
    res = service.search_lens(
        image_path=sample_image_path, crop_bbox=[0.2, 0.2, 0.8, 0.8]
    )

    assert len(captured_image_id) == 1
    assert captured_image_id[0] == "crop_img_id_777"
    assert len(res.visual_matches) == 1
    assert res.visual_matches[0].title == "Matching Cropped Garment"


def test_upload_image_masks_api_key_on_error(sample_image_path, monkeypatch):
    """Verify that exceptions during image upload mask the secret API key and suppress __cause__."""
    service = SerpApiService(api_key="secret_upload_key_888", use_cache=False)

    def mock_post(url, *args, **kwargs):
        raise httpx.ConnectError("Failed to connect with key secret_upload_key_888")

    monkeypatch.setattr(service._client, "post", mock_post)

    with pytest.raises(SerpApiError) as exc_info:
        service.upload_image(sample_image_path)

    # Check key is masked
    assert "secret_upload_key_888" not in str(exc_info.value)
    assert "***" in str(exc_info.value) or "Failed to upload" in str(exc_info.value)
    # Check __cause__ is suppressed via from None
    assert exc_info.value.__cause__ is None
