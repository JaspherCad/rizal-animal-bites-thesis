"""
Test script for the new interpretability endpoint
Run this after starting the FastAPI server
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"

def test_interpretability():
    """Test the interpretability endpoint"""
    
    print("=" * 60)
    print("🧪 TESTING MODEL INTERPRETABILITY ENDPOINT")
    print("=" * 60)
    
    # First, get available municipalities
    print("\n1️⃣ Fetching available municipalities...")
    response = requests.get(f"{BASE_URL}/api/municipalities")
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch municipalities: {response.status_code}")
        return
    
    data = response.json()
    municipalities = data['municipalities']
    
    if not municipalities:
        print("❌ No municipalities found!")
        return
    
    # Get first municipality and first barangay
    first_mun = municipalities[0]
    municipality_name = first_mun['municipality']
    first_barangay = first_mun['barangays'][0]['name']
    
    print(f"✅ Testing with: {first_barangay}, {municipality_name}")
    
    # Test interpretability endpoint
    print(f"\n2️⃣ Fetching interpretability data...")
    url = f"{BASE_URL}/api/interpretability/{municipality_name}/{first_barangay}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch interpretability: {response.status_code}")
        print(f"   Response: {response.text}")
        return
    
    interp_data = response.json()
    
    if not interp_data['success']:
        print("❌ Interpretability extraction failed!")
        return
    
    print("✅ Successfully retrieved interpretability data!")
    
    # Display results
    print("\n" + "=" * 60)
    print("📊 INTERPRETABILITY RESULTS")
    print("=" * 60)
    
    interp = interp_data['interpretability']
    
    # Trend
    trend_data = interp['trend']
    print(f"\n📈 TREND COMPONENT:")
    print(f"   Description: {trend_data['description']}")
    print(f"   Data points: {len(trend_data['values'])}")
    if trend_data['values']:
        print(f"   Range: {min(trend_data['values']):.2f} to {max(trend_data['values']):.2f}")
        print(f"   Sample (first 3): {trend_data['values'][:3]}")
    
    # Seasonality
    seasonality_data = interp['seasonality']
    print(f"\n🌊 SEASONALITY COMPONENT:")
    print(f"   Description: {seasonality_data['description']}")
    print(f"   Data points: {len(seasonality_data['values'])}")
    if seasonality_data['values']:
        print(f"   Range: {min(seasonality_data['values']):.2f} to {max(seasonality_data['values']):.2f}")
        print(f"   Sample (first 3): {seasonality_data['values'][:3]}")
    
    # Feature Importance
    feature_imp = interp['feature_importance']
    print(f"\n🎯 FEATURE IMPORTANCE (Top 5):")
    print(f"   Description: {feature_imp['description']}")
    for i, feat in enumerate(feature_imp['top_3_features'], 1):
        print(f"   {i}. {feat['feature']}: {feat['percentage']:.2f}% (importance: {feat['importance']:.4f})")
    
    # Changepoints
    changepoints = interp['changepoints']
    print(f"\n🔄 CHANGEPOINTS DETECTED:")
    print(f"   Description: {changepoints['description']}")
    print(f"   Total changepoints: {len(changepoints['points'])}")
    if changepoints['points']:
        print("   Dates:")
        for cp in changepoints['points'][:5]:  # Show first 5
            print(f"      - {cp['date']}: {cp['value']:.2f}")
    
    # Model Config
    config = interp['model_config']
    print(f"\n⚙️ MODEL CONFIGURATION:")
    for key, value in config.items():
        print(f"   - {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    # Save sample response to file
    with open('sample_interpretability_response.json', 'w') as f:
        json.dump(interp_data, f, indent=2)
    print("\n💾 Sample response saved to: sample_interpretability_response.json")

if __name__ == "__main__":
    try:
        test_interpretability()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server!")
        print("   Make sure the FastAPI server is running:")
        print("   cd backend && python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
