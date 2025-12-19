/**
 * Format ISO date string to readable format
 * @param {string} isoDate - ISO date string
 * @param {string} format - 'short' for YYYY-MM-DD, 'long' for MMM dd, yyyy
 * @returns {string} Formatted date string
 */
export const formatDate = (isoDate, format = 'short') => {
  if (!isoDate) return 'N/A';
  
  const date = new Date(isoDate);
  
  if (isNaN(date.getTime())) {
    return 'Invalid Date';
  }
  
  if (format === 'long') {
    // Format: Jan 15, 2024
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  }
  
  // Default short format: 2024-01-15
  return date.toISOString().split('T')[0];
};

/**
 * Format month-year for display
 * @param {string} dateString - Date string in YYYY-MM format or full ISO
 * @returns {string} Formatted as "Jan 2024"
 */
export const formatMonthYear = (dateString) => {
  if (!dateString) return 'N/A';
  
  const date = new Date(dateString);
  
  if (isNaN(date.getTime())) {
    return 'Invalid Date';
  }
  
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short'
  });
};

/**
 * Get relative time description
 * @param {string} dateString - ISO date string
 * @returns {string} Relative time like "2 months ago"
 */
export const getRelativeTime = (dateString) => {
  if (!dateString) return 'N/A';
  
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 30) return `${diffDays} days ago`;
  
  const diffMonths = Math.floor(diffDays / 30);
  if (diffMonths === 1) return '1 month ago';
  if (diffMonths < 12) return `${diffMonths} months ago`;
  
  const diffYears = Math.floor(diffMonths / 12);
  return diffYears === 1 ? '1 year ago' : `${diffYears} years ago`;
};
