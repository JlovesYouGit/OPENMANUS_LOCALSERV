import { motion } from 'motion/react';
import { Brain, Network, Cpu, Sparkles, Zap, Code2, ArrowRight, Github } from 'lucide-react';
import { Button } from './ui/button';
import { Navigation } from './Navigation';
import { AnimatedParticles } from './AnimatedParticles';
import { FloatingOrbs } from './FloatingOrbs';
import { GlassmorphicCard } from './GlassmorphicCard';
import { OpenManusLogo } from './OpenManusLogo';
import { ThinkingIndicator } from './ThinkingIndicator';

export function LandingPage() {
  return (
    <div 
      className="relative min-h-screen overflow-hidden"
      style={{
        background: 'linear-gradient(135deg, #1a0b2e 0%, #2d1b4e 50%, #1a0b2e 100%)',
      }}
    >
      {/* Animated background layers */}
      <FloatingOrbs />
      <AnimatedParticles />
      
      {/* Subtle grid overlay */}
      <div 
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage: `
            linear-gradient(rgba(168, 85, 247, 0.5) 1px, transparent 1px),
            linear-gradient(90deg, rgba(168, 85, 247, 0.5) 1px, transparent 1px)
          `,
          backgroundSize: '80px 80px',
        }}
      />

      {/* Navigation */}
      <Navigation />

      {/* Main content */}
      <div className="relative z-10">
        {/* Hero Section */}
        <section className="min-h-screen flex items-center justify-center px-6 pt-20">
          <div className="max-w-6xl mx-auto text-center">
            {/* Animated logo */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1, delay: 0.3 }}
              className="flex justify-center mb-12"
            >
              <OpenManusLogo size={120} showGlow={true} />
            </motion.div>

            {/* Main headline */}
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.5 }}
              className="mb-6 bg-gradient-to-r from-white via-purple-100 to-cyan-100 bg-clip-text text-transparent"
              style={{ fontSize: '5rem', fontWeight: 700, lineHeight: 1.1, letterSpacing: '-0.02em' }}
            >
              OpenManus
            </motion.h1>

            {/* Tagline */}
            <motion.h2
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.7 }}
              className="mb-8 text-white/70"
              style={{ fontSize: '1.75rem', fontWeight: 400, letterSpacing: '-0.01em' }}
            >
              The Intelligent Agent Platform
            </motion.h2>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.9 }}
              className="mb-12 text-white/50 max-w-2xl mx-auto leading-relaxed"
              style={{ fontSize: '1.125rem' }}
            >
              Deploy autonomous AI agents with advanced reasoning capabilities.
              Build, orchestrate, and scale intelligent workflows powered by state-of-the-art language models.
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 1.1 }}
              className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16"
            >
              {/* Primary CTA */}
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
                className="relative group"
              >
                {/* Glow effect */}
                <motion.div
                  className="absolute -inset-1 rounded-2xl opacity-70 blur-xl"
                  style={{
                    background: 'linear-gradient(90deg, #06b6d4, #a855f7, #e879f9)',
                  }}
                  animate={{
                    opacity: [0.5, 0.8, 0.5],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                />

                <Button
                  className="relative px-8 py-6 overflow-hidden border-0 rounded-xl"
                  style={{
                    background: 'linear-gradient(135deg, #06b6d4 0%, #a855f7 50%, #e879f9 100%)',
                    fontSize: '1.0625rem',
                    fontWeight: 600,
                  }}
                  size="lg"
                >
                  {/* Shimmer effect */}
                  <motion.div
                    className="absolute inset-0"
                    style={{
                      background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
                    }}
                    animate={{
                      x: [-300, 300],
                    }}
                    transition={{
                      duration: 2.5,
                      repeat: Infinity,
                      ease: 'linear',
                    }}
                  />

                  <span className="relative flex items-center gap-2 text-white">
                    Get Started
                    <motion.div
                      animate={{ x: [0, 4, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    >
                      <ArrowRight className="w-5 h-5" />
                    </motion.div>
                  </span>
                </Button>
              </motion.div>

              {/* Secondary CTA */}
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button
                  variant="outline"
                  className="px-8 py-6 bg-white/5 backdrop-blur-xl border-white/20 text-white hover:bg-white/10 hover:border-white/30 rounded-xl"
                  style={{ fontSize: '1.0625rem', fontWeight: 600 }}
                  size="lg"
                  onClick={() => window.open('https://github.com/FoundationAgents/OpenManus', '_blank')}
                >
                  <Github className="w-5 h-5 mr-2" />
                  View on GitHub
                </Button>
              </motion.div>
            </motion.div>

            {/* Status indicators */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1, delay: 1.3 }}
              className="flex items-center justify-center gap-8 text-sm text-white/40"
            >
              <div className="flex items-center gap-2">
                <ThinkingIndicator variant="dots" size="sm" />
                <span>AI Processing</span>
              </div>
              <div className="w-1 h-1 rounded-full bg-white/20" />
              <div className="flex items-center gap-2">
                <ThinkingIndicator variant="ring" size="sm" />
                <span>Multi-Agent</span>
              </div>
              <div className="w-1 h-1 rounded-full bg-white/20" />
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>localhost:5000</span>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-32 px-6">
          <div className="max-w-6xl mx-auto">
            {/* Section header */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.8 }}
              className="text-center mb-20"
            >
              <h2 
                className="mb-4 bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent"
                style={{ fontSize: '2.5rem', fontWeight: 600, letterSpacing: '-0.01em' }}
              >
                Built for the Future of AI
              </h2>
              <p className="text-white/50 max-w-2xl mx-auto" style={{ fontSize: '1.0625rem' }}>
                Powerful features designed for developers building the next generation of intelligent applications
              </p>
            </motion.div>

            {/* 3-column feature grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8" id="features">
              <GlassmorphicCard
                icon={Brain}
                title="Autonomous Agents"
                description="Deploy AI agents that think, reason, and execute complex tasks independently. Advanced planning and decision-making capabilities out of the box."
                accentColor="#06b6d4"
                delay={0}
              />
              
              <GlassmorphicCard
                icon={Network}
                title="Multi-Agent Orchestration"
                description="Coordinate teams of specialized agents working together. Seamless communication protocols and shared context management for collaborative problem-solving."
                accentColor="#e879f9"
                delay={0.1}
              />
              
              <GlassmorphicCard
                icon={Cpu}
                title="Flexible Integration"
                description="Work with any LLM provider or custom models. Plug-and-play architecture supports OpenAI, Anthropic, local models, and custom handlers."
                accentColor="#a855f7"
                delay={0.2}
              />
            </div>
          </div>
        </section>

        {/* Additional Features Section */}
        <section className="py-32 px-6">
          <div className="max-w-6xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <GlassmorphicCard
                icon={Sparkles}
                title="Advanced Reasoning"
                description="Leverage cutting-edge reasoning algorithms. Chain-of-thought processing, self-reflection, and iterative refinement for superior results."
                accentColor="#e879f9"
                delay={0}
              />
              
              <GlassmorphicCard
                icon={Zap}
                title="Real-Time Performance"
                description="Optimized for speed without sacrificing quality. Stream responses, parallel processing, and efficient resource management built-in."
                accentColor="#06b6d4"
                delay={0.1}
              />
              
              <GlassmorphicCard
                icon={Code2}
                title="Developer-First"
                description="Clean APIs, comprehensive documentation, and extensible architecture. Built by developers, for developers who demand flexibility."
                accentColor="#a855f7"
                delay={0.2}
              />
            </div>
          </div>
        </section>

        {/* Footer / CTA Section */}
        <section className="py-32 px-6">
          <div className="max-w-4xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="rounded-3xl bg-gradient-to-br from-white/[0.08] to-white/[0.02] backdrop-blur-xl border border-white/10 p-12 relative overflow-hidden"
            >
              {/* Background accent */}
              <div 
                className="absolute inset-0 opacity-30"
                style={{
                  background: 'radial-gradient(circle at 50% 0%, rgba(168, 85, 247, 0.3), transparent 60%)',
                }}
              />

              <div className="relative z-10">
                <h2 
                  className="mb-4 bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent"
                  style={{ fontSize: '2.25rem', fontWeight: 600 }}
                >
                  Ready to Build?
                </h2>
                <p className="text-white/60 mb-8 max-w-xl mx-auto" style={{ fontSize: '1.0625rem' }}>
                  Join developers building intelligent agent systems with OpenManus. 
                  Open source, extensible, and production-ready.
                </p>

                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                  <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.98 }}>
                    <Button
                      className="px-8 py-6 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white border-0 rounded-xl"
                      style={{ fontSize: '1.0625rem', fontWeight: 600 }}
                      size="lg"
                    >
                      Start Building Now
                    </Button>
                  </motion.div>

                  <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.98 }}>
                    <Button
                      variant="ghost"
                      className="px-8 py-6 text-white/80 hover:text-white hover:bg-white/5 rounded-xl"
                      style={{ fontSize: '1.0625rem', fontWeight: 600 }}
                      size="lg"
                      onClick={() => window.open('https://github.com/FoundationAgents/OpenManus', '_blank')}
                    >
                      Read Documentation
                    </Button>
                  </motion.div>
                </div>
              </div>
            </motion.div>

            {/* Footer text */}
            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 1, delay: 0.3 }}
              className="text-white/30 text-sm mt-12"
            >
              OpenManus • localhost:5000 • MIT License
            </motion.p>
          </div>
        </section>
      </div>
    </div>
  );
}
