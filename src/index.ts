import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import fs from "fs";
import path from "path";
import FormData from "form-data";
import fetch from "node-fetch";

const IMGBB_API_KEY = process.env.IMGBB_API_KEY;

const server = new Server(
  { name: "flin-imgbb-mcp", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "upload_image",
      description:
        "Lädt ein Bild aus einem lokalen Dateipfad zu imgbb hoch und gibt die öffentliche URL zurück.",
      inputSchema: {
        type: "object",
        properties: {
          file_path: {
            type: "string",
            description:
              "Absoluter oder relativer Pfad zur Bilddatei (z.B. /tmp/images/foto.png)",
          },
          name: {
            type: "string",
            description: "Optionaler Name für das Bild bei imgbb",
          },
          expiration: {
            type: "number",
            description:
              "Optionale Ablaufzeit in Sekunden (60–15552000). Danach wird das Bild automatisch gelöscht.",
          },
        },
        required: ["file_path"],
      },
    },
    {
      name: "list_images",
      description:
        "Listet alle Bilddateien in einem lokalen Ordner auf (png, jpg, jpeg, gif, webp, bmp).",
      inputSchema: {
        type: "object",
        properties: {
          folder_path: {
            type: "string",
            description: "Absoluter Pfad zum Ordner mit den Bildern",
          },
        },
        required: ["folder_path"],
      },
    },
    {
      name: "upload_all_images",
      description:
        "Lädt alle Bilder aus einem lokalen Ordner zu imgbb hoch und gibt eine Liste aller URLs zurück.",
      inputSchema: {
        type: "object",
        properties: {
          folder_path: {
            type: "string",
            description: "Absoluter Pfad zum Ordner mit den Bildern",
          },
          expiration: {
            type: "number",
            description:
              "Optionale Ablaufzeit in Sekunden (60–15552000) für alle Bilder",
          },
        },
        required: ["folder_path"],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (!IMGBB_API_KEY) {
    return {
      content: [
        {
          type: "text",
          text: "Fehler: IMGBB_API_KEY Umgebungsvariable ist nicht gesetzt.",
        },
      ],
      isError: true,
    };
  }

  if (name === "upload_image") {
    const filePath = String(args?.file_path ?? "");
    const imageName = args?.name ? String(args.name) : undefined;
    const expiration = args?.expiration ? Number(args.expiration) : undefined;

    if (!filePath) {
      return {
        content: [{ type: "text", text: "Fehler: file_path ist erforderlich." }],
        isError: true,
      };
    }

    const resolvedPath = path.resolve(filePath);

    if (!fs.existsSync(resolvedPath)) {
      return {
        content: [
          {
            type: "text",
            text: `Fehler: Datei nicht gefunden: ${resolvedPath}`,
          },
        ],
        isError: true,
      };
    }

    try {
      const result = await uploadToImgbb(
        resolvedPath,
        imageName,
        expiration
      );
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (err) {
      return {
        content: [
          {
            type: "text",
            text: `Upload fehlgeschlagen: ${err instanceof Error ? err.message : String(err)}`,
          },
        ],
        isError: true,
      };
    }
  }

  if (name === "list_images") {
    const folderPath = String(args?.folder_path ?? "");
    const resolvedFolder = path.resolve(folderPath);

    if (!fs.existsSync(resolvedFolder)) {
      return {
        content: [
          {
            type: "text",
            text: `Fehler: Ordner nicht gefunden: ${resolvedFolder}`,
          },
        ],
        isError: true,
      };
    }

    const imageExtensions = new Set([
      ".png",
      ".jpg",
      ".jpeg",
      ".gif",
      ".webp",
      ".bmp",
    ]);
    const files = fs
      .readdirSync(resolvedFolder)
      .filter((f) =>
        imageExtensions.has(path.extname(f).toLowerCase())
      )
      .map((f) => path.join(resolvedFolder, f));

    return {
      content: [
        {
          type: "text",
          text:
            files.length > 0
              ? `Gefundene Bilder (${files.length}):\n${files.join("\n")}`
              : `Keine Bilder in ${resolvedFolder} gefunden.`,
        },
      ],
    };
  }

  if (name === "upload_all_images") {
    const folderPath = String(args?.folder_path ?? "");
    const expiration = args?.expiration ? Number(args.expiration) : undefined;
    const resolvedFolder = path.resolve(folderPath);

    if (!fs.existsSync(resolvedFolder)) {
      return {
        content: [
          {
            type: "text",
            text: `Fehler: Ordner nicht gefunden: ${resolvedFolder}`,
          },
        ],
        isError: true,
      };
    }

    const imageExtensions = new Set([
      ".png",
      ".jpg",
      ".jpeg",
      ".gif",
      ".webp",
      ".bmp",
    ]);
    const files = fs
      .readdirSync(resolvedFolder)
      .filter((f) =>
        imageExtensions.has(path.extname(f).toLowerCase())
      )
      .map((f) => path.join(resolvedFolder, f));

    if (files.length === 0) {
      return {
        content: [
          {
            type: "text",
            text: `Keine Bilder in ${resolvedFolder} gefunden.`,
          },
        ],
      };
    }

    const results: Array<{ file: string; url?: string; error?: string }> = [];

    for (const file of files) {
      try {
        const result = await uploadToImgbb(
          file,
          path.basename(file, path.extname(file)),
          expiration
        );
        results.push({ file: path.basename(file), url: result.url });
      } catch (err) {
        results.push({
          file: path.basename(file),
          error: err instanceof Error ? err.message : String(err),
        });
      }
    }

    const summary = results
      .map((r) =>
        r.url
          ? `✓ ${r.file}: ${r.url}`
          : `✗ ${r.file}: ${r.error}`
      )
      .join("\n");

    return {
      content: [
        {
          type: "text",
          text: `Upload-Ergebnisse (${results.length} Dateien):\n\n${summary}`,
        },
      ],
    };
  }

  return {
    content: [{ type: "text", text: `Unbekanntes Tool: ${name}` }],
    isError: true,
  };
});

async function uploadToImgbb(
  filePath: string,
  name?: string,
  expiration?: number
): Promise<{ url: string; display_url: string; delete_url: string; title: string }> {
  const form = new FormData();
  form.append("image", fs.createReadStream(filePath));
  if (name) form.append("name", name);

  let apiUrl = `https://api.imgbb.com/1/upload?key=${IMGBB_API_KEY}`;
  if (expiration) apiUrl += `&expiration=${expiration}`;

  const response = await fetch(apiUrl, {
    method: "POST",
    body: form,
    headers: form.getHeaders(),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`imgbb API Fehler ${response.status}: ${text}`);
  }

  const json = (await response.json()) as {
    success: boolean;
    status: number;
    data: {
      url: string;
      display_url: string;
      delete_url: string;
      title: string;
      url_viewer: string;
      id: string;
    };
  };

  if (!json.success) {
    throw new Error(`imgbb Upload fehlgeschlagen: ${JSON.stringify(json)}`);
  }

  return {
    url: json.data.url,
    display_url: json.data.display_url,
    delete_url: json.data.delete_url,
    title: json.data.title,
  };
}

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("flin-imgbb-mcp server läuft...");
}

main().catch((err) => {
  console.error("Fataler Fehler:", err);
  process.exit(1);
});
