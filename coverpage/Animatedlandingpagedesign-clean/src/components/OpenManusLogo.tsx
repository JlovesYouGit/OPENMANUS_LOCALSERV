import { motion } from 'motion/react';

interface OpenManusLogoProps {
  size?: number;
  showGlow?: boolean;
}

export function OpenManusLogo({ size = 64, showGlow = true }: OpenManusLogoProps) {
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Rotating outer orbital ring */}
        <motion.g
          animate={{ rotate: 360 }}
          transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
          style={{ transformOrigin: '32px 32px' }}
        >
          <motion.circle
            cx="32"
            cy="32"
            r="28"
            stroke="url(#gradient-outer)"
            strokeWidth="2"
            fill="none"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{ duration: 2, ease: 'easeInOut' }}
          />
        </motion.g>
        
        {/* Inner neural network pattern */}
        <motion.path
          d="M32 12 L32 22 M32 42 L32 52 M12 32 L22 32 M42 32 L52 32"
          stroke="url(#gradient-lines)"
          strokeWidth="2"
          strokeLinecap="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1.5, delay: 0.3 }}
        />
        
        {/* Center hexagon */}
        <motion.path
          d="M32 20 L42 26 L42 38 L32 44 L22 38 L22 26 Z"
          fill="url(#gradient-center)"
          stroke="url(#gradient-stroke)"
          strokeWidth="2"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.5 }}
        />
        
        {/* Orbiting nodes */}
        {[0, 90, 180, 270].map((angle, i) => {
          const radian = (angle * Math.PI) / 180;
          const x = 32 + Math.cos(radian) * 18;
          const y = 32 + Math.sin(radian) * 18;
          return (
            <motion.circle
              key={i}
              cx={x}
              cy={y}
              r="2.5"
              fill="#06b6d4"
              initial={{ scale: 0 }}
              animate={{ scale: [0, 1.2, 1] }}
              transition={{ duration: 0.5, delay: 0.8 + i * 0.1 }}
            />
          );
        })}
        
        {/* Pulsing center core */}
        <motion.circle
          cx="32"
          cy="32"
          r="4"
          fill="#e879f9"
          initial={{ scale: 0 }}
          animate={{ 
            scale: [1, 1.2, 1],
            opacity: [0.8, 1, 0.8],
          }}
          transition={{ 
            duration: 2, 
            delay: 1,
            repeat: Infinity,
            ease: 'easeInOut'
          }}
        />
        
        <defs>
          <linearGradient id="gradient-outer" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#06b6d4" />
            <stop offset="50%" stopColor="#a855f7" />
            <stop offset="100%" stopColor="#e879f9" />
          </linearGradient>
          <linearGradient id="gradient-lines" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#06b6d4" />
            <stop offset="100%" stopColor="#e879f9" />
          </linearGradient>
          <linearGradient id="gradient-center" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#e879f9" stopOpacity="0.2" />
          </linearGradient>
          <linearGradient id="gradient-stroke" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#06b6d4" />
            <stop offset="100%" stopColor="#e879f9" />
          </linearGradient>
        </defs>
      </svg>
      
      {/* Animated glow effect */}
      {showGlow && (
        <>
          <motion.div
            className="absolute inset-0 rounded-full"
            style={{
              background: 'radial-gradient(circle, rgba(168, 85, 247, 0.4) 0%, transparent 70%)',
              filter: 'blur(12px)',
            }}
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.4, 0.6, 0.4],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
          <motion.div
            className="absolute inset-0 rounded-full"
            style={{
              background: 'radial-gradient(circle, rgba(6, 182, 212, 0.3) 0%, transparent 70%)',
              filter: 'blur(16px)',
            }}
            animate={{
              scale: [1.2, 1, 1.2],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        </>
      )}
    </div>
  );
}
