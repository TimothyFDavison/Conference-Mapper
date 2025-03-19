// /src/hooks/useMarkers.js
import { useState, useEffect } from "react";
import { fetchMarkers } from "../services/api";

const useMarkers = (selectedOptions, startDate, endDate, openCfp) => {
  const [markers, setMarkers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    const filters = {
      categories: selectedOptions,
      start_date: startDate,
      end_date: endDate,
      open_cfp: openCfp,
    };

    fetchMarkers(filters)
      .then(data => {
        setMarkers(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching markers:", err);
        setError(err);
        setLoading(false);
      });
  }, [selectedOptions, startDate, endDate, openCfp]);

  return { markers, loading, error };
};

export default useMarkers;
