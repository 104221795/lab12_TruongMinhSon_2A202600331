"""
Test script for rate limiting
Run: python test_advanced.py --test rate-limit
"""
import argparse
import time
import requests

BASE_URL = "http://localhost:8001"


def get_token():
    """Get JWT token"""
    resp = requests.post(
        f"{BASE_URL}/auth/token",
        json={"username": "student", "password": "demo123"}
    )
    return resp.json()["access_token"]


def test_rate_limit():
    """Test rate limiting - 10 requests/min for user"""
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== Rate Limit Test ===")
    print("Limit: 10 requests/minute for 'student' role\n")
    
    results = []
    for i in range(20):
        try:
            resp = requests.post(
                f"{BASE_URL}/ask",
                json={"question": f"test {i}"},
                headers=headers
            )
            status = resp.status_code
            if status == 200:
                remaining = resp.json().get("usage", {}).get("requests_remaining", "N/A")
                results.append(f"Request {i+1}: ✅ 200 (remaining: {remaining})")
            elif status == 429:
                results.append(f"Request {i+1}: ❌ 429 Rate Limited")
            else:
                results.append(f"Request {i+1}: ❌ {status} - {resp.text}")
        except Exception as e:
            results.append(f"Request {i+1}: ❌ Error - {e}")
        
        # Small delay between requests
        time.sleep(0.1)
    
    for r in results:
        print(r)
    
    # Summary
    success = sum(1 for r in results if "✅" in r)
    rate_limited = sum(1 for r in results if "429" in r)
    print(f"\n=== Summary ===")
    print(f"Successful: {success}/20")
    print(f"Rate Limited: {rate_limited}/20")


def test_cost_guard():
    """Test cost guard / budget"""
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== Cost Guard Test ===")
    print("Budget: $1/day for 'student' role\n")
    
    for i in range(5):
        try:
            resp = requests.post(
                f"{BASE_URL}/ask",
                json={"question": "test cost guard"},
                headers=headers
            )
            if resp.status_code == 200:
                usage = resp.json().get("usage", {})
                print(f"Request {i+1}: ✅ Budget remaining: ${usage.get('budget_remaining_usd', 'N/A')}")
            elif resp.status_code == 402:
                print(f"Request {i+1}: ❌ 402 Budget Exceeded")
            else:
                print(f"Request {i+1}: ❌ {resp.status_code}")
        except Exception as e:
            print(f"Request {i+1}: ❌ Error - {e}")
        
        time.sleep(0.2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", choices=["rate-limit", "cost-guard"], required=True)
    args = parser.parse_args()
    
    if args.test == "rate-limit":
        test_rate_limit()
    elif args.test == "cost-guard":
        test_cost_guard()