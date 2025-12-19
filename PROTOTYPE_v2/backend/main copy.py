# ==============================================
# RABIES FORECASTING DASHBOARD - FastAPI Backend
# ==============================================

import pickle
import os
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import ML libraries (required for unpickling)
from neuralprophet import NeuralProphet
import xgboost as xgb

# Initialize FastAPI
app = FastAPI(
    title="Rabies Forecasting Dashboard API",
    version="2.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================
# PREDICTION FUNCTIONS
# ==============================================

def extract_model_components(model_data):
    """
    Extract interpretability components from NeuralProphet and XGBoost models.
    Returns trend, seasonality, holidays, and feature importance data.
    """
    try:
        np_model = model_data['np_model']
        xgb_model = model_data['xgb_model']
        
        # Collect all historical dates and actual values
        dates_list = []
        actuals_list = []
        
        # Get training data
        if 'train_dates' in model_data and 'train_actuals' in model_data:
            train_dates = pd.to_datetime(model_data['train_dates'])
            train_actuals = model_data['train_actuals']
            dates_list.extend(train_dates)
            actuals_list.extend(train_actuals)
        
        # Get validation data
        if 'dates' in model_data and 'actuals' in model_data:
            val_dates = pd.to_datetime(model_data['dates'])
            val_actuals = model_data['actuals']
            dates_list.extend(val_dates)
            actuals_list.extend(val_actuals)
        
        if not dates_list:
            raise ValueError("No historical data available in model")
        
        # Create DataFrame with historical data (NeuralProphet needs 'ds' and 'y')
        df_components = pd.DataFrame({
            'ds': dates_list,
            'y': actuals_list
        })
        
        # Sort by date and remove duplicates
        df_components = df_components.drop_duplicates(subset=['ds']).sort_values('ds').reset_index(drop=True)
        
        # Get NeuralProphet components decomposition
        # This includes trend, seasonality patterns, AND holidays
        forecast_df = np_model.predict(df_components)
        
        # Debug: Print available columns
        print(f"🔍 NeuralProphet forecast columns: {forecast_df.columns.tolist()}")
        
        # Extract components
        components = {
            'trend': [],
            'yearly_seasonality': [],
            'holidays': [],  # NEW: Holiday effects
            'dates': []
        }
        
        # Find holiday column name (different NeuralProphet versions use different names)
        # NeuralProphet combines all holidays into 'events_additive' column
        holiday_col = None
        if 'events_additive' in forecast_df.columns:
            holiday_col = 'events_additive'
            print(f"✅ Found holiday column: {holiday_col}")
        else:
            # Fallback: look for any column with 'holiday' or 'event' in name
            for col in forecast_df.columns:
                if 'holiday' in col.lower() or ('event' in col.lower() and 'additive' in col.lower()):
                    holiday_col = col
                    print(f"✅ Found holiday column: {holiday_col}")
                    break
        
        for i in range(len(df_components)):
            date = df_components['ds'].iloc[i]
            components['dates'].append(date.strftime('%Y-%m'))
            
            # Trend component (try different column names)
            if 'trend' in forecast_df.columns:
                components['trend'].append(round(float(forecast_df['trend'].iloc[i]), 2))
            elif 'yhat1' in forecast_df.columns:
                # If no explicit trend, use the prediction itself
                components['trend'].append(round(float(forecast_df['yhat1'].iloc[i]), 2))
            else:
                components['trend'].append(0)
            
            # Yearly seasonality (if exists)
            # NeuralProphet might use different naming conventions
            season_col = None
            for col in ['season_yearly', 'seasonal_yearly', 'yearly', 'seasonality']:
                if col in forecast_df.columns:
                    season_col = col
                    break
            
            if season_col:
                components['yearly_seasonality'].append(round(float(forecast_df[season_col].iloc[i]), 2))
            else:
                # If no seasonality component, it might be 0 or not configured
                components['yearly_seasonality'].append(0)
            
            # Holiday effects (NEW!)
            if holiday_col:
                components['holidays'].append(round(float(forecast_df[holiday_col].iloc[i]), 2))
            else:
                components['holidays'].append(0)
        
        # XGBoost Feature Importance
        feature_names = [
            'Year', 'Month', 'lag_1', 'lag_2', 'rolling_mean_3',
            'rolling_std_3', 'lag_12', 'month_sin', 'month_cos',
            'rate_of_change_1', 'np_prediction'
        ]
        
        importance_scores = xgb_model.feature_importances_
        feature_importance = [
            {
                'feature': feature_names[i],
                'importance': round(float(importance_scores[i]), 4),
                'percentage': round(float(importance_scores[i] * 100), 2)
            }
            for i in range(len(feature_names))
        ]
        
        # Sort by importance
        feature_importance = sorted(feature_importance, key=lambda x: x['importance'], reverse=True)
        
        # Get changepoints (if available in NeuralProphet)
        changepoints = []
        if hasattr(np_model, 'config_trend') and hasattr(np_model, 'model'):
            # NeuralProphet stores changepoint dates internally
            # This is an approximation based on trend changes
            trend_values = components['trend']
            for i in range(1, len(trend_values) - 1):
                # Detect significant trend changes
                change = abs(trend_values[i] - trend_values[i-1])
                if change > np.std(trend_values) * 1.5:  # Significant change threshold
                    changepoints.append({
                        'date': components['dates'][i],
                        'value': trend_values[i]
                    })
        
        # Identify significant holiday effects WITH NAMES
        holiday_effects = []
        if components['holidays']:
            holiday_values = np.array(components['holidays'])
            
            # Get all individual event columns to identify which holiday occurred on each date
            event_columns = [col for col in forecast_df.columns if col.startswith('event_')]
            
            # Find dates where holiday effect is significant (non-zero or above threshold)
            for i, effect in enumerate(holiday_values):
                if abs(effect) > 0.1:  # Threshold for significant effect
                    # Find which holiday(s) occurred on this date
                    holiday_names = []
                    for event_col in event_columns:
                        if abs(forecast_df[event_col].iloc[i]) > 0.01:  # Holiday is active
                            # Extract holiday name from column (e.g., 'event_New Year's Day' -> 'New Year's Day')
                            holiday_name = event_col.replace('event_', '').replace('_', ' ')
                            holiday_names.append(holiday_name)
                    
                    # Combine multiple holidays with " + " if multiple occur on same date
                    holiday_label = ' + '.join(holiday_names) if holiday_names else 'Holiday'
                    
                    holiday_effects.append({
                        'date': components['dates'][i],
                        'holiday': holiday_label,
                        'effect': round(float(effect), 2),
                        'impact': 'Positive' if effect > 0 else 'Negative'
                    })
        
        # Check if holidays are configured
        has_holidays = holiday_col is not None
        
        return {
            'success': True,
            'components': components,
            'feature_importance': feature_importance,
            'changepoints': changepoints[:10],  # Limit to top 10 changepoints
            'holiday_effects': holiday_effects[:20],  # Top 20 significant holiday effects
            'has_holidays': has_holidays,
            'model_info': {
                'neuralprophet_changepoint_prior_scale': getattr(np_model.config_trend, 'changepoints_range', 'N/A'),
                'xgboost_n_estimators': xgb_model.n_estimators if hasattr(xgb_model, 'n_estimators') else 'N/A',
                'xgboost_max_depth': xgb_model.max_depth if hasattr(xgb_model, 'max_depth') else 'N/A',
                'holidays_configured': 'Yes' if has_holidays else 'No'
            }
        }
    
    except Exception as e:
        print(f"❌ Component extraction error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'components': {'trend': [], 'yearly_seasonality': [], 'holidays': [], 'dates': []},
            'feature_importance': [],
            'changepoints': [],
            'holiday_effects': [],
            'has_holidays': False
        }


def predict_next_month(model_data):
    """Predict next month using saved models."""
    try:
        np_model = model_data['np_model']
        xgb_model = model_data['xgb_model']
        training_end = model_data['training_end']
        
        # Generate next month date
        next_month = training_end + pd.DateOffset(months=1)
        future_df = pd.DataFrame({'ds': [next_month], 'y': [0]})
        
        # Get NeuralProphet prediction
        np_forecast = np_model.predict(future_df)
        np_baseline = np_forecast['yhat1'].values[0]
        
        # Prepare XGBoost features (EXACT order as training)
        X_future = pd.DataFrame({
            'Year': [next_month.year],
            'Month': [next_month.month],
            'lag_1': [0],
            'lag_2': [0],
            'rolling_mean_3': [0],
            'rolling_std_3': [0],
            'lag_12': [0],
            'month_sin': [np.sin(2 * np.pi * next_month.month / 12)],
            'month_cos': [np.cos(2 * np.pi * next_month.month / 12)],
            'rate_of_change_1': [0],
            'np_prediction': [np_baseline]
        })
        
        # Get XGBoost correction
        xgb_residual = xgb_model.predict(X_future)[0]
        
        # Hybrid prediction
        hybrid_pred = max(0, np_baseline + xgb_residual)
        
        return hybrid_pred
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return None


def predict_future_months(model_data, months_ahead=12):
    """
    Predict multiple months into the future.
    Returns list of predictions with dates.
    """
    try:
        np_model = model_data['np_model']
        xgb_model = model_data['xgb_model']
        validation_end = model_data.get('validation_end', model_data['training_end'])
        
        # Start predictions from validation end + 1 month
        start_date = validation_end + pd.DateOffset(months=1)
        
        # Generate future dates TEMPLATE
        future_dates = pd.date_range(start=start_date, periods=months_ahead, freq='MS')
        future_df = pd.DataFrame({'ds': future_dates, 'y': [0] * months_ahead})
        
        # Get NeuralProphet predictions for all future dates
        np_forecast = np_model.predict(future_df)
        np_predictions = np_forecast['yhat1'].values
        


        # XGBOOST PHASE
        # Prepare features for each future month
        predictions = []
        for i, future_date in enumerate(future_dates):
            # Prepare XGBoost features
            # ITO YUNG NASA FEATURE IMPORTANCE! so feed np_prediction here!
            X_future = pd.DataFrame({
                'Year': [future_date.year],
                'Month': [future_date.month],
                'lag_1': [0],  # In real scenario, use last prediction
                'lag_2': [0],
                'rolling_mean_3': [0],
                'rolling_std_3': [0],
                'lag_12': [0],
                'month_sin': [np.sin(2 * np.pi * future_date.month / 12)],
                'month_cos': [np.cos(2 * np.pi * future_date.month / 12)],
                'rate_of_change_1': [0],
                'np_prediction': [np_predictions[i]]
            })
            
            # Get XGBoost correction
            xgb_residual = xgb_model.predict(X_future)[0]
            
            # Hybrid prediction
            hybrid_pred = max(0, float(np_predictions[i] + xgb_residual))
            
            predictions.append({
                'date': future_date.strftime('%Y-%m'),
                'predicted': round(hybrid_pred, 1)
            })
        
        return predictions
    except Exception as e:
        print(f"❌ Future prediction error: {e}")
        return []

# ==============================================
# LOAD MODELS
# ==============================================
#MODEL_DIR = "../../saved_models_v2/FINALIZED_barangay_models_20251031_140501"
MODEL_DIR = "../../saved_models_v2/AFINALIZED_barangay_models_20251103_002104"
#lightGbm prophet\DONT DEELTE THESE FILES\saved_models_v2\AFINALIZED_barangay_models_20251103_002104

def load_all_models():
    """Load all barangay models."""
    models = {}
    
    if not os.path.exists(MODEL_DIR):
        print(f"❌ Model directory not found: {MODEL_DIR}")
        return models
    
    print(f"📂 Loading models from: {MODEL_DIR}")
    
    # 🔥 FIX: Handle both flat and nested directory structures
    for first_level in os.listdir(MODEL_DIR):
        first_path = os.path.join(MODEL_DIR, first_level)
        
        if os.path.isdir(first_path):
            # Check if there are .pkl files directly here
            pkl_files = [f for f in os.listdir(first_path) if f.endswith('.pkl')]
            
            if pkl_files:
                # Flat structure: MODEL_DIR/MUNICIPALITY/*.pkl
                for model_file in pkl_files:
                    try:
                        with open(os.path.join(first_path, model_file), 'rb') as f:
                            model_data = pickle.load(f)
                            
                            municipality = model_data['municipality']
                            barangay = model_data['barangay']
                            key = f"{municipality}_{barangay}"
                            
                            models[key] = model_data
                            
                    except Exception as e:
                        print(f"⚠️ Failed to load {model_file}: {e}")
            else:
                # Nested structure: MODEL_DIR/EXTRA_FOLDER/MUNICIPALITY/*.pkl
                for second_level in os.listdir(first_path):
                    second_path = os.path.join(first_path, second_level)
                    
                    if os.path.isdir(second_path):
                        for model_file in os.listdir(second_path):
                            if model_file.endswith('.pkl'):
                                try:
                                    with open(os.path.join(second_path, model_file), 'rb') as f:
                                        model_data = pickle.load(f)
                                        
                                        municipality = model_data['municipality']
                                        barangay = model_data['barangay']
                                        key = f"{municipality}_{barangay}"
                                        
                                        models[key] = model_data
                                        
                                except Exception as e:
                                    print(f"⚠️ Failed to load {model_file}: {e}")
    
    print(f"✅ Loaded {len(models)} barangay models\n")
    return models

# Load models on startup
MODELS = load_all_models()

# ==============================================
# API ENDPOINTS
# ==============================================

@app.get("/")
async def root():
    """Health check."""
    return {
        "status": "operational",
        "version": "2.1.0",
        "models_loaded": len(MODELS),
        "features": ["forecasting", "risk_assessment", "model_interpretability"]
    }

def calculate_risk_level(model_data, forecast_months=8):
    """Calculate risk level based on historical data and forecast."""
    try:
        # Get historical validation data
        if 'actuals' not in model_data or len(model_data['actuals']) == 0:
            return 'UNKNOWN', '#666666', '⚪'
        
        actuals = np.array(model_data['actuals'])
        historical_avg = float(np.mean(actuals))
        historical_max = float(np.max(actuals))
        
        # Get future forecast (8 months)
        future_predictions = predict_future_months(model_data, months_ahead=forecast_months)
        if not future_predictions:
            return 'UNKNOWN', '#666666', '⚪'
        
        forecast_avg = np.mean([p['predicted'] for p in future_predictions])
        
        # Risk thresholds
        max_threshold = historical_max * 0.8  # 80% of historical max
        avg_threshold = historical_avg * 1.2  # 20% above average
        
        # Determine risk level
        if forecast_avg > max_threshold:
            return 'HIGH', '#d32f2f', '🔴'
        elif forecast_avg > avg_threshold:
            return 'MEDIUM', '#f57c00', '🟡'
        else:
            return 'LOW', '#388e3c', '🟢'
    except Exception as e:
        print(f"Risk calculation error: {e}")
        return 'UNKNOWN', '#666666', '⚪'


@app.get("/api/municipalities")
async def get_municipalities():
    """Get list of municipalities with summary stats and risk levels."""
    summaries = {}
    
    print("🔄 Calculating risk levels for all barangays...")
    
    for key, model_data in MODELS.items():
        mun = model_data['municipality']
        
        if mun not in summaries:
            summaries[mun] = {
                'municipality': mun,
                'barangays': [],
                'total_barangays': 0,
                'avg_mae': [],
                'risk_counts': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            }
        
        # Convert numpy types to Python native types
        mae_value = model_data.get('mae', 0)
        if hasattr(mae_value, 'item'):  # numpy type
            mae_value = mae_value.item()
        
        pred_value = predict_next_month(model_data) or 0
        if hasattr(pred_value, 'item'):  # numpy type
            pred_value = pred_value.item()
        
        # Calculate risk level
        risk_level, risk_color, risk_icon = calculate_risk_level(model_data, forecast_months=8)
        
        barangay_info = {
            'name': str(model_data['barangay']),
            'mae': round(float(mae_value), 2),
            'predicted_next': round(float(pred_value), 1),
            'risk_level': risk_level,
            'risk_color': risk_color,
            'risk_icon': risk_icon
        }
        
        summaries[mun]['barangays'].append(barangay_info)
        summaries[mun]['total_barangays'] += 1
        summaries[mun]['avg_mae'].append(barangay_info['mae'])
        
        # Count risk levels
        if risk_level in summaries[mun]['risk_counts']:
            summaries[mun]['risk_counts'][risk_level] += 1
    
    # Calculate averages
    result = []
    for mun, data in summaries.items():
        avg_mae = float(np.mean(data['avg_mae']))
        result.append({
            'municipality': str(mun),
            'barangays': sorted(data['barangays'], key=lambda x: x['predicted_next'], reverse=True),
            'total_barangays': int(data['total_barangays']),
            'avg_mae': round(avg_mae, 2),
            'risk_summary': data['risk_counts']
        })
    
    print(f"✅ Risk levels calculated for {len(MODELS)} barangays\n")
    return {"success": True, "municipalities": result}

@app.get("/api/barangay/{municipality}/{barangay}")
async def get_barangay_details(municipality: str, barangay: str):
    """Get detailed data for specific barangay."""
    key = f"{municipality}_{barangay}"
    
    if key not in MODELS:
        raise HTTPException(status_code=404, detail=f"Barangay not found: {key}")
    
    model_data = MODELS[key]
    
    # Helper function to convert numpy to Python types
    def to_python_type(value):
        if hasattr(value, 'item'):  # numpy type
            return value.item()
        return value
    
    # Extract metrics with proper type conversion
    # Try different metric key variations
    print(f"\n🔍 DEBUG: Looking for metrics in model_data keys: {list(model_data.keys())}")
    
    # The model uses 'hybrid_mae' and 'hybrid_mase'
    metrics = {
        'mae': round(float(to_python_type(
            model_data.get('hybrid_mae', model_data.get('val_mae', model_data.get('mae', 0)))
        )), 2),
        'rmse': round(float(to_python_type(
            model_data.get('hybrid_rmse', model_data.get('val_rmse', model_data.get('rmse', 0)))
        )), 2),
        'mape': round(float(to_python_type(
            model_data.get('hybrid_mape', model_data.get('val_mape', model_data.get('mape', 0)))
        )), 2),
        'r2': round(float(to_python_type(
            model_data.get('hybrid_r2', model_data.get('val_r2', model_data.get('r2', 0)))
        )), 3),
        'mase': round(float(to_python_type(
            model_data.get('hybrid_mase', model_data.get('val_mase', model_data.get('mase', 0)))
        )), 3)
    }
    
    print(f"📊 Extracted metrics: {metrics}")
    
    # Extract training data
    train_data = []
    if 'train_dates' in model_data:
        for i in range(len(model_data['train_dates'])):
            train_data.append({
                'date': pd.Timestamp(model_data['train_dates'][i]).strftime('%Y-%m'),
                'actual': float(to_python_type(model_data['train_actuals'][i])),
                'predicted': float(to_python_type(model_data['train_predictions'][i]))
            })
    
    print(f"📈 Training data points: {len(train_data)}")
    if train_data:
        print(f"   Sample: {train_data[0]}")
    
    # Extract validation data
    val_data = []
    if 'dates' in model_data:
        for i in range(len(model_data['dates'])):
            val_data.append({
                'date': pd.Timestamp(model_data['dates'][i]).strftime('%Y-%m'),
                'actual': float(to_python_type(model_data['actuals'][i])),
                'predicted': float(to_python_type(model_data['predictions'][i]))
            })
    
    print(f"📉 Validation data points: {len(val_data)}")
    if val_data:
        print(f"   Sample: {val_data[0]}")
    
    # Get next month prediction
    next_pred = predict_next_month(model_data)
    
    response = {
        'success': True,
        'barangay': {
            'municipality': str(model_data['municipality']),
            'barangay': str(model_data['barangay']),
            'metrics': metrics,
            'training_data': train_data,
            'validation_data': val_data,
            'next_month_prediction': round(float(to_python_type(next_pred)), 1) if next_pred else None,
            'has_chart_data': len(train_data) > 0 or len(val_data) > 0
        }
    }
    
    print(f"✅ Returning response with chart data: {response['barangay']['has_chart_data']}\n")
    return response

@app.get("/api/forecast/{municipality}/{barangay}")
async def get_future_forecast(municipality: str, barangay: str, months: int = 8):
    """
    Get future forecasts for a specific barangay.
    Predicts up to 'months' months into the future (default: 8 months for safer approach).
    """
    key = f"{municipality}_{barangay}"
    
    if key not in MODELS:
        raise HTTPException(status_code=404, detail=f"Barangay not found: {key}")
    
    model_data = MODELS[key]
    
    # Validate months parameter
    if months < 1 or months > 24:
        raise HTTPException(status_code=400, detail="Months must be between 1 and 24")
    
    # Get future predictions
    future_predictions = predict_future_months(model_data, months_ahead=months)
    
    if not future_predictions:
        raise HTTPException(status_code=500, detail="Failed to generate predictions")
    
    # Get validation end date for context
    validation_end = model_data.get('validation_end', model_data['training_end'])
    
    print(f"🔮 Generated {len(future_predictions)} future predictions for {barangay}, {municipality}")
    
    return {
        'success': True,
        'forecast': {
            'municipality': str(model_data['municipality']),
            'barangay': str(model_data['barangay']),
            'validation_end': validation_end.strftime('%Y-%m'),
            'forecast_start': future_predictions[0]['date'] if future_predictions else None,
            'forecast_end': future_predictions[-1]['date'] if future_predictions else None,
            'predictions': future_predictions
        }
    }

@app.get("/api/interpretability/{municipality}/{barangay}")
async def get_model_interpretability(municipality: str, barangay: str):
    """
    Get model interpretability data including:
    - Trend decomposition
    - Seasonality patterns
    - Feature importance from XGBoost
    - Changepoints detection
    
    This helps understand HOW the model makes predictions (not a black box!)
    """
    key = f"{municipality}_{barangay}"
    
    if key not in MODELS:
        raise HTTPException(status_code=404, detail=f"Barangay not found: {key}")
    
    model_data = MODELS[key]
    
    print(f"🔍 Extracting interpretability components for {barangay}, {municipality}...")
    
    # Extract all interpretability components
    interpretability_data = extract_model_components(model_data)
    
    if not interpretability_data['success']:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to extract model components: {interpretability_data.get('error', 'Unknown error')}"
        )
    
    response = {
        'success': True,
        'interpretability': {
            'municipality': str(model_data['municipality']),
            'barangay': str(model_data['barangay']),
            
            # Time series decomposition
            'trend': {
                'dates': interpretability_data['components']['dates'],
                'values': interpretability_data['components']['trend'],
                'description': 'Long-term direction of rabies cases (upward/downward pattern)'
            },
            
            'seasonality': {
                'dates': interpretability_data['components']['dates'],
                'values': interpretability_data['components']['yearly_seasonality'],
                'description': 'Recurring yearly patterns (e.g., higher cases in certain months)'
            },
            
            # Holiday effects (NEW!)
            'holidays': {
                'dates': interpretability_data['components']['dates'],
                'values': interpretability_data['components']['holidays'],
                'description': 'Philippine public holiday effects on rabies cases',
                'significant_effects': interpretability_data['holiday_effects'],
                'has_holidays': interpretability_data['has_holidays']
            },
            
            # Feature importance from XGBoost
            'feature_importance': {
                'features': interpretability_data['feature_importance'],
                'description': 'Which factors contribute most to predictions',
                'top_3_features': interpretability_data['feature_importance'][:3]
            },
            
            # Changepoints
            'changepoints': {
                'points': interpretability_data['changepoints'],
                'description': 'Dates where the trend significantly changed (e.g., policy changes, outbreaks)'
            },
            
            # Model configuration info
            'model_config': interpretability_data['model_info']
        }
    }
    
    print(f"✅ Interpretability data extracted successfully")
    print(f"   - Trend points: {len(interpretability_data['components']['trend'])}")
    print(f"   - Seasonality points: {len(interpretability_data['components']['yearly_seasonality'])}")
    print(f"   - Holiday points: {len(interpretability_data['components']['holidays'])}")
    print(f"   - Holidays configured: {interpretability_data['has_holidays']}")
    print(f"   - Significant holiday effects: {len(interpretability_data['holiday_effects'])}")
    print(f"   - Feature importance: {len(interpretability_data['feature_importance'])} features")
    print(f"   - Changepoints detected: {len(interpretability_data['changepoints'])}\n")
    
    return response

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Rabies Forecasting Dashboard API...")
    print(f"📊 Loaded {len(MODELS)} models")
    print("🌐 API: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
