import { useEffect, useState } from "react";
import { fetchCategories } from "../services/api";

const useCategories = () => {
  const [categoryOptions, setCategoryOptions] = useState([]);
  const [loadingCategories, setLoadingCategories] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCategories()
      .then(options => {
        setCategoryOptions(options);
        setLoadingCategories(false);
      })
      .catch(err => {
        console.error("Error fetching options:", err);
        setError(err);
        setLoadingCategories(false);
      });
  }, []);

  return { categoryOptions, loadingCategories, error };
};

export default useCategories;
