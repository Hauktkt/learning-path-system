import Link from "next/link";
import Image from "next/image";

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-indigo-600 to-purple-700 py-20 md:py-32">
        <div className="absolute inset-0 overflow-hidden opacity-20">
          <div className="absolute inset-0 bg-[url('/grid-pattern.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]"></div>
        </div>
        <div className="container mx-auto px-4 flex flex-col md:flex-row items-center">
          <div className="md:w-1/2 text-center md:text-left mb-10 md:mb-0">
            <h1 className="text-4xl md:text-5xl font-bold mb-6 text-white leading-tight">
              Lộ Trình Học Tập <span className="text-yellow-300">Thông Minh</span> Dành Riêng Cho Bạn
            </h1>
            <p className="text-xl text-indigo-100 mb-8 max-w-2xl mx-auto md:mx-0">
              Ứng dụng AI để tạo ra lộ trình học tập cá nhân hóa phù hợp với mục tiêu, trình độ và sở thích của bạn.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start">
              <Link
                href="/create-path"
                className="bg-white text-indigo-700 px-8 py-3 rounded-lg text-lg font-medium hover:bg-indigo-50 transition-colors shadow-lg"
              >
                Bắt Đầu Ngay
              </Link>
              <Link
                href="/intro"
                className="bg-transparent text-white border-2 border-white px-8 py-3 rounded-lg text-lg font-medium hover:bg-white/10 transition-colors"
              >
                Tìm Hiểu Thêm
              </Link>
            </div>
          </div>
          <div className="md:w-1/2 relative h-64 md:h-96">
            <div className="relative w-full h-full">
              <Image
                src="/learning-hero.svg"
                alt="Learning Path Visualization"
                fill
                className="object-contain"
                priority
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-4">Tính Năng Nổi Bật</h2>
          <p className="text-center text-gray-600 mb-12 max-w-3xl mx-auto">
            PersonalEDU giúp bạn tối ưu hóa việc học thông qua công nghệ AI và theo dõi tiến độ thông minh
          </p>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-xl shadow-md transition-all duration-300 hover:shadow-lg border border-gray-100">
              <div className="w-14 h-14 bg-indigo-100 rounded-lg flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-3">Lộ Trình Cá Nhân Hóa</h3>
              <p className="text-gray-600">
                AI phân tích mục tiêu học tập, trình độ và sở thích để tạo lộ trình học tập tùy chỉnh hoàn toàn phù hợp với bạn.
              </p>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-md transition-all duration-300 hover:shadow-lg border border-gray-100">
              <div className="w-14 h-14 bg-indigo-100 rounded-lg flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-3">Quản Lý Nhiệm Vụ</h3>
              <p className="text-gray-600">
                Theo dõi tiến độ với nhiệm vụ hàng ngày, đánh dấu hoàn thành và nhận thông báo nhắc nhở thông minh.
              </p>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-md transition-all duration-300 hover:shadow-lg border border-gray-100">
              <div className="w-14 h-14 bg-indigo-100 rounded-lg flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-3">Phân Tích Tiến Độ</h3>
              <p className="text-gray-600">
                Xem biểu đồ phân tích chi tiết, theo dõi tiến trình và nhận đề xuất cải thiện dựa trên dữ liệu học tập của bạn.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-4">Cách Thức Hoạt Động</h2>
          <p className="text-center text-gray-600 mb-12 max-w-3xl mx-auto">
            Chỉ với vài bước đơn giản, bạn sẽ có ngay lộ trình học tập cá nhân hóa
          </p>
          <div className="grid md:grid-cols-4 gap-8 relative">
            <div className="hidden md:block absolute top-1/2 left-0 right-0 h-0.5 bg-indigo-200 -z-10 transform -translate-y-1/2"></div>
            {[
              {
                step: 1,
                title: "Nhập thông tin",
                description: "Chia sẻ mục tiêu, trình độ và sở thích của bạn"
              },
              {
                step: 2,
                title: "AI phân tích",
                description: "Hệ thống AI tạo lộ trình phù hợp với nhu cầu của bạn"
              },
              {
                step: 3,
                title: "Xem & Tùy chỉnh",
                description: "Xem lộ trình và điều chỉnh theo ý muốn"
              },
              {
                step: 4,
                title: "Bắt đầu học tập",
                description: "Hoàn thành nhiệm vụ và theo dõi tiến độ"
              }
            ].map((item, index) => (
              <div key={index} className="text-center relative">
                <div className="w-12 h-12 bg-indigo-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 z-10 relative">
                  {item.step}
                </div>
                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                <p className="text-gray-600">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-indigo-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-4">Người Dùng Nói Gì</h2>
          <p className="text-center text-gray-600 mb-12 max-w-3xl mx-auto">
            Hàng nghìn người dùng đã cải thiện kỹ năng và đạt được mục tiêu học tập với PersonalEDU
          </p>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                name: "Nguyễn Văn A",
                role: "Developer",
                content: "Lộ trình học tập đã giúp tôi học React từ cơ bản đến nâng cao chỉ trong 3 tháng. Các nhiệm vụ được phân chia rất hợp lý."
              },
              {
                name: "Trần Thị B",
                role: "Sinh viên",
                content: "Tôi rất ấn tượng với khả năng tùy chỉnh lộ trình. Hệ thống đề xuất chính xác những gì tôi cần học để đạt được mục tiêu."
              },
              {
                name: "Lê Văn C",
                role: "UI/UX Designer",
                content: "Dashboard theo dõi tiến độ rất trực quan và thú vị. Tôi có thể thấy rõ sự tiến bộ của mình qua từng ngày."
              }
            ].map((testimonial, index) => (
              <div key={index} className="bg-white p-6 rounded-xl shadow-md">
                <div className="flex flex-col h-full">
                  <div className="flex-grow">
                    <p className="italic text-gray-600 mb-4">"{testimonial.content}"</p>
                  </div>
                  <div className="mt-4 flex items-center">
                    <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center">
                      <span className="text-indigo-600 font-bold">{testimonial.name.charAt(0)}</span>
                    </div>
                    <div className="ml-3">
                      <p className="font-medium">{testimonial.name}</p>
                      <p className="text-sm text-gray-500">{testimonial.role}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">Sẵn Sàng Để Bắt Đầu?</h2>
          <p className="text-xl mb-8 max-w-3xl mx-auto">
            Tạo lộ trình học tập cá nhân ngay hôm nay và trải nghiệm sự khác biệt
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/create-path"
              className="bg-white text-indigo-600 px-8 py-3 rounded-lg text-lg font-medium hover:bg-indigo-50 transition-colors shadow-lg"
            >
              Tạo Lộ Trình Ngay
            </Link>
            <Link
              href="/register"
              className="bg-transparent text-white border-2 border-white px-8 py-3 rounded-lg text-lg font-medium hover:bg-white/10 transition-colors"
            >
              Đăng Ký Tài Khoản
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
