"use client";

import { useEffect, useState } from "react";
import { StoredLearningPath, LearningPathResponse, WeeklyStats, LearningPath, Task } from "@/types";
import { useRouter } from "next/navigation";
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from "chart.js";
import { Doughnut, Bar } from "react-chartjs-2";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import * as learningPathService from "@/api/learningPathService";
import Spinner from "@/components/Spinner";
import Alert from "@/components/Alert";
import { format, parseISO, isSameDay } from 'date-fns';
import { vi } from 'date-fns/locale';

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

// Helper component for Stat Card
interface StatCardProps {
  title: string;
  value: string | number;
  unit?: string;
  description?: string;
  children?: React.ReactNode; // For charts or other content
}
const StatCard: React.FC<StatCardProps> = ({ title, value, unit, description, children }) => (
  <div className="bg-white p-5 rounded-lg shadow">
    <h3 className="text-base font-medium text-gray-500 mb-1 truncate">{title}</h3>
    <div className="flex items-baseline gap-x-2 mb-2">
      <span className="text-3xl font-bold tracking-tight text-gray-900">{value}</span>
      {unit && <span className="text-sm font-medium text-gray-500">{unit}</span>}
    </div>
    {description && <p className="text-sm text-gray-500">{description}</p>}
    {children && <div className="mt-4">{children}</div>}
  </div>
);

// Helper component for Section
interface SectionProps {
  title: string;
  children: React.ReactNode;
  titleClassName?: string;
  containerClassName?: string;
}
const Section: React.FC<SectionProps> = ({ title, children, titleClassName = "text-xl font-semibold text-gray-800 mb-4", containerClassName = "bg-white p-6 rounded-lg shadow-md" }) => (
  <section className={containerClassName}>
    <h2 className={titleClassName}>{title}</h2>
    {children}
  </section>
);

export default function Dashboard() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [savedLearningPath, setSavedLearningPath] = useState<StoredLearningPath | null>(null);
  const [generatedPath, setGeneratedPath] = useState<LearningPath | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [completedTasks, setCompletedTasks] = useState<number>(0);
  const [totalTasks, setTotalTasks] = useState<number>(0);
  const [todayTasksCount, setTodayTasksCount] = useState<number>(0);
  const [weeklyStats, setWeeklyStats] = useState<WeeklyStats | null>(null);
  const [activePathId, setActivePathId] = useState<number | null>(null);

  const fetchDashboardData = async (forceFetchSaved: boolean = false) => {
    if (!user) return;
    setLoading(true);
    setError("");
    setInfo("");

    let fetchedPath: StoredLearningPath | null = null;
    let statsData: WeeklyStats | null = null;
    let generatedPathFromStorage: LearningPath | null = null;
    let savedPathIdFromStorage: number | null = activePathId;

    if (!forceFetchSaved && !savedPathIdFromStorage) {
      const idStr = localStorage.getItem("savedLearningPathId");
      if (idStr) {
        savedPathIdFromStorage = parseInt(idStr, 10);
        setActivePathId(savedPathIdFromStorage);
      }
    }

    try {
      // First try to get path from localStorage ID
      if (savedPathIdFromStorage) {
        try {
          fetchedPath = await learningPathService.getLearningPathById(savedPathIdFromStorage);
          setSavedLearningPath(fetchedPath);
          setGeneratedPath(null);
          localStorage.removeItem("generatedLearningPath");
        } catch (detailError: any) {
          console.error(`Error fetching saved path ${savedPathIdFromStorage}:`, detailError);

          // Nếu lỗi xác thực (401) sẽ được xử lý bởi interceptor
          if (detailError.response && detailError.response.status !== 401) {
            setError(`Không thể tải chi tiết lộ trình đã lưu (ID: ${savedPathIdFromStorage}). Lỗi: ${detailError.message}`);
            // Chỉ xóa ID nếu không phải lỗi xác thực - lỗi xác thực sẽ được xử lý riêng
            if (detailError.response && detailError.response.status === 404) {
              localStorage.removeItem("savedLearningPathId");
              setActivePathId(null);
            }
          }
        }
      }

      // If no path found through localStorage ID, try to get the user's paths from the API
      if (!fetchedPath) {
        try {
          const userPaths = await learningPathService.getUserLearningPaths();

          if (userPaths && userPaths.length > 0) {
            // Get the most recently created path
            const mostRecentPath = userPaths.sort((a, b) =>
              new Date(b.created_at || "").getTime() - new Date(a.created_at || "").getTime()
            )[0];

            try {
              fetchedPath = await learningPathService.getLearningPathById(mostRecentPath.id);
              setSavedLearningPath(fetchedPath);
              setActivePathId(mostRecentPath.id);
              localStorage.setItem("savedLearningPathId", mostRecentPath.id.toString());
              setGeneratedPath(null);
              localStorage.removeItem("generatedLearningPath");
            } catch (pathDetailError: any) {
              console.error(`Error fetching most recent path details:`, pathDetailError);
              if (pathDetailError.response && pathDetailError.response.status !== 401) {
                setError(`Không thể tải chi tiết lộ trình gần đây nhất. Lỗi: ${pathDetailError.message}`);
              }
            }
          }
        } catch (pathsError: any) {
          console.error("Error fetching user's learning paths:", pathsError);
          if (pathsError.response && pathsError.response.status !== 401) {
            setError(`Không thể tải danh sách lộ trình. Lỗi: ${pathsError.message}`);
          }
        }
      }

      // If still no path, check for a generated path in localStorage
      if (!fetchedPath) {
        const generatedPathJson = localStorage.getItem("generatedLearningPath");
        if (generatedPathJson) {
          try {
            const savedResponse = JSON.parse(generatedPathJson) as LearningPathResponse;
            if (savedResponse?.learning_path) {
              generatedPathFromStorage = savedResponse.learning_path;
              setGeneratedPath(generatedPathFromStorage);
              setSavedLearningPath(null);
              setInfo("Bạn có một lộ trình vừa tạo chưa được lưu. Lưu lại để theo dõi tiến độ.");
            }
          } catch (parseError) {
            console.error("Error parsing generated path from localStorage:", parseError);
            localStorage.removeItem("generatedLearningPath");
          }
        }
      }

      // Get weekly stats
      try {
        statsData = await learningPathService.getWeeklyStats();
        setWeeklyStats(statsData);
      } catch (statsError: any) {
        console.error("Error fetching weekly stats:", statsError);
        if (statsError.response && statsError.response.status !== 401) {
          // Không hiển thị lỗi này cho người dùng, chỉ ghi log
        }
      }

      // Calculate statistics if we have a saved path
      if (fetchedPath) {
        setSavedLearningPath(fetchedPath);
        let completedCount = 0;
        let totalCount = 0;
        const today = new Date();
        let todayCount = 0;
        if (fetchedPath.tasks_by_phase) {
          Object.values(fetchedPath.tasks_by_phase).forEach(tasks => {
            totalCount += tasks.length;
            completedCount += tasks.filter(task => task.completed).length;
            todayCount += tasks.filter(task => {
              if (!task.date) return false;
              try {
                return isSameDay(parseISO(task.date), today);
              } catch (e) { return false; }
            }).length;
          });
        }
        setTodayTasksCount(todayCount);
        setTotalTasks(totalCount);
        setCompletedTasks(completedCount);
      } else {
        setTotalTasks(0);
        setCompletedTasks(0);
        setTodayTasksCount(0);
      }

      if (!fetchedPath && !generatedPathFromStorage && !error) {
        setInfo("Bạn chưa có lộ trình nào. Hãy tạo một lộ trình mới!");
      }

    } catch (error: any) {
      console.error("Error loading dashboard data:", error);
      if (error.response && error.response.status === 401) {
        // Lỗi xác thực đã được interceptor xử lý
      } else {
        setError(`Lỗi tải dữ liệu dashboard: ${error.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
      return;
    }
    if (user) {
      const idStr = localStorage.getItem("savedLearningPathId");
      if (idStr) {
        setActivePathId(parseInt(idStr, 10));
      }
      fetchDashboardData();
    }
  }, [user, authLoading, router]);

  const handleToggleTask = async (taskId: number, currentStatus: boolean) => {
    if (!savedLearningPath) return;

    const updatedPath = JSON.parse(JSON.stringify(savedLearningPath)) as StoredLearningPath;
    let taskFound = false;
    let originalStatus = false;
    let phaseName: string | null = null;
    let taskIndex = -1;

    for (const currentPhaseName in updatedPath.tasks_by_phase) {
      const tasksInPhase = updatedPath.tasks_by_phase[currentPhaseName];
      if (Array.isArray(tasksInPhase)) {
        const foundIndex = tasksInPhase.findIndex(t => t.id === taskId);
        if (foundIndex !== -1) {
          originalStatus = tasksInPhase[foundIndex].completed;
          tasksInPhase[foundIndex].completed = !currentStatus;
          taskFound = true;
          phaseName = currentPhaseName;
          taskIndex = foundIndex;
          break;
        }
      }
    }

    if (taskFound) {
      setSavedLearningPath(updatedPath);
      setCompletedTasks(prev => currentStatus ? prev - 1 : prev + 1);
    }

    try {
      await learningPathService.toggleTaskCompletion(taskId);
    } catch (toggleError) {
      console.error("Error toggling task completion:", toggleError);
      setError("Lỗi cập nhật trạng thái nhiệm vụ.");
      if (taskFound && phaseName && taskIndex !== -1) {
        setSavedLearningPath(prevPath => {
          if (!prevPath) return null;
          const revertPath = JSON.parse(JSON.stringify(prevPath)) as StoredLearningPath;
          const tasksInPhase = revertPath.tasks_by_phase?.[phaseName!];
          if (Array.isArray(tasksInPhase) && tasksInPhase[taskIndex]) {
            tasksInPhase[taskIndex].completed = originalStatus;
          }
          return revertPath;
        });
        setCompletedTasks(prev => originalStatus ? prev + 1 : prev - 1);
      }
    }
  };

  const handleSaveGeneratedPath = async () => {
    if (!generatedPath || !user) return;

    const generatedPathJson = localStorage.getItem("generatedLearningPath");
    if (!generatedPathJson) {
      setError("Không tìm thấy dữ liệu lộ trình đã tạo trong localStorage.");
      return;
    }

    let pathResponse: LearningPathResponse;
    try {
      pathResponse = JSON.parse(generatedPathJson);
      if (!pathResponse || !pathResponse.learning_path) {
        throw new Error("Dữ liệu lộ trình trong localStorage không hợp lệ.")
      }
    } catch (parseError: any) {
      setError(`Lỗi đọc dữ liệu lộ trình từ localStorage: ${parseError.message}`);
      localStorage.removeItem("generatedLearningPath");
      return;
    }

    setIsSaving(true);
    setError("");
    setInfo("");

    try {
      console.log("Calling backend to save learning path:", pathResponse);
      const saveResponse = await learningPathService.createOrUpdateLearningPath(0, pathResponse);

      const newPathId = saveResponse.path_id;
      if (!newPathId) {
        throw new Error("API không trả về ID lộ trình sau khi lưu.");
      }

      console.log(`Backend saved path with ID: ${newPathId}`);

      setActivePathId(newPathId);
      setGeneratedPath(null);

      localStorage.setItem("savedLearningPathId", newPathId.toString());
      localStorage.removeItem("generatedLearningPath");

      setInfo("Đã lưu lộ trình thành công! Đang tải lại dữ liệu từ server...");

      await fetchDashboardData(true);

    } catch (saveError: any) {
      console.error("Error saving path via API:", saveError);
      setError(saveError.response?.data?.error || saveError.message || "Lỗi khi lưu lộ trình qua API.");
    } finally {
      setIsSaving(false);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <Spinner />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const displayPathData = savedLearningPath || generatedPath;
  const isSavedPath = !!savedLearningPath;

  if (!displayPathData) {
    return (
      <div className="max-w-lg mx-auto py-12 px-6 text-center bg-white rounded-lg shadow-md">
        {info && <Alert message={info} type="info" />}
        {error && <Alert message={error} type="error" />}
        {!info && !error && (
          <Alert message="Bạn chưa có lộ trình nào. Hãy tạo một lộ trình mới!" type="info" />
        )}
        <Link
          href="/create-path"
          className="mt-6 inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
        >
          Tạo lộ trình mới
        </Link>
      </div>
    );
  }

  const { field = "N/A", level = "N/A", duration = 0, daily_hours = 0 } = displayPathData as any;

  const progressChartData = isSavedPath ? {
    labels: ["Hoàn thành", "Còn lại"],
    datasets: [
      {
        data: [completedTasks, Math.max(0, totalTasks - completedTasks)],
        backgroundColor: ["#4F46E5", "#E5E7EB"],
        borderColor: ["#FFFFFF"], // White border for doughnut
        borderWidth: 2,
      },
    ],
  } : null;

  const weeklyChartData = {
    labels: weeklyStats?.labels ?? ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
    datasets: [
      {
        label: "Số giờ học",
        data: weeklyStats?.data ?? [0, 0, 0, 0, 0, 0, 0],
        backgroundColor: "#6366F1", // Indigo-500
        borderRadius: 4,
        barThickness: 15,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true, grid: { display: false } }, x: { grid: { display: false } } },
  };
  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '70%', // Make doughnut thinner
    plugins: { legend: { display: false }, tooltip: { enabled: true } }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-10 px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Bảng Điều Khiển</h1>
        </div>

        {error && <Alert message={error} type="error" />}
        {info && <Alert message={info} type="info" />}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow col-span-1 flex flex-col">
            <h2 className="text-lg font-semibold mb-4 text-gray-800">{isSavedPath ? 'Lộ trình hiện tại' : 'Lộ trình (Chưa lưu)'}</h2>

            <div className="space-y-2 mb-5 text-sm">
              <div className="flex justify-between"><span className="font-medium text-gray-600">Lĩnh vực:</span> <span className="text-gray-800 text-right">{field}</span></div>
              <div className="flex justify-between"><span className="font-medium text-gray-600">Trình độ:</span> <span className="text-gray-800 text-right">{level}</span></div>
              <div className="flex justify-between"><span className="font-medium text-gray-600">Thời gian:</span> <span className="text-gray-800 text-right">{duration} tháng</span></div>
              <div className="flex justify-between"><span className="font-medium text-gray-600">Giờ học:</span> <span className="text-gray-800 text-right">{daily_hours} giờ/ngày</span></div>
            </div>

            {isSavedPath && (
              <div className="mt-auto border-t border-gray-200 pt-5">
                <h3 className="text-base font-medium text-gray-500 mb-3 text-center">Tiến độ tổng quan</h3>
                {progressChartData && totalTasks > 0 ? (
                  <div className="relative w-36 h-36 md:w-40 md:h-40 mx-auto">
                    <Doughnut data={progressChartData} options={doughnutOptions} />
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-center pointer-events-none">
                      <span className="text-2xl font-bold text-gray-900">{Math.round((completedTasks / totalTasks) * 100)}%</span>
                      <span className="text-xs text-gray-500">Hoàn thành</span>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500 italic text-center text-sm mt-4">Chưa có dữ liệu tiến độ.</p>
                )}
                {totalTasks > 0 &&
                  <p className="mt-3 text-center text-sm text-gray-600">Đã xong {completedTasks} / {totalTasks} nhiệm vụ</p>
                }
              </div>
            )}
          </div>

          <div className="col-span-1 lg:col-span-2 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white p-5 rounded-lg shadow">
                <h3 className="text-base font-medium text-gray-500 mb-3 truncate">Giờ học Tuần Này</h3>
                {weeklyStats?.data && weeklyStats.data.some(d => d > 0) ? (
                  <div className="h-40">
                    <Bar data={weeklyChartData} options={chartOptions} />
                  </div>
                ) : (
                  <p className="text-gray-500 italic text-sm mt-2">Không có dữ liệu.</p>
                )}
              </div>
              <StatCard
                title="Chuỗi Ngày Học Liên Tục"
                value={weeklyStats?.overall_stats?.current_streak ?? 0}
                unit="ngày"
                description={weeklyStats?.overall_stats?.current_streak ? "Hãy duy trì đều đặn!" : "Bắt đầu học ngay!"}
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Section title="Nhiệm vụ Hôm Nay" containerClassName="bg-white p-5 rounded-lg shadow" titleClassName="text-base font-medium text-gray-500 mb-3">
                {isSavedPath ? (
                  <ul className="space-y-2">
                    {savedLearningPath?.tasks_by_phase?.[new Date().toISOString().split('T')[0]]
                      ?.filter(task => !task.completed)
                      .slice(0, 3)
                      .map((task) => (
                        <li key={task.id} className="flex items-center justify-between text-sm group">
                          <span className={`truncate mr-2 ${task.completed ? 'line-through text-gray-400' : 'text-gray-700'}`}>
                            {task.title}
                          </span>
                          <button
                            onClick={() => handleToggleTask(task.id, task.completed)}
                            className={`opacity-0 group-hover:opacity-100 transition-opacity ml-auto px-2 py-0.5 rounded text-xs font-medium focus:outline-none focus:ring-1 focus:ring-offset-1 ${task.completed
                              ? 'bg-gray-100 text-gray-500 hover:bg-gray-200 focus:ring-gray-300'
                              : 'bg-indigo-100 text-indigo-600 hover:bg-indigo-200 focus:ring-indigo-400'
                              }`}
                          >
                            {task.completed ? 'Hủy' : 'Xong'}
                          </button>
                        </li>
                      )) ?? <li className="text-sm text-gray-400 italic">Không có nhiệm vụ nào cho hôm nay.</li>}
                    {savedLearningPath?.tasks_by_phase?.[new Date().toISOString().split('T')[0]] &&
                      savedLearningPath.tasks_by_phase[new Date().toISOString().split('T')[0]].filter(t => !t.completed).length === 0 && (
                        <li className="text-sm text-gray-400 italic">Tuyệt vời! Đã hoàn thành hết nhiệm vụ hôm nay.</li>
                      )}
                    {!savedLearningPath?.tasks_by_phase?.[new Date().toISOString().split('T')[0]] && (
                      <li className="text-sm text-gray-400 italic">Không có nhiệm vụ nào cho hôm nay.</li>
                    )}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-400 italic">Lưu lộ trình để xem nhiệm vụ.</p>
                )}
                <div className="mt-3 text-right">
                  <Link href="/tasks" className="text-xs font-medium text-indigo-600 hover:text-indigo-800">
                    Xem tất cả &rarr;
                  </Link>
                </div>
              </Section>

              <StatCard
                title="Thành Tích"
                value="0"
                unit="thành tích"
                description="Tính năng sắp ra mắt"
              />
            </div>
          </div>
        </div>

        {isSavedPath && savedLearningPath?.tasks_by_phase && Object.keys(savedLearningPath.tasks_by_phase).length > 0 && (
          <Section title="Tổng quan Giai Đoạn Học Tập">
            <div className="space-y-6">
              {Object.entries(savedLearningPath.tasks_by_phase).map(([phaseName, tasks], index) => {
                const totalPhaseTasks = tasks.length;
                const completedPhaseTasks = tasks.filter(t => t.completed).length;
                const phaseProgress = totalPhaseTasks > 0 ? Math.round((completedPhaseTasks / totalPhaseTasks) * 100) : 0;

                return (
                  <div key={phaseName}>
                    <div className="flex justify-between items-baseline mb-1">
                      <h3 className="text-md font-medium text-gray-700">Giai đoạn {index + 1}: {phaseName.replace(/_/g, ' ')}</h3>
                      <span className="text-sm font-medium text-indigo-600">{phaseProgress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-indigo-600 h-2 rounded-full" style={{ width: `${phaseProgress}%` }}></div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">Hoàn thành: {completedPhaseTasks}/{totalPhaseTasks}</p>
                  </div>
                );
              })}
            </div>
          </Section>
        )}

        {!isSavedPath && generatedPath && (
          <div className="mt-8 text-center pb-8">
            <button
              onClick={handleSaveGeneratedPath}
              disabled={isSaving}
              className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-50 focus:ring-green-500 disabled:opacity-70 transition-colors"
            >
              {isSaving ? <Spinner /> : "Lưu Lộ Trình Này"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
} 