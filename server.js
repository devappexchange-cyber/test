import express from "express";
import fetch from "node-fetch";

const app = express();
app.use(express.json());

// 🔥 Replace ONLY this with your MCP ID (not full URL)
const MCP_BASE_URL = "https://backend.composio.dev/v3/mcp/YOUR_MCP_ID";

// 🔐 API key from Render env
const API_KEY = process.env.COMPOSIO_API_KEY;

// ✅ Health check
app.get("/", (req, res) => {
  res.send("✅ Composio MCP Proxy is running");
});

// ✅ MCP Proxy Endpoint
app.post("/mcp", async (req, res) => {
  try {
    console.log("➡️ Incoming:", req.body);

    const response = await fetch(MCP_BASE_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
      },
      body: JSON.stringify(req.body)
    });

    const data = await response.json();

    console.log("⬅️ Response:", data);

    res.json(data);

  } catch (error) {
    console.error("❌ Error:", error);
    res.status(500).json({ error: error.message });
  }
});

// ✅ Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
