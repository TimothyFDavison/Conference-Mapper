import { API_BASE_URL } from '../config/apiConfig';

export const fetchCategories = async () => {
  const response = await fetch(`${API_BASE_URL}/categories`);
  if (!response.ok) {
    throw new Error("Error fetching categories");
  }
  const data = await response.json();
  return data.map(option => ({
    value: option,
    label: option.charAt(0).toUpperCase() + option.slice(1)
  }));
};

export const fetchMarkers = async (filters) => {
  const response = await fetch(`${API_BASE_URL}/markers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(filters),
  });
  if (!response.ok) {
    throw new Error("Error fetching markers");
  }
  return response.json();
};