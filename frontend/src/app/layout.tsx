import React from 'react';
import type { Metadata } from 'next';
import { AuthProvider } from '../context/AuthContext';
import Navigation from '../components/Navigation';
import ChatbotWrapper from '../components/ChatbotWrapper';

import './globals.css';

export const metadata: Metadata = {
  title: 'PersonalEDU - Lộ trình học tập cá nhân hóa',
  description: 'Tạo và quản lý lộ trình học tập cá nhân hóa phù hợp với mục tiêu của bạn',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="vi">
      <body className="bg-gray-50 min-h-screen overflow-x-hidden">
        <AuthProvider>
          <Navigation />
          <div className="pt-16">
            {children}
          </div>
          <ChatbotWrapper />
        </AuthProvider>
      </body>
    </html>
  );
}
