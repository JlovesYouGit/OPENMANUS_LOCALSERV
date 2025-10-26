import { motion } from 'motion/react';

interface ThinkingIndicatorProps {
  variant?: 'dots' | 'ring' | 'pulse';
  size?: 'sm' | 'md' | 'lg';
}

export function ThinkingIndicator({ variant = 'dots', size = 'md' }: ThinkingIndicatorProps) {
  const sizeMap = {
    sm: { dot: 4, ring: 24, spacing: 2 },
    md: { dot: 6, ring: 32, spacing: 3 },
    lg: { dot: 8, ring: 40, spacing: 4 },
  };

  const dimensions = sizeMap[size];

  if (variant === 'dots') {
    return (
      <div className="flex items-center gap-2">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="rounded-full bg-gradient-to-r from-cyan-400 to-purple-500"
            style={{ width: dimensions.dot, height: dimensions.dot }}
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 1.2,
              repeat: Infinity,
              delay: i * 0.2,
              ease: 'easeInOut',
            }}
          />
        ))}
      </div>
    );
  }

  if (variant === 'ring') {
    return (
      <div className="relative" style={{ width: dimensions.ring, height: dimensions.ring }}>
        <svg
          width={dimensions.ring}
          height={dimensions.ring}
          viewBox="0 0 40 40"
          className="absolute inset-0"
        >
          {/* Background ring */}
          <circle
            cx="20"
            cy="20"
            r="16"
            fill="none"
            stroke="rgba(168, 85, 247, 0.2)"
            strokeWidth="3"
          />
          
          {/* Animated progress ring */}
          <motion.circle
            cx="20"
            cy="20"
            r="16"
            fill="none"
            stroke="url(#progress-gradient)"
            strokeWidth="3"
            strokeLinecap="round"
            strokeDasharray="100"
            initial={{ strokeDashoffset: 100 }}
            animate={{ 
              strokeDashoffset: [100, 0, 100],
              rotate: [0, 360],
            }}
            transition={{
              strokeDashoffset: { duration: 2, repeat: Infinity, ease: 'easeInOut' },
              rotate: { duration: 3, repeat: Infinity, ease: 'linear' },
            }}
            style={{ transformOrigin: 'center' }}
          />
          
          <defs>
            <linearGradient id="progress-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#06b6d4" />
              <stop offset="50%" stopColor="#a855f7" />
              <stop offset="100%" stopColor="#e879f9" />
            </linearGradient>
          </defs>
        </svg>
      </div>
    );
  }

  // Pulse variant
  return (
    <div className="relative" style={{ width: dimensions.ring, height: dimensions.ring }}>
      <motion.div
        className="absolute inset-0 rounded-full bg-gradient-to-r from-cyan-500 to-purple-500"
        animate={{
          scale: [1, 1.3, 1],
          opacity: [0.6, 0.3, 0.6],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
      <motion.div
        className="absolute inset-2 rounded-full bg-gradient-to-r from-purple-500 to-pink-500"
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.8, 0.5, 0.8],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 0.3,
        }}
      />
    </div>
  );
}
