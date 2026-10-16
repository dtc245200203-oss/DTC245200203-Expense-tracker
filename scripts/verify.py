import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

print("=== CHECKING PROMETHEUS TARGETS ===")
try:
    with urllib.request.urlopen("http://localhost:9090/api/v1/targets") as res:
        data = json.loads(res.read().decode())
        for t in data["data"]["activeTargets"]:
            print(f"- Target {t['scrapePool']} ({t['labels'].get('instance', '')}): {t['health'].upper()}")
except Exception as e:
    print(f"Error checking Prometheus: {e}")

print("\n=== CHECKING LOKI READY STATUS ===")
try:
    with urllib.request.urlopen("http://localhost:3100/ready") as res:
        print(f"Loki Status: {res.read().decode().strip()}")
except Exception as e:
    print(f"Error checking Loki: {e}")

print("\n=== CHECKING GRAFANA HEALTH ===")
try:
    with urllib.request.urlopen("http://localhost:3001/api/health") as res:
        print(f"Grafana Health: {res.read().decode().strip()}")
except Exception as e:
    print(f"Error checking Grafana: {e}")

print("\n=== CHECKING EXPENSE APP VIA HTTPS ===")
try:
    req = urllib.request.Request("https://localhost/healthz")
    with urllib.request.urlopen(req, context=ctx) as res:
        print(f"App Health via Nginx HTTPS: {res.read().decode().strip()}")
except Exception as e:
    print(f"Error checking App via HTTPS: {e}")
