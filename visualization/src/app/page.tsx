'use client';

import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, Stars } from '@react-three/drei';
import { motion } from 'framer-motion';
import { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Link from 'next/link';
import { Activity, Zap, Brain, Sparkles, ChevronDown } from 'lucide-react';

// Register GSAP plugins
if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

// Detroit 2056 Skyline 3D Component
function DetroitSkyline() {
  return (
    <group>
      {/* Stars background */}
      <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
      
      {/* Ambient lighting */}
      <ambientLight intensity={0.3} />
      <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={0.5} />
      <pointLight position={[-10, -10, -10]} intensity={0.2} color="#8b5cf6" />
      
      {/* Futuristic buildings */}
      {Array.from({ length: 20 }).map((_, i) => (
        <mesh key={i} position={[
          (Math.random() - 0.5) * 40,
          Math.random() * 5 + 2,
          (Math.random() - 0.5) * 40 - 20
        ]}>
          <boxGeometry args={[
            Math.random() * 2 + 1,
            Math.random() * 10 + 5,
            Math.random() * 2 + 1
          ]} />
          <meshStandardMaterial
            color={`hsl(${260 + Math.random() * 40}, 70%, ${20 + Math.random() * 20}%)`}
            emissive="#8b5cf6"
            emissiveIntensity={0.1}
          />
        </mesh>
      ))}
      
      {/* Central tower (ARCHON HQ) */}
      <mesh position={[0, 8, -15]}>
        <cylinderGeometry args={[2, 3, 20, 8]} />
        <meshStandardMaterial
          color="#1a0a2e"
          emissive="#8b5cf6"
          emissiveIntensity={0.3}
        />
      </mesh>
      
      {/* Floating platform */}
      <mesh position={[0, 0, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[15, 64]} />
        <meshStandardMaterial
          color="#0a0a0f"
          emissive="#ec4899"
          emissiveIntensity={0.1}
          transparent
          opacity={0.5}
        />
      </mesh>
    </group>
  );
}

// Agent Card Component
function AgentCard({ agent, index }: { agent: any; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.2, duration: 0.6 }}
      viewport={{ once: true }}
      whileHover={{ scale: 1.02 }}
      className={`glass-container p-8 rounded-2xl backdrop-blur-xl ${
        agent.type === 'analytical' 
          ? 'bg-blue-500/10 border-blue-500/30' 
          : 'bg-pink-500/10 border-pink-500/30'
      }`}
    >
      <div className="flex items-center gap-4 mb-4">
        <div className={`w-16 h-16 rounded-full flex items-center justify-center ${
          agent.type === 'analytical' ? 'bg-blue-500' : 'bg-pink-500'
        }`}>
          {agent.type === 'analytical' ? (
            <Brain className="w-8 h-8 text-white" />
          ) : (
            <Sparkles className="w-8 h-8 text-white" />
          )}
        </div>
        <div>
          <h3 className="text-3xl font-bold" style={{ 
            color: agent.type === 'analytical' ? '#60a5fa' : '#f472b6' 
          }}>
            {agent.name}
          </h3>
          <p className="text-gray-400">{agent.role}</p>
        </div>
      </div>
      <ul className="space-y-2 text-gray-300">
        {agent.capabilities.map((cap: string, i: number) => (
          <li key={i}>• {cap}</li>
        ))}
      </ul>
      <div className="mt-4 flex items-center gap-2 text-sm text-gray-400">
        <Activity className="w-4 h-4 animate-pulse text-green-500" />
        <span>Active • {agent.tasks_completed} tasks completed</span>
      </div>
    </motion.div>
  );
}

export default function LandingPage() {
  const heroRef = useRef<HTMLDivElement>(null);
  const [agents, setAgents] = useState([
    {
      id: 'pauli',
      name: 'Pauli',
      type: 'analytical',
      role: 'Analytics & Logic Core',
      capabilities: [
        'Data analysis & pattern recognition',
        'Logic verification & validation',
        'System diagnostics & monitoring',
        'Mathematical computations'
      ],
      tasks_completed: 127
    },
    {
      id: 'synthia',
      name: 'Synthia',
      type: 'creative',
      role: 'Creative & Synthesis Core',
      capabilities: [
        'Content synthesis & generation',
        'Creative problem solving',
        'Natural language processing',
        'User interaction & communication'
      ],
      tasks_completed: 89
    }
  ]);

  useEffect(() => {
    // GSAP scroll animations
    if (heroRef.current) {
      gsap.fromTo(
        '.hero-text',
        { opacity: 0, y: 100 },
        {
          opacity: 1,
          y: 0,
          duration: 1.2,
          stagger: 0.2,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: heroRef.current,
            start: 'top 80%',
          },
        }
      );
    }
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-black text-white overflow-x-hidden">
      {/* Hero Section with Louie Newton */}
      <section
        ref={heroRef}
        className="relative h-screen flex items-center justify-center overflow-hidden"
      >
        {/* Detroit 2056 Skyline Background */}
        <div className="absolute inset-0 z-0">
          <Canvas camera={{ position: [0, 5, 15], fov: 60 }}>
            <DetroitSkyline />
            <OrbitControls 
              enableZoom={false} 
              enablePan={false}
              autoRotate
              autoRotateSpeed={0.5}
              maxPolarAngle={Math.PI / 2}
              minPolarAngle={Math.PI / 3}
            />
            <Environment preset="night" />
          </Canvas>
        </div>

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-purple-900/20 to-black/80 z-[1]" />

        {/* Glass Morphism Container */}
        <div className="relative z-10 max-w-6xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1 }}
            className="glass-container p-12 rounded-3xl backdrop-blur-xl bg-white/10 border border-white/20"
          >
            {/* Louie Newton Avatar */}
            <div className="flex flex-col md:flex-row items-center gap-8 mb-8">
              <motion.div 
                className="w-48 h-48 rounded-full overflow-hidden border-4 border-purple-500 shadow-2xl glow-effect"
                animate={{ y: [0, -10, 0] }}
                transition={{ repeat: Infinity, duration: 4 }}
              >
                <div className="w-full h-full bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center">
                  <span className="text-6xl">🤖</span>
                </div>
              </motion.div>
              <div className="text-center md:text-left">
                <h1 className="hero-text text-6xl md:text-7xl font-bold mb-4 gradient-text">
                  ARCHON X
                </h1>
                <p className="hero-text text-2xl text-gray-300 mb-2">
                  Dual-Crew Agentic Operating System
                </p>
                <p className="hero-text text-lg text-purple-400">
                  Featuring Louie Newton • Detroit 2056
                </p>
              </div>
            </div>

            {/* Mission Statement */}
            <p className="hero-text text-xl text-gray-200 mb-8 leading-relaxed text-center">
              Revolutionary AI sovereignty system combining{' '}
              <span className="text-purple-400 font-bold">64 specialized agents</span>{' '}
              for autonomous task execution, creative synthesis, and ethical governance.
            </p>

            {/* Stats */}
            <div className="hero-text grid grid-cols-3 gap-4 mb-8">
              <div className="text-center p-4 bg-white/5 rounded-xl">
                <div className="text-3xl font-bold text-purple-400">64</div>
                <div className="text-sm text-gray-400">Specialized Agents</div>
              </div>
              <div className="text-center p-4 bg-white/5 rounded-xl">
                <div className="text-3xl font-bold text-pink-400">2</div>
                <div className="text-sm text-gray-400">Core Crews</div>
              </div>
              <div className="text-center p-4 bg-white/5 rounded-xl">
                <div className="text-3xl font-bold text-blue-400">∞</div>
                <div className="text-sm text-gray-400">Possibilities</div>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="hero-text flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/dashboard">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl font-bold text-lg shadow-xl hover:shadow-purple-500/50 transition-all flex items-center justify-center gap-2"
                >
                  <Zap className="w-5 h-5" />
                  Launch Dashboard
                </motion.button>
              </Link>
              <Link href="/docs">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="w-full sm:w-auto px-8 py-4 border-2 border-purple-500 rounded-xl font-bold text-lg hover:bg-purple-500/20 transition-all"
                >
                  View Documentation
                </motion.button>
              </Link>
            </div>
          </motion.div>
        </div>

        {/* Scroll Indicator */}
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ repeat: Infinity, duration: 2 }}
          className="absolute bottom-10 left-1/2 transform -translate-x-1/2 z-10"
        >
          <ChevronDown className="w-8 h-8 text-purple-400" />
        </motion.div>
      </section>

      {/* Agent Showcase Section */}
      <section className="py-20 px-6 relative">
        <div className="absolute inset-0 bg-gradient-to-b from-black/50 to-transparent" />
        <div className="max-w-7xl mx-auto relative z-10">
          <motion.h2 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-5xl font-bold text-center mb-16 gradient-text"
          >
            Meet the Dual Crew
          </motion.h2>

          <div className="grid md:grid-cols-2 gap-8">
            {agents.map((agent, index) => (
              <AgentCard key={agent.id} agent={agent} index={index} />
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.h2 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-5xl font-bold text-center mb-16 gradient-text"
          >
            System Capabilities
          </motion.h2>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: '🧠', title: 'Autonomous Execution', desc: 'Self-directed task completion with minimal human oversight' },
              { icon: '🎨', title: 'Creative Synthesis', desc: 'Generate novel solutions through multi-agent collaboration' },
              { icon: '⚖️', title: 'YEDL Ethics', desc: 'Built-in ethical governance for responsible AI operation' },
              { icon: '🔊', title: 'Voice Interface', desc: 'Natural voice commands for hands-free interaction' },
              { icon: '📹', title: 'Video Agents', desc: 'Visual processing and generation capabilities' },
              { icon: '🔄', title: 'A2A Protocol', desc: 'Seamless agent-to-agent communication' },
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1, duration: 0.5 }}
                viewport={{ once: true }}
                className="glass-container p-6 rounded-xl text-center"
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="text-gray-400">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-white/10">
        <div className="max-w-7xl mx-auto text-center text-gray-400">
          <p className="mb-2">ARCHON X v2.6.0 • Built with YEDL Ethics • Detroit 2056</p>
          <p className="text-sm">© 2056 ARCHON X Systems. All rights reserved.</p>
        </div>
      </footer>
    </main>
  );
}