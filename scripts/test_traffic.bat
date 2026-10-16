@echo off
echo ==============================================================================
echo [EXPENSE TRACKER] Generating Real-time Test Traffic & Metrics
echo ==============================================================================

set BASE_URL=https://localhost
set INSECURE=-k

echo [1/4] Testing Health Endpoint...
curl %INSECURE% -s -i %BASE_URL%/healthz
echo.

echo [2/4] Testing Prometheus Metrics Endpoint...
curl %INSECURE% -s %BASE_URL%/metrics | findstr /i "expense_tracker"
echo.

echo [3/4] Creating Test Transactions (POST /api/transactions)...
curl %INSECURE% -s -X POST %BASE_URL%/api/transactions -H "Content-Type: application/json" -d "{\"type\":\"expense\",\"amount\":125000,\"category_id\":1,\"description\":\"Tra sua va snack chieu\"}"
echo.
curl %INSECURE% -s -X POST %BASE_URL%/api/transactions -H "Content-Type: application/json" -d "{\"type\":\"income\",\"amount\":5000000,\"category_id\":9,\"description\":\"Thuong KPI tuan 3\"}"
echo.
curl %INSECURE% -s -X POST %BASE_URL%/api/transactions -H "Content-Type: application/json" -d "{\"type\":\"expense\",\"amount\":450000,\"category_id\":4,\"description\":\"Sach DevOps va System Administration\"}"
echo.

echo [4/4] Querying Analytics Stats...
curl %INSECURE% -s %BASE_URL%/api/stats
echo.
echo ==============================================================================
echo Traffic generation complete! Check Grafana at http://localhost:3001
echo ==============================================================================
pause
