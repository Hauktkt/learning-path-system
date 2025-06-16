"use client";

import React, { ReactNode, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  BiHomeAlt,
  BiTask,
  BiCalendarAlt,
  BiUser,
  BiCog,
  BiMenu,
  BiX,
  BiStats
} from 'react-icons/bi';

interface DashboardLayoutProps {
  children: ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const pathname = usePathname();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const navItems = [
    { href: '/dashboard', icon: <BiHomeAlt />, label: 'Dashboard' },
    { href: '/tasks', icon: <BiTask />, label: 'Tasks' },
    { href: '/calendar', icon: <BiCalendarAlt />, label: 'Calendar' },
    { href: '/profile', icon: <BiUser />, label: 'Profile' },
    { href: '/admin', icon: <BiStats />, label: 'Admin Stats' },
    { href: '/settings', icon: <BiCog />, label: 'Settings' },
  ];

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-30 w-64 transform bg-indigo-700 transition duration-300 lg:static lg:translate-x-0 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
      >
        <div className="flex h-16 items-center justify-between px-6 text-white">
          <span className="text-xl font-semibold">PersonalEDU</span>
          <button
            className="lg:hidden"
            onClick={toggleSidebar}
          >
            <BiX size={24} />
          </button>
        </div>
        <nav className="mt-6 space-y-1 px-4">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center rounded-md px-4 py-3 text-sm font-medium transition-colors ${pathname === item.href
                ? 'bg-indigo-800 text-white'
                : 'text-indigo-100 hover:bg-indigo-600'
                }`}
            >
              <span className="mr-3">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Navbar */}
        <header className="flex h-16 items-center justify-between bg-white px-6 shadow-sm">
          <button
            className="text-gray-500 focus:outline-none lg:hidden"
            onClick={toggleSidebar}
          >
            <BiMenu size={24} />
          </button>
          <div className="flex items-center">
            <div className="relative">
              <div className="h-8 w-8 rounded-full bg-indigo-500 flex items-center justify-center text-white">
                <BiUser />
              </div>
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout; 