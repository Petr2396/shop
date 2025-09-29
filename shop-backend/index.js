const express = require("express");
const cors = require("cors");
const { Pool, types } = require("pg");
require('dotenv').config();



const app = express();
app.use(cors());
app.use(express.json());

const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

app.get('/api/products', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM products');

    res.set('Content-Range', `products 0-${result.rows.length - 1}/${result.rows.length}`);
    res.set('Access-Control-Expose-Headers', 'Content-Range');
    res.set('Content-Type', 'application/json; charset=utf-8');
    res.json(result.rows); // без перекодировки

  } catch (err) {
    console.error('🔥 Ошибка в /api/products:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

  


// ЮKassa оплата
app.post("/api/pay", async (req, res) => {
  try {
    const { amount, description } = req.body;
    const payment = await yookassa.createPayment(amount, description);
    res.json(payment);
  } catch (error) {
    console.error("Payment error:", error);
    res.status(500).json({ error: "Payment error" });
  }
});

app.listen(5000, () => console.log("API running on port 5000")); 