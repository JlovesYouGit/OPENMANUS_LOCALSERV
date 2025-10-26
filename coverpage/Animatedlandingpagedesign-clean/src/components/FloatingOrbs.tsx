import { motion } from 'motion/react';

export function FloatingOrbs() {
  const orbs = [
    {
      id: 1,
      size: 600,
      color: 'rgba(168, 85, 247, 0.4)', // Purple
      initialX: '20%',
      initialY: '10%',
      animateX: [0, 100, -50, 0],
      animateY: [0, -80, 50, 0],
      duration: 25,
      blur: '100px',
    },
    {
      id: 2,
      size: 700,
      color: 'rgba(6, 182, 212, 0.35)', // Cyan
      initialX: '70%',
      initialY: '60%',
      animateX: [0, -80, 60, 0],
      animateY: [0, 100, -40, 0],
      duration: 30,
      blur: '120px',
    },
    {
      id: 3,
      size: 500,
      color: 'rgba(232, 121, 249, 0.3)', // Pink/Magenta
      initialX: '50%',
      initialY: '80%',
      animateX: [0, 70, -70, 0],
      animateY: [0, -60, 80, 0],
      duration: 28,
      blur: '90px',
    },
    {
      id: 4,
      size: 550,
      color: 'rgba(59, 130, 246, 0.25)', // Blue
      initialX: '10%',
      initialY: '70%',
      animateX: [0, 90, -30, 0],
      animateY: [0, -90, 30, 0],
      duration: 32,
      blur: '110px',
    },
  ];

  return (
    <div className="absolute inset-0 overflow-hidden">
      {orbs.map((orb) => (
        <motion.div
          key={orb.id}
          className="absolute rounded-full"
          style={{
            width: orb.size,
            height: orb.size,
            left: orb.initialX,
            top: orb.initialY,
            background: `radial-gradient(circle, ${orb.color} 0%, transparent 70%)`,
            filter: `blur(${orb.blur})`,
          }}
          animate={{
            x: orb.animateX,
            y: orb.animateY,
            scale: [1, 1.2, 0.9, 1],
            opacity: [0.6, 0.8, 0.5, 0.6],
          }}
          transition={{
            duration: orb.duration,
            repeat: Infinity,
            ease: 'easeInOut',
            times: [0, 0.33, 0.66, 1],
          }}
        />
      ))}
    </div>
  );
}
