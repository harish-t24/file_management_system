const express = require("express");
const cors = require("cors");
const path = require("path");
const axios = require("axios");
const crypto = require("crypto");

const app = express();
const PORT = process.env.PORT || 8080;

app.use(cors());
app.use(express.json());
app.use("/pages", express.static(path.join(__dirname, "pages")));

// ─── Utility: simple password hash (SHA-256) ────────────────────────────────
function hashPassword(password) {
  return crypto.createHash("sha256").update(password).digest("hex");
}

// ─── Home ────────────────────────────────────────────────────────────────────
app.get("/", (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <title>Home Page</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    </head>
    <body>
      <h1>Hello from Express</h1>
      <p>This HTML is rendered directly from the route.</p>
    </body>
    </html>
  `);
});

// ─── Serve static HTML pages ─────────────────────────────────────────────────
// FIX: Replaced browser fetch() with axios (reliable in Node.js)
app.get("/page/:name", async (req, res) => {
  const pageName = req.params.name;

  if (!/^[a-zA-Z0-9-_]+$/.test(pageName)) {
    return res.status(400).send("Invalid page name");
  }

  const filePath = path.join(__dirname, "pages", `${pageName}.html`);

  try {
    const { data } = await axios.get(
      `http://localhost:${PORT}/pages/${pageName}.html`
    );
    res.setHeader("Content-Type", "text/html");
    return res.send(data);
  } catch (error) {
    if (error.response && error.response.status === 404) {
      return res.status(404).send("HTML page not found");
    }
    return res.status(500).send("Error fetching HTML content");
  }
});

// ─── In-memory user store ────────────────────────────────────────────────────
const users = [];

// ─── Register ────────────────────────────────────────────────────────────────
// FIX: Added field validation, removed password from console.log, hash password
app.post("/api/auth/register", (req, res) => {
  const { name, email, password } = req.body;

  if (!name || !email || !password) {
    return res.status(400).send("Name, email, and password are required");
  }

  if (users.find((u) => u.email === email)) {
    return res.status(400).send("Email already registered");
  }

  users.push({
    id: crypto.randomUUID(),
    name,
    email,
    password: hashPassword(password), // FIX: never store plain-text passwords
  });

  console.log(`New user registered: ${name} <${email}>`); // FIX: no password log
  res.status(201).send("User registered successfully");
});

// ─── Login ───────────────────────────────────────────────────────────────────
// FIX: Compare hashed passwords
app.post("/api/auth/login", (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).send("Email and password are required");
    }

    const user = users.find(
      (u) => u.email === email && u.password === hashPassword(password)
    );

    if (!user) {
      return res.status(401).send("Invalid email or password");
    }

    res.status(200).send({ id: user.id });
  } catch (err) {
    return res.status(500).send("Server error");
  }
});

// ─── Products list ───────────────────────────────────────────────────────────
// FIX: Use /products/search endpoint when a search query is present
app.get("/api/products", async (req, res) => {
  try {
    const { limit, skip, search, select } = req.query;

    const params = {
      ...(limit ? { limit } : {}),
      ...(skip ? { skip } : {}),
      ...(select ? { select } : {}),
    };

    // FIX: dummyjson requires /products/search?q=... for search queries
    const url = search
      ? `https://dummyjson.com/products/search`
      : `https://dummyjson.com/products`;

    if (search) params.q = search;

    const response = await axios.get(url, { params });
    return res.status(200).send(response.data);
  } catch (err) {
    return res.status(500).send("Server error");
  }
});

// ─── Single product ──────────────────────────────────────────────────────────
app.get("/api/products/:id", async (req, res) => {
  try {
    const { data } = await axios.get(
      `https://dummyjson.com/products/${req.params.id}`
    );
    return res.status(200).send(data);
  } catch (err) {
    if (err.response && err.response.status === 404) {
      return res.status(404).send("Product not found");
    }
    return res.status(500).send("Server error");
  }
});

// ─── 404 catch-all ───────────────────────────────────────────────────────────
// FIX: Added catch-all for unknown routes
app.use((req, res) => {
  res.status(404).send("Route not found");
});

// ─── Start server ────────────────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
