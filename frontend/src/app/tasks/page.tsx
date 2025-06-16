"use client";

import React, { useState, useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import * as learningPathService from '@/api/learningPathService';
import { StoredLearningPath, Task } from '@/types';
import Alert from '@/components/Alert';
import Spinner from '@/components/Spinner';
import Link from "next/link";
import {
  startOfWeek, endOfWeek, addDays, isSameDay,
  isWithinInterval, format, parseISO, addWeeks,
  getDay
} from 'date-fns';
import { vi } from 'date-fns/locale'; // Import Vietnamese locale

export default function TasksPage() {
  const { user, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [learningPath, setLearningPath] = useState<StoredLearningPath | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activePathId, setActivePathId] = useState<number | null>(null);
  const [weekOffset, setWeekOffset] = useState(0); // State for current week offset
  const [allTasks, setAllTasks] = useState<Task[]>([]); // State for all tasks flattened

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    } else if (user) {
      const savedIdStr = localStorage.getItem("savedLearningPathId");
      if (savedIdStr) {
        const id = parseInt(savedIdStr, 10);
        setActivePathId(id);
        fetchPathDetails(id);
      } else {
        setError("Không tìm thấy lộ trình học tập nào đã lưu. Vui lòng tạo hoặc lưu một lộ trình trên Dashboard.");
        setLoading(false);
      }
    }
  }, [user, authLoading, router]);

  const fetchPathDetails = async (pathId: number) => {
    setLoading(true);
    setError("");
    try {
      const pathData = await learningPathService.getLearningPathById(pathId);
      setLearningPath(pathData);
      // Flatten tasks_by_phase into a single array
      if (pathData?.tasks_by_phase) {
        const flattenedTasks = Object.values(pathData.tasks_by_phase).flat();
        setAllTasks(flattenedTasks);
      } else {
        setAllTasks([]);
      }
    } catch (err: any) {
      console.error("Error fetching learning path details:", err);
      setError(err.message || "Lỗi khi tải chi tiết lộ trình học tập.");
      setLearningPath(null);
      setAllTasks([]);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTask = async (taskId: number, currentStatus: boolean) => {
    if (!activePathId) return;

    // Find the task and its original status in the flattened list
    const taskIndex = allTasks.findIndex(t => t.id === taskId);
    if (taskIndex === -1) return; // Task not found

    const originalTask = allTasks[taskIndex];
    const originalStatus = originalTask.completed;

    // Optimistic UI Update
    setAllTasks(prevTasks => [
      ...prevTasks.slice(0, taskIndex),
      { ...originalTask, completed: !currentStatus },
      ...prevTasks.slice(taskIndex + 1)
    ]);

    // Call API
    try {
      await learningPathService.toggleTaskCompletion(taskId);
    } catch (toggleError: any) {
      console.error("Error toggling task:", toggleError);
      setError("Lỗi khi cập nhật trạng thái nhiệm vụ. Đang hoàn tác...");
      // Revert UI on API error
      setAllTasks(prevTasks => [
        ...prevTasks.slice(0, taskIndex),
        { ...originalTask, completed: originalStatus }, // Revert to original status
        ...prevTasks.slice(taskIndex + 1)
      ]);
    }
  };

  // --- Date Calculations and Task Filtering --- 
  const { currentWeekStart, currentWeekEnd, todayTasks, currentWeekTasksGrouped } = useMemo(() => {
    const today = new Date();
    const currentWeekStart = startOfWeek(addWeeks(today, weekOffset), { weekStartsOn: 1, locale: vi });
    const currentWeekEnd = endOfWeek(addWeeks(today, weekOffset), { weekStartsOn: 1, locale: vi });

    const tasksInCurrentWeek = allTasks.filter(task => {
      if (!task.date) return false;
      try {
        const taskDate = parseISO(task.date); // Parse ISO string date
        return isWithinInterval(taskDate, { start: currentWeekStart, end: currentWeekEnd });
      } catch (e) {
        console.error(`Invalid date format for task ${task.id}: ${task.date}`);
        return false;
      }
    });

    const todayTasks = tasksInCurrentWeek.filter(task => {
      if (!task.date) return false;
      try {
        return isSameDay(parseISO(task.date), today);
      } catch (e) { return false; }
    });

    // Group tasks by day for the weekly view
    const grouped: { [key: string]: Task[] } = {};
    tasksInCurrentWeek.forEach(task => {
      if (!task.date) return;
      try {
        const taskDateStr = format(parseISO(task.date), 'yyyy-MM-dd');
        if (!grouped[taskDateStr]) {
          grouped[taskDateStr] = [];
        }
        grouped[taskDateStr].push(task);
      } catch (e) { /* ignore tasks with invalid dates */ }
    });

    // Sort grouped tasks by date string
    const sortedGrouped = Object.entries(grouped).sort(([dateA], [dateB]) => dateA.localeCompare(dateB));
    const currentWeekTasksGrouped = Object.fromEntries(sortedGrouped);

    return { currentWeekStart, currentWeekEnd, todayTasks, currentWeekTasksGrouped };
  }, [allTasks, weekOffset]);

  // --- Week Navigation --- 
  const handleWeekChange = (offsetChange: number) => {
    setWeekOffset(prev => prev + offsetChange);
  };

  // --- Render Logic --- 

  if (authLoading || loading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh] bg-gray-50">
        <Spinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8 flex items-center justify-center">
        <div className="max-w-2xl w-full bg-white rounded-xl shadow-lg p-8 text-center">
          <div className="mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" className="mx-auto h-14 w-14 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <Alert message={error} type="error" />
          <Link href="/dashboard" className="mt-6 inline-flex items-center px-5 py-2.5 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors">
            Quay lại Dashboard
          </Link>
        </div>
      </div>
    );
  }

  if (!learningPath) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8 flex items-center justify-center">
        <div className="max-w-2xl w-full bg-white rounded-xl shadow-lg p-8 text-center">
          <div className="mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" className="mx-auto h-14 w-14 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <Alert message="Không có dữ liệu lộ trình học tập." type="info" />
          <Link href="/create-path" className="mt-6 inline-flex items-center px-5 py-2.5 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors">
            Tạo lộ trình mới
          </Link>
        </div>
      </div>
    );
  }

  // Refined task item renderer
  const renderTaskItem = (task: Task, isToday: boolean = false) => (
    <li key={task.id} className="group">
      <div className={`flex items-center justify-between p-4 rounded-xl transition-all duration-200 ${task.completed
        ? 'bg-green-50 border border-green-200'
        : 'bg-white border border-gray-200 hover:border-indigo-200 hover:shadow-md'
        } ${isToday ? 'shadow-sm' : ''}`}>
        <div className="flex items-start space-x-3 flex-1">
          <div className={`w-5 h-5 mt-0.5 flex-shrink-0 rounded-full border ${task.completed
            ? 'bg-green-100 border-green-400'
            : 'bg-white border-gray-300'
            } flex items-center justify-center`}>
            {task.completed && (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            )}
          </div>
          <span className={`text-sm ${task.completed ? 'line-through text-gray-500' : 'text-gray-800'}`}>
            {task.title}
          </span>
        </div>
        <button
          onClick={() => handleToggleTask(task.id, task.completed)}
          className={`px-4 py-1.5 ml-3 rounded-md text-xs font-semibold uppercase tracking-wide transition-all 
            ${task.completed
              ? 'bg-white text-gray-500 border border-gray-300 hover:bg-gray-100'
              : 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm'
            }`}
        >
          {task.completed ? 'Hủy' : 'Hoàn thành'}
        </button>
      </div>
    </li>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto py-12 px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Header section with week navigation */}
        <div className="bg-white rounded-xl shadow-md p-5 flex flex-col sm:flex-row justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4 sm:mb-0">Quản lý Nhiệm vụ</h1>

          <div className="flex items-center bg-gray-50 p-1.5 rounded-lg border border-gray-200">
            <button
              onClick={() => handleWeekChange(-1)}
              className="p-2 rounded-md hover:bg-gray-100 text-gray-600 hover:text-gray-800 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500"
              aria-label="Tuần trước"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <div className="text-center mx-4">
              <p className="font-semibold text-sm text-gray-800">
                {format(currentWeekStart, 'dd/MM')} - {format(currentWeekEnd, 'dd/MM/yyyy')}
              </p>
              {weekOffset === 0 && (
                <p className="text-xs font-medium text-indigo-600">Tuần hiện tại</p>
              )}
            </div>

            <button
              onClick={() => handleWeekChange(1)}
              className="p-2 rounded-md hover:bg-gray-100 text-gray-600 hover:text-gray-800 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500"
              aria-label="Tuần sau"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>

        {/* Main content grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
          {/* Today's tasks section */}
          <section aria-labelledby="todays-tasks-heading" className="lg:col-span-1 space-y-4">
            <div className="flex items-center gap-2 px-1">
              <h2 id="todays-tasks-heading" className="text-xl font-semibold text-gray-800">Hôm Nay</h2>
              <span className="text-sm font-medium bg-indigo-100 text-indigo-800 py-0.5 px-2 rounded-full">
                {format(new Date(), 'dd/MM')}
              </span>
            </div>

            <div className="bg-white p-5 rounded-xl shadow-md">
              {todayTasks.length > 0 ? (
                <ul className="space-y-3">
                  {todayTasks.map(task => renderTaskItem(task, true))}
                </ul>
              ) : (
                <div className="text-center py-10">
                  <svg xmlns="http://www.w3.org/2000/svg" className="mx-auto h-14 w-14 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="mt-4 text-sm text-gray-500 font-medium">Tuyệt vời! Không có nhiệm vụ nào cho hôm nay.</p>
                </div>
              )}
            </div>
          </section>

          {/* Week's tasks section */}
          <section aria-labelledby="weeks-tasks-heading" className="lg:col-span-2 space-y-4">
            <h2 id="weeks-tasks-heading" className="text-xl font-semibold text-gray-800 px-1">Tuần Này</h2>

            {Object.keys(currentWeekTasksGrouped).length > 0 ? (
              <div className="space-y-4">
                {Object.entries(currentWeekTasksGrouped).map(([dateStr, tasks]) => {
                  const dateObj = parseISO(dateStr);
                  if (isSameDay(dateObj, new Date())) return null;

                  const formattedDate = dateObj instanceof Date && !isNaN(dateObj.valueOf())
                    ? format(dateObj, 'EEEE, dd/MM/yyyy', { locale: vi })
                    : 'Ngày không hợp lệ';

                  return (
                    <div key={dateStr} className="bg-white p-5 rounded-xl shadow-md">
                      <h3 className="text-md font-semibold mb-4 text-indigo-700 border-b border-indigo-100 pb-2.5">
                        {formattedDate}
                      </h3>
                      <ul className="space-y-3">
                        {tasks.map(task => renderTaskItem(task))}
                      </ul>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="bg-white p-8 rounded-xl shadow-md text-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="mx-auto h-16 w-16 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p className="mt-4 text-gray-500 font-medium">
                  Không có nhiệm vụ nào được lên lịch cho phần còn lại của tuần này.
                </p>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}