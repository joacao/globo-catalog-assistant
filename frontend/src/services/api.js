import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const askQuestion = async (questionText, conversationId = null) => {
  // conversationId null/undefined no primeiro turno -> backend gera um novo.
  // Nos turnos seguintes, reenviamos o mesmo ID pra manter o histórico.
  const response = await axios.post(`${API_BASE_URL}/ask`, {
    question: questionText,
    conversation_id: conversationId
  });
  return response.data; // inclui { answer, references, conversation_id }
};