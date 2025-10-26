import { motion } from 'motion/react';
import { LucideIcon } from 'lucide-react';

interface GlassmorphicCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  accentColor: string;
  delay?: number;
}

export function GlassmorphicCard({
  icon: Icon,
  title,
  description,
  accentColor,
  delay = 0,
}: GlassmorphicCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-100px' }}
      transition={{ duration: 0.8, delay }}
      whileHover={{ 
        y: -8,
        transition: { duration: 0.3, ease: 'easeOut' }
      }}
      className="group relative h-full"
    >
      {/* Glassmorphic card container */}
      <div className="relative h-full rounded-2xl bg-gradient-to-br from-white/[0.08] to-white/[0.02] backdrop-blur-xl border border-white/10 p-8 overflow-hidden transition-all duration-500">
        
        {/* Animated gradient overlay on hover */}
        <motion.div
          className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-700"
          style={{
            background: `radial-gradient(circle at 50% 0%, ${accentColor}15 0%, transparent 70%)`,
          }}
        />
        
        {/* Neon border glow on hover */}
        <motion.div
          className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
          style={{
            boxShadow: `inset 0 0 60px ${accentColor}20, 0 0 30px ${accentColor}10`,
          }}
        />

        {/* Content */}
        <div className="relative z-10">
          {/* Icon */}
          <motion.div
            className="mb-6 inline-flex"
            whileHover={{ scale: 1.1, rotate: 5 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
          >
            <div 
              className="relative w-16 h-16 rounded-2xl flex items-center justify-center"
              style={{
                background: `linear-gradient(135deg, ${accentColor}25, ${accentColor}10)`,
                border: `1px solid ${accentColor}30`,
              }}
            >
              <Icon className="w-8 h-8 text-white" strokeWidth={1.5} />
              
              {/* Icon glow */}
              <motion.div
                className="absolute inset-0 rounded-2xl"
                style={{
                  background: `linear-gradient(135deg, ${accentColor}40, transparent)`,
                  filter: 'blur(12px)',
                }}
                animate={{
                  opacity: [0.4, 0.7, 0.4],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              />
            </div>
          </motion.div>

          {/* Title */}
          <h3 
            className="mb-4 bg-gradient-to-br from-white via-white/90 to-white/70 bg-clip-text text-transparent"
            style={{ fontSize: '1.5rem', fontWeight: 600, lineHeight: 1.3 }}
          >
            {title}
          </h3>

          {/* Description */}
          <p 
            className="text-white/60 leading-relaxed"
            style={{ fontSize: '0.9375rem' }}
          >
            {description}
          </p>

          {/* Accent line */}
          <motion.div
            className="mt-6 h-0.5 rounded-full"
            style={{
              background: `linear-gradient(90deg, ${accentColor}, transparent)`,
            }}
            initial={{ width: 0 }}
            whileInView={{ width: '50%' }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: delay + 0.3 }}
          />
        </div>

        {/* Subtle corner accent */}
        <div 
          className="absolute top-0 right-0 w-32 h-32 opacity-20 blur-2xl"
          style={{
            background: `radial-gradient(circle, ${accentColor}, transparent)`,
          }}
        />
      </div>
    </motion.div>
  );
}
