import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Trophy, Medal, Star, Hash, Loader2 } from 'lucide-react';
import Sidebar from '../components/Sidebar';

export default function TopSkills() {
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch top skills from your Flask backend
    axios.get('http://localhost:5001/api/skills/top')
      .then(res => {
        if (res.data.success) {
          setSkills(res.data.data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching top skills:", err);
        setLoading(false);
      });
  }, []);

  // Helper function to render different icons for Top 3
  const getRankIcon = (rank) => {
    if (rank === 1) return <Trophy className="text-yellow-400" size={28} />;
    if (rank === 2) return <Medal className="text-zinc-300" size={28} />;
    if (rank === 3) return <Medal className="text-amber-700" size={28} />;
    return <Hash className="text-zinc-500" size={24} />;
  };

  return (
    <div className="min-h-screen bg-brand-dark flex">
      <Sidebar />

      <div className="flex-1 ml-64 p-8 overflow-y-auto">
        <div className="max-w-4xl mx-auto space-y-8">
          
          {/* Header */}
          <div className="flex items-center gap-4">
            <div className="p-4 bg-brand-saffron/10 border border-brand-saffron/20 rounded-2xl">
              <Trophy className="text-brand-saffron" size={32} />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Global Top Skills</h1>
              <p className="text-zinc-400 mt-1">The most in-demand technologies across all job postings.</p>
            </div>
          </div>

          {/* List Container */}
          <div className="bg-brand-card rounded-xl border border-zinc-800 shadow-xl overflow-hidden">
            {loading ? (
              <div className="p-12 flex flex-col items-center justify-center text-zinc-500">
                <Loader2 className="animate-spin mb-4" size={32} />
                <p>Calculating market rankings...</p>
              </div>
            ) : (
              <div className="divide-y divide-zinc-800/50">
                {skills.map((item, index) => (
                  <div 
                    key={index} 
                    className={`p-6 flex items-center gap-6 transition-colors hover:bg-zinc-800/30 ${
                      item.rank === 1 ? 'bg-brand-saffron/5' : ''
                    }`}
                  >
                    {/* Rank Icon */}
                    <div className="w-12 flex justify-center font-bold text-xl">
                      {getRankIcon(item.rank)}
                    </div>

                    {/* Skill Name & Progress Bar */}
                    <div className="flex-1">
                      <div className="flex justify-between items-end mb-2">
                        <h3 className="text-xl font-bold text-white capitalize flex items-center gap-2">
                          {item.skill}
                          {item.rank === 1 && <Star className="text-brand-saffron fill-brand-saffron" size={16} />}
                        </h3>
                        <span className="text-zinc-400 text-sm font-medium">
                          {item.jobs} mentions
                        </span>
                      </div>
                      
                      {/* Visual Bar */}
                      <div className="w-full bg-zinc-900 rounded-full h-2.5 border border-zinc-800">
                        <div 
                          className={`h-2.5 rounded-full ${
                            item.rank === 1 ? 'bg-gradient-to-r from-brand-amber to-brand-saffron shadow-[0_0_10px_rgba(249,115,22,0.5)]' : 
                            item.rank <= 3 ? 'bg-brand-saffron' : 
                            'bg-brand-blue'
                          }`} 
                          style={{ width: item.percentage }}
                        ></div>
                      </div>
                    </div>

                    {/* Percentage */}
                    <div className="w-20 text-right">
                      <span className="text-lg font-bold text-white">{item.percentage}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}