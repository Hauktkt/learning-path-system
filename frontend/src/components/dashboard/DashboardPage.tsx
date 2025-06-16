import React from 'react';
import StatCard from './StatCard';
import RecentTasks from './RecentTasks';
import {
  BiDollar,
  BiNotepad,
  BiUser,
  BiCheckCircle
} from 'react-icons/bi';

const DashboardPage: React.FC = () => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Doanh thu"
          value="$24,000"
          icon={<BiDollar className="text-blue-500" />}
          trend={12.5}
          trendLabel="so với tháng trước"
        />
        <StatCard
          title="Dự án"
          value="42"
          icon={<BiNotepad className="text-green-500" />}
          trend={-2.7}
          trendLabel="so với tháng trước"
        />
        <StatCard
          title="Người dùng"
          value="1,258"
          icon={<BiUser className="text-purple-500" />}
          trend={8.1}
          trendLabel="so với tháng trước"
        />
        <StatCard
          title="Hoàn thành"
          value="85%"
          icon={<BiCheckCircle className="text-yellow-500" />}
          trend={5.4}
          trendLabel="so với tháng trước"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold mb-4">Thống kê gần đây</h2>
          <div className="h-80 flex items-center justify-center bg-gray-50 rounded-lg">
            {/* Chart component would go here */}
            <p className="text-gray-500">Biểu đồ thống kê</p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold mb-4">Công việc gần đây</h2>
          <RecentTasks />
        </div>
      </div>
    </div>
  );
};

export default DashboardPage; 