interface AlertProps {
  message: string;
  type: 'error' | 'warning' | 'info' | 'success';
}

export default function Alert({ message, type }: AlertProps) {
  const baseClasses = "p-4 rounded-md mb-6";
  let typeClasses = "";

  switch (type) {
    case 'error':
      typeClasses = "bg-red-100 text-red-700";
      break;
    case 'warning':
      typeClasses = "bg-yellow-100 text-yellow-700";
      break;
    case 'success':
      typeClasses = "bg-green-100 text-green-700";
      break;
    case 'info':
    default:
      typeClasses = "bg-blue-100 text-blue-700";
      break;
  }

  return (
    <div className={`${baseClasses} ${typeClasses}`} role="alert">
      {message}
    </div>
  );
} 