require('dotenv').config();
const fs = require('fs');
const express = require('express');
const path = require('path');
const db = require('./db');
const metrics = require('./metrics');

const app = express();
const PORT = process.env.PORT || 3000;

const LOG_DIR = '/var/log/app';
const LOG_FILE = path.join(LOG_DIR, 'app.log');

function writeLog(data) {
  const line = JSON.stringify(data);
  console.log(line);
  try {
    if (!fs.existsSync(LOG_DIR)) {
      fs.mkdirSync(LOG_DIR, { recursive: true });
    }
    fs.appendFileSync(LOG_FILE, line + '\n');
  } catch (e) {
    // Non-fatal if filesystem is read-only
  }
}

// Body parsing
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Metrics & Logging Middleware
app.use((req, res, next) => {
  const start = process.hrtime();
  
  res.on('finish', () => {
    const diff = process.hrtime(start);
    const durationSeconds = diff[0] + diff[1] / 1e9;
    const durationMs = Math.round(durationSeconds * 1000);
    
    // Normalize route path for Prometheus labels to avoid high cardinality
    let route = req.baseUrl + (req.route ? req.route.path : req.path);
    if (route.startsWith('/api/transactions/') && route.length > '/api/transactions/'.length) {
      route = '/api/transactions/:id';
    }

    metrics.httpRequestsTotal.inc({
      method: req.method,
      route: route,
      status_code: res.statusCode
    });

    metrics.httpRequestDurationSeconds.observe({
      method: req.method,
      route: route,
      status_code: res.statusCode
    }, durationSeconds);

    // Structured JSON log for Loki / Promtail
    const logLevel = res.statusCode >= 500 ? 'error' : (res.statusCode >= 400 ? 'warn' : 'info');
    writeLog({
      level: logLevel,
      timestamp: new Date().toISOString(),
      service: 'expense-app',
      method: req.method,
      path: req.originalUrl,
      status: res.statusCode,
      duration_ms: durationMs,
      ip: req.headers['x-forwarded-for'] || req.socket.remoteAddress,
      user_agent: req.headers['user-agent'] || 'unknown'
    });
  });

  next();
});

// Serve frontend static assets
app.use(express.static(path.join(__dirname, '../public')));

// Prometheus metrics endpoint
app.get('/metrics', async (req, res) => {
  try {
    await metrics.refreshBusinessMetrics(db);
    res.set('Content-Type', metrics.register.contentType);
    res.end(await metrics.register.metrics());
  } catch (err) {
    res.status(500).end(err.message);
  }
});

// Health check endpoint
app.get('/healthz', async (req, res) => {
  try {
    await db.query('SELECT 1');
    res.json({
      status: 'healthy',
      database: 'connected',
      uptime: process.uptime(),
      timestamp: new Date().toISOString()
    });
  } catch (err) {
    res.status(503).json({
      status: 'unhealthy',
      database: 'disconnected',
      error: err.message
    });
  }
});

// API: Get categories
app.get('/api/categories', async (req, res, next) => {
  try {
    const { rows } = await db.query('SELECT * FROM categories ORDER BY type DESC, name ASC');
    res.json(rows);
  } catch (err) {
    next(err);
  }
});

// API: Create custom category
app.post('/api/categories', async (req, res, next) => {
  try {
    const { name, type, icon, color } = req.body;
    if (!name || !type || !['income', 'expense'].includes(type)) {
      return res.status(400).json({ error: 'Valid name and type (income/expense) required' });
    }
    const { rows } = await db.query(
      'INSERT INTO categories (name, type, icon, color) VALUES ($1, $2, $3, $4) RETURNING *',
      [name, type, icon || 'tag', color || '#4f46e5']
    );
    res.status(201).json(rows[0]);
  } catch (err) {
    next(err);
  }
});

// API: Get transactions (with filtering)
app.get('/api/transactions', async (req, res, next) => {
  try {
    const { type, category_id, start_date, end_date, search, limit = 100 } = req.query;
    let query = `
      SELECT t.id, t.amount, t.type, t.description, t.transaction_date, t.created_at,
             c.id AS category_id, c.name AS category_name, c.icon AS category_icon, c.color AS category_color
      FROM transactions t
      JOIN categories c ON t.category_id = c.id
      WHERE 1=1
    `;
    const params = [];

    if (type && ['income', 'expense'].includes(type)) {
      params.push(type);
      query += ` AND t.type = $${params.length}`;
    }

    if (category_id) {
      params.push(parseInt(category_id, 10));
      query += ` AND t.category_id = $${params.length}`;
    }

    if (start_date) {
      params.push(start_date);
      query += ` AND t.transaction_date >= $${params.length}`;
    }

    if (end_date) {
      params.push(end_date);
      query += ` AND t.transaction_date <= $${params.length}`;
    }

    if (search) {
      params.push(`%${search}%`);
      query += ` AND (t.description ILIKE $${params.length} OR c.name ILIKE $${params.length})`;
    }

    query += ` ORDER BY t.transaction_date DESC, t.id DESC LIMIT $${params.length + 1}`;
    params.push(parseInt(limit, 10));

    const { rows } = await db.query(query, params);
    res.json(rows);
  } catch (err) {
    next(err);
  }
});

// API: Add transaction
app.post('/api/transactions', async (req, res, next) => {
  try {
    const { amount, type, category_id, transaction_date, description } = req.body;
    
    if (!amount || isNaN(amount) || parseFloat(amount) <= 0) {
      return res.status(400).json({ error: 'Amount must be a positive number' });
    }
    if (!type || !['income', 'expense'].includes(type)) {
      return res.status(400).json({ error: 'Type must be income or expense' });
    }
    if (!category_id) {
      return res.status(400).json({ error: 'Category is required' });
    }

    const date = transaction_date || new Date().toISOString().split('T')[0];
    const desc = description || '';

    const { rows } = await db.query(
      `INSERT INTO transactions (amount, type, category_id, transaction_date, description)
       VALUES ($1, $2, $3, $4, $5) RETURNING *`,
      [parseFloat(amount), type, parseInt(category_id, 10), date, desc]
    );

    await metrics.refreshBusinessMetrics(db);

    writeLog({
      level: 'info',
      timestamp: new Date().toISOString(),
      service: 'expense-app',
      action: 'transaction_created',
      transaction_id: rows[0].id,
      type: rows[0].type,
      amount: rows[0].amount
    });

    res.status(201).json(rows[0]);
  } catch (err) {
    next(err);
  }
});

// API: Update transaction
app.put('/api/transactions/:id', async (req, res, next) => {
  try {
    const { id } = req.params;
    const { amount, type, category_id, transaction_date, description } = req.body;

    const { rows } = await db.query(
      `UPDATE transactions 
       SET amount = COALESCE($1, amount),
           type = COALESCE($2, type),
           category_id = COALESCE($3, category_id),
           transaction_date = COALESCE($4, transaction_date),
           description = COALESCE($5, description),
           updated_at = CURRENT_TIMESTAMP
       WHERE id = $6 RETURNING *`,
      [amount ? parseFloat(amount) : null, type, category_id ? parseInt(category_id, 10) : null, transaction_date, description, parseInt(id, 10)]
    );

    if (rows.length === 0) {
      return res.status(404).json({ error: 'Transaction not found' });
    }

    await metrics.refreshBusinessMetrics(db);
    res.json(rows[0]);
  } catch (err) {
    next(err);
  }
});

// API: Delete transaction
app.delete('/api/transactions/:id', async (req, res, next) => {
  try {
    const { id } = req.params;
    const { rowCount } = await db.query('DELETE FROM transactions WHERE id = $1', [parseInt(id, 10)]);
    if (rowCount === 0) {
      return res.status(404).json({ error: 'Transaction not found' });
    }

    await metrics.refreshBusinessMetrics(db);

    writeLog({
      level: 'info',
      timestamp: new Date().toISOString(),
      service: 'expense-app',
      action: 'transaction_deleted',
      transaction_id: parseInt(id, 10)
    });

    res.json({ message: 'Transaction deleted successfully' });
  } catch (err) {
    next(err);
  }
});

// API: Dashboard stats & analytics
app.get('/api/stats', async (req, res, next) => {
  try {
    // 1. Overall totals
    const totalsRes = await db.query(`
      SELECT 
        COUNT(*)::int AS total_count,
        COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS total_income,
        COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS total_expense
      FROM transactions
    `);

    const totalIncome = parseFloat(totalsRes.rows[0].total_income);
    const totalExpense = parseFloat(totalsRes.rows[0].total_expense);
    const netBalance = totalIncome - totalExpense;

    // 2. Expense Breakdown by Category
    const categoryRes = await db.query(`
      SELECT c.name, c.color, c.icon, COALESCE(SUM(t.amount), 0) AS amount
      FROM categories c
      JOIN transactions t ON t.category_id = c.id
      WHERE t.type = 'expense'
      GROUP BY c.id, c.name, c.color, c.icon
      ORDER BY amount DESC
    `);

    // 3. Monthly Trend (last 6 months)
    const trendRes = await db.query(`
      SELECT 
        TO_CHAR(transaction_date, 'YYYY-MM') AS month,
        COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS income,
        COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS expense
      FROM transactions
      GROUP BY TO_CHAR(transaction_date, 'YYYY-MM')
      ORDER BY month ASC
      LIMIT 12
    `);

    res.json({
      summary: {
        totalTransactions: totalsRes.rows[0].total_count,
        totalIncome,
        totalExpense,
        netBalance
      },
      categoryBreakdown: categoryRes.rows.map(r => ({
        name: r.name,
        color: r.color,
        icon: r.icon,
        amount: parseFloat(r.amount)
      })),
      monthlyTrend: trendRes.rows.map(r => ({
        month: r.month,
        income: parseFloat(r.income),
        expense: parseFloat(r.expense)
      }))
    });
  } catch (err) {
    next(err);
  }
});

// API: Export CSV
app.get('/api/export-csv', async (req, res, next) => {
  try {
    const { rows } = await db.query(`
      SELECT t.id, t.transaction_date, t.type, c.name AS category, t.amount, t.description
      FROM transactions t
      JOIN categories c ON t.category_id = c.id
      ORDER BY t.transaction_date DESC, t.id DESC
    `);

    let csv = 'ID,Date,Type,Category,Amount (VND),Description\n';
    rows.forEach(r => {
      const desc = `"${(r.description || '').replace(/"/g, '""')}"`;
      csv += `${r.id},${r.transaction_date.toISOString().split('T')[0]},${r.type},${r.category},${r.amount},${desc}\n`;
    });

    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', 'attachment; filename="expense-report.csv"');
    res.send(csv);
  } catch (err) {
    next(err);
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(JSON.stringify({
    level: 'error',
    timestamp: new Date().toISOString(),
    service: 'expense-app',
    message: err.message,
    stack: err.stack,
    path: req.originalUrl
  }));

  res.status(500).json({
    error: 'Internal Server Error',
    message: process.env.NODE_ENV === 'production' ? 'An unexpected error occurred' : err.message
  });
});

// Start Server after Database Ready
async function start() {
  try {
    await db.waitForDatabase();
    await metrics.refreshBusinessMetrics(db);
    
    app.listen(PORT, '0.0.0.0', () => {
      console.log(JSON.stringify({
        level: 'info',
        timestamp: new Date().toISOString(),
        service: 'expense-app',
        message: `Expense Tracker Server running on port ${PORT}`,
        env: process.env.NODE_ENV || 'development'
      }));
    });
  } catch (err) {
    console.error(JSON.stringify({
      level: 'fatal',
      timestamp: new Date().toISOString(),
      service: 'expense-app',
      message: 'Failed to start server due to database connection failure',
      error: err.message
    }));
    process.exit(1);
  }
}

start();
