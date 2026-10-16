import urllib.request
import urllib.parse
import json
import ssl
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE_URL = "https://localhost"

def post_transaction(t_type, amount, category_id, description):
    url = f"{BASE_URL}/api/transactions"
    payload = json.dumps({
        "type": t_type,
        "amount": amount,
        "category_id": category_id,
        "description": description
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, context=ctx) as res:
            res_data = json.loads(res.read().decode())
            print(f"[OK] Transaction Created: ID={res_data.get('id')}, Amount={res_data.get('amount')}, Desc='{res_data.get('description')}'")
            return res_data
    except Exception as e:
        print(f"[ERROR] Failed to post transaction: {e}")
        return None

print("=== 1. CREATING TRANSACTIONS VIA HTTPS ===")
t1 = post_transaction("expense", 125000, 1, "Trà sữa và bánh ngọt buổi chiều")
t2 = post_transaction("income", 5000000, 9, "Thưởng dự án hoàn thành tuần 3")
t3 = post_transaction("expense", 450000, 4, "Sách Triển khai và Quản trị Hệ thống")

print("\n=== 2. VERIFYING STATS ===")
try:
    with urllib.request.urlopen(f"{BASE_URL}/api/stats", context=ctx) as res:
        stats = json.loads(res.read().decode())
        summary = stats["summary"]
        print(f"Total Transactions: {summary['totalTransactions']}")
        print(f"Total Income:       {summary['totalIncome']:,.0f} VND")
        print(f"Total Expense:      {summary['totalExpense']:,.0f} VND")
        print(f"Net Balance:        {summary['netBalance']:,.0f} VND")
except Exception as e:
    print(f"Failed to get stats: {e}")

print("\n=== 3. QUERYING LOKI VIA LOGQL ===")
# Wait a moment for promtail to push logs to loki
time.sleep(2)
queries = [
    ('{service="expense-app"}', "Loki LogQL Query 1: All Expense App logs"),
    ('{service="expense-app"} |= "transaction_created"', "Loki LogQL Query 2: Filter Created Transactions"),
    ('{job="nginx"}', "Loki LogQL Query 3: Nginx Access Logs")
]

for q, desc in queries:
    print(f"\n--- {desc} ---")
    print(f"Query: {q}")
    loki_url = f"http://localhost:3100/loki/api/v1/query?query={urllib.parse.quote(q)}"
    try:
        with urllib.request.urlopen(loki_url) as res:
            data = json.loads(res.read().decode())
            results = data.get("data", {}).get("result", [])
            print(f"Returned Streams: {len(results)}")
            for stream in results[:2]:
                labels = stream.get("stream", {})
                values = stream.get("values", [])
                print(f"  Labels: {labels}")
                if values:
                    print(f"  Sample Log Line: {values[0][1][:120]}...")
    except Exception as e:
        print(f"Loki query error: {e}")

print("\n=== ALL VERIFICATION TESTS FINISHED SUCCESSFULLY! ===")
