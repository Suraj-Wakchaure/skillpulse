import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Target, ArrowRight, BrainCircuit, TrendingUp, ShieldCheck, Globe, Calculator, Bot } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Legend } from 'recharts';

export default function LandingPage() {
    const [topSkills, setTopSkills] = useState([]);
    const [categories, setCategories] = useState([]);

    useEffect(() => {
        // Fetch live market data for the charts
        const fetchData = async () => {
            try {
                const skillsRes = await axios.get('http://localhost:5001/api/skills/top');
                if (skillsRes.data.success) {
                    // Format data for the bar chart
                    setTopSkills(skillsRes.data.data.slice(0, 6).map(item => ({
                        name: item.skill.toUpperCase(),
                        Demand: item.jobs
                    })));
                }

                const catRes = await axios.get('http://localhost:5001/api/categories');
                if (catRes.data.success) {
                    setCategories(catRes.data.data.map(item => ({
                        name: item.category,
                        value: item.mentions
                    })));
                }
            } catch (err) {
                console.error("Error fetching landing page data:", err);
            }
        };
        fetchData();
    }, []);

    const COLORS = ['#f97316', '#fbbf24', '#fcd34d', '#3b82f6', '#10b981', '#8b5cf6'];

    return (
        <div className="min-h-screen bg-brand-dark text-white font-sans selection:bg-brand-saffron selection:text-slate-900">

                {/* Navbar */}
                <nav className="container mx-auto px-6 py-6 flex justify-between items-center relative z-10 sticky top-0 bg-brand-dark/80 backdrop-blur-md border-b border-zinc-800/50">
                    <div className="flex items-center gap-2">
                        <Target className="text-brand-saffron" size={32} />
                        <span className="text-2xl font-black tracking-tight">Skill<span className="text-brand-saffron">Pulse</span></span>
                    </div>

                    {/* 🔥 NEW JUMP LINKS 🔥 */}
                    <div className="hidden md:flex items-center gap-8">
                        <a href="#analytics" className="text-zinc-400 hover:text-brand-saffron text-sm font-bold transition-colors">Analytics</a>
                        <a href="#features" className="text-zinc-400 hover:text-brand-saffron text-sm font-bold transition-colors">Features</a>
                    </div>

                    <div className="flex items-center gap-4">
                        <Link to="/login" className="text-zinc-300 hover:text-white font-medium transition-colors">Sign In</Link>
                        <Link to="/signup" className="px-5 py-2.5 bg-brand-saffron text-slate-900 font-bold rounded-lg hover:bg-brand-amber transition-colors">
                            Get Started
                        </Link>
                    </div>
                </nav>

                {/* Hero Section */}
                <main className="container mx-auto px-6 pt-20 pb-16 text-center">
                    <div className="max-w-4xl mx-auto space-y-8">
                        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-brand-saffron/10 border border-brand-saffron/20 text-brand-saffron font-medium text-sm mb-4">
                            <span className="w-2 h-2 rounded-full bg-brand-saffron animate-pulse"></span>
                            Live Job Market Analysis
                        </div>

                        <h1 className="text-5xl md:text-7xl font-black tracking-tight leading-tight">
                            Stop Guessing. <br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-saffron to-brand-amber">
                                Know Exactly What to Learn.
                            </span>
                        </h1>

                        <p className="text-xl text-zinc-400 max-w-2xl mx-auto leading-relaxed">
                            SkillPulse analyzes thousands of live job postings to generate AI-powered, personalized learning roadmaps for your dream tech career.
                        </p>

                        <div className="pt-8">
                            <Link to="/signup" className="inline-flex items-center gap-2 px-8 py-4 bg-brand-saffron text-slate-900 text-lg font-bold rounded-xl hover:bg-brand-amber transition-all hover:scale-105 shadow-[0_0_40px_rgba(249,115,22,0.3)]">
                                Build My AI Roadmap <ArrowRight size={20} />
                            </Link>
                        </div>
                    </div>
                </main>

                {/* Data Visualizations Section */}
                <section id="analytics" className="bg-zinc-900/50 border-y border-zinc-800 py-20 mt-10 scroll-mt-24">
                    <div className="container mx-auto px-6">
                        <div className="text-center mb-16">
                            <h2 className="text-3xl font-bold mb-4">Real-Time Market Intelligence</h2>
                            <p className="text-zinc-400">Powered by automated data scraping from global job boards.</p>
                        </div>

                        <div className="grid md:grid-cols-2 gap-12 max-w-6xl mx-auto">

                            {/* Bar Chart */}
                            <div className="bg-brand-card p-8 rounded-2xl border border-zinc-800 shadow-xl">
                                <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                                    <TrendingUp className="text-brand-saffron" /> Top In-Demand Tech Skills
                                </h3>
                                <div className="h-72 w-full">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={topSkills} layout="vertical" margin={{ top: 0, right: 0, left: 20, bottom: 0 }}>
                                            <XAxis type="number" hide />
                                            <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: '#a1a1aa', fontSize: 12 }} />
                                            <Tooltip cursor={{ fill: '#27272a' }} contentStyle={{ backgroundColor: '#18181b', borderColor: '#3f3f46', color: '#fff' }} />
                                            <Bar dataKey="Demand" fill="#f97316" radius={[0, 4, 4, 0]} barSize={24} />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            {/* Pie Chart */}
                            <div className="bg-brand-card p-8 rounded-2xl border border-zinc-800 shadow-xl">
                                <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                                    <BrainCircuit className="text-brand-saffron" /> Market Skill Categories
                                </h3>
                                <div className="h-72 w-full">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <PieChart>
                                            <Pie
                                                data={categories.map((entry, index) => ({
                                                    ...entry,
                                                    fill: COLORS[index % COLORS.length]
                                                }))}
                                                cx="50%" cy="50%"
                                                innerRadius={60} outerRadius={90}
                                                paddingAngle={5}
                                                dataKey="value"
                                                label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                                                labelLine={false}
                                            />
                                            <Tooltip contentStyle={{ backgroundColor: '#18181b', borderColor: '#3f3f46', color: '#fff' }} />
                                            <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '12px', color: '#a1a1aa' }} />
                                        </PieChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                        </div>
                    </div>
                </section>

                {/* Real-World USPs Section (Upgraded UI) */}
                <section id="features" className="container mx-auto px-6 py-24 border-b border-zinc-800 scroll-mt-20">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-black text-white tracking-tight">Why SkillPulse?</h2>
                        <p className="text-zinc-400 mt-4 text-lg max-w-2xl mx-auto">Bridging the gap between academic curriculums and real-world industry demands.</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">

                        <div className="bg-zinc-900 border border-zinc-800 p-8 rounded-2xl hover:-translate-y-2 hover:border-brand-saffron/50 hover:shadow-[0_0_30px_rgba(249,115,22,0.15)] transition-all duration-300">
                            <div className="w-14 h-14 bg-brand-saffron/10 text-brand-saffron rounded-xl flex items-center justify-center mb-6 border border-brand-saffron/20">
                                <Globe size={28} />
                            </div>
                            <h3 className="text-xl font-bold text-white mb-3">1. Live Market Intelligence</h3>
                            <p className="text-zinc-400 leading-relaxed">Unlike static roadmaps, SkillPulse continuously scrapes real job postings to ensure you are learning what companies are actually hiring for today.</p>
                        </div>

                        <div className="bg-zinc-900 border border-zinc-800 p-8 rounded-2xl hover:-translate-y-2 hover:border-brand-saffron/50 hover:shadow-[0_0_30px_rgba(249,115,22,0.15)] transition-all duration-300">
                            <div className="w-14 h-14 bg-brand-saffron/10 text-brand-saffron rounded-xl flex items-center justify-center mb-6 border border-brand-saffron/20">
                                <Calculator size={28} />
                            </div>
                            <h3 className="text-xl font-bold text-white mb-3">2. Mathematical Skill Gap</h3>
                            <p className="text-zinc-400 leading-relaxed">Input your current skillset and target role. Our algorithm calculates exactly what you are missing, ranking skills by actual market demand.</p>
                        </div>

                        <div className="bg-zinc-900 border border-zinc-800 p-8 rounded-2xl hover:-translate-y-2 hover:border-brand-saffron/50 hover:shadow-[0_0_30px_rgba(249,115,22,0.15)] transition-all duration-300">
                            <div className="w-14 h-14 bg-brand-saffron/10 text-brand-saffron rounded-xl flex items-center justify-center mb-6 border border-brand-saffron/20">
                                <Bot size={28} />
                            </div>
                            <h3 className="text-xl font-bold text-white mb-3">3. AI-Generated Paths</h3>
                            <p className="text-zinc-400 leading-relaxed">We feed your unique skill gap data into Llama 3.3 to instantly generate a step-by-step, actionable learning timeline tailored specifically to you.</p>
                        </div>

                    </div>
                </section>

                {/* Real Footer */}
                <footer className="border-t border-zinc-800 py-8 mt-auto">
                    <div className="container mx-auto px-6 text-center flex flex-col items-center justify-center">
                        <div className="flex items-center gap-2 mb-2">
                            <Target className="text-zinc-600" size={20} />
                            <span className="text-lg font-black tracking-tight text-zinc-500">SkillPulse</span>
                        </div>
                        <p className="text-zinc-500 text-sm">© 2026 Developed by Suraj Wakchaure.</p>
                    </div>
                </footer>

            </div>
            );
}