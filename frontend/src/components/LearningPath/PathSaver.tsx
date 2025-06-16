import React, { useState } from 'react';
import { LearningPathResponse } from '@/types';
import { saveLearningPath } from '@/api/learningPathService';

interface PathSaverProps {
  learningPathData: LearningPathResponse;
  onPathSaved?: (pathId: number) => void;
}

export const PathSaver: React.FC<PathSaverProps> = ({ learningPathData, onPathSaved }) => {
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const handleSavePath = async () => {
    if (!learningPathData) return;

    setIsSaving(true);
    setSaveError(null);

    console.log("Saving learning path data:", learningPathData);

    try {
      const result = await saveLearningPath(0, learningPathData);
      console.log("Save result:", result);

      alert('Lộ trình học tập đã được lưu thành công!');

      if (onPathSaved) {
        onPathSaved(result.path_id);
      }
    } catch (error: any) {
      console.error('Error saving learning path:', error);
      console.error('Error details:', error.response?.data || error.message);

      const errorMessage = error.response?.data?.error || error.message || 'Lỗi không xác định';
      setSaveError(errorMessage);

      alert(`Lỗi khi lưu lộ trình: ${errorMessage}. Vui lòng đảm bảo bạn đã đăng nhập.`);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="mt-6">
      {saveError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {saveError}
        </div>
      )}

      <button
        onClick={handleSavePath}
        disabled={isSaving}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        {isSaving ? 'Đang lưu...' : 'Lưu lộ trình học tập'}
      </button>
      <p className="text-sm text-gray-500 mt-2">
        Lưu lộ trình này để theo dõi tiến độ và nhận thông báo nhắc nhở.
      </p>
    </div>
  );
}; 