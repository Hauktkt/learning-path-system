"use client";

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';

export default function IntroPage() {
  return (
    <div className="pt-20 min-h-screen">
      {/* Hero section */}
      <section className="bg-gradient-to-br from-indigo-600 to-purple-700 py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-6 text-white">
            Giới Thiệu Về <span className="text-yellow-300">PersonalEDU</span>
          </h1>
          <p className="text-xl text-indigo-100 mb-8 max-w-3xl mx-auto">
            Nền tảng học tập cá nhân hóa giúp bạn đạt được mục tiêu nhanh chóng và hiệu quả
          </p>
        </div>
      </section>

      {/* About section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold mb-8 text-center">Sứ Mệnh Của Chúng Tôi</h2>
            <p className="text-lg text-gray-700 mb-6">
              PersonalEDU được phát triển với sứ mệnh giúp mọi người tiếp cận với việc học tập một cách hiệu quả và phù hợp với cá nhân. Chúng tôi tin rằng mỗi người đều có một lộ trình học tập riêng biệt, và công nghệ AI có thể giúp xác định lộ trình đó một cách chính xác.
            </p>
            <p className="text-lg text-gray-700 mb-6">
              Với nền tảng của chúng tôi, bạn có thể:
            </p>
            <ul className="list-disc pl-6 mb-6 text-lg text-gray-700 space-y-2">
              <li>Tạo lộ trình học tập cá nhân hóa dựa trên mục tiêu của bạn</li>
              <li>Theo dõi tiến độ và duy trì động lực học tập</li>
              <li>Nhận được các tài nguyên học tập phù hợp với trình độ</li>
              <li>Điều chỉnh lộ trình khi mục tiêu hoặc ưu tiên thay đổi</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Features section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold mb-12 text-center">Tính Năng Nổi Bật</h2>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mb-4 mx-auto">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2 text-center">Lộ Trình Cá Nhân Hóa</h3>
              <p className="text-gray-600 text-center">
                Tạo lộ trình học tập dựa trên mục tiêu, sở thích và trình độ của bạn.
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mb-4 mx-auto">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2 text-center">Theo Dõi Tiến Độ</h3>
              <p className="text-gray-600 text-center">
                Dashboard trực quan giúp theo dõi và đánh giá tiến độ học tập.
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mb-4 mx-auto">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2 text-center">Công Nghệ AI</h3>
              <p className="text-gray-600 text-center">
                Ứng dụng AI để tạo lộ trình tối ưu và đề xuất tài nguyên phù hợp.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">Bắt Đầu Ngay Hôm Nay</h2>
          <p className="text-xl mb-8 max-w-3xl mx-auto">
            Tạo lộ trình học tập cá nhân và bắt đầu hành trình phát triển của bạn
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/create-path"
              className="bg-white text-indigo-600 px-8 py-3 rounded-lg text-lg font-medium hover:bg-indigo-50 transition-colors shadow-lg"
            >
              Tạo Lộ Trình
            </Link>
            <Link
              href="/register"
              className="bg-transparent text-white border-2 border-white px-8 py-3 rounded-lg text-lg font-medium hover:bg-white/10 transition-colors"
            >
              Đăng Ký
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
} 