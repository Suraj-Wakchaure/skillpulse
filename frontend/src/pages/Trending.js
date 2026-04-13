import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, TrendingDown, Flame, Snowflake, Loader2 } from 'lucide-react';
import Sidebar from '../components/Sidebar';

export default function Trending() {
  const [trends, setTrends] = useState({ rising: [], declining: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('http://localhost:5001/api/trends')
      .then(res => {
        if (res.data.success) {
          setTrends(res.data.data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching trends:", err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="min-h-screen bg-brand-dark flex">
      <Sidebar />

      <div className="flex-1 ml-64 p-8 overflow-y-auto">
        <div className="max-w-6xl mx-auto space-y-8">
          
          {/* Header */}
          <div className="flex items-center gap-4 mb-8">
            <div className="p-4 bg-brand-saffron/10 border border-brand-saffron/20 rounded-2xl">
              <TrendingUp className="text-brand-saffron" size={32} />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Market Trends</h1>
              <p className="text-zinc-400 mt-1">Track which technologies are gaining momentum and which are cooling down.</p>
            </div>
          </div>

          {loading ? (
             <div className="flex flex-col items-center justify-center py-20 text-zinc-500">
               <Loader2 className="animate-spin mb-4" size={32} />
               <p>Analyzing market momentum...</p>
             </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              
              {/* 🚀 RISING SKILLS COLUMN */}
              <div className="bg-brand-card rounded-xl border border-zinc-800 shadow-xl overflow-hidden">
                <div className="p-6 border-b border-zinc-800 bg-zinc-900/50 flex items-center gap-3">
                  <Flame className="text-orange-500" size={24} />
                  <h2 className="text-xl font-bold text-white">Surging in Demand</h2>
                </div>
                <div className="divide-y divide-zinc-800/50">
                  {trends.rising.length > 0 ? trends.rising.map((item, index) => (
                    <div key={index} className="p-5 flex items-center justify-between hover:bg-zinc-800/30 transition-colors">
                      <div>
                        <h3 className="text-lg font-bold text-white capitalize">{item.skill}</h3>
                        <span className="text-sm text-zinc-400">{item.jobs} recent jobs</span>
                      </div>
                      <div className="flex items-center gap-2 text-green-500 bg-green-500/10 px-3 py-1.5 rounded-lg border border-green-500/20">
                        <TrendingUp size={18} />
                        <span className="font-bold">{item.change}</span>
                      </div>
                    </div>
                  )) : (
                    <div className="p-8 text-center text-zinc-500">Not enough historical data to show rising trends yet.</div>
                  )}
                </div>
              </div>

              {/* ❄️ DECLINING SKILLS COLUMN */}
              <div className="bg-brand-card rounded-xl border border-zinc-800 shadow-xl overflow-hidden">
                <div className="p-6 border-b border-zinc-800 bg-zinc-900/50 flex items-center gap-3">
                  <Snowflake className="text-blue-400" size={24} />
                  <h2 className="text-xl font-bold text-white">Cooling Down</h2>
                </div>
                <div className="divide-y divide-zinc-800/50">
                  {trends.declining.length > 0 ? trends.declining.map((item, index) => (
                    <div key={index} className="p-5 flex items-center justify-between hover:bg-zinc-800/30 transition-colors">
                      <div>
                        <h3 className="text-lg font-bold text-white capitalize">{item.skill}</h3>
                        <span className="text-sm text-zinc-400">{item.jobs} recent jobs</span>
                      </div>
                      <div className="flex items-center gap-2 text-red-400 bg-red-400/10 px-3 py-1.5 rounded-lg border border-red-400/20">
                        <TrendingDown size={18} />
                        <span className="font-bold">{item.change}</span>
                      </div>
                    </div>
                  )) : (
                    <div className="p-8 text-center text-zinc-500">Not enough historical data to show declining trends yet.</div>
                  )}
                </div>
              </div>

            </div>
          )}

        </div>
      </div>
    </div>
  );
}