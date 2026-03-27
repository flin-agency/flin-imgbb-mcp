"""MCP server for uploading images to ImgBB."""

import os
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}

mcp = FastMCP("flin-imgbb-mcp")


def _get_api_key() -> str:
    key = os.environ.get("IMGBB_API_KEY", "")
    if not key:
        raise ValueError(
            "IMGBB_API_KEY environment variable is not set. "
            "Get your API key at https://api.imgbb.com/"
        )
    return key


async def _upload_to_imgbb(
    file_path: Path,
    name: str | None = None,
    expiration: int | None = None,
) -> dict:
    api_key = _get_api_key()

    params: dict[str, str] = {"key": api_key}
    if expiration is not None:
        params["expiration"] = str(expiration)

    with file_path.open("rb") as f:
        files = {"image": (file_path.name, f, "application/octet-stream")}
        data: dict[str, str] = {}
        if name:
            data["name"] = name

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.imgbb.com/1/upload",
                params=params,
                files=files,
                data=data,
            )

    response.raise_for_status()
    json_data = response.json()

    if not json_data.get("success"):
        raise RuntimeError(f"ImgBB upload failed: {json_data}")

    return {
        "url": json_data["data"]["url"],
        "display_url": json_data["data"]["display_url"],
        "delete_url": json_data["data"]["delete_url"],
        "title": json_data["data"]["title"],
    }


@mcp.tool()
async def upload_image(
    file_path: str,
    name: str | None = None,
    expiration: int | None = None,
) -> str:
    """Upload a single image file to ImgBB and return its public URL.

    Args:
        file_path: Absolute or relative path to the image file.
        name: Optional name for the image on ImgBB.
        expiration: Optional expiration time in seconds (60-15552000).
            After this time the image is automatically deleted.
    """
    path = Path(file_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    result = await _upload_to_imgbb(path, name=name, expiration=expiration)
    return "\n".join(f"{k}: {v}" for k, v in result.items())


@mcp.tool()
def list_images(folder_path: str) -> str:
    """List all image files in a local folder (png, jpg, jpeg, gif, webp, bmp).

    Args:
        folder_path: Absolute path to the folder containing images.
    """
    folder = Path(folder_path).resolve()
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")
    if not folder.is_dir():
        raise ValueError(f"Path is not a directory: {folder}")

    images = sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )

    if not images:
        return f"No images found in {folder}"

    lines = [f"Found {len(images)} image(s):"] + [str(p) for p in images]
    return "\n".join(lines)


@mcp.tool()
async def upload_all_images(
    folder_path: str,
    expiration: int | None = None,
) -> str:
    """Upload all images from a local folder to ImgBB.

    Args:
        folder_path: Absolute path to the folder containing images.
        expiration: Optional expiration time in seconds (60-15552000) for all images.
    """
    folder = Path(folder_path).resolve()
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")
    if not folder.is_dir():
        raise ValueError(f"Path is not a directory: {folder}")

    images = sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )

    if not images:
        return f"No images found in {folder}"

    results = []
    for image_path in images:
        try:
            result = await _upload_to_imgbb(
                image_path,
                name=image_path.stem,
                expiration=expiration,
            )
            results.append(f"OK {image_path.name}: {result['url']}")
        except Exception as e:
            results.append(f"FAIL {image_path.name}: {e}")

    lines = [f"Upload results ({len(results)} files):", ""] + results
    return "\n".join(lines)


def main() -> None:
    """Entry point for the flin-imgbb-mcp server."""
    mcp.run()


if __name__ == "__main__":
    main()
