# ==============================================
# RABIES ALERT SYSTEM - FastAPI Backend
# ==============================================

import pickle
import os
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import ML libraries (required for unpickling saved models)
from neuralprophet import NeuralProphet
import xgboost as xgb

# Initialize FastAPI
app = FastAPI(
    title="Rabies Forecasting Alert System",
    description="AI-powered rabies case forecasting and alert system for Rizal Province",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================
# 🔥 NEW: PREDICTION FUNCTION (SAME AS TRAINING!)
# ==============================================

def predict_future_months(model_data, num_months=1):
    """
    Predict future months using saved NeuralProphet + XGBoost models.
    Uses EXACT SAME METHOD as training phase.
    """
    try:
        np_model = model_data['np_model']
        xgb_model = model_data['xgb_model']
        training_end = model_data['training_end']
        barangay = model_data.get('barangay', 'Unknown')
        municipality = model_data.get('municipality', 'Unknown')
        
        # Generate future dates
        future_dates = pd.date_range(
            start=training_end + pd.DateOffset(months=1),
            periods=num_months,
            freq='MS'
        )
        
        # Debug: Check if we're predicting reasonable dates
        print(f"   � {municipality}/{barangay}: Training ended {training_end.strftime('%Y-%m')}, predicting {future_dates[0].strftime('%Y-%m')}")
        
        # �🔥 FIX: NeuralProphet needs 'y' column (can be dummy values for prediction)
        future_df = pd.DataFrame({
            'ds': future_dates,
            'y': 0  # Dummy values - not used in prediction
        })
        
        # Get NeuralProphet baseline (SAME AS TRAINING!)
        np_forecast = np_model.predict(future_df)
        np_baseline = np_forecast['yhat1'].values
        
        # Debug: Check NP baseline range
        print(f"   � NP baseline range: {np_baseline.min():.1f} to {np_baseline.max():.1f}")
        
        # �🔥 CRITICAL: Prepare XGBoost features in EXACT SAME ORDER as training!
        # Training order: Year, Month, lag_1, lag_2, rolling_mean_3, rolling_std_3, 
        #                 lag_12, month_sin, month_cos, rate_of_change_1, np_prediction
        X_future = pd.DataFrame({
            'Year': future_dates.year,
            'Month': future_dates.month,
            'lag_1': 0,  # No future actuals available
            'lag_2': 0,
            'rolling_mean_3': 0,
            'rolling_std_3': 0,
            'lag_12': 0,
            'month_sin': np.sin(2 * np.pi * future_dates.month / 12),
            'month_cos': np.cos(2 * np.pi * future_dates.month / 12),
            'rate_of_change_1': 0,
            'np_prediction': np_baseline  # LAST! (as in training)
        })
        
        # Get XGBoost corrections
        xgb_residuals = xgb_model.predict(X_future)
        
        # Debug: Check XGB residuals
        print(f"   🔧 XGB residuals: {xgb_residuals.min():.1f} to {xgb_residuals.max():.1f}")
        
        # HYBRID PREDICTION (EXACT SAME AS TRAINING!)
        hybrid_predictions = np_baseline + xgb_residuals
        hybrid_predictions = np.maximum(hybrid_predictions, 0)  # Non-negative
        
        # Debug: Final prediction
        print(f"   ✅ Final prediction: {hybrid_predictions[0]:.1f} cases\n")
        
        return hybrid_predictions, future_dates
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        import traceback
        traceback.print_exc()
        return None, None

# ==============================================
# MODELS & DATA LOADING
# ==============================================

class RabiesAlertSystem:
    """
    Alert system for rabies forecasting based on municipality-specific thresholds.
    """
    
    # Municipality-specific thresholds (cases/month)
    THRESHOLDS = {
        'CITY OF ANTIPOLO': {'high': 50, 'medium': 30, 'low': 15},
        'TAYTAY': {'high': 30, 'medium': 20, 'low': 10},
        'CAINTA': {'high': 40, 'medium': 25, 'low': 12},
        'ANGONO': {'high': 35, 'medium': 20, 'low': 10}
    }
    
    # Dry season months (higher rabies risk)
    DRY_SEASON_MONTHS = [1, 2, 3, 4, 5]  # January-May
    
    def __init__(self, model_dir: str):
        """Initialize with model directory."""
        self.models = self.load_models(model_dir)
        print(f"✅ Loaded {len(self.models)} barangay models")
    
    def load_models(self, model_dir: str) -> Dict:
        """Load all saved models from directory."""
        loaded_models = {}
        
        # 🔥 UPDATED: Handle new model structure with timestamp folders
        # Check if model_dir has timestamp subdirectories
        if not os.path.exists(model_dir):
            print(f"❌ Model directory not found: {model_dir}")
            return loaded_models
        
        # Find the most recent trained_models folder
        timestamp_dirs = [d for d in os.listdir(model_dir) if d.startswith('trained_models_')]
        if timestamp_dirs:
            # Use most recent
            timestamp_dirs.sort(reverse=True)
            model_dir = os.path.join(model_dir, timestamp_dirs[0])
            print(f"📂 Using models from: {timestamp_dirs[0]}")
        
        # Load individual models
        for municipality_dir in os.listdir(model_dir):
            mun_path = os.path.join(model_dir, municipality_dir)
            
            if os.path.isdir(mun_path):
                for model_file in os.listdir(mun_path):
                    if model_file.endswith('.pkl'):
                        try:
                            with open(os.path.join(mun_path, model_file), 'rb') as f:
                                model_data = pickle.load(f)
                                key = f"{model_data['municipality']}_{model_data['barangay']}"
                                loaded_models[key] = model_data
                                # Debug: Print first 3 keys to verify format
                                if len(loaded_models) <= 3:
                                    print(f"   📝 Loaded: {key}")
                        except Exception as e:
                            print(f"⚠️ Failed to load {model_file}: {e}")
        
        return loaded_models
    
    def check_threshold_alert(self, municipality: str, predicted_cases: float) -> tuple:
        """Check if cases exceed thresholds."""
        thresholds = self.THRESHOLDS.get(municipality, self.THRESHOLDS['TAYTAY'])
        
        if predicted_cases > thresholds['high']:
            return "HIGH", f"🔴 CRITICAL: {predicted_cases:.0f} cases (>{thresholds['high']} threshold)"
        elif predicted_cases > thresholds['medium']:
            return "MEDIUM", f"🟡 WARNING: {predicted_cases:.0f} cases (>{thresholds['medium']} threshold)"
        elif predicted_cases > thresholds['low']:
            return "LOW", f"🟢 ADVISORY: {predicted_cases:.0f} cases (>{thresholds['low']} threshold)"
        else:
            return "NORMAL", f"✅ Normal: {predicted_cases:.0f} cases"
    
    def check_seasonal_surge(self, forecast_month: int, predicted_cases: float, historical_avg: float) -> tuple:
        """Detect seasonal surges."""
        is_dry_season = forecast_month in self.DRY_SEASON_MONTHS
        
        if is_dry_season and predicted_cases > historical_avg * 1.5:
            return True, "🌞 DRY-SEASON SURGE"
        elif not is_dry_season and predicted_cases > historical_avg * 2.0:
            return True, "⚠️ UNUSUAL SURGE"
        
        return False, "No surge"
    
    def generate_alerts(self, municipality: Optional[str] = None) -> List[Dict]:
        """Generate alerts for all or specific municipality."""
        alerts = []
        
        for key, model_data in self.models.items():
            mun = model_data['municipality']
            
            # Filter by municipality if specified
            if municipality and mun != municipality:
                continue
            
            barangay = model_data['barangay']
            
            # 🔥 NEW: Use live prediction for next month!
            predictions, forecast_dates = predict_future_months(model_data, num_months=1)
            
            if predictions is None:
                continue  # Skip if prediction failed
            
            predicted_cases = float(predictions[0])
            forecast_date = forecast_dates[0]
            forecast_month = forecast_date.month
            
            # Get historical average from training data
            # Check if we have the new model structure or old structure
            if 'train_predictions' in model_data:
                historical_avg = float(np.mean(model_data['train_actuals']))
            else:
                # Fallback for old model structure
                historical_avg = float(np.mean(model_data.get('actual_train', [10])))
            
            # Check alerts
            alert_level, threshold_msg = self.check_threshold_alert(mun, predicted_cases)
            is_surge, surge_msg = self.check_seasonal_surge(forecast_month, predicted_cases, historical_avg)
            
            # Only include if alert triggered
            if alert_level != "NORMAL" or is_surge:
                alerts.append({
                    'municipality': mun,
                    'barangay': barangay,
                    'forecast_date': pd.Timestamp(forecast_date).strftime('%Y-%m'),
                    'predicted_cases': round(predicted_cases, 1),
                    'historical_avg': round(historical_avg, 1),
                    'alert_level': alert_level,
                    'message': threshold_msg,
                    'seasonal_alert': surge_msg,
                    'model_mae': round(float(model_data.get('hybrid_mae', 0)), 2)
                })
        
        # Sort by severity
        severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        alerts.sort(key=lambda x: (severity_order.get(x['alert_level'], 3), -x['predicted_cases']))
        
        return alerts
    
    def get_municipality_summary(self) -> List[Dict]:
        """Get summary statistics per municipality."""
        summaries = {}
        
        for model_data in self.models.values():
            mun = model_data['municipality']
            
            if mun not in summaries:
                summaries[mun] = {
                    'municipality': mun,
                    'total_barangays': 0,
                    'total_predicted_cases': 0,
                    'avg_mae': [],
                    'high_alerts': 0,
                    'medium_alerts': 0,
                    'low_alerts': 0
                }
            
            summaries[mun]['total_barangays'] += 1
            
            # 🔥 NEW: Use live predictions
            predictions, _ = predict_future_months(model_data, num_months=1)
            if predictions is not None:
                predicted = float(predictions[0])
                summaries[mun]['total_predicted_cases'] += predicted
                
                # Count alerts
                level, _ = self.check_threshold_alert(mun, predicted)
                if level == "HIGH":
                    summaries[mun]['high_alerts'] += 1
                elif level == "MEDIUM":
                    summaries[mun]['medium_alerts'] += 1
                elif level == "LOW":
                    summaries[mun]['low_alerts'] += 1
            
            summaries[mun]['avg_mae'].append(float(model_data.get('hybrid_mae', 0)))
        
        # Calculate averages
        result = []
        for mun, data in summaries.items():
            result.append({
                'municipality': mun,
                'total_barangays': data['total_barangays'],
                'total_predicted_cases': round(data['total_predicted_cases'], 0),
                'avg_mae': round(np.mean(data['avg_mae']), 2),
                'high_alerts': data['high_alerts'],
                'medium_alerts': data['medium_alerts'],
                'low_alerts': data['low_alerts']
            })
        
        return result

# Initialize alert system
# 🔥 UPDATED: Point to new saved_models directory
MODEL_DIR = "../../saved_models_v2/FINALIZED_barangay_models_20251028_005355"
alert_system = RabiesAlertSystem(MODEL_DIR)

# ==============================================
# API ENDPOINTS
# ==============================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Rabies Alert System API",
        "status": "operational",
        "version": "1.0.0",
        "total_barangays": len(alert_system.models)
    }

@app.get("/api/alerts")
async def get_alerts(municipality: Optional[str] = None):
    """
    Get all active alerts.
    
    Query params:
        - municipality: Filter by specific municipality (optional)
    """
    try:
        alerts = alert_system.generate_alerts(municipality)
        return {
            "success": True,
            "count": len(alerts),
            "alerts": alerts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/municipalities")
async def get_municipalities():
    """Get summary statistics for all municipalities."""
    try:
        summaries = alert_system.get_municipality_summary()
        return {
            "success": True,
            "municipalities": summaries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/barangay/{municipality}/{barangay}")
async def get_barangay_details(municipality: str, barangay: str):
    """Get detailed forecast data for specific barangay."""
    try:
        key = f"{municipality}_{barangay}"
        
        if key not in alert_system.models:
            # Try to find similar keys for debugging
            similar_keys = [k for k in alert_system.models.keys() if municipality in k]
            print(f"❌ Key not found: {key}")
            print(f"   Available keys for {municipality}: {similar_keys[:5]}")
            raise HTTPException(status_code=404, detail=f"Barangay not found. Available: {similar_keys[:3]}")
        
        model_data = alert_system.models[key]
        
        # 🔥 FIX: Extract metrics from the correct fields
        # Your training saves these as: mae, rmse, mape, mase, r2
        metrics = {
            "mae": round(float(model_data.get('mae', model_data.get('hybrid_mae', 0))), 2),
            "rmse": round(float(model_data.get('rmse', model_data.get('hybrid_rmse', 0))), 2),
            "mape": round(float(model_data.get('mape', model_data.get('hybrid_mape', 0))), 2),
            "mase": round(float(model_data.get('mase', model_data.get('hybrid_mase', 0))), 3),
            "r2": round(float(model_data.get('r2', model_data.get('hybrid_r2', 0))), 3)
        }
        
        # 🔥 FIX: Get training and validation data
        train_series = []
        val_series = []
        
        # Check if we have the data arrays
        if 'train_dates' in model_data and 'train_actuals' in model_data:
            train_series = [
                {
                    "date": pd.Timestamp(d).strftime('%Y-%m'),
                    "actual": float(a),
                    "predicted": float(p)
                }
                for d, a, p in zip(
                    model_data['train_dates'],
                    model_data['train_actuals'],
                    model_data['train_predictions']
                )
            ]
        
        if 'dates' in model_data and 'actuals' in model_data:
            val_series = [
                {
                    "date": pd.Timestamp(d).strftime('%Y-%m'),
                    "actual": float(a),
                    "predicted": float(p)
                }
                for d, a, p in zip(
                    model_data['dates'],
                    model_data['actuals'],
                    model_data['predictions']
                )
            ]
        
        print(f"📊 {key}: metrics={metrics}, train_points={len(train_series)}, val_points={len(val_series)}")
        
        return {
            "success": True,
            "barangay": {
                "municipality": model_data['municipality'],
                "barangay": model_data['barangay'],
                "metrics": metrics,
                "training_data": train_series,
                "validation_data": val_series
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/thresholds")
async def get_thresholds():
    """Get municipality-specific alert thresholds."""
    return {
        "success": True,
        "thresholds": alert_system.THRESHOLDS
    }

@app.get("/api/forecast/{municipality}/{barangay}")
async def get_barangay_forecast(municipality: str, barangay: str, months: int = 6):
    """
    🔥 NEW: Get multi-month forecast for specific barangay.
    Uses the saved NeuralProphet + XGBoost models to predict future months.
    """
    try:
        key = f"{municipality}_{barangay}"
        
        if key not in alert_system.models:
            raise HTTPException(status_code=404, detail=f"Model not found for {municipality} - {barangay}")
        
        model_data = alert_system.models[key]
        
        # Predict next N months using the same method as training!
        predictions, forecast_dates = predict_future_months(model_data, num_months=months)
        
        if predictions is None:
            raise HTTPException(status_code=500, detail="Failed to generate forecast")
        
        # Format response
        forecast = []
        for date, pred in zip(forecast_dates, predictions):
            # Check alert level for this prediction
            alert_level, threshold_msg = alert_system.check_threshold_alert(municipality, float(pred))
            
            forecast.append({
                'date': date.strftime('%Y-%m'),
                'predicted_cases': round(float(pred), 1),
                'alert_level': alert_level,
                'alert_message': threshold_msg
            })
        
        return {
            'success': True,
            'municipality': municipality,
            'barangay': barangay,
            'training_end': model_data['training_end'].strftime('%Y-%m'),
            'forecast_months': months,
            'forecast': forecast,
            'model_mae': round(float(model_data.get('hybrid_mae', 0)), 2),
            'model_mase': round(float(model_data.get('hybrid_mase', 0)), 3)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Rabies Alert System API...")
    print(f"📊 Loaded {len(alert_system.models)} barangay models")
    print("🌐 API available at: http://localhost:8000")
    print("📖 Docs available at: http://localhost:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
