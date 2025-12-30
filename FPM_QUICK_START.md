# 🚀 Quick Start Guide: Using the Rabies-Weather FPM Model

## ⚡ TL;DR

**Model File**: `rabies_weather_fpm_model.pkl` (739 KB)  
**Purpose**: Predict rabies risk based on weather patterns  
**Input**: Monthly weather data (temp, humidity, rain, wind, sunshine)  
**Output**: Risk level (HIGH/MEDIUM/LOW) + recommendations

---

## 📦 What's Included

```
rabies_weather_fpm_model.pkl          # Main model (739 KB)
monthly_fpm_rabies_rules.csv          # All 1,029 rules
monthly_fpm_HIGH_RISK_rules.csv       # 534 high-risk rules
monthly_fpm_LOW_RISK_rules.csv        # 270 low-risk rules
monthly_aggregated_data.csv           # Training data
FREQUENT_PATTERN_MINING_DOCUMENTATION.md  # Full documentation
```

---

## 🔥 Quick Usage (5 Minutes)

### Step 1: Load Model

```python
import pickle

with open('rabies_weather_fpm_model.pkl', 'rb') as f:
    model = pickle.load(f)

print(f"Loaded model with {model['summary']['rabies_related_rules']} rules")
# Output: Loaded model with 1029 rules
```

### Step 2: Prepare Weather Data

```python
# Example: Weather forecast for next month
weather = {
    'tmean_c': 27.5,                    # Temperature (°C)
    'rh_pct': 86.3,                     # Humidity (%)
    'precip_mm': 391,                   # Rainfall (mm)
    'wind_speed_10m_max_kmh': 11.7,     # Wind speed (km/h)
    'sunshine_hours': 150               # Sunshine (hours)
}
```

### Step 3: Categorize Weather

```python
import pandas as pd

def categorize(weather, model):
    temp = pd.cut([weather['tmean_c']], 
                  bins=model['thresholds']['temperature']['bins'],
                  labels=model['thresholds']['temperature']['labels'])[0]
    
    humidity = pd.cut([weather['rh_pct']], 
                      bins=model['thresholds']['humidity']['bins'],
                      labels=model['thresholds']['humidity']['labels'])[0]
    
    rain = pd.cut([weather['precip_mm']], 
                  bins=model['thresholds']['precipitation']['bins'],
                  labels=model['thresholds']['precipitation']['labels'])[0]
    
    wind = pd.cut([weather['wind_speed_10m_max_kmh']], 
                  bins=model['thresholds']['wind']['bins'],
                  labels=model['thresholds']['wind']['labels'])[0]
    
    return f"Humidity: {humidity}, Wind: {wind}, Rain: {rain}"

result = categorize(weather, model)
print(result)
# Output: Humidity: Very_High_Humidity, Wind: Calm, Rain: Wet_Month
```

### Step 4: Check Risk

```python
# Quick check against top high-risk pattern
top_pattern = model['top_high_risk_pattern']

print("Top High-Risk Pattern:")
print(f"  Conditions: {top_pattern['conditions']}")
print(f"  Confidence: {top_pattern['confidence']:.1%}")
print(f"  Lift: {top_pattern['lift']:.2f}")

# If your weather matches: Very_High_Humidity + Calm + Wet_Month
# → HIGH RISK!
```

---

## 🎯 Key Patterns to Remember

### 🔴 HIGH RISK Pattern
```
IF: Very High Humidity (>85%) 
    + Calm winds (<15 km/h)
    + Wet month (>300mm rain)
THEN: Very High Rabies Cases
      Confidence: 22%
      Lift: 3.44× stronger than random
```

**Actions**:
- ✅ Send SMS alerts
- ✅ Stock vaccines
- ✅ Deploy extra teams
- ✅ Daily monitoring

### 🟢 LOW RISK Pattern
```
IF: Low Humidity (<70%)
    + Breezy winds (15-25 km/h)
    + Dry month (<100mm rain)
THEN: Low/No Rabies Cases
      Confidence: 19.4%
      Lift: 4.09× stronger than random
```

**Actions**:
- ✅ Routine surveillance
- ✅ Community vaccination drives
- ✅ Reallocate resources

---

## 📊 Model Stats at a Glance

| Metric | Value |
|--------|-------|
| Training Data | 1,627 monthly records |
| Time Period | 2022-2025 (post-break only) |
| Barangays | 32 (Rizal Province) |
| Total Rules | 4,258 |
| High-Risk Rules | 534 |
| Strongest Lift | 4.09× |
| Model Size | 739 KB |

---

## ⚠️ Important Notes

1. **Monthly Data Only**: Model expects monthly aggregates, not daily
2. **Post-Break Only**: Valid for 2022+ (12× increase occurred in 2022)
3. **Philippine Climate**: Thresholds calibrated for tropical monsoon climate
4. **Correlation ≠ Causation**: Shows associations, not definitive causes

---

## 🔗 Next Steps

- **Full Documentation**: See `FREQUENT_PATTERN_MINING_DOCUMENTATION.md`
- **Notebook**: `TrainingFrequentPatternMiningWeather.ipynb`
- **Rule Details**: Check CSV files for complete rule lists

---

## 💡 Example API Response

```json
{
  "risk_level": "HIGH",
  "confidence": 0.22,
  "weather_conditions": {
    "temp": "Moderate",
    "humidity": "Very_High_Humidity",
    "rain": "Wet_Month",
    "wind": "Calm",
    "sunshine": "Low_Sun"
  },
  "matched_patterns": 3,
  "recommendations": [
    "Send SMS alerts to all health workers",
    "Stock up on PEP vaccines (expect ~150 cases)",
    "Deploy 2-3 additional vaccination teams",
    "Launch awareness campaigns",
    "Switch to daily case reporting"
  ],
  "estimated_cases": 150,
  "estimated_cost": "₱525,000"
}
```

---

**Ready to Deploy!** 🚀

