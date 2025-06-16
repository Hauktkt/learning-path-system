import React, { ReactNode } from 'react';
import { BiUpArrowAlt, BiDownArrowAlt } from 'react-icons/bi';

interface StatCardProps {
  title: string;
  value: string;
  icon: ReactNode;
  trend?: {
    value: string;
    isPositive: boolean;
  };
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, trend }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <h3 className="text-gray-500 text-sm font-medium">{title}</h3>
        <div className="text-gray-400">{icon}</div>
      </div>
      <div className="mt-2">
        <p className="text-3xl font-bold text-gray-900">{value}</p>
        {trend && (
          <div className="flex items-center mt-2">
            {trend.isPositive ? (
              <BiUpArrowAlt className="text-green-500" />
            ) : (
              <BiDownArrowAlt className="text-red-500" />
            )}
            <span className={`text-sm ml-1 ${trend.isPositive ? 'text-green-500' : 'text-red-500'}`}>
              {trend.value}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default StatCard; 