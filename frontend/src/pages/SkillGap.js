import React, { useState } from 'react';
import axios from 'axios';
import { Target, Plus, X, Loader2, AlertCircle, TrendingUp, Briefcase, CheckCircle2, Building2, Map } from 'lucide-react';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../context/AuthContext';
import ReactMarkdown from 'react-markdown';

export default function SkillGap() {
    const [skillInput, setSkillInput] = useState('');
    const [userSkills, setUserSkills] = useState(['HTML', 'CSS', 'JavaScript']); // Some defaults
    const [targetRole, setTargetRole] = useState('Full Stack Developer');
    const { user } = useAuth();
    const [saveStatus, setSaveStatus] = useState('');
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState('');

    // Handle adding skills as "Chips"
    const handleAddSkill = (e) => {
        e.preventDefault();
        if (skillInput.trim() && !userSkills.includes(skillInput.trim())) {
            setUserSkills([...userSkills, skillInput.trim()]);
            setSkillInput('');
        }
    };

    const removeSkill = (skillToRemove) => {
        setUserSkills(userSkills.filter(skill => skill !== skillToRemove));
    };



    // Call the Flask API
    const analyzeGap = async () => {
        if (userSkills.length === 0) {
            setError("Please add at least one skill.");
            return;
        }
        if (!targetRole) {
            setError("Please select a target role.");
            return;
        }

        setLoading(true);
        setError('');
        setResults(null);

        try {
            const response = await axios.post('https://skillpulse-api-2026.onrender.com/api/skill-gap', {
                skills: userSkills,
                role: targetRole
            });

            if (response.data.success) {
                if (response.data.data.error) {
                    setError(response.data.data.error); // Catch "No jobs found" error
                } else {
                    setResults(response.data.data);
                }
            } else {
                setError("Failed to analyze skills.");
            }
        } catch (err) {
            console.error(err);
            setError("Server error. Make sure your Python backend is running.");
        }
        setLoading(false);
    };

    const handleSavePath = async () => {
        if (!user?.email) {
            alert("Please log in to save paths.");
            return;
        }

        setSaveStatus('saving');
        try {
            const res = await axios.post('https://skillpulse-api-2026.onrender.com/api/paths/save', {
                email: user.email,
                role: targetRole,
                missing_skills: results.skills_missing
            });

            if (res.data.success) {
                setSaveStatus('saved');
                setTimeout(() => setSaveStatus(''), 3000);
            } else if (res.data.limit_reached) {
                alert(res.data.message); // This pops up the "Max 3 paths" warning!
                setSaveStatus('');
            }
        } catch (err) {
            console.error(err);
            alert("Error saving path.");
            setSaveStatus('');
        }
    };


    return (
        <div className="min-h-screen bg-brand-dark flex">
            <Sidebar />

            <div className="flex-1 ml-64 p-8 overflow-y-auto">
                <div className="max-w-5xl mx-auto space-y-8">

                    {/* Header */}
                    <div>
                        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                            <Target className="text-brand-saffron" size={32} />
                            Skill Gap Analyzer
                        </h1>
                        <p className="text-zinc-400 mt-2">Discover exactly what you need to learn to land your dream role.</p>
                    </div>

                    {/* INPUT SECTION */}
                    <div className="bg-brand-card p-8 rounded-xl border border-zinc-800 shadow-lg">
                        <div className="grid md:grid-cols-2 gap-8">

                            {/* Left: Skills Input */}
                            <div>
                                <label className="block text-sm font-medium text-zinc-300 mb-2">1. Your Current Skills</label>
                                <form onSubmit={handleAddSkill} className="flex gap-2 mb-4">
                                    <input
                                        type="text"
                                        value={skillInput}
                                        onChange={(e) => setSkillInput(e.target.value)}
                                        placeholder="e.g. Python, React..."
                                        className="flex-1 px-4 py-2 bg-brand-dark border border-zinc-700 rounded-lg text-white focus:outline-none focus:border-brand-saffron"
                                    />
                                    <button type="submit" className="px-4 py-2 bg-zinc-800 text-white rounded-lg hover:bg-zinc-700 transition">
                                        <Plus size={20} />
                                    </button>
                                </form>

                                {/* Skill Chips */}
                                <div className="flex flex-wrap gap-2">
                                    {userSkills.map(skill => (
                                        <span key={skill} className="px-3 py-1.5 bg-brand-saffron/10 border border-brand-saffron/20 text-brand-saffron rounded-full flex items-center gap-2 text-sm">
                                            {skill}
                                            <button onClick={() => removeSkill(skill)} className="hover:text-white transition"><X size={14} /></button>
                                        </span>
                                    ))}
                                    {userSkills.length === 0 && <span className="text-zinc-500 text-sm">No skills added yet.</span>}
                                </div>
                            </div>

                            {/* Right: Target Role */}
                            <div>
                                <label className="block text-sm font-medium text-zinc-300 mb-2">2. Your Target Role</label>
                                <div className="relative mb-6">
                                    <Briefcase className="absolute left-3 top-3 text-zinc-500" size={20} />
                                    <input
                                        type="text"
                                        list="role-suggestions"
                                        value={targetRole}
                                        onChange={(e) => setTargetRole(e.target.value)}
                                        placeholder="e.g. Data Analyst, Prompt Engineer..."
                                        className="w-full pl-10 pr-4 py-2.5 bg-brand-dark border border-zinc-700 rounded-lg text-white focus:outline-none focus:border-brand-saffron"
                                    />
                                    <datalist id="role-suggestions">
                                        <option value="Software Developer" />
                                        <option value="Full Stack Developer" />
                                        <option value="Data Analyst" />
                                        <option value="DevOps Engineer" />
                                        <option value="Machine Learning Engineer" />
                                        <option value="Cloud Architect" />
                                        <option value="UI/UX Designer" />
                                        <option value="Prompt Engineer" />
                                    </datalist>
                                </div>

                                <button
                                    onClick={analyzeGap}
                                    disabled={loading}
                                    className="w-full py-3 bg-gradient-to-r from-brand-saffron to-brand-amber text-slate-900 font-bold rounded-lg hover:shadow-lg hover:shadow-brand-saffron/20 transition disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2"
                                >
                                    {loading ? (
                                        <><Loader2 className="animate-spin" size={20} /> AI is analyzing market data...</>
                                    ) : (
                                        <><Target size={20} /> Analyze My Skill Gap</>
                                    )}
                                </button>
                            </div>
                        </div>

                        {error && (
                            <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg flex items-start gap-3">
                                <AlertCircle size={20} className="mt-0.5" />
                                <p>{error}</p>
                            </div>
                        )}
                    </div>

                    {/* RESULTS SECTION */}
                    {results && !loading && (
                        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">

                            {/* Top Stats */}
                            <div className="grid md:grid-cols-3 gap-6">
                                <div className="bg-brand-card p-6 rounded-xl border border-zinc-800 flex items-center justify-between">
                                    <div>
                                        <p className="text-zinc-400 text-sm">Market Match Score</p>
                                        <p className="text-3xl font-bold text-white mt-1">{results.match_percentage}%</p>
                                    </div>
                                    <div className="w-16 h-16 rounded-full border-4 border-brand-saffron flex items-center justify-center text-brand-saffron">
                                        <Target size={24} />
                                    </div>
                                </div>

                                <div className="bg-brand-card p-6 rounded-xl border border-zinc-800">
                                    <p className="text-zinc-400 text-sm">Skills You Have</p>
                                    <p className="text-2xl font-bold text-white mt-1">{results.skills_you_have?.length || 0}</p>
                                    <p className="text-sm text-green-400 mt-2 flex items-center gap-1"><CheckCircle2 size={14} /> Verified</p>
                                </div>

                                <div className="bg-brand-card p-6 rounded-xl border border-zinc-800">
                                    <p className="text-zinc-400 text-sm">Jobs Analyzed</p>
                                    <p className="text-2xl font-bold text-white mt-1">{results.total_jobs}</p>
                                    <p className="text-sm text-brand-saffron mt-2 flex items-center gap-1"><TrendingUp size={14} /> Real-time data</p>
                                </div>
                            </div>

                            {/* Top Hiring Companies Section */}
                            {results.top_companies && results.top_companies.length > 0 && (
                                <div className="bg-brand-card p-6 rounded-xl border border-zinc-800">
                                    <div className="flex items-center gap-2 mb-4">
                                        <Building2 className="text-zinc-400" size={20} />
                                        <h3 className="text-white font-bold">Top Companies Hiring This Role</h3>
                                    </div>
                                    <div className="flex flex-wrap gap-3">
                                        {results.top_companies.map((company, index) => (
                                            <span key={index} className="px-4 py-2 bg-zinc-800/50 border border-zinc-700 text-zinc-300 rounded-lg text-sm font-medium hover:bg-zinc-800 hover:text-white transition-colors cursor-default">
                                                {company}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Missing Skills Table */}
                            <div className="bg-brand-card rounded-xl border border-zinc-800 overflow-hidden">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-white font-bold">Priority Skills to Learn</h3>

                                    {/* 🔥 THE NEW SAVE BUTTON 🔥 */}
                                    <button
                                        onClick={handleSavePath}
                                        disabled={saveStatus === 'saving' || saveStatus === 'saved'}
                                        className={`px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition-colors ${saveStatus === 'saved'
                                            ? 'bg-green-500/20 text-green-400'
                                            : 'bg-brand-saffron text-slate-900 hover:bg-brand-amber'
                                            }`}
                                    >
                                        {saveStatus === 'saved' ? (
                                            <><CheckCircle2 size={16} /> Saved to Path!</>
                                        ) : saveStatus === 'saving' ? (
                                            <><Loader2 className="animate-spin" size={16} /> Saving...</>
                                        ) : (
                                            <><Map size={16} /> Save to Learning Path</>
                                        )}
                                    </button>
                                </div>
                                <div className="overflow-x-auto">
                                    <table className="w-full text-left">
                                        <thead className="bg-brand-dark/50 text-zinc-400 text-sm">
                                            <tr>
                                                <th className="px-6 py-4 font-medium">Rank</th>
                                                <th className="px-6 py-4 font-medium">Skill</th>
                                                <th className="px-6 py-4 font-medium">Demand</th>
                                                <th className="px-6 py-4 font-medium">Est. Time</th>
                                                <th className="px-6 py-4 font-medium">Priority</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-zinc-800/50 text-zinc-300">
                                            {results.skills_missing?.map((skill, index) => (
                                                <tr key={index} className="hover:bg-zinc-800/30 transition">
                                                    <td className="px-6 py-4">#{skill.learn_order}</td>
                                                    <td className="px-6 py-4 font-bold text-white capitalize">{skill.skill}</td>
                                                    <td className="px-6 py-4">
                                                        <div className="flex items-center gap-2">
                                                            <span className="w-16 bg-zinc-800 rounded-full h-2">
                                                                <span className="bg-brand-blue h-2 rounded-full block" style={{ width: `${skill.percentage}%` }}></span>
                                                            </span>
                                                            <span className="text-xs">{skill.percentage}%</span>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 text-sm">{skill.estimated_time}</td>
                                                    <td className="px-6 py-4">
                                                        <span className={`px-2.5 py-1 text-xs font-bold rounded-full ${skill.priority === 'CRITICAL' ? 'bg-red-500/10 text-red-500 border border-red-500/20' :
                                                            skill.priority === 'HIGH' ? 'bg-brand-saffron/10 text-brand-saffron border border-brand-saffron/20' :
                                                                'bg-zinc-800 text-zinc-400 border border-zinc-700'
                                                            }`}>
                                                            {skill.priority}
                                                        </span>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            {/* AI Roadmap */}
                            <div className="bg-gradient-to-br from-brand-card to-zinc-900 p-8 rounded-xl border border-zinc-800">
                                <div className="flex items-center gap-3 mb-6">
                                    <div className="p-2 bg-brand-saffron/20 text-brand-saffron rounded-lg">
                                        <Target size={24} />
                                    </div>
                                    <h2 className="text-2xl font-bold text-white">Your AI Learning Roadmap</h2>
                                </div>

                                <div className="prose prose-invert max-w-none text-zinc-300 leading-relaxed">
                                    <ReactMarkdown>{results.ai_roadmap}</ReactMarkdown>
                                </div>
                            </div>

                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}