"use client";

import { useState, useEffect } from "react";
import { FormData, LearningPathResponse } from "@/types";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { generateLearningPath } from "@/api/learningPathService";
import Spinner from "@/components/Spinner";
import Alert from "@/components/Alert";
import Image from "next/image";

const fieldOptions = [
  "Web Development",
  "Mobile Development",
  "Data Science",
  "Machine Learning",
  "Cybersecurity",
  "Cloud Computing",
  "Game Development",
  "DevOps",
  "Blockchain",
  "UI/UX Design",
  "Java programming",
  "Python programming",
  "JavaScript programming",
];

const interestOptions = [
  "Web Development",
  "Mobile app",
  "Data visualization",
  "AI/ML",
  "Security",
  "Cloud services",
  "Game design",
  "Automation",
  "IoT",
  "User interface design",
];

// Các bước tạo lộ trình
const steps = [
  { id: 1, name: "Lĩnh vực" },
  { id: 2, name: "Trình độ & Thời gian" },
  { id: 3, name: "Sở thích" },
  { id: 4, name: "Xác nhận" },
];

export default function CreatePath() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [formData, setFormData] = useState<FormData>({
    field: "",
    level: "Beginner",
    duration: 2,
    daily_hours: 2,
    interests: [],
  });
  const [dailyHours, setDailyHours] = useState<number>(2);
  const [currentStep, setCurrentStep] = useState(1);

  useEffect(() => {
    // Check if user is authenticated
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  const calculateDailyHours = (months: number) => {
    // Simple calculation - for a real app, this would be more complex
    const totalHours = months * 80; // Rough estimate of 80 hours per month
    const dailyHours = Math.ceil(totalHours / (months * 30));
    setDailyHours(dailyHours);
    setFormData(prev => ({ ...prev, daily_hours: dailyHours }));
  };

  const handleFieldChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFormData({ ...formData, field: e.target.value });
  };

  const handleLevelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFormData({ ...formData, level: e.target.value });
  };

  const handleDurationChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const duration = parseInt(e.target.value);
    setFormData({ ...formData, duration });
    calculateDailyHours(duration);
  };

  const handleInterestChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = e.target;
    setFormData({
      ...formData,
      interests: checked
        ? [...formData.interests, value]
        : formData.interests.filter((interest) => interest !== value),
    });
  };

  const handleDailyHoursChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const hours = parseInt(e.target.value);
    setFormData({ ...formData, daily_hours: hours });
    setDailyHours(hours);
  };

  const nextStep = () => {
    // Validate current step
    if (currentStep === 1 && !formData.field) {
      setError("Vui lòng chọn lĩnh vực học tập");
      return;
    }

    if (currentStep === 3 && formData.interests.length === 0) {
      setError("Vui lòng chọn ít nhất một sở thích");
      return;
    }

    setError("");
    setCurrentStep(currentStep + 1);
  };

  const prevStep = () => {
    setError("");
    setCurrentStep(currentStep - 1);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    if (!user) {
      setError("Bạn cần đăng nhập để tạo lộ trình học tập");
      setIsLoading(false);
      return;
    }

    try {
      // Prepare data for API
      const apiData = {
        field: formData.field,
        level: formData.level,
        duration: formData.duration,
        daily_hours: formData.daily_hours,
        interests: formData.interests
      };

      // Generate learning path using the API service
      const response = await generateLearningPath(apiData);

      // Save to localStorage as backup/generated path
      localStorage.setItem("generatedLearningPath", JSON.stringify(response));

      // Only remove savedLearningPathId if we have a new generated path
      // This prevents data loss when the user has created a path but not saved it yet
      if (response && response.learning_path) {
        localStorage.removeItem("savedLearningPathId");
      }

      // Navigate to the dashboard
      router.push("/dashboard");
    } catch (err: any) {
      console.error("Form submission error:", err);
      setError(err.message || "Đã xảy ra lỗi khi tạo lộ trình học tập.");
    } finally {
      setIsLoading(false);
    }
  };

  if (authLoading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <Spinner />
      </div>
    );
  }

  if (!user) {
    return null; // Router will redirect to login
  }

  // Stepper component
  const StepperUI = () => (
    <div className="mb-8">
      <div className="flex justify-between">
        {steps.map((step) => (
          <div key={step.id} className="flex-1 relative">
            <div className={`flex flex-col items-center ${step.id < currentStep ? 'text-indigo-600' : step.id === currentStep ? 'text-indigo-800' : 'text-gray-400'}`}>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${step.id < currentStep
                ? 'bg-indigo-600 text-white border-indigo-600'
                : step.id === currentStep
                  ? 'bg-white text-indigo-800 border-indigo-800'
                  : 'bg-white text-gray-400 border-gray-300'
                } z-10`}>
                {step.id < currentStep ? (
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  step.id
                )}
              </div>
              <span className="mt-2 text-sm hidden md:block">{step.name}</span>
            </div>
            {step.id < steps.length && (
              <div className={`absolute top-5 -z-10 left-1/2 w-full border-t ${step.id < currentStep ? 'border-indigo-600' : 'border-gray-300'
                }`}></div>
            )}
          </div>
        ))}
      </div>
      <div className="mt-4 md:hidden flex justify-between">
        {steps.map((step) => (
          <div
            key={step.id}
            className={`text-xs ${step.id === currentStep ? 'text-indigo-800 font-medium' : 'text-gray-500'}`}
          >
            {step.name}
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 relative">
      {isLoading && (
        <div className="fixed inset-0 bg-gray-800 bg-opacity-75 flex justify-center items-center z-20">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full">
            <Spinner />
            <p className="text-center mt-4 text-gray-700">Đang tạo lộ trình học tập...</p>
          </div>
        </div>
      )}

      <h1 className="text-3xl font-bold mb-2 text-center">Tạo Lộ Trình Học Tập Cá Nhân</h1>
      <p className="text-center text-gray-600 mb-8">
        Điền thông tin dưới đây để nhận lộ trình học tập được cá nhân hóa cho bạn
      </p>

      <StepperUI />

      {error && (
        <Alert message={error} type="error" />
      )}

      <div className="bg-white p-6 rounded-xl shadow-md mb-6">
        <form onSubmit={handleSubmit}>
          {/* Step 1: Field selection */}
          {currentStep === 1 && (
            <div className="space-y-6">
              <div className="flex flex-col md:flex-row items-center gap-10">
                <div className="md:w-1/2">
                  <h2 className="text-xl font-bold mb-4 text-gray-800">Chọn lĩnh vực học tập</h2>
                  <p className="text-gray-600 mb-6">
                    Lĩnh vực bạn muốn học sẽ giúp chúng tôi tạo lộ trình phù hợp với mục tiêu của bạn.
                  </p>
                  <div className="mb-6">
                    <label htmlFor="field" className="block text-gray-700 font-medium mb-2">
                      Mục tiêu học tập <span className="text-red-500">*</span>
                    </label>
                    <select
                      id="field"
                      value={formData.field}
                      onChange={handleFieldChange}
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="">Chọn lĩnh vực</option>
                      {fieldOptions.map((field) => (
                        <option key={field} value={field}>
                          {field}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="md:w-1/2 flex justify-center">
                  <div className="relative w-60 h-60">
                    <Image
                      src="/study-field.svg"
                      alt="Chọn lĩnh vực học tập"
                      fill
                      className="object-contain"
                    />
                  </div>
                </div>
              </div>
              <div className="flex justify-end pt-4">
                <button
                  type="button"
                  onClick={nextStep}
                  disabled={!formData.field}
                  className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none"
                >
                  Tiếp Theo
                </button>
              </div>
            </div>
          )}

          {/* Step 2: Level and Duration */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <div className="flex flex-col md:flex-row items-center gap-10">
                <div className="md:w-1/2">
                  <h2 className="text-xl font-bold mb-4 text-gray-800">Trình độ và thời gian học tập</h2>
                  <p className="text-gray-600 mb-6">
                    Thông tin về trình độ và thời gian giúp chúng tôi điều chỉnh độ khó và phân bổ nội dung học tập.
                  </p>

                  <div className="mb-6">
                    <label htmlFor="level" className="block text-gray-700 font-medium mb-2">
                      Trình độ mong muốn
                    </label>
                    <select
                      id="level"
                      value={formData.level}
                      onChange={handleLevelChange}
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="Beginner">Beginner - Người mới bắt đầu</option>
                      <option value="Intermediate">Intermediate - Trình độ trung bình</option>
                      <option value="Advanced">Advanced - Trình độ nâng cao</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="duration" className="block text-gray-700 font-medium mb-2">
                        Mục tiêu hoàn thành
                      </label>
                      <select
                        id="duration"
                        value={formData.duration}
                        onChange={handleDurationChange}
                        required
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      >
                        <option value="1">1 tháng</option>
                        <option value="2">2 tháng</option>
                        <option value="3">3 tháng</option>
                        <option value="6">6 tháng</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="daily_hours" className="block text-gray-700 font-medium mb-2">
                        Giờ học mỗi ngày
                      </label>
                      <select
                        id="daily_hours"
                        value={formData.daily_hours}
                        onChange={handleDailyHoursChange}
                        required
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      >
                        <option value="1">1 giờ</option>
                        <option value="2">2 giờ</option>
                        <option value="3">3 giờ</option>
                        <option value="4">4 giờ</option>
                      </select>
                    </div>
                  </div>
                </div>
                <div className="md:w-1/2 flex justify-center">
                  <div className="relative w-60 h-60">
                    <Image
                      src="/study-time.svg"
                      alt="Thời gian học tập"
                      fill
                      className="object-contain"
                    />
                  </div>
                </div>
              </div>
              <div className="flex justify-between pt-4">
                <button
                  type="button"
                  onClick={prevStep}
                  className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                >
                  Quay Lại
                </button>
                <button
                  type="button"
                  onClick={nextStep}
                  className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                >
                  Tiếp Theo
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Interests */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <div className="flex flex-col md:flex-row items-center gap-10">
                <div className="md:w-1/2">
                  <h2 className="text-xl font-bold mb-4 text-gray-800">Sở thích của bạn</h2>
                  <p className="text-gray-600 mb-6">
                    Chọn các sở thích để lộ trình của bạn được cá nhân hóa và thú vị hơn.
                  </p>

                  <div className="mb-6">
                    <label className="block text-gray-700 font-medium mb-3">
                      Sở thích <span className="text-red-500">*</span>
                    </label>
                    <div className="grid grid-cols-2 gap-3">
                      {interestOptions.map((interest) => (
                        <label
                          key={interest}
                          className={`flex items-center p-3 rounded-lg border ${formData.interests.includes(interest)
                            ? "border-indigo-600 bg-indigo-50"
                            : "border-gray-300 hover:bg-gray-50"
                            } transition-colors cursor-pointer`}
                        >
                          <input
                            type="checkbox"
                            value={interest}
                            checked={formData.interests.includes(interest)}
                            onChange={handleInterestChange}
                            className="sr-only"
                          />
                          <span className={`${formData.interests.includes(interest)
                            ? "bg-indigo-600"
                            : "bg-gray-200"
                            } w-5 h-5 mr-3 rounded flex items-center justify-center`}>
                            {formData.interests.includes(interest) && (
                              <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                              </svg>
                            )}
                          </span>
                          <span className={`${formData.interests.includes(interest) ? "text-indigo-800" : "text-gray-700"
                            }`}>
                            {interest}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="md:w-1/2 flex justify-center">
                  <div className="relative w-60 h-60">
                    <Image
                      src="/interests.svg"
                      alt="Sở thích của bạn"
                      fill
                      className="object-contain"
                    />
                  </div>
                </div>
              </div>
              <div className="flex justify-between pt-4">
                <button
                  type="button"
                  onClick={prevStep}
                  className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                >
                  Quay Lại
                </button>
                <button
                  type="button"
                  onClick={nextStep}
                  disabled={formData.interests.length === 0}
                  className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none"
                >
                  Tiếp Theo
                </button>
              </div>
            </div>
          )}

          {/* Step 4: Review and Submit */}
          {currentStep === 4 && (
            <div className="space-y-6">
              <h2 className="text-xl font-bold mb-4 text-gray-800">Xác nhận thông tin</h2>
              <p className="text-gray-600 mb-6">
                Kiểm tra các thông tin dưới đây trước khi tạo lộ trình học tập của bạn.
              </p>

              <div className="bg-gray-50 rounded-xl p-6 divide-y divide-gray-200">
                <div className="py-3 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Lĩnh vực</h3>
                    <p className="mt-1 text-lg font-medium">{formData.field}</p>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Trình độ</h3>
                    <p className="mt-1 text-lg font-medium">{formData.level}</p>
                  </div>
                </div>
                <div className="py-3 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Thời gian học tập</h3>
                    <p className="mt-1 text-lg font-medium">{formData.duration} tháng</p>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Giờ học mỗi ngày</h3>
                    <p className="mt-1 text-lg font-medium">{formData.daily_hours} giờ</p>
                  </div>
                </div>
                <div className="py-3">
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Sở thích</h3>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {formData.interests.map((interest) => (
                      <span key={interest} className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm">
                        {interest}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex justify-between pt-4">
                <button
                  type="button"
                  onClick={prevStep}
                  className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                >
                  Quay Lại
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                >
                  Tạo Lộ Trình
                </button>
              </div>
            </div>
          )}
        </form>
      </div>

      <div className="text-center text-sm text-gray-500">
        <p>Hệ thống AI sẽ phân tích thông tin của bạn để tạo lộ trình học tập tốt nhất.</p>
      </div>
    </div>
  );
} 