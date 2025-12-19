# 🔍 Model Interpretability Guide

## Overview
This guide explains the interpretability features added to the Rabies Forecasting Dashboard to make the model predictions **transparent and explainable** (not a black box!).

---

## 🎯 What You Can Now See

### 1. **TREND COMPONENT** 📈
**What it shows:** The long-term direction of rabies cases over time.

**Why it matters:**
- Identifies if cases are generally increasing or decreasing
- Helps understand the baseline pattern before seasonal effects
- Shows impact of long-term interventions (e.g., vaccination campaigns)

**Example Interpretation:**
- Upward trend → Cases are increasing over time (needs intervention)
- Downward trend → Interventions are working
- Flat trend → Stable situation

---

### 2. **SEASONALITY COMPONENT** 🌊
**What it shows:** Recurring patterns that repeat every year.

**Why it matters:**
- Identifies which months typically have higher/lower cases
- Helps plan seasonal interventions
- Separates seasonal patterns from actual trends

**Example Interpretation:**
- Peak in March-May → Plan vaccination drives before these months
- Low in December-January → Natural low season
- High variance → Strong seasonal effect

---

### 3. **FEATURE IMPORTANCE** 🎯
**What it shows:** Which factors the XGBoost model considers most important for predictions.

**Features Tracked:**
1. `np_prediction` - NeuralProphet baseline forecast
2. `lag_12` - Cases from 12 months ago (yearly pattern)
3. `rolling_mean_3` - Average of last 3 months
4. `lag_1` - Previous month's cases
5. `Month` - Current month number
6. `month_sin/cos` - Cyclical month encoding
7. Other engineered features

**Why it matters:**
- Shows what drives the model's decisions
- Validates that the model uses logical patterns
- Helps identify if the model is overfitting to noise

**Example Interpretation:**
- High importance on `lag_12` → Strong yearly seasonality
- High importance on `np_prediction` → Hybrid model working well
- High importance on `rolling_mean_3` → Recent trends matter

---

### 4. **CHANGEPOINTS** 🔄
**What it shows:** Dates where the trend significantly changed direction.

**Why it matters:**
- Identifies when major events occurred (outbreaks, policy changes)
- Helps correlate data patterns with real-world events
- Validates model's ability to adapt to changing conditions

**Example Interpretation:**
- Changepoint in June 2023 → Possible outbreak started
- Changepoint in January 2024 → Intervention program began
- Multiple changepoints → Volatile situation

---

## 🚀 How to Use the New Endpoint

### API Endpoint
```
GET /api/interpretability/{municipality}/{barangay}
```

### Example Request
```bash
curl http://localhost:8000/api/interpretability/CAINTA/SAN%20ISIDRO
```

### Response Structure
```json
{
  "success": true,
  "interpretability": {
    "municipality": "CAINTA",
    "barangay": "SAN ISIDRO",
    
    "trend": {
      "dates": ["2022-01", "2022-02", ...],
      "values": [5.2, 5.4, 5.6, ...],
      "description": "Long-term direction of rabies cases"
    },
    
    "seasonality": {
      "dates": ["2022-01", "2022-02", ...],
      "values": [0.3, -0.1, 0.5, ...],
      "description": "Recurring yearly patterns"
    },
    
    "feature_importance": {
      "features": [
        {
          "feature": "np_prediction",
          "importance": 0.3542,
          "percentage": 35.42
        },
        {
          "feature": "lag_12",
          "importance": 0.2134,
          "percentage": 21.34
        },
        ...
      ],
      "description": "Which factors contribute most to predictions",
      "top_3_features": [...]
    },
    
    "changepoints": {
      "points": [
        {"date": "2023-06", "value": 8.5},
        {"date": "2024-01", "value": 6.2}
      ],
      "description": "Dates where the trend significantly changed"
    },
    
    "model_config": {
      "neuralprophet_changepoint_prior_scale": "...",
      "xgboost_n_estimators": 100,
      "xgboost_max_depth": 5
    }
  }
}
```

---

## 📊 Frontend Integration Ideas

### 1. **Trend & Seasonality Charts**
```javascript
// Line chart showing decomposition
<Chart>
  <Line data={trend} label="Trend" color="blue" />
  <Line data={seasonality} label="Seasonality" color="green" />
  <Line data={actual} label="Actual" color="black" />
</Chart>
```

### 2. **Feature Importance Bar Chart**
```javascript
// Horizontal bar chart
<BarChart data={featureImportance}>
  {features.map(f => 
    <Bar key={f.feature} value={f.percentage} label={f.feature} />
  )}
</BarChart>
```

### 3. **Changepoints Markers**
```javascript
// Add markers to main forecast chart
{changepoints.map(cp => 
  <VerticalLine 
    x={cp.date} 
    label="Changepoint"
    color="red"
    dashed
  />
)}
```

### 4. **Interpretability Tab/Panel**
Add a new tab in the barangay detail view:
- Tab 1: Forecast (existing)
- Tab 2: **Model Interpretability** (new!)
- Tab 3: Historical Data

---

## 🔬 Technical Details

### How It Works

1. **NeuralProphet Components:**
   - Uses built-in `.predict()` method which returns decomposed components
   - Extracts `trend` and `season_yearly` columns
   - Works on the full historical date range

2. **XGBoost Feature Importance:**
   - Uses `.feature_importances_` attribute
   - Normalized scores summing to 1.0
   - Shows relative importance of each input feature

3. **Changepoint Detection:**
   - Analyzes trend derivative (rate of change)
   - Flags points where trend changes exceed 1.5 standard deviations
   - Simplified approach (NeuralProphet has internal changepoints too)

### Dependencies
All required libraries are already in your `requirements.txt`:
- `neuralprophet` - For trend/seasonality decomposition
- `xgboost` - For feature importance
- `pandas`, `numpy` - For data manipulation

---

## 🎨 UI/UX Recommendations

### Visual Design
1. **Trend Chart**: Blue line with gradual slope
2. **Seasonality Chart**: Green oscillating pattern
3. **Feature Importance**: Horizontal bars (top 5-7 features)
4. **Changepoints**: Red vertical dashed lines on main chart

### Information Hierarchy
```
┌─────────────────────────────────────┐
│  📊 Model Interpretability          │
├─────────────────────────────────────┤
│                                     │
│  🎯 What Drives Predictions         │
│  [Feature Importance Bar Chart]     │
│                                     │
│  📈 Trend Analysis                  │
│  [Trend Line Chart]                 │
│                                     │
│  🌊 Seasonal Patterns               │
│  [Seasonality Line Chart]           │
│                                     │
│  🔄 Significant Changes             │
│  [Changepoints List/Timeline]       │
│                                     │
└─────────────────────────────────────┘
```

### Tooltips & Explanations
Add info icons (ℹ️) with explanations:
- "Trend shows the overall direction independent of seasonal effects"
- "Seasonality represents recurring yearly patterns"
- "Higher feature importance means stronger influence on predictions"

---

## 📝 Example Use Cases

### Use Case 1: Explaining High Risk
**Question:** "Why is this barangay marked as HIGH RISK?"

**Answer with Interpretability:**
1. Check Trend → "Upward trend showing 15% increase over last year"
2. Check Seasonality → "Currently in peak season (March-May)"
3. Check Feature Importance → "Model heavily weighs recent 3-month average"
4. Check Changepoint → "Trend changed in January 2025, indicating outbreak start"

### Use Case 2: Validating Interventions
**Question:** "Did our vaccination campaign work?"

**Answer with Interpretability:**
1. Check Changepoint → "Trend shift detected in intervention month"
2. Check Trend → "Downward slope after intervention date"
3. Compare Actual vs Predicted → "Cases lower than predicted"

### Use Case 3: Planning Resources
**Question:** "When should we increase resources?"

**Answer with Interpretability:**
1. Check Seasonality → "Peak in April-June every year"
2. Check Trend → "Overall trend is upward"
3. Plan → "Prepare extra resources March-July"

---

## 🧪 Testing

Run the test script:
```bash
cd backend
python test_interpretability.py
```

This will:
1. Fetch a sample barangay
2. Call the interpretability endpoint
3. Display all components
4. Save sample response to `sample_interpretability_response.json`

---

## 🚨 Important Notes

### Limitations
1. **Changepoint detection is simplified** - Uses statistical approach rather than NeuralProphet's internal mechanism
2. **Feature importance is global** - Shows overall importance, not per-prediction explanation
3. **Seasonality** - Currently only yearly; could add weekly/monthly if needed

### Future Enhancements
- [ ] Add SHAP values for individual prediction explanations
- [ ] Include confidence intervals for trend/seasonality
- [ ] Add holiday effects if configured in NeuralProphet
- [ ] Interactive changepoint annotations with event labels
- [ ] Comparative analysis across barangays

---

## 📞 Support

If you have questions about interpretability:
1. Check API docs: `http://localhost:8000/docs`
2. Review this guide
3. Test with: `python test_interpretability.py`
4. Inspect sample JSON: `sample_interpretability_response.json`

---

**Version:** 2.1.0  
**Last Updated:** October 28, 2025  
**Feature:** Model Interpretability & Transparency
