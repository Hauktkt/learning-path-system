'use client';

import dynamic from 'next/dynamic';

// Dynamically import GeminiChatbot with no SSR
const GeminiChatbot = dynamic(() => import('./GeminiChatbot'), {
  ssr: false
});

export default function ChatbotWrapper() {
  return <GeminiChatbot />;
} 