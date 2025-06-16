import React from 'react';
import { BiUserCheck, BiTask, BiTime, BiCalendarCheck } from 'react-icons/bi';
import StatCard from './StatCard';

const DashboardStats: React.FC = () => {
  const stats = [
    {
      title: 'Total Tasks',
      value: '152',
      icon: <BiTask size={20} />,
      trend: {
        value: '12%',
        isPositive: true
      }
    },
    {
      title: 'Completed Tasks',
      value: '86',
      icon: <BiCalendarCheck size={20} />,
      trend: {
        value: '8%',
        isPositive: true
      }
    },
    {
      title: 'Pending Tasks',
      value: '43',
      icon: <BiTime size={20} />,
      trend: {
        value: '5%',
        isPositive: false
      }
    },
    {
      title: 'Active Users',
      value: '12',
      icon: <BiUserCheck size={20} />,
      trend: {
        value: '18%',
        isPositive: true
      }
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => (
        <StatCard
          key={index}
          title={stat.title}
          value={stat.value}
          icon={stat.icon}
          trend={stat.trend}
        />
      ))}
    </div>
  );
};

export default DashboardStats; 