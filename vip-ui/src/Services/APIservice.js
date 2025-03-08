const API_BASE_URL= "localhost:8000/api/v1";
export default async function fetchData(endpoint){
    try {
        const response = await fetch(`${API_BASE_URL}/${endpoint}`);
        if (!response.ok) {
          throw new Error("Failed to fetch data");
        }
        return await response.json();
      } catch (error) {
        console.error("API error:", error);
        throw error;
      }
}