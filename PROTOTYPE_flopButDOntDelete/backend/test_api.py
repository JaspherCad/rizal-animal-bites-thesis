"""
Quick test script to verify the updated API works
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("1️⃣ Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_alerts():
    """Test alerts endpoint"""
    print("2️⃣ Testing alerts endpoint...")
    response = requests.get(f"{BASE_URL}/api/alerts")
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Total alerts: {data['count']}")
    if data['alerts']:
        print(f"   First alert: {data['alerts'][0]['barangay']} - {data['alerts'][0]['predicted_cases']} cases")
    print()

def test_municipalities():
    """Test municipalities summary"""
    print("3️⃣ Testing municipalities endpoint...")
    response = requests.get(f"{BASE_URL}/api/municipalities")
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Municipalities: {len(data['municipalities'])}")
    for mun in data['municipalities']:
        print(f"      {mun['municipality']}: {mun['total_barangays']} barangays, {mun['total_predicted_cases']} cases")
    print()

def test_forecast():
    """Test new forecast endpoint"""
    print("4️⃣ Testing NEW forecast endpoint...")
    # Try CAINTA - San Isidro for 6 months
    response = requests.get(f"{BASE_URL}/api/forecast/CAINTA/San_Isidro?months=6")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Barangay: {data['barangay']}")
        print(f"   Training ended: {data['training_end']}")
        print(f"   Forecast months: {data['forecast_months']}")
        print(f"   Model MAE: {data['model_mae']}")
        print()
        print("   📊 Forecast:")
        for item in data['forecast']:
            print(f"      {item['date']}: {item['predicted_cases']} cases ({item['alert_level']})")
    else:
        print(f"   ❌ Failed: {response.status_code}")
        print(f"   Error: {response.text}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING UPDATED RABIES ALERT API")
    print("=" * 60)
    print()
    
    try:
        test_health()
        test_alerts()
        test_municipalities()
        test_forecast()
        
        print("=" * 60)
        print("✅ ALL TESTS COMPLETED!")
        print("=" * 60)
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to API")
        print("   Make sure backend is running: python main.py")
    except Exception as e:
        print(f"❌ ERROR: {e}")
