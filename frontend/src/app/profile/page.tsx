"use client";

import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Spinner from "@/components/Spinner";
import Alert from "@/components/Alert"; // Có thể dùng để hiển thị lỗi nếu fetch user thất bại

export default function ProfilePage() {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
    }
  }, [user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <Spinner />
      </div>
    );
  }

  if (!user) {
    return null; // Redirecting...
  }

  const handleLogout = async () => {
    await logout();
    router.push('/login'); // Chuyển hướng sau khi logout
  };

  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6">Thông Tin Tài Khoản</h1>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="mb-4">
          <p className="text-sm text-gray-500">Tên đăng nhập</p>
          <p className="text-lg font-medium">{user.username}</p>
        </div>
        <div className="mb-4">
          <p className="text-sm text-gray-500">Email</p>
          <p className="text-lg font-medium">{user.email}</p>
        </div>
        {user.name && (
          <div className="mb-6">
            <p className="text-sm text-gray-500">Tên hiển thị</p>
            <p className="text-lg font-medium">{user.name}</p>
          </div>
        )}
        {/* Có thể thêm các trường thông tin khác hoặc nút chỉnh sửa ở đây */}
        <button
          onClick={handleLogout}
          className="w-full mt-4 bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline transition-colors"
        >
          Đăng xuất
        </button>
      </div>
    </div>
  );
} 