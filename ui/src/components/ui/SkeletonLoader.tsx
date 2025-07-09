import React from 'react'

interface SkeletonLoaderProps {
  className?: string
  count?: number
  height?: string
  width?: string
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({ 
  className = '', 
  count = 1,
  height = 'h-4',
  width = 'w-full'
}) => {
  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          className={`skeleton ${height} ${width} ${className}`}
        />
      ))}
    </>
  )
}

export const StepCardSkeleton: React.FC = () => {
  return (
    <div className="relative">
      <div className="w-full p-4 rounded-lg border border-gray-700 animate-pulse">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-gray-800" />
          <div className="flex-1">
            <SkeletonLoader height="h-5" width="w-2/3" className="mb-2" />
            <SkeletonLoader height="h-4" width="w-full" />
          </div>
          <SkeletonLoader height="h-5" width="w-5" />
        </div>
      </div>
    </div>
  )
}

export const FormSkeleton: React.FC = () => {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, index) => (
          <div key={index} className="space-y-2">
            <SkeletonLoader height="h-4" width="w-24" className="mb-2" />
            <SkeletonLoader height="h-12" width="w-full" className="rounded-lg" />
          </div>
        ))}
      </div>
      <div className="flex gap-3 pt-4">
        <SkeletonLoader height="h-12" width="w-full" className="rounded-lg" />
        <SkeletonLoader height="h-12" width="w-32" className="rounded-lg" />
      </div>
    </div>
  )
}