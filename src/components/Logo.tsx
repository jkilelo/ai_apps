import React from 'react'

interface LogoProps {
  className?: string
}

export const Logo: React.FC<LogoProps> = ({ className = "w-10 h-10" }) => {
  return (
    <svg 
      viewBox="0 0 100 100" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <circle cx="50" cy="50" r="45" fill="#FF3C28" opacity="0.1"/>
      <circle cx="50" cy="50" r="45" stroke="#FF3C28" strokeWidth="3"/>
      
      {/* Stylized deer/antelope silhouette */}
      <path 
        d="M30 65 C30 65, 35 45, 40 40 C42 38, 45 37, 48 37 C50 37, 52 37, 54 38 C56 39, 58 40, 60 42 C62 44, 64 46, 65 48 C66 50, 67 52, 67 55 C67 58, 66 60, 65 62 C64 64, 62 65, 60 65 L55 65 L50 65 L45 65 L40 65 L35 65 L30 65 Z" 
        fill="#FF3C28"
      />
      
      {/* Head and antlers */}
      <path 
        d="M60 42 C62 40, 64 38, 66 37 C68 36, 70 36, 70 36 L68 34 M70 36 L72 34 M70 36 L71 38" 
        stroke="#FF3C28" 
        strokeWidth="2" 
        strokeLinecap="round"
      />
      
      {/* Legs */}
      <path 
        d="M40 65 L38 75 M45 65 L43 75 M55 65 L57 75 M60 65 L62 75" 
        stroke="#FF3C28" 
        strokeWidth="2" 
        strokeLinecap="round"
      />
      
      {/* Tree/Branch */}
      <path 
        d="M25 35 C25 35, 28 32, 32 30 C34 29, 36 28, 38 28 C40 28, 42 29, 43 30" 
        stroke="#255BE3" 
        strokeWidth="2" 
        strokeLinecap="round"
      />
      <path 
        d="M32 30 L30 25 M36 28 L35 23" 
        stroke="#255BE3" 
        strokeWidth="2" 
        strokeLinecap="round"
      />
    </svg>
  )
}