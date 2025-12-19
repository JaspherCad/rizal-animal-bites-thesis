import { useState, useEffect } from 'react';
import * as api from './api';

/**
 * Hook to fetch all municipalities data
 * @returns {object} { municipalities, loading, error, refetch }
 */
export const useMunicipalities = () => {
  const [municipalities, setMunicipalities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMunicipalities = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getMunicipalities();
      setMunicipalities(data.municipalities || []);
    } catch (err) {
      console.error('Error fetching municipalities:', err);
      setError(err.message || 'Failed to load municipalities');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMunicipalities();
  }, []);

  return {
    municipalities,
    loading,
    error,
    refetch: fetchMunicipalities,
  };
};

/**
 * Hook to fetch barangay data
 * @param {string} municipality - Municipality name
 * @param {string} barangay - Barangay name
 * @returns {object} { barangayData, loading, error, refetch }
 */
export const useBarangayData = (municipality, barangay) => {
  const [barangayData, setBarangayData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchBarangayData = async () => {
    if (!municipality || !barangay) return;

    try {
      setLoading(true);
      setError(null);
      const data = await api.getBarangayData(municipality, barangay);
      setBarangayData(data.barangay);
    } catch (err) {
      console.error('Error fetching barangay data:', err);
      setError(err.message || 'Failed to load barangay data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBarangayData();
  }, [municipality, barangay]);

  return {
    barangayData,
    loading,
    error,
    refetch: fetchBarangayData,
  };
};

/**
 * Hook to fetch forecast data
 * @param {string} municipality - Municipality name
 * @param {string} barangay - Barangay name
 * @param {number} months - Number of months to forecast
 * @returns {object} { forecastData, loading, error, fetchForecast }
 */
export const useForecast = (municipality, barangay, months = 8) => {
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchForecast = async () => {
    if (!municipality || !barangay) return;

    try {
      setLoading(true);
      setError(null);
      const data = await api.getForecast(municipality, barangay, months);
      setForecastData(data.forecast);
    } catch (err) {
      console.error('Error fetching forecast:', err);
      setError(err.message || 'Failed to load forecast');
    } finally {
      setLoading(false);
    }
  };

  return {
    forecastData,
    loading,
    error,
    fetchForecast,
  };
};

/**
 * Hook to fetch interpretability data
 * @param {string} municipality - Municipality name
 * @param {string} barangay - Barangay name
 * @returns {object} { interpretabilityData, loading, error, fetchInterpretability }
 */
export const useInterpretability = (municipality, barangay) => {
  const [interpretabilityData, setInterpretabilityData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchInterpretability = async () => {
    if (!municipality || !barangay) return;

    try {
      setLoading(true);
      setError(null);
      const data = await api.getInterpretability(municipality, barangay);
      setInterpretabilityData(data.interpretability);
    } catch (err) {
      console.error('Error fetching interpretability:', err);
      setError(err.message || 'Failed to load interpretability data');
    } finally {
      setLoading(false);
    }
  };

  return {
    interpretabilityData,
    loading,
    error,
    fetchInterpretability,
  };
};
