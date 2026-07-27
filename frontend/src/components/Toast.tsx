"use client";

import { useEffect, useState } from "react";

export interface ToastProps {
  show: boolean;
  message: string;
  type: "success" | "info" | "error";
  onDone: () => void;
}

export default function Toast({ show, message, type, onDone }: ToastProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (show) {
      setVisible(true);
      const timer = setTimeout(() => {
        setVisible(false);
        setTimeout(onDone, 300); // 等 fade out 动画结束
      }, 10000);
      return () => clearTimeout(timer);
    }
  }, [show, onDone]);

  if (!show && !visible) return null;

  const bgColor =
    type === "success"
      ? "bg-green-500"
      : type === "error"
        ? "bg-red-500"
        : "bg-gray-600";

  return (
    <div
      className={`fixed top-4 left-1/2 -translate-x-1/2 z-50 px-5 py-3 rounded-lg shadow-lg text-white text-sm font-medium transition-all duration-300 ${
        bgColor
      } ${visible && show ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-2"}`}
    >
      {message}
    </div>
  );
}
