# flin-imgbb-mcp

MCP-Server zum Hochladen von Bildern aus einem lokalen Ordner zu [imgbb](https://imgbb.com).

## Installation

```bash
npm install
npm run build
```

## Konfiguration

API-Schlüssel als Umgebungsvariable setzen:

```bash
export IMGBB_API_KEY=your_api_key_here
```

Den API-Schlüssel bekommst du unter: https://api.imgbb.com/

## MCP-Konfiguration (Claude Desktop / Claude Code)

In `claude_desktop_config.json` oder `settings.json` eintragen:

```json
{
  "mcpServers": {
    "flin-imgbb-mcp": {
      "command": "node",
      "args": ["/absoluter/pfad/zu/flin-imgbb-mcp/dist/index.js"],
      "env": {
        "IMGBB_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Tools

### `upload_image`
Lädt eine einzelne Bilddatei hoch und gibt die URL zurück.

| Parameter    | Typ    | Pflicht | Beschreibung                              |
|-------------|--------|---------|-------------------------------------------|
| `file_path` | string | ✓       | Pfad zur Bilddatei                        |
| `name`      | string |         | Optionaler Name bei imgbb                 |
| `expiration`| number |         | Ablaufzeit in Sekunden (60–15552000)      |

**Rückgabe:**
```json
{
  "url": "https://i.ibb.co/...",
  "display_url": "https://i.ibb.co/...",
  "delete_url": "https://ibb.co/.../...",
  "title": "bildname"
}
```

### `list_images`
Listet alle Bilder in einem Ordner auf (png, jpg, jpeg, gif, webp, bmp).

| Parameter     | Typ    | Pflicht | Beschreibung         |
|--------------|--------|---------|----------------------|
| `folder_path` | string | ✓       | Pfad zum Bildordner  |

### `upload_all_images`
Lädt alle Bilder aus einem Ordner hoch und gibt alle URLs zurück.

| Parameter     | Typ    | Pflicht | Beschreibung                         |
|--------------|--------|---------|--------------------------------------|
| `folder_path` | string | ✓       | Pfad zum Bildordner                  |
| `expiration`  | number |         | Ablaufzeit in Sekunden für alle Bilder |

## Entwicklung

```bash
npm run dev   # TypeScript direkt ausführen (ohne Build)
npm run build # Kompilieren nach dist/
npm start     # Kompilierten Server starten
```
