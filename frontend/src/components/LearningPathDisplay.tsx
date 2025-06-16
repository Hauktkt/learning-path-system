import { LearningPath } from "@/types";
import { useState } from "react";

interface LearningPathDisplayProps {
  learningPath: LearningPath;
}

export default function LearningPathDisplay({ learningPath }: LearningPathDisplayProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'phases' | 'courses' | 'projects' | 'resources'>('overview');

  return (
    <div className="space-y-6">
      {/* Header with basic info */}
      <div className="bg-gradient-to-r from-indigo-600 to-indigo-800 rounded-xl shadow-lg p-6 text-white">
        <h2 className="text-2xl font-bold mb-3">Lộ Trình: {learningPath.field}</h2>
        <div className="grid md:grid-cols-4 gap-4 mt-4">
          <div className="bg-white/10 p-3 rounded-lg backdrop-blur-sm">
            <span className="block text-sm opacity-80 mb-1">Lĩnh vực</span>
            <span className="font-semibold">{learningPath.field}</span>
          </div>
          <div className="bg-white/10 p-3 rounded-lg backdrop-blur-sm">
            <span className="block text-sm opacity-80 mb-1">Trình độ</span>
            <span className="font-semibold">{learningPath.level}</span>
          </div>
          <div className="bg-white/10 p-3 rounded-lg backdrop-blur-sm">
            <span className="block text-sm opacity-80 mb-1">Thời gian</span>
            <span className="font-semibold">{learningPath.duration} tháng</span>
          </div>
          <div className="bg-white/10 p-3 rounded-lg backdrop-blur-sm">
            <span className="block text-sm opacity-80 mb-1">Học mỗi ngày</span>
            <span className="font-semibold">{learningPath.daily_hours} giờ</span>
          </div>
        </div>
      </div>

      {/* Tab navigation */}
      <div className="bg-white rounded-xl shadow p-1 flex overflow-x-auto scrollbar-hide border border-gray-100">
        {[
          { id: 'overview', label: 'Tổng quan' },
          { id: 'phases', label: 'Giai đoạn' },
          { id: 'courses', label: 'Khóa học' },
          { id: 'projects', label: 'Dự án' },
          { id: 'resources', label: 'Tài liệu' },
        ].map((tab) => (
          <button
            key={tab.id}
            className={`px-4 py-2 rounded-lg font-medium text-sm flex-shrink-0 transition-colors ${activeTab === tab.id
              ? 'bg-indigo-100 text-indigo-800'
              : 'text-gray-600 hover:bg-gray-100'
              }`}
            onClick={() => setActiveTab(tab.id as any)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="bg-white rounded-xl shadow-md p-6">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3">Tổng quan lộ trình</h3>
              <p className="text-gray-700">{learningPath.overview}</p>
            </div>

            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3">Sở thích</h3>
              <div className="flex flex-wrap gap-2">
                {learningPath.interests.map((interest, index) => (
                  <span key={index} className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm">
                    {interest}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3">Kết quả mong đợi</h3>
              <div className="bg-indigo-50 p-4 rounded-lg">
                <ul className="space-y-2">
                  {[
                    "Hiểu và áp dụng được các kiến thức cơ bản về " + learningPath.field,
                    "Xây dựng được các dự án thực tế trong lĩnh vực " + learningPath.field,
                    "Có thể tự tin ứng tuyển vào các vị trí liên quan đến " + learningPath.field
                  ].map((result, idx) => (
                    <li key={idx} className="flex items-start">
                      <svg className="h-5 w-5 text-indigo-600 mr-2 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>{result}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Phases Tab */}
        {activeTab === 'phases' && (
          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Các giai đoạn học tập</h3>
            <div className="space-y-6">
              {learningPath.phases.map((phase, index) => (
                <div key={index} className="relative">
                  {/* Timeline connector */}
                  {index < learningPath.phases.length - 1 && (
                    <div className="absolute left-6 top-14 bottom-0 w-0.5 bg-indigo-200"></div>
                  )}

                  <div className="flex">
                    <div className="flex-shrink-0 mt-1">
                      <div className="flex items-center justify-center w-12 h-12 rounded-full bg-indigo-100 text-indigo-700 text-lg font-bold">
                        {index + 1}
                      </div>
                    </div>
                    <div className="ml-4 flex-grow">
                      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4 hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-center mb-2">
                          <h4 className="font-bold text-lg text-gray-800">{phase.name}</h4>
                          <span className="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded-full">
                            {phase.duration} ngày
                          </span>
                        </div>
                        <ul className="space-y-2 mt-3">
                          {phase.tasks.map((task, taskIndex) => (
                            <li key={taskIndex} className="flex items-start">
                              <div className="bg-gray-100 rounded-full p-1 mr-2 mt-0.5">
                                <svg className="h-3 w-3 text-indigo-600" fill="currentColor" viewBox="0 0 24 24">
                                  <circle cx="12" cy="12" r="10" />
                                </svg>
                              </div>
                              <span className="text-gray-700">{task}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Courses Tab */}
        {activeTab === 'courses' && (
          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Khóa học gợi ý</h3>
            <div className="grid md:grid-cols-2 gap-4">
              {learningPath.courses.map((course, index) => (
                <div key={index} className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow p-4">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="font-bold text-indigo-700">{course.title}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium 
                      ${course.level === 'Beginner' ? 'bg-green-100 text-green-800' :
                        course.level === 'Intermediate' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'}`}
                    >
                      {course.level}
                    </span>
                  </div>
                  <div className="mb-3">
                    <span className="text-sm text-gray-500">Thời lượng:</span>
                    <span className="text-sm font-medium ml-1">{course.duration} giờ</span>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-700 block mb-2">Chủ đề chính:</span>
                    <div className="flex flex-wrap gap-2">
                      {course.topics.map((topic, topicIndex) => (
                        <span key={topicIndex} className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-xs">
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Projects Tab */}
        {activeTab === 'projects' && (
          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Dự án thực hành</h3>
            <div className="space-y-4">
              {learningPath.projects.map((project, index) => (
                <div key={index} className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-4 border border-indigo-100">
                  <div className="flex items-center mb-2">
                    <div className="bg-indigo-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold mr-3">
                      {index + 1}
                    </div>
                    <h4 className="font-medium text-lg">{project}</h4>
                  </div>
                  <div className="ml-11">
                    <p className="text-gray-600 text-sm">
                      Dự án này sẽ giúp bạn áp dụng kiến thức đã học và xây dựng portfolio của mình.
                    </p>
                    <div className="mt-2 flex gap-2">
                      <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                        Thực hành
                      </span>
                      <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
                        Portfolio
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Resources Tab */}
        {activeTab === 'resources' && (
          <div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Tài liệu tham khảo</h3>
            <div className="grid md:grid-cols-2 gap-4">
              {learningPath.resources.map((resource, index) => (
                <div key={index} className="bg-white rounded-lg border border-gray-200 p-4 flex items-start shadow-sm hover:shadow-md transition-shadow">
                  <div className="bg-indigo-100 rounded-lg p-2 mr-3 flex-shrink-0">
                    <svg className="h-5 w-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-gray-800">{resource}</p>
                    <div className="mt-2 flex gap-2">
                      <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded">
                        Tài liệu
                      </span>
                      {resource.toLowerCase().includes('book') && (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded">
                          Sách
                        </span>
                      )}
                      {resource.toLowerCase().includes('course') && (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                          Khóa học
                        </span>
                      )}
                      {resource.toLowerCase().includes('documentation') && (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
                          Tài liệu chính thức
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 