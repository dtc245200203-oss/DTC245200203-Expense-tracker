@echo off
echo ==============================================================================
echo [EXPENSE TRACKER] Loki LogQL Automated Verification Queries
echo ==============================================================================

set LOKI_URL=http://localhost:3100

echo [QUERY 1] Retrieve Application Logs: {service="expense-app"}
curl -s -G "%LOKI_URL%/loki/api/v1/query" --data-urlencode "query={service=\"expense-app\"}" | python -m json.tool
echo.

echo ------------------------------------------------------------------------------
echo [QUERY 2] Retrieve Nginx Access Logs with Filter: {job="nginx"}
curl -s -G "%LOKI_URL%/loki/api/v1/query" --data-urlencode "query={job=\"nginx\"}" | python -m json.tool
echo.

echo ------------------------------------------------------------------------------
echo [QUERY 3] Filter Business Transaction Logs: {service="expense-app"} |= "transaction_created"
curl -s -G "%LOKI_URL%/loki/api/v1/query" --data-urlencode "query={service=\"expense-app\"} |= \"transaction_created\"" | python -m json.tool
echo.

echo ------------------------------------------------------------------------------
echo [QUERY 4] Log Rate over 1 minute: rate({job="nginx"}[1m])
curl -s -G "%LOKI_URL%/loki/api/v1/query" --data-urlencode "query=rate({job=\"nginx\"}[1m])" | python -m json.tool
echo.
echo ==============================================================================
echo Verification Finished!
echo ==============================================================================
pause
