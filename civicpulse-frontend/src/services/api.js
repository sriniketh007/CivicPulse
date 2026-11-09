const API_BASE_URL = import.meta.env.PROD ? '' : 'http://localhost:8000';

// We restored your original function name here: classifyCitizenText
export const classifyCitizenText = async (text, queryTopic = "General Community Needs") => {
    const formData = new FormData();
    formData.append("text", text);
    formData.append("query_topic", queryTopic);

    try {
        const response = await fetch(`${API_BASE_URL}/api/citizen/classify-text`, {
            method: 'POST',
            body: formData,
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error("Error submitting report:", error);
        throw error;
    }
};

// The new function for the dashboard
export const getSavedReports = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/citizen/reports`, {
            method: 'GET',
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error("Error fetching reports:", error);
        throw error;
    }
};