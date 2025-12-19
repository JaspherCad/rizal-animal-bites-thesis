import axiosInstance from '../../api/axiosInstance';

/**
 * Fetch all municipalities with their barangays and risk summaries
 * @returns {Promise} Response with municipalities array
 */
export const getMunicipalities = async () => {
  const response = await axiosInstance.get('/api/municipalities');
  return response.data;
};

/**
 * Fetch detailed data for a specific barangay
 * @param {string} municipality - Municipality name
 * @param {string} barangay - Barangay name
 * @returns {Promise} Response with barangay details, metrics, and historical data
 */
export const getBarangayData = async (municipality, barangay) => {
  const encodedMun = encodeURIComponent(municipality);
  const encodedBarangay = encodeURIComponent(barangay);
  const response = await axiosInstance.get(
    `/api/barangay/${encodedMun}/${encodedBarangay}`
  );
  return response.data;
};

/**
 * Get future forecast for a barangay
 * @param {string} municipality - Municipality name
 * @param {string} barangay - Barangay name
 * @param {number} months - Number of months to forecast (default: 8)
 * @returns {Promise} Response with forecast predictions
 */
export const getForecast = async (municipality, barangay, months = 8) => {
  const encodedMun = encodeURIComponent(municipality);
  const encodedBarangay = encodeURIComponent(barangay);
  const response = await axiosInstance.get(
    `/api/forecast/${encodedMun}/${encodedBarangay}?months=${months}`
  );
  return response.data;
};

/**
 * Get model interpretability data for a barangay
 * @param {string} municipality - Municipality name
 * @param {string} barangay - Barangay name
 * @returns {Promise} Response with interpretability insights
 */
export const getInterpretability = async (municipality, barangay) => {
  const encodedMun = encodeURIComponent(municipality);
  const encodedBarangay = encodeURIComponent(barangay);
  const response = await axiosInstance.get(
    `/api/interpretability/${encodedMun}/${encodedBarangay}`
  );
  return response.data;
};

/**
 * Download CSV report for a barangay
 * @param {string} municipality - Municipality name
 * @param {string} barangay - Barangay name
 * @returns {Promise<Blob>} CSV file blob
 */
export const downloadCSVReport = async (municipality, barangay) => {
  const encodedMun = encodeURIComponent(municipality);
  const encodedBarangay = encodeURIComponent(barangay);
  const response = await axiosInstance.get(
    `/api/report/csv/${encodedMun}/${encodedBarangay}`,
    { responseType: 'blob' }
  );
  return response.data;
};

/**
 * Download PDF report for a barangay
 * @param {string} municipality - Municipality name
 * @param {string} barangay - Barangay name
 * @returns {Promise<Blob>} PDF file blob
 */
export const downloadPDFReport = async (municipality, barangay) => {
  const encodedMun = encodeURIComponent(municipality);
  const encodedBarangay = encodeURIComponent(barangay);
  const response = await axiosInstance.get(
    `/api/report/pdf/${encodedMun}/${encodedBarangay}`,
    { responseType: 'blob' }
  );
  return response.data;
};

/**
 * Download Model Insights PDF report
 * @param {string} municipality - Municipality name
 * @param {string} barangay - Barangay name
 * @returns {Promise<Blob>} PDF file blob
 */
export const downloadInsightsPDF = async (municipality, barangay) => {
  const encodedMun = encodeURIComponent(municipality);
  const encodedBarangay = encodeURIComponent(barangay);
  const response = await axiosInstance.get(
    `/api/report/insights/${encodedMun}/${encodedBarangay}`,
    { responseType: 'blob' }
  );
  return response.data;
};
