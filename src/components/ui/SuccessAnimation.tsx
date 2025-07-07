import React, { useEffect, useState } from 'react'

interface SuccessAnimationProps {
  onComplete?: () => void
}

export const SuccessAnimation: React.FC<SuccessAnimationProps> = ({ onComplete }) => {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false)
      onComplete?.()
    }, 2000)

    return () => clearTimeout(timer)
  }, [onComplete])

  if (!isVisible) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none">
      <div className="relative">
        <div className="absolute inset-0 bg-green-500 rounded-full blur-3xl opacity-30 animate-ping" />
        <div className="relative bg-gray-800 rounded-full p-8 shadow-2xl">
          <svg
            className="w-24 h-24 text-green-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M5 13l4 4L19 7"
              className="animate-[draw_0.5s_ease-out_forwards]"
              style={{
                strokeDasharray: 30,
                strokeDashoffset: 30,
              }}
            />
          </svg>
        </div>
      </div>
      
      <style jsx>{`
        @keyframes draw {
          to {
            stroke-dashoffset: 0;
          }
        }
      `}</style>
    </div>
  )
}