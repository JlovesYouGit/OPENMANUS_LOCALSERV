import { motion } from 'motion/react';
import { OpenManusLogo } from './OpenManusLogo';

export function Navigation() {
  return (
    <motion.nav
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6 }}
      className="fixed top-0 left-0 right-0 z-50 px-6 py-4"
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo and brand */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="flex items-center gap-3"
        >
          <OpenManusLogo size={40} showGlow={false} />
          <span className="text-white/90 tracking-tight" style={{ fontSize: '1.25rem', fontWeight: 600 }}>
            OpenManus
          </span>
        </motion.div>

        {/* Status badge */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex items-center gap-6"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 backdrop-blur-xl border border-white/10">
            <motion.div
              className="w-2 h-2 rounded-full bg-cyan-400"
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.7, 1, 0.7],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
            <span className="text-sm text-white/80">System Online</span>
            
            {/* Neon glow effect */}
            <motion.div
              className="absolute inset-0 rounded-full"
              style={{
                background: 'radial-gradient(circle, rgba(6, 182, 212, 0.3) 0%, transparent 70%)',
                filter: 'blur(8px)',
              }}
              animate={{
                opacity: [0.3, 0.6, 0.3],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
          </div>

          {/* Nav links */}
          <div className="hidden md:flex items-center gap-6 text-sm text-white/60">
            <motion.a
              href="#features"
              whileHover={{ color: 'rgba(255, 255, 255, 0.9)' }}
              className="hover:text-white/90 transition-colors"
            >
              Features
            </motion.a>
            <motion.a
              href="https://github.com/FoundationAgents/OpenManus"
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ color: 'rgba(255, 255, 255, 0.9)' }}
              className="hover:text-white/90 transition-colors"
            >
              Documentation
            </motion.a>
            <motion.a
              href="https://github.com/FoundationAgents/OpenManus"
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ color: 'rgba(255, 255, 255, 0.9)' }}
              className="hover:text-white/90 transition-colors"
            >
              GitHub
            </motion.a>
          </div>

          {/* CTA Button */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.98 }}
            className="hidden lg:block relative px-6 py-2.5 rounded-full overflow-hidden"
            style={{
              background: 'linear-gradient(135deg, #06b6d4 0%, #a855f7 50%, #e879f9 100%)',
            }}
          >
            {/* Shimmer effect */}
            <motion.div
              className="absolute inset-0"
              style={{
                background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
              }}
              animate={{
                x: [-200, 200],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'linear',
              }}
            />
            <span className="relative text-white text-sm" style={{ fontWeight: 600 }}>
              Get Started
            </span>
          </motion.button>
        </motion.div>
      </div>
    </motion.nav>
  );
}
