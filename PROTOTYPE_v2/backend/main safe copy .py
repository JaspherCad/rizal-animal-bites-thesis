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
from fastapi.responses import StreamingResponse, FileResponse
import io
from io import BytesIO

# Import ML libraries (required for unpickling)
from neuralprophet import NeuralProphet
import xgboost as xgb

# Initialize FastAPI
app = FastAPI(
    title="Rabies Forecasting Dashboard API",
    version="2.1.0"
)

print(1)  # 🧪 TEST: Copilot can edit Python code!

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================
# FEATURE ENGINEERING FOR MUNICIPALITIES
# ==============================================

def add_cainta_seasonal_features(df):
    """Add CAINTA-specific seasonal patterns"""
    df = df.copy()
    
    # MAY PEAK: May is consistently highest across all years
    df['may_peak'] = (df['ds'].dt.month == 5).astype(int)
    
    # LOW SEASON: Jan-Feb-March-April consistently lowest
    df['low_season'] = ((df['ds'].dt.month >= 1) & (df['ds'].dt.month <= 4)).astype(int)
    
    # SPRING RAMP-UP: March-April-May increasing pattern
    df['spring_ramp'] = ((df['ds'].dt.month >= 3) & (df['ds'].dt.month <= 5)).astype(int)
    
    # HOLIDAY EFFECT: January specifically (New Year impact)
    df['january_holiday'] = (df['ds'].dt.month == 1).astype(int)
    
    # POST-MAY DECLINE: June onwards typically lower than May
    df['post_may_decline'] = ((df['ds'].dt.month >= 6) & (df['ds'].dt.month <= 12)).astype(int)
    
    return df


def add_angono_seasonal_features(df):
    """Add ANGONO-specific seasonal patterns as binary features"""
    df = df.copy()
    
    # HIGH SEASON: April-May-June (consistently high across 2022-2025)
    df['high_season'] = df['ds'].dt.month.isin([4, 5, 6]).astype(int)
    
    # JULY DIP: Always drops after high season
    df['july_dip'] = (df['ds'].dt.month == 7).astype(int)
    
    # AUGUST RISE: Increases again after July dip
    df['august_rise'] = (df['ds'].dt.month == 8).astype(int)
    
    # LOW SEASON: December-January (consistently lowest)
    df['low_season'] = df['ds'].dt.month.isin([12, 1]).astype(int)
    
    # POST-APRIL 2024 REGIME: Higher volatility period
    df['post_april_2024'] = (df['ds'] >= pd.Timestamp('2024-04-01')).astype(int)
    
    return df

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
        municipality = model_data.get('municipality', '')  # 🆕 Get municipality for seasonal features
        
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

        
        
        # 🆕 ADD WEATHER REGRESSORS WITH ACTUAL HISTORICAL VALUES
        weather_cols = model_data.get('regressors', {}).get('weather', [])
        weather_data = model_data.get('weather_data', {})
        if weather_cols:
            print(f"   🌤️ Adding {len(weather_cols)} weather columns for component extraction")
            if weather_data:
                # Use actual historical weather values
                for col in weather_cols:
                    if col in weather_data and len(weather_data[col]) == len(df_components):
                        df_components[col] = weather_data[col]
                        print(f"      ✅ {col}: Using historical values (mean={np.mean(weather_data[col]):.2f})")
                    else:
                        df_components[col] = 0.0  # Fallback to neutral
                        print(f"      ⚠️ {col}: No data available, using neutral values")
            else:
                # Fallback: use neutral values (shouldn't happen with retrained models)
                for col in weather_cols:
                    df_components[col] = 0.0
                print(f"      ⚠️ No historical weather data saved in model, using neutral values")
        
        # 🆕 ADD VACCINATION REGRESSORS WITH ACTUAL HISTORICAL VALUES
        municipality = model_data.get('municipality', '')
        vax_cols = model_data.get('regressors', {}).get('vaccination', [])
        vaccination_data = model_data.get('vaccination_data', {})
        if vax_cols and municipality == "CITY OF ANTIPOLO":
            print(f"   💉 Adding {len(vax_cols)} vaccination columns for component extraction")
            if vaccination_data:
                # Use actual historical vaccination campaign data
                for col in vax_cols:
                    if col in vaccination_data and len(vaccination_data[col]) == len(df_components):
                        df_components[col] = vaccination_data[col]
                        active_months = sum(vaccination_data[col])
                        print(f"      ✅ {col}: Using historical values ({active_months} active months)")
                    else:
                        df_components[col] = 0
                        print(f"      ⚠️ {col}: No data available, using neutral values")
            else:
                # Fallback: use neutral values
                for col in vax_cols:
                    df_components[col] = 0
                print(f"      ⚠️ No historical vaccination data saved in model, using neutral values")
        else:
            # DEBUG: Check if vaccination data exists in a different format
            if municipality == "CITY OF ANTIPOLO":
                print(f"   ⚠️ ANTIPOLO detected but no vaccination regressors found in metadata")
                print(f"   📋 Regressor metadata: {model_data.get('regressors', {})}")
        
        # 🆕 ADD SEASONAL REGRESSORS WITH ACTUAL HISTORICAL VALUES
        seasonal_cols = model_data.get('regressors', {}).get('seasonal', [])
        seasonal_data = model_data.get('seasonal_data', {})
        
        # 🔥 CRITICAL: Always add seasonal features for CAINTA/ANGONO (even if not in metadata)
        if municipality == "CAINTA":
            print(f"   🎯 Adding CAINTA seasonal features for component extraction")
            df_components = add_cainta_seasonal_features(df_components)
            print(f"      ✅ CAINTA features added: {['may_peak', 'low_season', 'spring_ramp', 'january_holiday', 'post_may_decline']}")
        elif municipality == "ANGONO":
            print(f"   🎯 Adding ANGONO seasonal features for component extraction")
            df_components = add_angono_seasonal_features(df_components)
            print(f"      ✅ ANGONO features added: {['high_season', 'july_dip', 'august_rise', 'low_season', 'post_april_2024']}")
        elif seasonal_cols:
            # For other municipalities with seasonal regressors in metadata
            print(f"   🎯 Adding {len(seasonal_cols)} seasonal columns for component extraction")
            if seasonal_data:
                # Use actual historical seasonal pattern data
                for col in seasonal_cols:
                    if col in seasonal_data and len(seasonal_data[col]) == len(df_components):
                        df_components[col] = seasonal_data[col]
                        active_months = sum(seasonal_data[col])
                        print(f"      ✅ {col}: Using historical values ({active_months} active months)")
                    else:
                        df_components[col] = 0
                        print(f"      ⚠️ {col}: No data available, using neutral values")
            else:
                for col in seasonal_cols:
                    df_components[col] = 0
                    print(f"      ⚠️ {col}: No data, using zeros")
        
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
            'weather_regressors': {},  # 🆕 Weather contributions
            'vaccination_regressors': {},  # 🆕 Vaccination campaign contributions
            'seasonal_regressors': {},  # 🆕 Custom seasonal features
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
        
        # 🆕 Get regressor metadata from saved model
        weather_cols = model_data.get('regressors', {}).get('weather', [])
        vax_cols = model_data.get('regressors', {}).get('vaccination', [])
        seasonal_cols = model_data.get('regressors', {}).get('seasonal', [])
        
        print(f"   🔍 Extracting regressors: Weather={len(weather_cols)}, Vaccination={len(vax_cols)}, Seasonal={len(seasonal_cols)}")
        
        # 🆕 Initialize regressor arrays
        for col in weather_cols:
            components['weather_regressors'][col] = []
        for col in vax_cols:
            components['vaccination_regressors'][col] = []
        for col in seasonal_cols:
            components['seasonal_regressors'][col] = []
        
        # 🔍 DEBUG: Check which regressor columns exist in forecast
        regressor_columns_found = [col for col in forecast_df.columns if 'future_regressor_' in col or 'season_' in col]
        if regressor_columns_found:
            print(f"   📊 Regressor columns in forecast: {regressor_columns_found[:10]}...")  # Show first 10
        
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
            
            # 🆕 Extract WEATHER regressor contributions
            # NeuralProphet stores regressor contributions as 'future_regressor_{regressor_name}'
            for col in weather_cols:
                regressor_col = f'future_regressor_{col}'
                if regressor_col in forecast_df.columns:
                    components['weather_regressors'][col].append(round(float(forecast_df[regressor_col].iloc[i]), 2))
                else:
                    # Try alternative naming: 'season_{col}'
                    alt_col = f'season_{col}'
                    if alt_col in forecast_df.columns:
                        components['weather_regressors'][col].append(round(float(forecast_df[alt_col].iloc[i]), 2))
                    else:
                        components['weather_regressors'][col].append(0.0)
            
            # 🆕 Extract VACCINATION regressor contributions
            for col in vax_cols:
                regressor_col = f'future_regressor_{col}'
                if regressor_col in forecast_df.columns:
                    components['vaccination_regressors'][col].append(round(float(forecast_df[regressor_col].iloc[i]), 2))
                else:
                    # Try alternative naming
                    alt_col = f'season_{col}'
                    if alt_col in forecast_df.columns:
                        components['vaccination_regressors'][col].append(round(float(forecast_df[alt_col].iloc[i]), 2))
                    else:
                        components['vaccination_regressors'][col].append(0.0)
            
            # 🆕 Extract SEASONAL regressor contributions
            for col in seasonal_cols:
                regressor_col = f'future_regressor_{col}'
                if regressor_col in forecast_df.columns:
                    components['seasonal_regressors'][col].append(round(float(forecast_df[regressor_col].iloc[i]), 2))
                else:
                    # Try alternative naming
                    alt_col = f'season_{col}'
                    if alt_col in forecast_df.columns:
                        components['seasonal_regressors'][col].append(round(float(forecast_df[alt_col].iloc[i]), 2))
                    else:
                        components['seasonal_regressors'][col].append(0.0)
        
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
            'regressor_metadata': model_data.get('regressors', {}),  # 🆕 Regressor metadata
            'model_info': {
                'neuralprophet_changepoint_prior_scale': getattr(np_model.config_trend, 'changepoints_range', 'N/A'),
                'xgboost_n_estimators': xgb_model.n_estimators if hasattr(xgb_model, 'n_estimators') else 'N/A',
                'xgboost_max_depth': xgb_model.max_depth if hasattr(xgb_model, 'max_depth') else 'N/A',
                'holidays_configured': 'Yes' if has_holidays else 'No',
                'weather_regressors_count': len(model_data.get('regressors', {}).get('weather', [])),  # 🆕
                'vaccination_regressors_count': len(model_data.get('regressors', {}).get('vaccination', [])),  # 🆕
                'seasonal_regressors_count': len(model_data.get('regressors', {}).get('seasonal', []))  # 🆕
            }
        }
    
    except Exception as e:
        print(f"❌ Component extraction error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'components': {
                'trend': [], 
                'yearly_seasonality': [], 
                'holidays': [], 
                'weather_regressors': {},  # 🆕
                'vaccination_regressors': {},  # 🆕
                'seasonal_regressors': {},  # 🆕
                'dates': []
            },
            'feature_importance': [],
            'changepoints': [],
            'holiday_effects': [],
            'has_holidays': False,
            'regressor_metadata': {}  # 🆕
        }


def predict_next_month(model_data):
    """Predict next month using saved models."""
    try:
        np_model = model_data['np_model']
        xgb_model = model_data['xgb_model']
        training_end = model_data['training_end']
        municipality = model_data.get('municipality', '')
        
        # Generate next month date
        next_month = training_end + pd.DateOffset(months=1)
        future_df = pd.DataFrame({'ds': [next_month], 'y': [0]})
        
        # 🆕 ADD WEATHER REGRESSORS (if model was trained with them)
        weather_cols = model_data.get('regressors', {}).get('weather', [])
        if weather_cols:
            for col in weather_cols:
                future_df[col] = 0.0  # Neutral weather impact
        
        # 🆕 ADD VACCINATION REGRESSORS (if model was trained with them)
        vax_cols = model_data.get('regressors', {}).get('vaccination', [])
        if vax_cols and municipality == "CITY OF ANTIPOLO":
            for col in vax_cols:
                future_df[col] = 0  # No active campaign
        
        # 🆕 ADD MUNICIPALITY-SPECIFIC SEASONAL FEATURES
        if municipality == "CAINTA":
            future_df = add_cainta_seasonal_features(future_df)
            print(f"   🎯 Added CAINTA seasonal features for prediction")
        elif municipality == "ANGONO":
            future_df = add_angono_seasonal_features(future_df)
            print(f"   🎯 Added ANGONO seasonal features for prediction")
        
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
        municipality = model_data.get('municipality', '')
        
        # Start predictions from validation end + 1 month
        start_date = validation_end + pd.DateOffset(months=1)
        
        # Generate future dates TEMPLATE
        future_dates = pd.date_range(start=start_date, periods=months_ahead, freq='MS')
        future_df = pd.DataFrame({'ds': future_dates, 'y': [0] * months_ahead})
        
        # 🆕 ADD WEATHER REGRESSORS (if model was trained with them)
        weather_cols = model_data.get('regressors', {}).get('weather', [])
        if weather_cols:
            print(f"   🌤️ Adding {len(weather_cols)} weather regressors for future prediction")
            # Use mean values from training data as defaults for future weather
            # In production, you'd use actual weather forecasts or historical averages
            for col in weather_cols:
                future_df[col] = 0.0  # Neutral impact (you can replace with historical means)
        
        # 🆕 ADD VACCINATION REGRESSORS (if model was trained with them - ANTIPOLO only)
        vax_cols = model_data.get('regressors', {}).get('vaccination', [])
        if vax_cols and municipality == "CITY OF ANTIPOLO":
            print(f"   💉 Adding {len(vax_cols)} vaccination regressors for future prediction")
            # Set to 0 (no active campaign) unless you want to simulate future campaigns
            for col in vax_cols:
                future_df[col] = 0  # No vaccination campaign by default
        
        # 🆕 ADD MUNICIPALITY-SPECIFIC SEASONAL FEATURES
        if municipality == "CAINTA":
            future_df = add_cainta_seasonal_features(future_df)
            print(f"   🎯 Added CAINTA seasonal features for future prediction")
        elif municipality == "ANGONO":
            future_df = add_angono_seasonal_features(future_df)
            print(f"   🎯 Added ANGONO seasonal features for future prediction")
        
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
        import traceback
        traceback.print_exc()
        return []

# ==============================================
# LOAD MODELS  Latest_FINALIZED_barangay_models_20251207_170009 STABLEST
#Latest_FINALIZED_barangay_models_20251223_110351 == DO NOT HAVE FUTURE REGRESSORS (cainta/angono non)
# ==============================================
MODEL_DIR = "../../saved_models_v2/Latest_FINALIZED_barangay_models_20251227_040907"
# MODEL_DIR = "../../saved_models_v2/Latest_FINALIZED_barangay_models_20251207_142420"
# MODEL_DIR = "../../saved_models_v2/AFINALIZED_barangay_models_20251103_002104"


def load_all_models():
    """Load all barangay models."""
    models = {}
    
    if not os.path.exists(MODEL_DIR):
        print(f"❌ Model directory not found: {MODEL_DIR}")
        return models
    
    print(f"📂 Loading models from: {MODEL_DIR}")
    
    for municipality_dir in os.listdir(MODEL_DIR):
        mun_path = os.path.join(MODEL_DIR, municipality_dir)
        
        if os.path.isdir(mun_path):
            for model_file in os.listdir(mun_path):
                if model_file.endswith('.pkl'):
                    try:
                        with open(os.path.join(mun_path, model_file), 'rb') as f:
                            model_data = pickle.load(f)
                            
                            municipality = model_data['municipality']
                            barangay = model_data['barangay']
                            key = f"{municipality}_{barangay}"
                            
                            # 🆕 DEBUG: Print regressor metadata for ANTIPOLO
                            if municipality == "CITY OF ANTIPOLO":
                                regressors = model_data.get('regressors', {})
                                print(f"   🔍 {barangay}: Weather={len(regressors.get('weather', []))}, Vax={len(regressors.get('vaccination', []))}, Seasonal={len(regressors.get('seasonal', []))}")
                            
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
    """
    Calculate risk level based on RECENT historical data (past 8 months) vs future forecast.
    Compares next 8 months forecast against past 8 months actual data (8-to-8 comparison).
    """
    try:
        # Get historical validation data
        if 'actuals' not in model_data or len(model_data['actuals']) == 0:
            return 'UNKNOWN', '#666666', '⚪'
        
        actuals = np.array(model_data['actuals'])
        
        # 🆕 USE ONLY PAST 8 MONTHS (or all available if less than 8)
        recent_months = min(8, len(actuals))
        recent_actuals = actuals[-recent_months:]  # Last 8 months
        
        recent_avg = float(np.mean(recent_actuals))
        recent_max = float(np.max(recent_actuals))
        
        print(f"   📊 Risk calculation: Using past {recent_months} months (avg={recent_avg:.1f}, max={recent_max:.1f})")
        
        # Get future forecast (8 months)
        future_predictions = predict_future_months(model_data, months_ahead=forecast_months)
        if not future_predictions:
            return 'UNKNOWN', '#666666', '⚪'
        
        forecast_avg = np.mean([p['predicted'] for p in future_predictions])
        
        print(f"   🔮 Next {forecast_months} months forecast avg: {forecast_avg:.1f}")
        
        # Risk thresholds (comparing 8-to-8)
        max_threshold = recent_max * 0.8  # 80% of recent max
        avg_threshold = recent_avg * 1.2  # 20% above recent average
        
        # Determine risk level
        if forecast_avg > max_threshold:
            print(f"   🔴 HIGH RISK: {forecast_avg:.1f} > {max_threshold:.1f} (80% of recent max)")
            return 'HIGH', '#d32f2f', '🔴'
        elif forecast_avg > avg_threshold:
            print(f"   🟡 MEDIUM RISK: {forecast_avg:.1f} > {avg_threshold:.1f} (120% of recent avg)")
            return 'MEDIUM', '#f57c00', '🟡'
        else:
            print(f"   🟢 LOW RISK: {forecast_avg:.1f} <= {avg_threshold:.1f}")
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
            
            # 🆕 Weather regressors
            'weather_regressors': {
                'data': interpretability_data['components']['weather_regressors'],
                'description': 'Weather factors impact on rabies cases (temperature, humidity, precipitation, etc.)',
                'columns': list(interpretability_data['components']['weather_regressors'].keys())
            },
            
            # 🆕 Vaccination regressors (ANTIPOLO only)
            'vaccination_regressors': {
                'data': interpretability_data['components']['vaccination_regressors'],
                'description': 'Vaccination campaign impact on rabies cases',
                'columns': list(interpretability_data['components']['vaccination_regressors'].keys())
            },
            
            # 🆕 Seasonal regressors (CAINTA/ANGONO)
            'seasonal_regressors': {
                'data': interpretability_data['components']['seasonal_regressors'],
                'description': 'Custom seasonal patterns specific to this municipality',
                'columns': list(interpretability_data['components']['seasonal_regressors'].keys())
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
    print(f"   - Weather regressors: {len(interpretability_data['components']['weather_regressors'])}")
    print(f"   - Vaccination regressors: {len(interpretability_data['components']['vaccination_regressors'])}")
    print(f"   - Seasonal regressors: {len(interpretability_data['components']['seasonal_regressors'])}")
    print(f"   - Feature importance: {len(interpretability_data['feature_importance'])} features")
    print(f"   - Changepoints detected: {len(interpretability_data['changepoints'])}\n")
    
    return response

# ==============================================
# 📊 REPORT GENERATION ENDPOINTS
# ==============================================

@app.get("/api/report/csv/{municipality}/{barangay}")
async def generate_csv_report(municipality: str, barangay: str):
    """
    Generate CSV report with forecast and interpretability data
    """
    print(f"\n📄 Generating CSV report for {municipality} - {barangay}")
    
    # Get the model - try exact match first, then case-insensitive
    model_key = f"{municipality}_{barangay}"
    print(f"🔍 Looking for model key: {model_key}")
    print(f"📋 Available models: {list(MODELS.keys())[:5]}...")  # Show first 5
    
    model_data = None
    
    # Try exact match first
    if model_key in MODELS:
        model_data = MODELS[model_key]
    else:
        # Try case-insensitive match
        model_key_upper = model_key.upper()
        for key in MODELS.keys():
            if key.upper() == model_key_upper:
                model_data = MODELS[key]
                print(f"✅ Found case-insensitive match: {key}")
                break
    
    if model_data is None:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_key}. Available: {list(MODELS.keys())}")
    
    # Generate forecast
    try:
        # Get the last date from the model (use validation_end or training_end)
        last_date = model_data.get('validation_end', model_data.get('training_end'))
        if last_date is None:
            # Fallback: get from validation dates
            if 'dates' in model_data and len(model_data['dates']) > 0:
                last_date = pd.Timestamp(model_data['dates'][-1])
            else:
                raise ValueError("Cannot determine last date from model data")
        
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=180,
            freq='D'
        )
        
        forecast_df = pd.DataFrame({
            'ds': future_dates,
            'y': [0] * len(future_dates)  # Dummy values for prediction
        })
        
        # Add regressors (handle both dict and DataFrame formats)
        if 'weather_data' in model_data and model_data['weather_data'] is not None:
            weather_data = model_data['weather_data']
            
            # Handle dict format (column -> list)
            if isinstance(weather_data, dict):
                weather_cols = [col for col in weather_data.keys() if col != 'ds']
                for col in weather_cols:
                    # Use mean of training data
                    forecast_df[col] = np.mean(weather_data[col]) if len(weather_data[col]) > 0 else 0.0
            # Handle DataFrame format
            elif hasattr(weather_data, 'columns'):
                weather_cols = [col for col in weather_data.columns if col != 'ds']
                for col in weather_cols:
                    forecast_df[col] = weather_data[col].mean()
        
        if 'vaccination_data' in model_data and model_data['vaccination_data'] is not None:
            vax_data = model_data['vaccination_data']
            
            # Handle dict format
            if isinstance(vax_data, dict):
                vax_cols = [col for col in vax_data.keys() if col != 'ds']
                for col in vax_cols:
                    forecast_df[col] = 0
            # Handle DataFrame format
            elif hasattr(vax_data, 'columns'):
                vax_cols = [col for col in vax_data.columns if col != 'ds']
                for col in vax_cols:
                    forecast_df[col] = 0
        
        if 'seasonal_data' in model_data and model_data['seasonal_data'] is not None:
            if municipality.upper() == 'CAINTA':
                forecast_df = add_cainta_seasonal_features(forecast_df)
            elif municipality.upper() == 'ANGONO':
                forecast_df = add_angono_seasonal_features(forecast_df)
        
        # Make predictions
        np_forecast = model_data['np_model'].predict(forecast_df)
        forecast_df['yhat1'] = np_forecast['yhat1']
        
        # 🔥 FIX: Prepare XGBoost features properly (don't pass all columns!)
        # XGBoost was trained on specific engineered features, not raw data
        xgb_predictions = []
        for idx in range(len(forecast_df)):
            row = forecast_df.iloc[idx]
            X_future = pd.DataFrame({
                'Year': [row['ds'].year],
                'Month': [row['ds'].month],
                'lag_1': [0],
                'lag_2': [0],
                'rolling_mean_3': [0],
                'rolling_std_3': [0],
                'lag_12': [0],
                'month_sin': [np.sin(2 * np.pi * row['ds'].month / 12)],
                'month_cos': [np.cos(2 * np.pi * row['ds'].month / 12)],
                'rate_of_change_1': [0],
                'np_prediction': [row['yhat1']]
            })
            xgb_predictions.append(model_data['xgb_model'].predict(X_future)[0])
        
        forecast_df['yhat'] = np.maximum(0, xgb_predictions)
        
        # Get interpretability components
        interpretability_data = extract_model_components(model_data)
        components_df = pd.DataFrame(interpretability_data['components'])
        
        # Merge forecast with components (use last available component values)
        if len(components_df) > 0:
            last_trend = components_df['trend'].iloc[-1]
            last_seasonality = components_df['yearly_seasonality'].iloc[-1]
            last_holiday = components_df['holidays'].iloc[-1]
        else:
            last_trend = 0
            last_seasonality = 0
            last_holiday = 0
        
        # Calculate risk levels
        def calculate_risk(cases):
            if cases > 5:
                return "HIGH"
            elif cases > 2:
                return "MEDIUM"
            else:
                return "LOW"
        
        # Create report DataFrame (build columns explicitly to avoid "Mixing dicts" error)
        date_col = forecast_df['ds'].dt.strftime('%Y-%m-%d').tolist()
        predicted_cases_col = forecast_df['yhat'].round(2).tolist()
        risk_level_col = [calculate_risk(val) for val in forecast_df['yhat']]
        trend_col = [last_trend] * len(forecast_df)
        seasonal_col = [last_seasonality] * len(forecast_df)
        holiday_col = [last_holiday] * len(forecast_df)
        
        report_df = pd.DataFrame({
            'Date': date_col,
            'Predicted_Cases': predicted_cases_col,
            'Risk_Level': risk_level_col,
            'Trend_Component': trend_col,
            'Seasonal_Component': seasonal_col,
            'Holiday_Effect': holiday_col
        })
        
        # Add weather impact summary
        if 'weather_regressors' in interpretability_data['components']:
            weather_impact = sum(interpretability_data['components']['weather_regressors'].values(), [])
            if weather_impact:
                report_df['Weather_Impact'] = np.mean(weather_impact)
            else:
                report_df['Weather_Impact'] = 0
        else:
            report_df['Weather_Impact'] = 0
        
        # Add vaccination impact summary
        if 'vaccination_regressors' in interpretability_data['components']:
            vax_impact = sum(interpretability_data['components']['vaccination_regressors'].values(), [])
            if vax_impact:
                report_df['Vaccination_Impact'] = np.mean(vax_impact)
            else:
                report_df['Vaccination_Impact'] = 0
        else:
            report_df['Vaccination_Impact'] = 0
        
        # Convert to CSV
        csv_buffer = io.StringIO()
        
        # Add metadata header
        csv_buffer.write(f"# Rabies Forecast Report\n")
        csv_buffer.write(f"# Municipality: {municipality}\n")
        csv_buffer.write(f"# Barangay: {barangay}\n")
        csv_buffer.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        csv_buffer.write(f"# Forecast Period: 180 days\n")
        csv_buffer.write(f"#\n")
        csv_buffer.write(f"# Model Metrics:\n")
        csv_buffer.write(f"# - MAE: {model_data.get('metrics', {}).get('mae', 'N/A')}\n")
        csv_buffer.write(f"# - RMSE: {model_data.get('metrics', {}).get('rmse', 'N/A')}\n")
        csv_buffer.write(f"# - R²: {model_data.get('metrics', {}).get('r2', 'N/A')}\n")
        csv_buffer.write(f"# - MASE: {model_data.get('metrics', {}).get('mase', 'N/A')}\n")
        csv_buffer.write(f"#\n")
        
        # === BARANGAY COMPARISON (Professor's Requirement) ===
        csv_buffer.write(f"# === COMPARISON WITH OTHER BARANGAYS IN {municipality} ===\n")
        csv_buffer.write(f"#\n")
        
        # Get all barangays in the same municipality
        municipality_barangays = []
        municipality_prefix = f"{municipality}_"
        
        for key, mdata in MODELS.items():
            # Case-insensitive comparison for municipality
            if key.upper().startswith(municipality_prefix.upper()):
                brgy_name = key.split('_', 1)[1]  # Keep original case
                metrics = mdata.get('metrics', {})
                municipality_barangays.append({
                    'Barangay': brgy_name,
                    'MAE': metrics.get('mae', 'N/A'),
                    'RMSE': metrics.get('rmse', 'N/A'),
                    'R2': metrics.get('r2', 'N/A'),
                    'MASE': metrics.get('mase', 'N/A'),
                    'Avg_Prediction': forecast_df['yhat'].mean() if key.upper() == f"{municipality}_{barangay}".upper() else 'N/A'
                })
        
        # Sort by MAE (best performing first)
        municipality_barangays.sort(key=lambda x: float(x['MAE']) if isinstance(x['MAE'], (int, float)) else 999)
        
        # Find rank of current barangay (case-insensitive)
        current_rank = next((i+1 for i, b in enumerate(municipality_barangays) 
                            if b['Barangay'].upper() == barangay.upper()), -1)
        
        csv_buffer.write(f"# {barangay} ranks #{current_rank} out of {len(municipality_barangays)} barangays in {municipality}\n")
        csv_buffer.write(f"# (Ranked by MAE - lower is better)\n")
        csv_buffer.write(f"#\n")
        
        # Write comparison table
        csv_buffer.write(f"# Barangay,MAE,RMSE,R2,MASE,Status\n")
        for idx, brgy in enumerate(municipality_barangays[:10], 1):  # Top 10
            status = ">>> THIS BARANGAY <<<" if brgy['Barangay'].upper() == barangay.upper() else ""
            csv_buffer.write(f"# {idx}. {brgy['Barangay']},{brgy['MAE']},{brgy['RMSE']},{brgy['R2']},{brgy['MASE']},{status}\n")
        csv_buffer.write(f"#\n")
        csv_buffer.write(f"# === END COMPARISON ===\n")
        csv_buffer.write(f"#\n")
        
        # Add forecast data
        report_df.to_csv(csv_buffer, index=False)
        
        # Create response
        csv_buffer.seek(0)
        filename = f"rabies_forecast_{municipality}_{barangay}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        return StreamingResponse(
            iter([csv_buffer.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        print(f"❌ Error generating CSV report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate CSV report: {str(e)}")


@app.get("/api/report/pdf/{municipality}/{barangay}")
async def generate_pdf_report(municipality: str, barangay: str):
    """
    Generate PDF report with forecast and interpretability visualizations
    """
    print(f"\n📄 Generating PDF report for {municipality} - {barangay}")
    
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="PDF generation requires: pip install reportlab matplotlib"
        )
    
    # Get the model - try exact match first, then case-insensitive
    model_key = f"{municipality}_{barangay}"
    print(f"🔍 Looking for model key: {model_key}")
    
    model_data = None
    
    # Try exact match first
    if model_key in MODELS:
        model_data = MODELS[model_key]
    else:
        # Try case-insensitive match
        model_key_upper = model_key.upper()
        for key in MODELS.keys():
            if key.upper() == model_key_upper:
                model_data = MODELS[key]
                print(f"✅ Found case-insensitive match: {key}")
                break
    
    if model_data is None:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_key}. Available: {list(MODELS.keys())}")
    
    # Generate forecast
    # Get the last date from the model (use validation_end or training_end)
    last_date = model_data.get('validation_end', model_data.get('training_end'))
    if last_date is None:
        # Fallback: get from validation dates
        if 'dates' in model_data and len(model_data['dates']) > 0:
            last_date = pd.Timestamp(model_data['dates'][-1])
        else:
            raise ValueError("Cannot determine last date from model data")
    
    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=180,
        freq='D'
    )
    
    forecast_df = pd.DataFrame({
        'ds': future_dates,
        'y': [0] * len(future_dates)  # Dummy values for prediction
    })
    
    # 🔍 DEBUG: Check types
    print(f"   🔍 weather_data type: {type(model_data.get('weather_data'))}")
    print(f"   🔍 vaccination_data type: {type(model_data.get('vaccination_data'))}")
    print(f"   🔍 seasonal_data type: {type(model_data.get('seasonal_data'))}")
    
    # Add regressors (handle both dict and DataFrame formats)
    if 'weather_data' in model_data and model_data['weather_data'] is not None:
        weather_data = model_data['weather_data']
        
        # Handle dict format (column -> list)
        if isinstance(weather_data, dict):
            weather_cols = [col for col in weather_data.keys() if col != 'ds']
            for col in weather_cols:
                # Use mean of training data
                forecast_df[col] = np.mean(weather_data[col]) if len(weather_data[col]) > 0 else 0.0
        # Handle DataFrame format
        elif hasattr(weather_data, 'columns'):
            weather_cols = [col for col in weather_data.columns if col != 'ds']
            for col in weather_cols:
                forecast_df[col] = weather_data[col].mean()
    
    if 'vaccination_data' in model_data and model_data['vaccination_data'] is not None:
        vax_data = model_data['vaccination_data']
        
        # Handle dict format
        if isinstance(vax_data, dict):
            vax_cols = [col for col in vax_data.keys() if col != 'ds']
            for col in vax_cols:
                forecast_df[col] = 0
        # Handle DataFrame format
        elif hasattr(vax_data, 'columns'):
            vax_cols = [col for col in vax_data.columns if col != 'ds']
            for col in vax_cols:
                forecast_df[col] = 0
    
    # 🆕 ADD SEASONAL FEATURES (models now trained with them!)
    if municipality.upper() == 'CAINTA':
        forecast_df = add_cainta_seasonal_features(forecast_df)
        print(f"   🎯 Added CAINTA seasonal features for PDF forecast")
    elif municipality.upper() == 'ANGONO':
        forecast_df = add_angono_seasonal_features(forecast_df)
        print(f"   🎯 Added ANGONO seasonal features for PDF forecast")
    
    # Make predictions
    np_forecast = model_data['np_model'].predict(forecast_df)
    forecast_df['yhat1'] = np_forecast['yhat1']
    
    # 🔥 FIX: Prepare XGBoost features properly (don't pass all columns!)
    # XGBoost was trained on specific engineered features, not raw data
    xgb_predictions = []
    for idx in range(len(forecast_df)):
        row = forecast_df.iloc[idx]
        X_future = pd.DataFrame({
            'Year': [row['ds'].year],
            'Month': [row['ds'].month],
            'lag_1': [0],
            'lag_2': [0],
            'rolling_mean_3': [0],
            'rolling_std_3': [0],
            'lag_12': [0],
            'month_sin': [np.sin(2 * np.pi * row['ds'].month / 12)],
            'month_cos': [np.cos(2 * np.pi * row['ds'].month / 12)],
            'rate_of_change_1': [0],
            'np_prediction': [row['yhat1']]
        })
        xgb_predictions.append(model_data['xgb_model'].predict(X_future)[0])
    
    forecast_df['yhat'] = np.maximum(0, xgb_predictions)
    
    # Get interpretability
    interpretability_data = extract_model_components(model_data)
    
    # Create PDF
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    story.append(Paragraph(f"Rabies Forecast Report", title_style))
    story.append(Paragraph(f"{municipality} - {barangay}", styles['Heading2']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # === EXECUTIVE SUMMARY ===
    story.append(Paragraph("Executive Summary", heading_style))
    
    avg_cases = forecast_df['yhat'].mean()
    max_cases = forecast_df['yhat'].max()
    total_cases = forecast_df['yhat'].sum()
    high_risk_days = len(forecast_df[forecast_df['yhat'] > 5])
    
    # Determine overall risk
    if avg_cases > 5:
        risk_level = "HIGH RISK"
        risk_color = colors.red
    elif avg_cases > 2:
        risk_level = "MEDIUM RISK"
        risk_color = colors.orange
    else:
        risk_level = "LOW RISK"
        risk_color = colors.green
    
    summary_text = f"""
    <b>Overall Assessment:</b> <font color="{risk_color.hexval() if hasattr(risk_color, 'hexval') else 'black'}">{risk_level}</font><br/>
    <br/>
    <b>Forecast Period:</b> Next 180 days ({forecast_df['ds'].min().strftime('%B %d, %Y')} to {forecast_df['ds'].max().strftime('%B %d, %Y')})<br/>
    <br/>
    <b>Key Findings:</b><br/>
    • Expected average: <b>{avg_cases:.1f} cases per day</b><br/>
    • Peak prediction: <b>{max_cases:.1f} cases</b> (on {forecast_df.loc[forecast_df['yhat'].idxmax(), 'ds'].strftime('%B %d, %Y')})<br/>
    • Total projected cases: <b>{total_cases:.0f} cases</b> over 6 months<br/>
    • High-risk days (&gt;5 cases): <b>{high_risk_days} days</b> ({(high_risk_days/180*100):.1f}% of forecast period)<br/>
    """
    
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # === BARANGAY COMPARISON (Professor's Requirement) ===
    story.append(Paragraph(f"Comparative Forecast Analysis - {municipality}", heading_style))
    
    # Get forecast predictions for all barangays in same municipality
    comparison_forecast_data = []
    for key, data in MODELS.items():
        if key.upper().startswith(f"{municipality.upper()}_"):
            brgy_name = key.split('_', 1)[1]
            
            # Use the existing predict_future_months function (6 months)
            try:
                future_predictions = predict_future_months(data, months_ahead=6)
                
                if future_predictions:
                    # Calculate statistics from monthly predictions
                    monthly_cases = [p['predicted'] for p in future_predictions]
                    avg_cases = np.mean(monthly_cases)
                    max_cases = np.max(monthly_cases)
                    total_cases = np.sum(monthly_cases)
                    high_risk_months = len([c for c in monthly_cases if c > 150])  # High risk = >150 cases/month (~5/day)
                    
                    # Determine risk level (based on average monthly cases)
                    if avg_cases > 150:  # ~5 cases/day
                        risk_level = "HIGH"
                    elif avg_cases > 60:  # ~2 cases/day
                        risk_level = "MEDIUM"
                    else:
                        risk_level = "LOW"
                    
                    comparison_forecast_data.append({
                        'barangay': brgy_name,
                        'avg_cases_monthly': avg_cases,  # Average cases per MONTH
                        'max_cases_monthly': max_cases,  # Peak month
                        'total_cases': total_cases,
                        'high_risk_months': high_risk_months,
                        'risk_level': risk_level,
                        'is_current': brgy_name.upper() == barangay.upper()
                    })
                else:
                    print(f"⚠️ No predictions for {brgy_name}")
                    
            except Exception as e:
                print(f"❌ Error comparing {brgy_name}: {e}")
                import traceback
                traceback.print_exc()
                continue
    
    # Sort by average monthly cases (highest risk first)
    comparison_forecast_data.sort(key=lambda x: x['avg_cases_monthly'], reverse=True)
    
    # Find rank of current barangay
    current_rank = next((i+1 for i, b in enumerate(comparison_forecast_data) 
                        if b['is_current']), -1)
    
    # Add explanation
    current_brgy_data = next((b for b in comparison_forecast_data if b['is_current']), None)
    if current_brgy_data:
        story.append(Paragraph(
            f"<b>{barangay}</b> ranks <b>#{current_rank}</b> out of <b>{len(comparison_forecast_data)}</b> barangays "
            f"with projected <b>{current_brgy_data['avg_cases_monthly']:.1f} cases/month</b> (Risk Level: <b>{current_brgy_data['risk_level']}</b>).",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.2*inch))
    
    # Create comparison table (top 10) - showing MONTHLY forecasts
    comparison_data = [['Rank', 'Barangay', 'Avg Cases/Month', 'Peak Month', 'Total (6mo)', 'High-Risk Months', 'Risk Level']]
    for idx, item in enumerate(comparison_forecast_data[:10], 1):
        brgy_display = item['barangay'] + (' ⭐' if item['is_current'] else '')
        comparison_data.append([
            str(idx),
            brgy_display,
            f"{item['avg_cases_monthly']:.1f}",
            f"{item['max_cases_monthly']:.1f}",
            f"{item['total_cases']:.0f}",
            str(item['high_risk_months']),
            item['risk_level']
        ])
    
    comparison_table = Table(comparison_data, colWidths=[0.5*inch, 1.8*inch, 1*inch, 0.9*inch, 0.9*inch, 1*inch, 0.8*inch])
    comparison_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8)
    ])
    
    # Highlight current barangay row
    for idx, item in enumerate(comparison_forecast_data[:10], 1):
        if item['is_current']:
            comparison_style.add('BACKGROUND', (0, idx), (-1, idx), colors.HexColor('#fff9c4'))
            comparison_style.add('FONTNAME', (0, idx), (-1, idx), 'Helvetica-Bold')
    
    comparison_table.setStyle(comparison_style)
    story.append(comparison_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Add actionable insights
    if current_brgy_data:
        if current_brgy_data['risk_level'] == 'HIGH':
            recommendation = ("⚠️ <b>HIGH PRIORITY:</b> This barangay requires immediate intervention. "
                            "Allocate additional veterinary resources, conduct intensive awareness campaigns, "
                            "and implement aggressive vaccination programs.")
        elif current_brgy_data['risk_level'] == 'MEDIUM':
            recommendation = ("⚡ <b>MODERATE ATTENTION:</b> Maintain regular monitoring and ensure vaccination "
                            "coverage remains high. Prepare contingency plans for potential case spikes.")
        else:
            recommendation = ("✓ <b>STABLE STATUS:</b> Continue standard prevention protocols. "
                            "Regular monitoring and community education programs should be maintained.")
        
        story.append(Paragraph(f"<b>Actionable Recommendation:</b><br/>{recommendation}", styles['Normal']))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Forecast Summary
    story.append(Paragraph("Forecast Summary (Next 180 Days)", heading_style))
    avg_cases = forecast_df['yhat'].mean()
    max_cases = forecast_df['yhat'].max()
    high_risk_days = len(forecast_df[forecast_df['yhat'] > 5])
    
    summary_data = [
        ['Metric', 'Value'],
        ['Average Predicted Cases/Day', f"{avg_cases:.2f}"],
        ['Maximum Predicted Cases/Day', f"{max_cases:.2f}"],
        ['High Risk Days (>5 cases)', f"{high_risk_days}"],
        ['Forecast Period', '180 days']
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Create forecast chart
    story.append(Paragraph("Forecast Visualization", heading_style))
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(forecast_df['ds'], forecast_df['yhat'], color='#3498db', linewidth=2)
    ax.fill_between(forecast_df['ds'], 0, forecast_df['yhat'], alpha=0.3, color='#3498db')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Predicted Cases', fontsize=12)
    ax.set_title('180-Day Rabies Cases Forecast', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save chart to buffer
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150)
    img_buffer.seek(0)
    plt.close()
    
    # Add chart to PDF
    img = Image(img_buffer, width=6*inch, height=3*inch)
    story.append(img)
    story.append(Spacer(1, 0.3*inch))
    
    # Interpretability Summary
    story.append(Paragraph("Model Interpretability", heading_style))
    feature_importance = interpretability_data.get('feature_importance', [])
    if feature_importance:
        story.append(Paragraph("Top Contributing Factors:", styles['Normal']))
        for i, feat in enumerate(feature_importance[:5], 1):
            story.append(Paragraph(f"{i}. {feat['feature']}: {feat['importance']:.1f}% importance", styles['Normal']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Recommendations
    story.append(Paragraph("Recommendations", heading_style))
    recommendations = []
    if high_risk_days > 30:
        recommendations.append("⚠️ HIGH ALERT: Significant number of high-risk days detected. Increase vaccination campaigns.")
    if avg_cases > 3:
        recommendations.append("📊 Monitor closely: Average daily cases above normal threshold.")
    else:
        recommendations.append("✅ Cases within normal range. Maintain current prevention measures.")
    
    for rec in recommendations:
        story.append(Paragraph(rec, styles['Normal']))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(
        "This report was automatically generated by the Rabies Forecasting System.",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
    ))
    
    # Build PDF
    doc.build(story)
    pdf_buffer.seek(0)
    
    filename = f"rabies_forecast_{municipality}_{barangay}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@app.get("/api/report/insights-pdf/{municipality}/{barangay}")
async def generate_insights_pdf(municipality: str, barangay: str):
    """
    Generate comprehensive Model Interpretability PDF with all visualizations
    """
    print(f"\n📊 Generating Interpretability PDF for {municipality} - {barangay}")
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="PDF generation requires: pip install reportlab matplotlib"
        )
    
    # Get model
    model_key = f"{municipality}_{barangay}"
    model_data = None
    
    if model_key in MODELS:
        model_data = MODELS[model_key]
    else:
        model_key_upper = model_key.upper()
        for key in MODELS.keys():
            if key.upper() == model_key_upper:
                model_data = MODELS[key]
                break
    
    if model_data is None:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_key}")
    
    # Get interpretability data
    interpretability_data = extract_model_components(model_data)
    
    if not interpretability_data['success']:
        raise HTTPException(status_code=500, detail="Failed to extract model components")
    
    # Create PDF
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=10
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=8,
        spaceBefore=8
    )
    
    # ===== TITLE PAGE =====
    story.append(Paragraph("🔍 Model Interpretability Report", title_style))
    story.append(Paragraph(f"{municipality} - {barangay}", styles['Heading2']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    intro_text = """
    <b>Understanding How the Model Makes Predictions</b><br/>
    <br/>
    This report shows the internal workings of the AI forecasting model, breaking down predictions into<br/>
    understandable components: trends, seasonal patterns, holiday effects, weather impacts, and vaccination campaigns.<br/>
    <br/>
    <i>This helps stakeholders understand WHY certain predictions are made, not just WHAT they are.</i>
    """
    story.append(Paragraph(intro_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # ===== TREND, SEASONALITY & HOLIDAYS CHART =====
    story.append(Paragraph("📈 Trend, Seasonality & Holiday Decomposition", heading_style))
    
    explanation = """
    <b>Trend:</b> Long-term direction of rabies cases (upward/downward pattern)<br/>
    <b>Seasonality:</b> Recurring yearly patterns (e.g., higher cases in certain months)<br/>
    <b>Holidays:</b> Philippine public holiday effects on rabies cases
    """
    story.append(Paragraph(explanation, styles['Normal']))
    story.append(Spacer(1, 0.15*inch))
    
    # Create decomposition chart
    fig, ax = plt.subplots(figsize=(10, 5))
    dates = interpretability_data['components']['dates']
    trend = interpretability_data['components']['trend']
    seasonality = interpretability_data['components']['yearly_seasonality']
    holidays = interpretability_data['components']['holidays']
    
    ax.plot(dates, trend, label='Trend', linewidth=2, color='#3498db')
    ax.plot(dates, seasonality, label='Seasonality', linewidth=2, color='#e74c3c', linestyle='--')
    ax.plot(dates, holidays, label='Holiday Effects', linewidth=2, color='#f39c12', alpha=0.7)
    
    ax.set_xlabel('Date', fontsize=10)
    ax.set_ylabel('Impact on Cases', fontsize=10)
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    plt.tight_layout()
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    img = Image(img_buffer, width=6.5*inch, height=3*inch)
    story.append(img)
    story.append(Spacer(1, 0.2*inch))
    
    # ===== SIGNIFICANT HOLIDAY EFFECTS =====
    if interpretability_data['holiday_effects']:
        story.append(Paragraph("🎉 Significant Holiday Effects Detected:", subheading_style))
        
        holiday_table_data = [['Date', 'Holiday', 'Impact', 'Effect']]
        for effect in interpretability_data['holiday_effects'][:10]:  # Top 10
            impact_icon = '📈' if effect['impact'] == 'Positive' else '📉'
            holiday_table_data.append([
                effect['date'],
                effect['holiday'],
                f"{effect['effect']:.1f} cases",
                impact_icon
            ])
        
        holiday_table = Table(holiday_table_data, colWidths=[1*inch, 2.5*inch, 1.2*inch, 0.8*inch])
        holiday_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]))
        story.append(holiday_table)
        story.append(Spacer(1, 0.15*inch))
        
        story.append(Paragraph(
            "<i>Note: Holidays include Philippine public holidays (New Year, Holy Week, Christmas, Independence Day, etc.)</i>",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.2*inch))
    
    # ===== WEATHER FACTORS =====
    if interpretability_data['components']['weather_regressors']:
        story.append(PageBreak())
        story.append(Paragraph("🌤️ Weather Factors Impact", heading_style))
        story.append(Paragraph(
            "Weather factors impact on rabies cases (temperature, humidity, precipitation, etc.)<br/>"
            "Shows how temperature, humidity, precipitation, and weather patterns affect rabies cases.",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.15*inch))
        
        # Create weather chart
        fig, ax = plt.subplots(figsize=(10, 5))
        weather_data = interpretability_data['components']['weather_regressors']
        
        for col, values in weather_data.items():
            if values and any(v != 0 for v in values):  # Only plot non-zero data
                label = col.replace('_', ' ').title()
                ax.plot(dates, values, label=label, linewidth=1.5, alpha=0.8)
        
        ax.set_xlabel('Date', fontsize=10)
        ax.set_ylabel('Impact on Cases', fontsize=10)
        ax.legend(loc='best', fontsize=8, ncol=2)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        plt.tight_layout()
        
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        img = Image(img_buffer, width=6.5*inch, height=3*inch)
        story.append(img)
        story.append(Spacer(1, 0.15*inch))
        
        story.append(Paragraph(
            "💡 <b>Interpretation:</b> Positive values indicate weather conditions that increase rabies cases, "
            "negative values indicate conditions that decrease cases.",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.2*inch))
    
    # ===== VACCINATION CAMPAIGNS =====
    if interpretability_data['components']['vaccination_regressors']:
        vax_data = interpretability_data['components']['vaccination_regressors']
        if any(values and any(v != 0 for v in values) for values in vax_data.values()):
            story.append(PageBreak())
            story.append(Paragraph("💉 Vaccination Campaign Impact", heading_style))
            story.append(Paragraph(
                "Vaccination campaign impact on rabies cases<br/>"
                "Shows the effect of mass vaccination drives on rabies case reduction.",
                styles['Normal']
            ))
            story.append(Spacer(1, 0.15*inch))
            
            # Create vaccination chart
            fig, ax = plt.subplots(figsize=(10, 5))
            
            for col, values in vax_data.items():
                if values and any(v != 0 for v in values):
                    label = col.replace('_', ' ').title()
                    ax.plot(dates, values, label=label, linewidth=2, marker='o', markersize=3)
            
            ax.set_xlabel('Date', fontsize=10)
            ax.set_ylabel('Impact on Cases', fontsize=10)
            ax.legend(loc='best', fontsize=9)
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
            ax.tick_params(axis='x', rotation=45, labelsize=8)
            plt.tight_layout()
            
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            img = Image(img_buffer, width=6.5*inch, height=3*inch)
            story.append(img)
            story.append(Spacer(1, 0.15*inch))
            
            story.append(Paragraph(
                "💡 <b>Interpretation:</b> Negative values indicate vaccination campaigns successfully reduced "
                "rabies cases during those periods.",
                styles['Normal']
            ))
            story.append(Spacer(1, 0.15*inch))
            
            story.append(Paragraph(
                "📅 <b>Campaigns:</b> 2023 (Jan-Mar): ~35,000 animals vaccinated | 2024 (Mar-Apr): ~35,000 animals vaccinated",
                styles['Normal']
            ))
            story.append(Spacer(1, 0.2*inch))
    
    # ===== FEATURE IMPORTANCE =====
    story.append(PageBreak())
    story.append(Paragraph("🎯 Feature Importance Analysis", heading_style))
    story.append(Paragraph(
        "Which factors contribute most to predictions? Understanding the model's decision-making process.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.15*inch))
    
    # Create feature importance chart
    features = interpretability_data['feature_importance'][:10]  # Top 10
    feature_names = [f['feature'] for f in features]
    importance_values = [f['percentage'] for f in features]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    colors_list = plt.cm.viridis(np.linspace(0.3, 0.9, len(feature_names)))
    bars = ax.barh(feature_names, importance_values, color=colors_list)
    
    ax.set_xlabel('Importance (%)', fontsize=10)
    ax.set_ylabel('Feature', fontsize=10)
    ax.set_title('Top 10 Most Important Features', fontsize=12, fontweight='bold')
    
    # Add percentage labels on bars
    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, f'{width:.1f}%',
                ha='left', va='center', fontsize=8, fontweight='bold')
    
    plt.tight_layout()
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    img = Image(img_buffer, width=6*inch, height=3.5*inch)
    story.append(img)
    story.append(Spacer(1, 0.15*inch))
    
    # Feature importance table
    fi_table_data = [['Rank', 'Feature', 'Importance', 'What It Means']]
    descriptions = {
        'np_prediction': 'NeuralProphet baseline prediction',
        'Month': 'Month of the year (seasonality)',
        'lag_1': 'Previous month cases',
        'lag_12': 'Same month last year',
        'rolling_mean_3': '3-month average trend',
        'month_sin': 'Seasonal cycle (sine wave)',
        'month_cos': 'Seasonal cycle (cosine wave)',
        'rate_of_change_1': 'How fast cases are changing',
        'Year': 'Long-term trend over years',
        'rolling_std_3': 'Variability in recent months'
    }
    
    for idx, feat in enumerate(features[:5], 1):  # Top 5 in table
        fi_table_data.append([
            str(idx),
            feat['feature'],
            f"{feat['percentage']:.1f}%",
            descriptions.get(feat['feature'], 'Contributing factor')
        ])
    
    fi_table = Table(fi_table_data, colWidths=[0.5*inch, 1.5*inch, 1*inch, 3.5*inch])
    fi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9)
    ]))
    story.append(fi_table)
    story.append(Spacer(1, 0.2*inch))
    
    # ===== MODEL CONFIGURATION =====
    story.append(Paragraph("⚙️ Model Configuration", heading_style))
    
    config_data = [
        ['Parameter', 'Value'],
        ['Model Type', 'NeuralProphet + XGBoost Hybrid'],
        ['Holidays Configured', interpretability_data['model_info']['holidays_configured']],
        ['Weather Regressors', str(interpretability_data['model_info']['weather_regressors_count'])],
        ['Vaccination Regressors', str(interpretability_data['model_info']['vaccination_regressors_count'])],
        ['Seasonal Features', str(interpretability_data['model_info']['seasonal_regressors_count'])],
        ['XGBoost Estimators', str(interpretability_data['model_info']['xgboost_n_estimators'])],
        ['XGBoost Max Depth', str(interpretability_data['model_info']['xgboost_max_depth'])]
    ]
    
    config_table = Table(config_data, colWidths=[2.5*inch, 2.5*inch])
    config_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9)
    ]))
    story.append(config_table)
    story.append(Spacer(1, 0.3*inch))
    
    # ===== FOOTER =====
    footer_text = """
    <br/>
    <i>This interpretability report was automatically generated by the Rabies Forecasting System.<br/>
    For questions or clarifications, please contact the data science team.</i>
    """
    story.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    
    # Return PDF
    pdf_buffer.seek(0)
    filename = f"rabies_model_insights_{municipality}_{barangay}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Rabies Forecasting Dashboard API...")
    print(f"📊 Loaded {len(MODELS)} models")
    print("🌐 API: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
