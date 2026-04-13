import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { Briefcase, Code2, TrendingUp, Activity } from 'lucide-react';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../context/AuthContext';

// Register Chart.js components
ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    // Fetch DB Stats from your Flask Backend
    axios.get('http://localhost:5001/api/stats')
      .then(res => setStats(res.data.data))
      .catch(err => console.error("Error fetching stats:", err));

    // Fetch Trends Chart Data from your Flask Backend
    axios.get('http://localhost:5001/api/trends-chart')
      .then(res => {
        const data = res.data.data;
        setChartData({
          labels: data.labels,
          datasets: [{
            label: 'Job Postings',
            data: data.values,
            backgroundColor: 'rgba(249, 115, 22, 0.2)', // Transparent Saffron
            borderColor: '#f97316', // Solid Saffron border
            borderWidth: 2,
            hoverBackgroundColor: 'rgba(249, 115, 22, 0.4)',
            borderRadius: 4,
          }]
        });
      })
      .catch(err => console.error("Error fetching chart data:", err));
  }, []);

  return (
    <div className="min-h-screen bg-brand-dark flex">
      {/* 1. Persistent Sidebar */}
      <Sidebar />

      {/* 2. Main Content Area (Offset by sidebar width 'ml-64') */}
      <div className="flex-1 ml-64 p-8">
        <div className="max-w-6xl mx-auto space-y-8">

          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold text-white">
              Welcome back, <span className="text-brand-saffron">{user?.name || 'Suraj'}</span>! 👋
            </h1>
            <p className="text-slate-400 mt-2">Here is your real-time tech market overview.</p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-brand-card p-6 rounded-xl border border-slate-800 flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-blue-500/10 text-blue-500 rounded-lg"><Briefcase size={24} /></div>
                <p className="text-slate-400 text-sm font-medium">Jobs Analyzed</p>
              </div>
              <p className="text-3xl font-bold text-white">{stats?.totalJobs || '...'}</p>
            </div>

            <div className="bg-brand-card p-6 rounded-xl border border-slate-800 flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-brand-saffron/10 text-brand-saffron rounded-lg"><Code2 size={24} /></div>
                <p className="text-slate-400 text-sm font-medium">Unique Skills</p>
              </div>
              <p className="text-3xl font-bold text-white">{stats?.uniqueSkills || '...'}</p>
            </div>

            <div className="bg-brand-card p-6 rounded-xl border border-slate-800 flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-green-500/10 text-green-500 rounded-lg"><TrendingUp size={24} /></div>
                <p className="text-slate-400 text-sm font-medium">Avg Skills per Job</p>
              </div>
              <p className="text-3xl font-bold text-white">{stats?.avgSkillsPerJob || '...'}</p>
            </div>

            <div className="bg-brand-card p-6 rounded-xl border border-slate-800 flex flex-col gap-4 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-24 h-24 bg-brand-saffron/5 rounded-bl-full -z-10"></div>
              <div className="flex items-center gap-3">
                <div className="p-3 bg-brand-saffron/20 text-brand-saffron rounded-lg"><Activity size={24} /></div>
                <p className="text-slate-400 text-sm font-medium">AI Accuracy</p>
              </div>
              <p className="text-3xl font-bold text-white">91%</p>
            </div>
          </div>

          {/* Chart Section */}
          <div className="bg-brand-card p-6 rounded-xl border border-slate-800 shadow-lg">
            <h2 className="text-xl font-bold text-white mb-6">Top In-Demand Skills</h2>
            <div className="h-[400px]">
              {chartData ? (
                <Bar
                  data={chartData}
                  options={{
                    indexAxis: 'y', // 🔥 THIS MAKES IT HORIZONTAL
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: false },
                      tooltip: {
                        backgroundColor: '#18181b', // Zinc-900
                        titleColor: '#f97316', // Saffron
                        bodyColor: '#e4e4e7', // Zinc-200
                        borderColor: '#27272a', // Zinc-800
                        borderWidth: 1,
                        padding: 12,
                        displayColors: false, // Hides the little color box
                      }
                    },
                    scales: {
                      x: { grid: { color: '#27272a' }, ticks: { color: '#a1a1aa' } },
                      y: { grid: { display: false }, ticks: { color: '#e4e4e7', font: { size: 13 } } }
                    }
                  }}
                />
              ) : (
                <div className="flex h-full items-center justify-center text-slate-500">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-brand-saffron mr-3"></div>
                  Fetching live market data...
                </div>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}