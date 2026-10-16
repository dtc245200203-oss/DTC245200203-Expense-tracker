const client = require('prom-client');

// Initialize default recommended Prometheus metrics
const register = new client.Registry();
client.collectDefaultMetrics({ register, prefix: 'expense_tracker_' });

// Custom HTTP request counter
const httpRequestsTotal = new client.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests processed by Expense Tracker',
  labelNames: ['method', 'route', 'status_code'],
});
register.registerMetric(httpRequestsTotal);

// Custom HTTP request duration histogram
const httpRequestDurationSeconds = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5]
});
register.registerMetric(httpRequestDurationSeconds);

// Custom Business Metrics: Active transactions count, income, expense, balance
const totalTransactionsGauge = new client.Gauge({
  name: 'expense_tracker_total_transactions',
  help: 'Total number of transactions recorded in database'
});
register.registerMetric(totalTransactionsGauge);

const totalIncomeGauge = new client.Gauge({
  name: 'expense_tracker_total_income',
  help: 'Total income amount recorded in database'
});
register.registerMetric(totalIncomeGauge);

const totalExpenseGauge = new client.Gauge({
  name: 'expense_tracker_total_expense',
  help: 'Total expense amount recorded in database'
});
register.registerMetric(totalExpenseGauge);

const netBalanceGauge = new client.Gauge({
  name: 'expense_tracker_net_balance',
  help: 'Net balance (Income - Expense) in database'
});
register.registerMetric(netBalanceGauge);

async function refreshBusinessMetrics(db) {
  try {
    const statsRes = await db.query(`
      SELECT 
        COUNT(*)::int AS count,
        COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS total_income,
        COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS total_expense
      FROM transactions
    `);
    
    if (statsRes.rows.length > 0) {
      const { count, total_income, total_expense } = statsRes.rows[0];
      const incomeNum = parseFloat(total_income);
      const expenseNum = parseFloat(total_expense);
      const balanceNum = incomeNum - expenseNum;

      totalTransactionsGauge.set(count);
      totalIncomeGauge.set(incomeNum);
      totalExpenseGauge.set(expenseNum);
      netBalanceGauge.set(balanceNum);
    }
  } catch (err) {
    // If table not ready yet, silently ignore
  }
}

module.exports = {
  register,
  httpRequestsTotal,
  httpRequestDurationSeconds,
  refreshBusinessMetrics
};
