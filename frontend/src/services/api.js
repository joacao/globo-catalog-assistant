import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const askQuestion = async (questionText) => {
  // Garante o envio do objeto com a chave "question"
  const response = await axios.post(`${API_BASE_URL}/ask`, {
    question: questionText
  });
  return response.data;
};