const { Pool } = require('pg');

const pool = new Pool({
  host: process.env.DB_HOST || 'postgres',
  port: parseInt(process.env.DB_PORT || '5432', 10),
  database: process.env.DB_NAME || 'expense_db',
  user: process.env.DB_USER || 'expense_user',
  password: process.env.DB_PASSWORD || 'ExpenseSecurePass2026!',
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 5000,
});

pool.on('error', (err) => {
  console.error(JSON.stringify({
    level: 'error',
    timestamp: new Date().toISOString(),
    service: 'db',
    message: 'Unexpected error on idle client',
    error: err.message
  }));
});

// Helper for testing DB connection with retry logic
async function waitForDatabase(retries = 15, delayMs = 2000) {
  for (let i = 1; i <= retries; i++) {
    try {
      const client = await pool.connect();
      console.log(JSON.stringify({
        level: 'info',
        timestamp: new Date().toISOString(),
        service: 'db',
        message: 'Successfully connected to PostgreSQL database',
        attempt: i
      }));
      client.release();
      return true;
    } catch (err) {
      console.warn(JSON.stringify({
        level: 'warn',
        timestamp: new Date().toISOString(),
        service: 'db',
        message: `Database connection attempt ${i}/${retries} failed, retrying in ${delayMs}ms...`,
        error: err.message
      }));
      if (i === retries) {
        throw new Error(`Failed to connect to database after ${retries} attempts`);
      }
      await new Promise(resolve => setTimeout(resolve, delayMs));
    }
  }
}

module.exports = {
  pool,
  query: (text, params) => pool.query(text, params),
  waitForDatabase
};
