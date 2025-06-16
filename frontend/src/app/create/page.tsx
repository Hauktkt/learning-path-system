'use client';

import React, { useState } from 'react';
import { generateLearningPath } from '@/api/learningPathService';
import { LearningPathParams, LearningPathResponse } from '@/types';
import { PathSaver } from '@/components/LearningPath/PathSaver';

export default function CreatePage() {
  const [currentStep, setCurrentStep] = useState<'form' | 'result'>('form');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [learningPath, setLearningPath] = useState<LearningPathResponse | null>(null);

  // Form state
  const [formState, setFormState] = useState<{
    field: string;
    level: string;
    duration: number;
    daily_hours: number;
    interests: string[];
  }>({
    field: '',
    level: 'Beginner',
    duration: 2,
    daily_hours: 2,
    interests: []
  });

  // Cập nhật state khi người dùng nhập liệu
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;

    if (name === 'interests') {
      // Xử lý interests dạng array
      const interestsArray = value.split(',').map(item => item.trim()).filter(Boolean);
      setFormState(prev => ({ ...prev, [name]: interestsArray }));
    } else if (name === 'duration' || name === 'daily_hours') {
      // Chuyển đổi sang số
      setFormState(prev => ({ ...prev, [name]: Number(value) }));
    } else {
      // Xử lý chuỗi thông thường
      setFormState(prev => ({ ...prev, [name]: value }));
    }
  };

  // Xử lý checkbox interests
  const handleInterestChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = e.target;

    setFormState(prev => {
      if (checked) {
        // Thêm interest nếu được chọn
        return { ...prev, interests: [...prev.interests, value] };
      } else {
        // Xóa interest nếu bỏ chọn
        return { ...prev, interests: prev.interests.filter(interest => interest !== value) };
      }
    });
  };

  // Submit form
  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Kiểm tra dữ liệu
    if (!formState.field) {
      setError('Vui lòng nhập lĩnh vực học tập');
      return;
    }
    if (!formState.level) {
      setError('Vui lòng chọn trình độ');
      return;
    }
    if (!formState.duration) {
      setError('Vui lòng chọn thời gian học');
      return;
    }
    if (!formState.daily_hours) {
      setError('Vui lòng chọn số giờ học mỗi ngày');
      return;
    }
    if (formState.interests.length === 0) {
      setError('Vui lòng chọn ít nhất một sở thích');
      return;
    }

    setIsLoading(true);
    setError(null);

    // Log dữ liệu để debug
    console.log("[DEBUG] Form data:", JSON.stringify(formState));

    try {
      // Gọi API tạo lộ trình
      const params: LearningPathParams = {
        field: formState.field,
        level: formState.level,
        duration: formState.duration,
        daily_hours: formState.daily_hours,
        interests: formState.interests
      };

      console.log("[DEBUG] API params:", JSON.stringify(params));

      const result = await generateLearningPath(params);
      console.log("[DEBUG] API result:", JSON.stringify(result));

      if (!result || !result.learning_path) {
        throw new Error("Không nhận được kết quả hợp lệ từ API");
      }

      // Lưu kết quả và chuyển sang trang kết quả
      setLearningPath(result);
      setCurrentStep('result');
    } catch (error: any) {
      console.error('[DEBUG] Error generating learning path:', error);
      console.error('[DEBUG] Error details:', error.response?.data || error.message);

      // Hiển thị thông báo lỗi thân thiện với người dùng
      const errorMessage = error.response?.data?.error || error.message || 'Đã xảy ra lỗi không xác định';
      setError(`Có lỗi xảy ra khi tạo lộ trình: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePathSaved = (pathId: number) => {
    // Redirect to path detail page
    window.location.href = `/learning-paths/${pathId}`;
  };

  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Tạo lộ trình học tập</h1>

      {currentStep === 'form' ? (
        <div className="max-w-2xl mx-auto">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleFormSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-1">Lĩnh vực học tập <span className="text-red-500">*</span></label>
              <input
                type="text"
                name="field"
                value={formState.field}
                onChange={handleInputChange}
                placeholder="VD: Python programming, Web development..."
                className="w-full px-4 py-2 border rounded-md"
                disabled={isLoading}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Trình độ <span className="text-red-500">*</span></label>
              <select
                name="level"
                value={formState.level}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border rounded-md"
                disabled={isLoading}
                required
              >
                <option value="">-- Chọn trình độ --</option>
                <option value="Beginner">Beginner (Người mới bắt đầu)</option>
                <option value="Intermediate">Intermediate (Trung cấp)</option>
                <option value="Advanced">Advanced (Nâng cao)</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">Chọn trình độ phù hợp với kiến thức hiện tại của bạn</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Thời gian học (tháng) <span className="text-red-500">*</span></label>
              <select
                name="duration"
                value={formState.duration.toString()}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border rounded-md"
                disabled={isLoading}
                required
              >
                <option value="">-- Chọn thời gian --</option>
                <option value="1">1 tháng</option>
                <option value="2">2 tháng</option>
                <option value="3">3 tháng</option>
                <option value="6">6 tháng</option>
                <option value="12">12 tháng</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">Khoảng thời gian bạn muốn hoàn thành lộ trình</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Số giờ học mỗi ngày <span className="text-red-500">*</span></label>
              <select
                name="daily_hours"
                value={formState.daily_hours.toString()}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border rounded-md"
                disabled={isLoading}
                required
              >
                <option value="">-- Chọn số giờ --</option>
                <option value="1">1 giờ/ngày</option>
                <option value="2">2 giờ/ngày</option>
                <option value="3">3 giờ/ngày</option>
                <option value="4">4 giờ/ngày</option>
                <option value="5">5 giờ/ngày</option>
                <option value="6">6 giờ/ngày</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">Số giờ bạn có thể dành cho việc học mỗi ngày</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Sở thích <span className="text-red-500">*</span></label>
              <div className="grid grid-cols-2 gap-2 mt-1">
                <div className="flex items-start">
                  <input
                    type="checkbox"
                    id="interest-web"
                    value="Web Development"
                    checked={formState.interests.includes('Web Development')}
                    onChange={handleInterestChange}
                    className="mt-1 mr-2"
                  />
                  <label htmlFor="interest-web">Web Development</label>
                </div>
                <div className="flex items-start">
                  <input
                    type="checkbox"
                    id="interest-data"
                    value="Data Science"
                    checked={formState.interests.includes('Data Science')}
                    onChange={handleInterestChange}
                    className="mt-1 mr-2"
                  />
                  <label htmlFor="interest-data">Data Science</label>
                </div>
                <div className="flex items-start">
                  <input
                    type="checkbox"
                    id="interest-mobile"
                    value="Mobile app"
                    checked={formState.interests.includes('Mobile app')}
                    onChange={handleInterestChange}
                    className="mt-1 mr-2"
                  />
                  <label htmlFor="interest-mobile">Mobile app</label>
                </div>
                <div className="flex items-start">
                  <input
                    type="checkbox"
                    id="interest-ai"
                    value="AI/ML"
                    checked={formState.interests.includes('AI/ML')}
                    onChange={handleInterestChange}
                    className="mt-1 mr-2"
                  />
                  <label htmlFor="interest-ai">AI/ML</label>
                </div>
                <div className="flex items-start">
                  <input
                    type="checkbox"
                    id="interest-cloud"
                    value="Cloud services"
                    checked={formState.interests.includes('Cloud services')}
                    onChange={handleInterestChange}
                    className="mt-1 mr-2"
                  />
                  <label htmlFor="interest-cloud">Cloud services</label>
                </div>
                <div className="flex items-start">
                  <input
                    type="checkbox"
                    id="interest-iot"
                    value="IoT"
                    checked={formState.interests.includes('IoT')}
                    onChange={handleInterestChange}
                    className="mt-1 mr-2"
                  />
                  <label htmlFor="interest-iot">IoT</label>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-2">Chọn lĩnh vực bạn quan tâm để lộ trình được cá nhân hóa</p>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? 'Đang tạo...' : 'Tạo lộ trình'}
            </button>
          </form>
        </div>
      ) : (
        <div className="max-w-3xl mx-auto">
          {learningPath && (
            <>
              <div className="bg-white shadow-md rounded-lg p-6 mb-6">
                <h2 className="text-2xl font-bold mb-4">{learningPath.learning_path.field}</h2>
                <p className="text-lg mb-4">{learningPath.learning_path.overview}</p>

                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-gray-50 p-4 rounded">
                    <span className="block text-sm text-gray-500">Trình độ</span>
                    <span className="font-medium">{learningPath.learning_path.level}</span>
                  </div>
                  <div className="bg-gray-50 p-4 rounded">
                    <span className="block text-sm text-gray-500">Thời gian</span>
                    <span className="font-medium">{learningPath.learning_path.duration} tháng</span>
                  </div>
                  <div className="bg-gray-50 p-4 rounded">
                    <span className="block text-sm text-gray-500">Số giờ mỗi ngày</span>
                    <span className="font-medium">{learningPath.learning_path.daily_hours} giờ</span>
                  </div>
                  <div className="bg-gray-50 p-4 rounded">
                    <span className="block text-sm text-gray-500">Sở thích</span>
                    <span className="font-medium">{learningPath.learning_path.interests.join(', ')}</span>
                  </div>
                </div>

                <PathSaver
                  learningPathData={learningPath}
                  onPathSaved={handlePathSaved}
                />

                <button
                  onClick={() => setCurrentStep('form')}
                  className="mt-4 text-blue-600 hover:underline"
                >
                  Quay lại form
                </button>
              </div>

              <div className="mb-8">
                <h3 className="text-xl font-bold mb-4">Giai đoạn học tập</h3>
                <div className="space-y-4">
                  {learningPath.learning_path.phases.map((phase, index) => (
                    <div key={index} className="bg-white shadow-md rounded-lg p-4">
                      <h4 className="font-bold">{phase.name}</h4>
                      <p className="text-sm text-gray-500 mb-2">Thời gian: {phase.duration} ngày</p>
                      <ul className="list-disc pl-5 space-y-1">
                        {phase.tasks.map((task, taskIndex) => (
                          <li key={taskIndex}>{task}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mb-8">
                <h3 className="text-xl font-bold mb-4">Khóa học</h3>
                <div className="space-y-4">
                  {learningPath.learning_path.courses.map((course, index) => (
                    <div key={index} className="bg-white shadow-md rounded-lg p-4">
                      <h4 className="font-bold">{course.title}</h4>
                      <p className="text-sm text-gray-500 mb-2">
                        Trình độ: {course.level} | Thời gian: {course.duration} giờ
                      </p>
                      <div>
                        <span className="font-medium">Chủ đề:</span>
                        <ul className="list-disc pl-5 mt-1 space-y-1">
                          {course.topics.map((topic, topicIndex) => (
                            <li key={topicIndex}>{topic}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mb-8">
                <h3 className="text-xl font-bold mb-4">Dự án thực hành</h3>
                <ul className="list-disc pl-5 bg-white shadow-md rounded-lg p-4 space-y-2">
                  {learningPath.learning_path.projects.map((project, index) => (
                    <li key={index}>{project}</li>
                  ))}
                </ul>
              </div>

              <div className="mb-8">
                <h3 className="text-xl font-bold mb-4">Mẹo học tập</h3>
                <ul className="list-disc pl-5 bg-white shadow-md rounded-lg p-4 space-y-2">
                  {learningPath.learning_path.tips.map((tip, index) => (
                    <li key={index}>{tip}</li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="text-xl font-bold mb-4">Tài nguyên học tập</h3>
                <ul className="list-disc pl-5 bg-white shadow-md rounded-lg p-4 space-y-2">
                  {learningPath.learning_path.resources.map((resource, index) => (
                    <li key={index}>{resource}</li>
                  ))}
                </ul>
              </div>
            </>
          )}
        </div>
      )}
    </main>
  );
} 