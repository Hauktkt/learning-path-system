import React from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, BarElement, ArcElement } from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface ChartSectionProps {
  className?: string;
}

export const ChartSection: React.FC<ChartSectionProps> = ({ className }) => {
  // Sample data for progress chart
  const progressData = {
    labels: ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'],
    datasets: [
      {
        label: 'Công việc hoàn thành',
        data: [5, 8, 12, 7, 15, 18, 13],
        borderColor: 'rgba(99, 102, 241, 1)',
        backgroundColor: 'rgba(99, 102, 241, 0.2)',
        tension: 0.3,
      },
    ],
  };

  // Sample data for tasks by category
  const categoryData = {
    labels: ['Học tập', 'Công việc', 'Cá nhân', 'Khác'],
    datasets: [
      {
        label: 'Công việc theo danh mục',
        data: [35, 25, 22, 18],
        backgroundColor: [
          'rgba(99, 102, 241, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
        ],
        borderColor: [
          'rgba(99, 102, 241, 1)',
          'rgba(59, 130, 246, 1)',
          'rgba(16, 185, 129, 1)',
          'rgba(245, 158, 11, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  // Sample data for weekly completion
  const weeklyData = {
    labels: ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'],
    datasets: [
      {
        label: 'Công việc theo ngày',
        data: [4, 8, 6, 9, 7, 5, 3],
        backgroundColor: 'rgba(99, 102, 241, 0.7)',
      },
    ],
  };

  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 gap-6 ${className}`}>
      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
        <h3 className="text-lg font-medium mb-4">Tiến độ công việc</h3>
        <Line
          data={progressData}
          options={{
            responsive: true,
            plugins: {
              legend: {
                position: 'top' as const,
              },
            },
          }}
        />
      </div>

      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
        <h3 className="text-lg font-medium mb-4">Phân loại công việc</h3>
        <div className="flex justify-center" style={{ height: '200px' }}>
          <Doughnut
            data={categoryData}
            options={{
              responsive: true,
              plugins: {
                legend: {
                  position: 'bottom' as const,
                },
              },
              maintainAspectRatio: false,
            }}
          />
        </div>
      </div>

      <div className="md:col-span-2 bg-white p-4 rounded-xl shadow-sm border border-gray-100">
        <h3 className="text-lg font-medium mb-4">Hoàn thành theo ngày</h3>
        <Bar
          data={weeklyData}
          options={{
            responsive: true,
            plugins: {
              legend: {
                display: false,
              },
            },
          }}
        />
      </div>
    </div>
  );
};

export default ChartSection; 