/**
 * MCP Server para ReservaT — Compatible con SSE + Streamable HTTP
 *
 * Expone herramientas (listar_servicios, buscar_servicios) via MCP.
 * Soporta dos transportes:
 *   1. Streamable HTTP (2025-11-25) → /mcp   (POST/GET/DELETE)
 *   2. HTTP + SSE (2024-11-05)      → /sse   (GET) + /messages (POST)
 */

import { randomUUID } from "node:crypto";
import express from "express";
import cors from "cors";
import helmet from "helmet";
import rateLimit from "express-rate-limit";
import pg from "pg";
import { z } from "zod";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

// ─── Config ─────────────────────────────────────────────────────
const PORT = Number(process.env.PORT ?? 8020);
const MCP_API_KEY = process.env.MCP_API_KEY;
const NODE_ENV = process.env.NODE_ENV ?? "development";

const CORS_ORIGINS = [
  "https://server-n8n.reservatonline.com",
  "https://reservatonline.com",
  "https://www.reservatonline.com",
  ...(NODE_ENV === "development"
    ? ["http://localhost:3000", "http://localhost:8020"]
    : []),
];

// ─── Database (sin fallbacks inseguros en producción) ───────────
if (
  NODE_ENV === "production" &&
  (!process.env.DB_USER || !process.env.DB_PASSWORD)
) {
  console.error("FATAL: DB_USER and DB_PASSWORD must be set in production");
  process.exit(1);
}

const pool = new pg.Pool({
  user: process.env.DB_USER ?? "postgres",
  password: process.env.DB_PASSWORD ?? "postgres",
  host: process.env.DB_HOST ?? "db",
  port: Number(process.env.DB_PORT ?? 5432),
  database: process.env.DB_NAME ?? "reservat",
  max: 20,
  connectionTimeoutMillis: 5_000,
  idleTimeoutMillis: 30_000,
});

pool.on("error", (err: Error) => console.error("[DB] Pool error:", err));

// ─── MCP Server factory ────────────────────────────────────────
function createServer() {
  const server = new McpServer(
    { name: "reservat-mcp", version: "1.0.0" },
    { capabilities: { logging: {} } },
  );

  // Tool: listar_servicios
  server.registerTool(
    "listar_servicios",
    {
      description: "Listar servicios activos de la base de datos (paginado).",
      inputSchema: {
        limite: z
          .number()
          .int()
          .positive()
          .max(100)
          .default(50)
          .describe("Máximo de resultados (max 100)"),
        pagina: z
          .number()
          .int()
          .min(0)
          .max(1000)
          .default(0)
          .describe("Número de página (0-indexed)"),
      },
    },
    async ({ limite, pagina }): Promise<CallToolResult> => {
      const offset = pagina * limite;
      const { rows } = await pool.query(
        `SELECT id_servicio, proveedor_id, nombre, descripcion, precio, moneda
         FROM usr_app.servicios
         WHERE activo = true
         LIMIT $1 OFFSET $2`,
        [limite, offset],
      );
      return {
        content: [{ type: "text", text: JSON.stringify(rows, null, 2) }],
      };
    },
  );

  // Tool: buscar_servicios
  server.registerTool(
    "buscar_servicios",
    {
      description:
        "Buscar servicios por nombre o descripción (parcial, case-insensitive).",
      inputSchema: {
        query: z
          .string()
          .min(1)
          .max(200)
          .describe("Texto a buscar en el nombre o descripción"),
        limite: z
          .number()
          .int()
          .positive()
          .max(100)
          .default(10)
          .describe("Máximo de resultados (max 100)"),
      },
    },
    async ({ query, limite }): Promise<CallToolResult> => {
      const { rows } = await pool.query(
        `SELECT id_servicio, proveedor_id, nombre, descripcion, precio, moneda
         FROM usr_app.servicios
         WHERE activo = true AND (nombre ILIKE $1 OR descripcion ILIKE $1)
         LIMIT $2`,
        [`%${query}%`, limite],
      );
      return {
        content: [{ type: "text", text: JSON.stringify(rows, null, 2) }],
      };
    },
  );

  return server;
}

// ─── Express App ────────────────────────────────────────────────
const app = express();

// Security headers
app.use(helmet());

// Body size limit (previene DoS via payload gigante)
app.use(express.json({ limit: "1mb" }));

// CORS restringido
app.use(
  cors({
    origin: CORS_ORIGINS,
    exposedHeaders: ["Mcp-Session-Id", "Last-Event-Id", "Mcp-Protocol-Version"],
  }),
);

// Rate limiting
app.use(
  rateLimit({
    windowMs: 60_000,
    max: 100,
    standardHeaders: true,
    legacyHeaders: false,
    message: { error: "Too many requests, try again later" },
  }),
);

// ─── API Key Auth Middleware ────────────────────────────────────
function apiKeyAuth(
  req: express.Request,
  res: express.Response,
  next: express.NextFunction,
) {
  // Skip auth in development if no key is set
  if (!MCP_API_KEY) {
    if (NODE_ENV === "production") {
      console.error("FATAL: MCP_API_KEY must be set in production");
      res.status(500).json({ error: "Server misconfigured" });
      return;
    }
    next();
    return;
  }

  const key = req.headers["x-api-key"] ?? req.query.apiKey;

  if (key !== MCP_API_KEY) {
    res.status(401).json({ error: "Unauthorized: invalid or missing API key" });
    return;
  }
  next();
}

// Session store (shared between both transports)
const transports: Record<
  string,
  StreamableHTTPServerTransport | SSEServerTransport
> = {};

// ─── Session cleanup (TTL 30 min) ──────────────────────────────
const SESSION_TTL_MS = 30 * 60 * 1000;
const sessionLastActivity = new Map<string, number>();

function touchSession(sid: string) {
  sessionLastActivity.set(sid, Date.now());
}

function removeSession(sid: string) {
  delete transports[sid];
  sessionLastActivity.delete(sid);
}

setInterval(() => {
  const now = Date.now();
  for (const [sid, lastActivity] of sessionLastActivity.entries()) {
    if (now - lastActivity > SESSION_TTL_MS) {
      console.log(`[SESSION] Expired: ${sid}`);
      const transport = transports[sid];
      if (transport) {
        transport.close().catch(() => {});
      }
      removeSession(sid);
    }
  }
}, 60_000);

// ═══════════════════════════════════════════════════════════════
// STREAMABLE HTTP TRANSPORT (protocol version 2025-11-25)
// ═══════════════════════════════════════════════════════════════

app.all(
  "/mcp",
  apiKeyAuth,
  async (req: express.Request, res: express.Response) => {
    try {
      const sessionId = req.headers["mcp-session-id"] as string | undefined;
      let transport: StreamableHTTPServerTransport;

      if (sessionId && transports[sessionId]) {
        const existing = transports[sessionId];
        if (existing instanceof StreamableHTTPServerTransport) {
          transport = existing;
          touchSession(sessionId);
        } else {
          res.status(400).json({
            jsonrpc: "2.0",
            error: {
              code: -32000,
              message: "Session uses a different transport",
            },
            id: null,
          });
          return;
        }
      } else if (
        !sessionId &&
        req.method === "POST" &&
        isInitializeRequest(req.body)
      ) {
        transport = new StreamableHTTPServerTransport({
          sessionIdGenerator: () => randomUUID(),
          onsessioninitialized: (sid: string) => {
            console.log(`[SESSION] Streamable HTTP: ${sid}`);
            transports[sid] = transport;
            touchSession(sid);
          },
        });

        transport.onclose = () => {
          const sid = transport.sessionId;
          if (sid) {
            console.log(`[SESSION] Closed: ${sid}`);
            removeSession(sid);
          }
        };

        const server = createServer();
        await server.connect(transport);
      } else {
        res.status(400).json({
          jsonrpc: "2.0",
          error: { code: -32000, message: "Bad Request: No valid session ID" },
          id: null,
        });
        return;
      }

      await transport.handleRequest(req, res, req.body);
    } catch (error) {
      console.error("[ERROR] /mcp:", error);
      if (!res.headersSent) {
        res.status(500).json({
          jsonrpc: "2.0",
          error: { code: -32603, message: "Internal server error" },
          id: null,
        });
      }
    }
  },
);

// ═══════════════════════════════════════════════════════════════
// DEPRECATED HTTP+SSE TRANSPORT (protocol version 2024-11-05)
// ═══════════════════════════════════════════════════════════════

app.get(
  "/sse",
  apiKeyAuth,
  async (_req: express.Request, res: express.Response) => {
    const transport = new SSEServerTransport("/messages", res);
    const sid = transport.sessionId;
    console.log(`[SESSION] SSE: ${sid}`);
    transports[sid] = transport;
    touchSession(sid);

    res.on("close", () => {
      console.log(`[SESSION] SSE closed: ${sid}`);
      removeSession(sid);
    });

    const server = createServer();
    await server.connect(transport);
  },
);

app.post("/messages", async (req: express.Request, res: express.Response) => {
  const sessionId = req.query.sessionId as string;
  const existing = transports[sessionId];

  if (existing instanceof SSEServerTransport) {
    touchSession(sessionId);
    await existing.handlePostMessage(req, res, req.body);
  } else {
    res.status(400).send("No transport found for sessionId");
  }
});

// ─── Health check (sin auth) ───────────────────────────────────
app.get("/healthchecker", (_req, res) => {
  res.json({ message: "MCP service is LIVE!!" });
});

app.get("/readiness", async (_req, res) => {
  try {
    const result = await pool.query("SELECT 1");
    res.json({ status: result.rows.length ? "Ready" : "Not Ready" });
  } catch {
    res.json({ status: "Not Ready" });
  }
});

app.get("/metrics", (_req, res) => {
  res.json({
    activeSessions: Object.keys(transports).length,
    uptime: process.uptime(),
    memoryUsage: process.memoryUsage().rss,
  });
});

// ─── Start ──────────────────────────────────────────────────────
app.listen(PORT, "0.0.0.0", () => {
  console.log(`[MCP] Server listening on port ${PORT} (${NODE_ENV})`);
  console.log(`[MCP] Streamable HTTP: POST/GET/DELETE /mcp`);
  console.log(`[MCP] Legacy SSE:      GET /sse + POST /messages`);
  console.log(
    `[MCP] Auth:            ${MCP_API_KEY ? "API key enabled" : "DISABLED (dev mode)"}`,
  );
  console.log(`[MCP] CORS origins:    ${CORS_ORIGINS.join(", ")}`);
});

// Graceful shutdown
for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, async () => {
    console.log(`[MCP] ${signal} received, shutting down...`);
    for (const sid of Object.keys(transports)) {
      try {
        await transports[sid].close();
        removeSession(sid);
      } catch (e) {
        console.error(`[ERROR] Closing session ${sid}:`, e);
      }
    }
    await pool.end();
    process.exit(0);
  });
}
