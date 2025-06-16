"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { usePathname } from "next/navigation";
import Image from "next/image";

export default function Navigation() {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  // Theo dõi scroll để thay đổi kiểu dáng thanh navigation
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    // Đặt state ban đầu
    handleScroll();

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleLogout = async () => {
    await logout();
    setIsMenuOpen(false);
  };

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const closeMenu = () => {
    setIsMenuOpen(false);
  };

  // Xác định nếu trang hiện tại là trang home
  const isHomePage = pathname === '/';

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled || !isHomePage
        ? "bg-white text-gray-800 shadow-md"
        : "bg-indigo-600/90 backdrop-blur-md text-white"
        }`}
    >
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <Link href={user ? "/dashboard" : "/"}
            className={`flex items-center text-2xl font-bold transition-colors ${isScrolled || !isHomePage ? "text-indigo-600" : "text-white"
              }`}
            onClick={closeMenu}
          >
            <span className="flex items-center">
              <Image
                src="/logo.svg"
                alt="PersonalEDU Logo"
                width={36}
                height={36}
                className="mr-2"
              />
              PersonalEDU
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex space-x-1 items-center">
            {user ? (
              <>
                <Link
                  href="/create-path"
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${pathname === '/create-path'
                    ? ((isScrolled || !isHomePage) ? 'bg-indigo-100 text-indigo-700' : 'bg-white/20 text-white')
                    : ((isScrolled || !isHomePage) ? 'hover:bg-indigo-50 text-gray-700' : 'hover:bg-white/10 text-white')
                    }`}
                >
                  Tạo Lộ Trình
                </Link>
                <Link
                  href="/dashboard"
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${pathname === '/dashboard'
                    ? ((isScrolled || !isHomePage) ? 'bg-indigo-100 text-indigo-700' : 'bg-white/20 text-white')
                    : ((isScrolled || !isHomePage) ? 'hover:bg-indigo-50 text-gray-700' : 'hover:bg-white/10 text-white')
                    }`}
                >
                  Dashboard
                </Link>
                <Link
                  href="/tasks"
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${pathname === '/tasks'
                    ? ((isScrolled || !isHomePage) ? 'bg-indigo-100 text-indigo-700' : 'bg-white/20 text-white')
                    : ((isScrolled || !isHomePage) ? 'hover:bg-indigo-50 text-gray-700' : 'hover:bg-white/10 text-white')
                    }`}
                >
                  Nhiệm Vụ
                </Link>

                <div className="relative group ml-2">
                  <button
                    className={`flex items-center space-x-1 px-3 py-2 rounded-md focus:outline-none ${(isScrolled || !isHomePage)
                      ? 'hover:bg-indigo-50 text-gray-700'
                      : 'hover:bg-white/10 text-white'
                      }`}
                  >
                    <span>{user.name || user.username}</span>
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 opacity-75" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-xl overflow-hidden z-20 invisible group-hover:visible origin-top-right transition-all opacity-0 group-hover:opacity-100 scale-95 group-hover:scale-100">
                    <div className="py-1">
                      <Link
                        href="/profile"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-700 transition-colors"
                      >
                        Tài Khoản
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-red-50 hover:text-red-700 transition-colors focus:outline-none"
                      >
                        Đăng Xuất
                      </button>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <>
                <Link
                  href="/intro"
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${pathname === '/intro'
                    ? ((isScrolled || !isHomePage) ? 'bg-indigo-100 text-indigo-700' : 'bg-white/20 text-white')
                    : ((isScrolled || !isHomePage) ? 'hover:bg-indigo-50 text-gray-700' : 'hover:bg-white/10 text-white')
                    }`}
                >
                  Giới Thiệu
                </Link>
                <Link
                  href="/login"
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${pathname === '/login'
                    ? ((isScrolled || !isHomePage) ? 'bg-indigo-100 text-indigo-700' : 'bg-white/20 text-white')
                    : ((isScrolled || !isHomePage) ? 'hover:bg-indigo-50 text-gray-700' : 'hover:bg-white/10 text-white')
                    }`}
                >
                  Đăng Nhập
                </Link>
                <Link
                  href="/register"
                  className={`${(isScrolled || !isHomePage)
                    ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                    : 'bg-white text-indigo-600 hover:bg-indigo-50'
                    } px-4 py-2 rounded-md text-sm font-medium transition-colors shadow-sm ml-2`}
                >
                  Đăng Ký
                </Link>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <button
            onClick={toggleMenu}
            className="md:hidden flex items-center"
            aria-label="Toggle menu"
          >
            {isMenuOpen ? (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className={`h-6 w-6 ${(isScrolled || !isHomePage) ? 'text-indigo-600' : 'text-white'}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className={`h-6 w-6 ${(isScrolled || !isHomePage) ? 'text-indigo-600' : 'text-white'}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
              </svg>
            )}
          </button>
        </div>

        {/* Mobile menu */}
        <div
          className={`${isMenuOpen ? 'max-h-screen opacity-100 visible' : 'max-h-0 opacity-0 invisible'
            } md:hidden transition-all duration-300 ease-in-out overflow-hidden`}
        >
          <div className="py-3 space-y-1 border-t border-gray-200">
            {user ? (
              <>
                <Link
                  href="/create-path"
                  className={`block px-4 py-2 rounded-md ${pathname === '/create-path' ? 'bg-indigo-100 text-indigo-700' : 'text-gray-700 hover:bg-indigo-50 hover:text-indigo-700'}`}
                  onClick={closeMenu}
                >
                  Tạo Lộ Trình
                </Link>
                <Link
                  href="/dashboard"
                  className={`block px-4 py-2 rounded-md ${pathname === '/dashboard' ? 'bg-indigo-100 text-indigo-700' : 'text-gray-700 hover:bg-indigo-50 hover:text-indigo-700'}`}
                  onClick={closeMenu}
                >
                  Dashboard
                </Link>
                <Link
                  href="/tasks"
                  className={`block px-4 py-2 rounded-md ${pathname === '/tasks' ? 'bg-indigo-100 text-indigo-700' : 'text-gray-700 hover:bg-indigo-50 hover:text-indigo-700'}`}
                  onClick={closeMenu}
                >
                  Nhiệm Vụ
                </Link>
                <Link
                  href="/profile"
                  className={`block px-4 py-2 rounded-md ${pathname === '/profile' ? 'bg-indigo-100 text-indigo-700' : 'text-gray-700 hover:bg-indigo-50 hover:text-indigo-700'}`}
                  onClick={closeMenu}
                >
                  Tài Khoản
                </Link>
                <button
                  onClick={handleLogout}
                  className="block w-full text-left px-4 py-2 rounded-md text-red-600 hover:bg-red-50 focus:outline-none"
                >
                  Đăng Xuất
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/intro"
                  className={`block px-4 py-2 rounded-md ${pathname === '/intro' ? 'bg-indigo-100 text-indigo-700' : 'text-gray-700 hover:bg-indigo-50 hover:text-indigo-700'}`}
                  onClick={closeMenu}
                >
                  Giới Thiệu
                </Link>
                <Link
                  href="/login"
                  className={`block px-4 py-2 rounded-md ${pathname === '/login' ? 'bg-indigo-100 text-indigo-700' : 'text-gray-700 hover:bg-indigo-50 hover:text-indigo-700'}`}
                  onClick={closeMenu}
                >
                  Đăng Nhập
                </Link>
                <Link
                  href="/register"
                  className="block px-4 py-2 rounded-md bg-indigo-600 text-white hover:bg-indigo-700 text-center mt-2"
                  onClick={closeMenu}
                >
                  Đăng Ký
                </Link>
              </>
            )}
          </div>
          <div className="pb-4"></div>
        </div>
      </div>
    </nav>
  );
} 