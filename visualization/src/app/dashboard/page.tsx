'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, Zap, Brain, Sparkles, Terminal, Settings, LogOut, Home } from 'lucide-react';
import Link from 'next/link';

interface AgentStatus {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'idle' | 'error';
  tasks_completed: number;
  current_task?: string;
}

// Agent Card Component
function AgentCard({ agent }: { agent: AgentStatus }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-container p-6 rounded-2xl relative overflow-hidden"
    >
      {/* Status Indicator */}
      <div className="absolute top-4 right-4">
        <div
          className={`w-3 h-3 rounded-full animate-pulse ${
            agent.status === 'active'
              ? 'bg-green-500'
              : agent.status === 'idle'
              ? 'bg-yellow-500'
              : 'bg-red-500'
          }`}
        />
      </div>

      {/* Agent Header */}
      <div className="flex items-center gap-4 mb-4">
        <div
          className={`w-12 h-12 rounded-full flex items-center justify-center ${
            agent.type === 'analytical'
              ? 'bg-blue-500/20 text-blue-400'
              : 'bg-pink-500/20 text-pink-400'
          }`}
        >
          {agent.type === 'analytical' ? (
            <Brain className="w-6 h-6" />
          ) : (
            <Sparkles className="w-6 h-6" />
          )}
        </div>
        <div>
          <h3 className="text-xl font-bold">{agent.name}</h3>
          <p className="text-sm text-gray-400">{agent.type}</p>
        </div>
      </div>

      {/* Metrics */}
      <div className="space-y-2 mb-4">
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Tasks Completed</span>
          <span className="font-bold text-purple-400">{agent.tasks_completed}</span>
        </div>
        {agent.current_task && (
          <div className="text-sm">
            <span className="text-gray-400">Current: </span>
            <span className="text-gray-200">{agent.current_task}</span>
          </div>
        )}
      </div>

      {/* Activity Pulse */}
      <div className="flex items-center gap-2 text-sm text-gray-400">
        <Activity className="w-4 h-4 animate-pulse text-green-500" />
        <span className="capitalize">{agent.status}</span>
      </div>
    </motion.div>
  );
}

// Task Input Component
function TaskInput({ onSubmit }: { onSubmit: (task: string) => void }) {
  const [task, setTask] = useState('');

  return (
    <div className="glass-container p-6 rounded-2xl">
      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
        <Terminal className="w-5 h-5 text-purple-400" />
        Submit Task
      </h3>
      <div className="flex gap-2">
        <input
          type="text"
          value={task}
          onChange={(e) => setTask(e.target.value)}
          placeholder="Enter a task for the agents..."
          className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:border-purple-500 transition-colors"
        />
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => {
            if (task.trim()) {
              onSubmit(task);
              setTask('');
            }
          }}
          className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl font-bold"
        >
          Execute
        </motion.button>
      </div>
    </div>
  );
}

// Activity Log Component
function ActivityLog({ activities }: { activities: { time: string; message: string; type: string }[] }) {
  return (
    <div className="glass-container p-6 rounded-2xl">
      <h3 className="text-xl font-bold mb-4">Activity Log</h3>
      <div className="space-y-3 max-h-64 overflow-y-auto">
        {activities.map((activity, index) => (
          <div key={index} className="flex items-start gap-3 text-sm">
            <span className="text-gray-500 shrink-0">{activity.time}</span>
            <span className={`${
              activity.type === 'success' ? 'text-green-400' :
              activity.type === 'error' ? 'text-red-400' :
              'text-gray-300'
            }`}>
              {activity.message}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [agents, setAgents] = useState<AgentStatus[]>([
    {
      id: 'pauli',
      name: 'Pauli',
      type: 'analytical',
      status: 'active',
      tasks_completed: 127,
      current_task: 'Analyzing data patterns...',
    },
    {
      id: 'synthia',
      name: 'Synthia',
      type: 'creative',
      status: 'active',
      tasks_completed: 89,
      current_task: 'Generating content...',
    },
  ]);

  const [activities, setActivities] = useState([
    { time: '12:45:32', message: 'Pauli completed data analysis task', type: 'success' },
    { time: '12:44:18', message: 'Synthia generated new content draft', type: 'success' },
    { time: '12:43:05', message: 'System health check passed', type: 'info' },
    { time: '12:42:00', message: 'New task submitted: Analyze Q4 metrics', type: 'info' },
  ]);

  const handleTaskSubmit = (task: string) => {
    // Add to activity log
    setActivities(prev => [
      { time: new Date().toLocaleTimeString(), message: `New task submitted: ${task}`, type: 'info' },
      ...prev
    ]);
    
    // Simulate agent response
    setTimeout(() => {
      setActivities(prev => [
        { time: new Date().toLocaleTimeString(), message: `Pauli started processing: ${task}`, type: 'success' },
        ...prev
      ]);
    }, 1000);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-black text-white">
      {/* Header */}
      <header className="border-b border-white/10 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/">
              <motion.button
                whileHover={{ scale: 1.05 }}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                <Home className="w-5 h-5" />
              </motion.button>
            </Link>
            <h1 className="text-2xl font-bold gradient-text">ARCHON X Dashboard</h1>
          </div>
          <div className="flex items-center gap-4">
            <motion.button
              whileHover={{ scale: 1.05 }}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <Settings className="w-5 h-5" />
            </motion.button>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-sm text-gray-400">System Online</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Active Agents', value: '2', color: 'text-green-400' },
            { label: 'Tasks Completed', value: '216', color: 'text-purple-400' },
            { label: 'System Load', value: '42%', color: 'text-blue-400' },
            { label: 'Uptime', value: '99.9%', color: 'text-pink-400' },
          ].map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass-container p-4 rounded-xl text-center"
            >
              <div className={`text-3xl font-bold ${stat.color}`}>{stat.value}</div>
              <div className="text-sm text-gray-400">{stat.label}</div>
            </motion.div>
          ))}
        </div>

        {/* Agent Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {agents.map((agent, index) => (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <AgentCard agent={agent} />
            </motion.div>
          ))}
        </div>

        {/* Task Input and Activity Log */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TaskInput onSubmit={handleTaskSubmit} />
          <ActivityLog activities={activities} />
        </div>
      </div>
    </main>
  );
}