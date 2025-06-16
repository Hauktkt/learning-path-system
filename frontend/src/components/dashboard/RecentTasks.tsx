import React from 'react';
import { BiCheck, BiX } from 'react-icons/bi';

interface Task {
  id: number;
  title: string;
  status: 'completed' | 'pending' | 'cancelled';
  date: string;
  assignee: string;
}

const RecentTasks: React.FC = () => {
  // Sample data - in a real app, this would come from an API
  const tasks: Task[] = [
    {
      id: 1,
      title: 'Hoàn thành báo cáo tài chính Q2',
      status: 'completed',
      date: '24/06/2023',
      assignee: 'Nguyễn Văn A',
    },
    {
      id: 2,
      title: 'Thiết kế giao diện trang chủ mới',
      status: 'pending',
      date: '28/06/2023',
      assignee: 'Trần Thị B',
    },
    {
      id: 3,
      title: 'Tích hợp API thanh toán',
      status: 'pending',
      date: '30/06/2023',
      assignee: 'Lê Văn C',
    },
    {
      id: 4,
      title: 'Cập nhật tài liệu hướng dẫn người dùng',
      status: 'cancelled',
      date: '22/06/2023',
      assignee: 'Phạm Thị D',
    },
    {
      id: 5,
      title: 'Kiểm tra lỗi trên phiên bản di động',
      status: 'completed',
      date: '26/06/2023',
      assignee: 'Hoàng Văn E',
    },
  ];

  const getStatusBadge = (status: Task['status']) => {
    switch (status) {
      case 'completed':
        return (
          <span className="flex items-center px-2 py-1 text-xs rounded-full text-green-800 bg-green-100">
            <BiCheck className="mr-1" />
            Hoàn thành
          </span>
        );
      case 'pending':
        return (
          <span className="flex items-center px-2 py-1 text-xs rounded-full text-yellow-800 bg-yellow-100">
            <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd"></path>
            </svg>
            Đang chờ
          </span>
        );
      case 'cancelled':
        return (
          <span className="flex items-center px-2 py-1 text-xs rounded-full text-red-800 bg-red-100">
            <BiX className="mr-1" />
            Đã hủy
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Nhiệm vụ
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Trạng thái
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Ngày
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Người thực hiện
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {tasks.map((task) => (
            <tr key={task.id}>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900">{task.title}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {getStatusBadge(task.status)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-500">{task.date}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-500">{task.assignee}</div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default RecentTasks; 