# flin-imgbb-mcp

MCP server for uploading images to [ImgBB](https://imgbb.com) from Claude-compatible clients.

## Quick Start

The recommended setup uses `uvx` — no repository clone or virtual environment required.

Add this to your Claude MCP configuration:

```json
{
  "mcpServers": {
    "imgbb": {
      "command": "uvx",
      "args": ["flin-imgbb-mcp@latest"],
      "env": {
        "IMGBB_API_KEY": "your-imgbb-api-key"
      }
    }
  }
}
```

Get your API key at [api.imgbb.com](https://api.imgbb.com/).

## Tools

### `upload_image`

Upload a single image file to ImgBB and get its public URL.

| Parameter    | Type   | Required | Description                                      |
|-------------|--------|----------|--------------------------------------------------|
| `file_path` | string | yes      | Absolute or relative path to the image file      |
| `name`      | string | no       | Optional name for the image on ImgBB             |
| `expiration`| number | no       | Expiration in seconds (60–15552000)              |

Returns: `url`, `display_url`, `delete_url`, `title`

### `list_images`

List all image files in a local folder (png, jpg, jpeg, gif, webp, bmp).

| Parameter     | Type   | Required | Description                  |
|--------------|--------|----------|------------------------------|
| `folder_path` | string | yes      | Absolute path to the folder  |

### `upload_all_images`

Upload all images from a local folder to ImgBB.

| Parameter     | Type   | Required | Description                                     |
|--------------|--------|----------|-------------------------------------------------|
| `folder_path` | string | yes      | Absolute path to the folder                     |
| `expiration`  | number | no       | Expiration in seconds (60–15552000) for all images |

## Configuration

| Environment Variable | Required | Description                  |
|---------------------|----------|------------------------------|
| `IMGBB_API_KEY`     | yes      | Your ImgBB API key           |

## Troubleshooting

**Server does not start / "IMGBB_API_KEY is not set"**
Make sure `IMGBB_API_KEY` is set in the `env` block of your MCP configuration. The server checks for it at startup and will exit with a clear error if it is missing.

**Upload fails with HTTP 400**
The file path must point to a valid image file. Supported formats: png, jpg, jpeg, gif, webp, bmp.

**`uvx` command not found**
Install `uv` from [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/).

## Development

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --group dev

# Run tests
uv run pytest tests/ -v

# Lint
uv run ruff check src/ tests/

# Build distribution artifacts
uv build
```

## Release

Releases are published to PyPI automatically when a version tag is pushed:

```bash
git tag v1.0.2
git push origin v1.0.2
```

The GitHub Actions release workflow builds the package and publishes it via PyPI Trusted Publishing.

## License

MIT
