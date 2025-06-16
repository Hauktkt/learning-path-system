import axios from 'axios';
import { GEMINI_API_KEY, GEMINI_API_URL } from '../config';

interface GeminiResponse {
  candidates: Array<{
    content: {
      parts: Array<{
        text: string;
      }>;
    };
  }>;
}

/**
 * Service for interacting with the Gemini API
 */
export const geminiService = {
  /**
   * Send a message to the Gemini AI model and get a response
   * @param message - The user's message
   * @returns The AI response text
   */
  async sendMessage(message: string): Promise<string> {
    try {
      if (!GEMINI_API_KEY) {
        throw new Error('Gemini API key is not configured');
      }

      const response = await axios.post<GeminiResponse>(
        `${GEMINI_API_URL}?key=${GEMINI_API_KEY}`,
        {
          contents: [
            {
              parts: [
                {
                  text: message,
                },
              ],
            },
          ],
        }
      );

      if (!response.data.candidates || response.data.candidates.length === 0) {
        throw new Error('No response received from Gemini API');
      }

      return response.data.candidates[0].content.parts[0].text;
    } catch (error) {
      console.error('Error in Gemini service:', error);
      throw error;
    }
  },
}; 