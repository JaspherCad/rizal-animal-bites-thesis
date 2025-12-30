# 🌤️ FPM Weather-Rabies Integration - Complete Explanation

## 📚 **What is FPM and How Does It Work?**

### **Frequent Pattern Mining (FPM)**
- **What it does**: Discovers patterns that frequently appear together in data
- **In our case**: Finds which weather combinations frequently appear with high/low rabies cases
- **Output**: 1,029 "association rules" like: `IF (High Humidity + Calm Winds + Heavy Rain) THEN High Rabies Cases`

### **Training Data**
- **1,627 monthly records** from 2022-2025
- **32 barangays** in Rizal Province
- **Weather variables**: Temperature, Humidity, Rainfall, Wind Speed, Sunshine
- **Rabies cases**: Monthly counts per barangay

---

## 🔍 **How We Use FPM (Current Implementation)**

### **⏱️ CRITICAL: Monthly Timeframe**
**The FPM model predicts risk for THE ENTIRE MONTH, not a single day!**

- **Training Data**: MONTHLY aggregated records (1 record = 1 barangay-month)
- **Weather Inputs**: MONTHLY values, not daily:
  - **Temperature**: Monthly average (e.g., 27.5°C for the whole month)
  - **Humidity**: Monthly average (e.g., 85% for the whole month)
  - **Precipitation**: **MONTHLY TOTAL** (e.g., 350mm for entire month, not daily)
  - **Wind Speed**: Monthly maximum peak (e.g., 12 km/h highest in month)
  - **Sunshine**: **MONTHLY TOTAL** (e.g., 150 hours for entire month)
- **Risk Assessment**: Predicts risk level for the ENTIRE MONTH ahead

**Why Monthly?**
- Daily data has 30.6% zero-case days → too sparse for pattern mining
- Monthly aggregation reduces zeros to 8.2% → strong patterns emerge
- Monthly predictions align with public health planning cycles

### **1. Weather Data Source**
**❌ CURRENTLY:** Using **TYPICAL MONTHLY VALUES** (not real-time!)
```python
typical_monthly_weather = {
    'tmean_c': 27.5,          # Monthly average temperature
    'rh_pct': 85.0,           # Monthly average humidity
    'precip_mm': 350,         # MONTHLY TOTAL rainfall (not daily!)
    'wind_speed_10m_max_kmh': 12.0,  # Monthly maximum wind speed
    'sunshine_hours': 150     # MONTHLY TOTAL sunshine (not daily!)
}
```

**✅ FOR PRODUCTION:** Should integrate monthly weather forecast API:
- **PAGASA Climate Forecast** (Philippine weather service - monthly outlooks)
- **OpenWeatherMap 30-Day Forecast**
- **WeatherAPI.com Monthly Climate Data**
- Fetch NEXT MONTH's forecast or CURRENT MONTH's accumulated values

### **2. Weather Categorization**
Convert numeric values → Categories using FPM thresholds:

| Weather Factor | Low | Moderate | High | Very High |
|----------------|-----|----------|------|-----------|
| **Humidity** | <70% | 70-80% | 80-85% | >85% |
| **Rainfall** | <100mm | 100-200mm | 200-300mm | >300mm |
| **Wind Speed** | >25 km/h (Breezy) | 15-25 km/h | <15 km/h (Calm) | - |
| **Temperature** | <20°C | 20-25°C | 25-30°C | >30°C |

### **3. Pattern Matching**
Check if current weather matches **TOP HIGH-RISK** or **TOP LOW-RISK** patterns:

#### **🔴 HIGH RISK Pattern**
```
IF: Very High Humidity (>85%)
    + Calm Winds (<15 km/h)
    + Wet Month (>300mm rain)
THEN: VERY HIGH RABIES CASES
    Confidence: 22%
    Lift: 3.44× (344% stronger than random)
```

#### **🟢 LOW RISK Pattern**
```
IF: Low Humidity (<70%)
    + Breezy Winds (15-25 km/h)
    + Dry Month (<100mm rain)
THEN: LOW/NO RABIES CASES
    Confidence: 19.4%
    Lift: 4.09× (409% stronger than random)
```

#### **🟡 MEDIUM RISK**
If weather doesn't match either pattern → **Default to MEDIUM risk**

### **4. Risk Factors Explained**
Backend now provides detailed lists of WHY the risk is what it is:

**HIGH RISK Factors:**
- 🔴 Very high humidity (>85%) creates favorable conditions for animal behavior changes
- 🔴 Calm winds (<15 km/h) reduce dispersion of animal scents, increasing animal encounters
- 🔴 Wet months (>300mm rain) drive animals to seek shelter near human settlements
- 🔴 Combination shows 3.44× stronger association with rabies cases
- 🔴 Historical data: This pattern occurred in 22% of high-case months

**LOW RISK Factors:**
- 🟢 Low humidity (<70%) reduces animal stress and aggressive behavior
- 🟢 Breezy winds (15-25 km/h) improve air circulation and reduce animal encounters
- 🟢 Dry months (<100mm rain) mean animals stay in natural habitats
- 🟢 This pattern shows 4.09× stronger association with LOW/NO cases
- 🟢 Historical data: This pattern occurred in 19.4% of low-case months

---

## 💡 **Why This Matters (Scientific Reasoning)**

### **Why Weather Affects Rabies Cases:**

1. **🌧️ Heavy Rainfall**
   - Forces stray animals to seek shelter
   - Animals move closer to human settlements
   - More human-animal encounters

2. **💧 High Humidity**
   - Increases animal stress levels
   - May trigger more aggressive behavior
   - Makes animals more active

3. **💨 Calm Winds**
   - Animal scents concentrate in areas
   - Attracts more animals to locations
   - Increases pack behavior in stray dogs

4. **🌡️ Moderate Temperatures (25-30°C)**
   - Optimal for animal activity
   - Animals remain active throughout day
   - More chances for bites

5. **🐕 Combined Effect**
   - All factors together create **"perfect storm"**
   - Significantly increases human-animal encounters
   - More encounters = more potential rabies exposures

---

## 📊 **What the UI Now Shows**

### **1. Risk Level Card** (Enhanced)
- Weather risk level: HIGH/MEDIUM/LOW
- Confidence percentage
- **NEW:** "Why This Risk Level?" explanation
- **NEW:** Detailed list of 5 risk factors

### **2. Weather Conditions Grid**
- 5 weather factors with icons
- Numeric values
- Categorical classification

### **3. FPM Pattern Thresholds** (NEW!)
Side-by-side comparison:
- **HIGH RISK Pattern** (red box):
  - Humidity: > 85%
  - Wind: < 15 km/h
  - Rainfall: > 300mm
  - Formula: `Very_High_Humidity + Calm + Wet_Month → VERY HIGH CASES`

- **LOW RISK Pattern** (green box):
  - Humidity: < 70%
  - Wind: 15-25 km/h
  - Rainfall: < 100mm
  - Formula: `Low_Humidity + Breezy + Dry_Month → LOW/NO CASES`

### **4. Why Weather Matters** (NEW!)
Scientific explanations in bullet list:
- 🌧️ Heavy rainfall forces animals near homes
- 💧 High humidity increases animal stress
- 💨 Calm winds concentrate scents
- 🌡️ Moderate temps keep animals active
- 🐕 Combined factors increase encounters

### **5. Matched Pattern Details**
- Exact conditions that matched
- Confidence: How often this pattern predicts correctly
- Lift: How much stronger than random

### **6. Actionable Recommendations**
Specific actions based on risk level

### **7. Model Info** (Enhanced)
- Total rules: 1,029
- High-risk patterns: 534
- Low-risk patterns: 270
- Data source: 1,627 monthly records
- Barangays: 32 (Rizal Province)

### **8. Explanation Box** (Enhanced)
- Why weather NOT used as regressor (hurt accuracy)
- How FPM runs independently
- **NEW:** Method explanation (correlation vs causation)

---

## ⚠️ **Current Limitations & Future Improvements**

### **Limitations:**
1. **❌ Not using real-time weather** - Currently typical values
2. **❌ Simple pattern matching** - Only checks top 2 patterns
3. **❌ No confidence intervals** - Just point estimates
4. **❌ No temporal trends** - Doesn't track weather changes over time

### **Future Improvements:**

#### **1. Real Weather Integration**
```python
# Example: OpenWeatherMap API
import requests

def get_current_weather(municipality, barangay):
    api_key = "YOUR_API_KEY"
    location = f"{barangay}, {municipality}, Rizal, Philippines"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
    
    response = requests.get(url)
    data = response.json()
    
    return {
        'tmean_c': data['main']['temp'] - 273.15,  # Kelvin to Celsius
        'rh_pct': data['main']['humidity'],
        'precip_mm': data['rain']['1h'] if 'rain' in data else 0,
        'wind_speed_10m_max_kmh': data['wind']['speed'] * 3.6,  # m/s to km/h
        'sunshine_hours': calculate_sunshine(data['clouds']['all'])
    }
```

#### **2. Enhanced Pattern Matching**
```python
# Instead of just top 2 patterns, check ALL 1,029 rules
matched_rules = []
for rule in fpm_model['rules']:
    if weather_matches_rule(current_weather, rule):
        matched_rules.append(rule)

# Aggregate confidence from multiple rules
avg_confidence = np.mean([r['confidence'] for r in matched_rules])
```

#### **3. Weather Forecast Integration**
```python
# Get 7-day forecast, predict risk for next week
forecast = get_weather_forecast(municipality, days=7)
for day in forecast:
    day_risk = get_weather_insights(day, fpm_model)
    # Show risk timeline
```

#### **4. Historical Weather Comparison**
```python
# Compare current weather to historical patterns
historical_avg = get_historical_weather(municipality, month=current_month)
deviation = current_weather - historical_avg
# Show: "Humidity is 15% higher than usual for this month"
```

---

## 🎯 **Key Takeaways**

### **What FPM Does:**
✅ Finds weather patterns associated with high/low rabies cases
✅ Provides risk assessment based on current weather
✅ Gives actionable recommendations
✅ Shows scientific reasoning for predictions

### **What FPM Does NOT Do:**
❌ Prove causation (only shows correlation)
❌ Replace the main forecasting model
❌ Use real-time weather data (yet)
❌ Account for other factors (vaccination campaigns, population density, etc.)

### **Why Separate from Forecast Model:**
- Weather regressors **reduced forecast accuracy**
- FPM runs **independently** for risk assessment
- Provides **complementary insights** without compromising predictions
- Useful for **resource planning** and **intervention timing**

---

## 📝 **Summary for Your Thesis**

**Research Contribution:**
> "While direct inclusion of weather variables as regressors in the NeuralProphet+XGBoost model 
> reduced forecast accuracy, we implemented a complementary Frequent Pattern Mining (FPM) analysis 
> to understand weather-rabies associations. The FPM model, trained on 1,627 monthly records across 
> 32 barangays, discovered 1,029 association rules linking specific weather combinations to rabies 
> case levels. This dual-model approach preserves forecast accuracy while providing valuable insights 
> for resource allocation and intervention planning based on weather patterns."

**Practical Impact:**
- Health workers can monitor weather forecasts
- When high-risk patterns detected → proactive interventions
- Resource allocation based on weather-informed risk levels
- Better preparation for potential case spikes

---

**Last Updated:** December 30, 2025
**Version:** 2.0 (Enhanced with detailed explanations)
