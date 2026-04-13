import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Map, CheckCircle2, Lock, PlayCircle, BookOpen, Loader2, PlusCircle, Trash2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../context/AuthContext';

export default function LearningPath() {
    const { user } = useAuth();
    const [savedPaths, setSavedPaths] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activePathIndex, setActivePathIndex] = useState(0);
    const [completedSteps, setCompletedSteps] = useState({}); // 🔥 Change [] to {}

    useEffect(() => {
        if (user?.email) {
            axios.get(`https://skillpulse-api-2026.onrender.com/api/paths/${user.email}`)
                .then(res => {
                    if (res.data.success) {
                        const paths = res.data.data.reverse();
                        setSavedPaths(paths); // Show newest first

                        // 🔥 LOAD SAVED PROGRESS FROM DATABASE 🔥
                        const initialCompleted = {};
                        paths.forEach(path => {
                            initialCompleted[path._id] = path.completed_steps || [];
                        });
                        setCompletedSteps(initialCompleted);
                    }
                    setLoading(false);
                })
                .catch(err => {
                    console.error("Error fetching paths:", err);
                    setLoading(false);
                });
        } else {
            setLoading(false);
        }
    }, [user]);

    const handleDeletePath = async (pathId) => {
        // Add a brutal confirmation so they don't click it by accident
        if (!window.confirm("Are you sure you want to delete this learning track? This cannot be undone.")) return;

        try {
            const res = await axios.delete(`https://skillpulse-api-2026.onrender.com/api/paths/${pathId}`);
            if (res.data.success) {
                // Remove it from the UI immediately without refreshing the page
                const newPaths = savedPaths.filter(p => p._id !== pathId);
                setSavedPaths(newPaths);
                setActivePathIndex(0); // Reset them back to the first tab
            }
        } catch (err) {
            console.error("Error deleting path:", err);
            alert("Failed to delete the path. Make sure your backend is running.");
        }
    };

    const handleMarkAsDone = async (pathId, stepId, totalSteps) => {
        const currentTrackDone = completedSteps[pathId] || [];
        const newTrackDone = [...currentTrackDone, stepId];

        // 1. Update UI instantly (Optimistic UI update)
        setCompletedSteps({ ...completedSteps, [pathId]: newTrackDone });

        // 2. Calculate the new completion percentage
        const newProgress = Math.round((newTrackDone.length / totalSteps) * 100);

        // 3. Update the savedPaths state so the Header percentage changes instantly
        setSavedPaths(savedPaths.map(p =>
            p._id === pathId ? { ...p, progress: newProgress, completed_steps: newTrackDone } : p
        ));

        // 4. Send to database permanently
        try {
            await axios.put(`https://skillpulse-api-2026.onrender.com/api/paths/${pathId}/progress`, {
                completed_steps: newTrackDone,
                progress: newProgress
            });
        } catch (err) {
            console.error("Error saving progress:", err);
            alert("Failed to save progress to database.");
        }
    };

    const getStatusIcon = (status) => {
        if (status === 'completed') return <CheckCircle2 className="text-green-500 bg-brand-dark" size={28} />;
        if (status === 'active') return <PlayCircle className="text-brand-saffron bg-brand-dark" size={28} />;
        return <Lock className="text-zinc-600 bg-brand-dark" size={28} />;
    };

    const currentPath = savedPaths[activePathIndex];

    return (
        <div className="min-h-screen bg-brand-dark flex">
            <Sidebar />

            <div className="flex-1 ml-64 p-8 overflow-y-auto">
                <div className="max-w-4xl mx-auto space-y-8">

                    {/* Header */}
                    {/* Header */}
                    <div className="flex items-center justify-between mb-10">
                        <div className="flex items-center gap-4">
                            <div className="p-4 bg-brand-saffron/10 border border-brand-saffron/20 rounded-2xl">
                                <Map className="text-brand-saffron" size={32} />
                            </div>
                            <div>
                                <h1 className="text-3xl font-bold text-white">My Learning Path</h1>
                                <p className="text-zinc-400 mt-1">
                                    {currentPath ? `${currentPath.target_role} Track • ${currentPath.progress}% Completed` : 'Track your career journey'}
                                </p>
                            </div>
                        </div>

                        {/* 🔥 THE DELETE BUTTON GOES HERE 🔥 */}
                        {currentPath && (
                            <button
                                onClick={() => handleDeletePath(currentPath._id)}
                                className="flex items-center gap-2 px-4 py-2 bg-red-500/10 text-red-400 font-bold border border-red-500/20 rounded-lg hover:bg-red-500/20 transition-colors"
                            >
                                <Trash2 size={20} />
                                Delete Track
                            </button>
                        )}
                    </div>

                    {loading ? (
                        <div className="flex flex-col items-center justify-center py-20 text-zinc-500">
                            <Loader2 className="animate-spin mb-4" size={32} />
                            <p>Loading your saved paths...</p>
                        </div>
                    ) : savedPaths.length === 0 ? (

                        <div className="bg-brand-card border border-zinc-800 rounded-xl p-12 text-center flex flex-col items-center">
                            {/* EMPTY STATE */}
                            <div className="w-20 h-20 bg-zinc-800/50 rounded-full flex items-center justify-center mb-6">
                                <Map className="text-zinc-500" size={32} />
                            </div>
                            <h2 className="text-2xl font-bold text-white mb-2">No Learning Paths Yet</h2>
                            <p className="text-zinc-400 mb-8 max-w-md">
                                Run a Skill Gap analysis for your dream role to generate and save a personalized learning roadmap.
                            </p>
                            <Link to="/skill-gap" className="flex items-center gap-2 px-6 py-3 bg-brand-saffron text-slate-900 font-bold rounded-lg hover:bg-brand-amber transition-colors">
                                <PlusCircle size={20} />
                                Analyze a Role
                            </Link>
                        </div>

                    ) : (

                        <div>
                            {/* Path Switcher Tabs (If multiple paths exist) */}
                            {savedPaths.length > 1 && (
                                <div className="flex gap-3 mb-8 pb-4 border-b border-zinc-800 overflow-x-auto">
                                    {savedPaths.map((path, idx) => (
                                        <button
                                            key={path._id}
                                            onClick={() => setActivePathIndex(idx)}
                                            className={`px-4 py-2 rounded-lg font-bold whitespace-nowrap transition-colors ${activePathIndex === idx
                                                ? 'bg-brand-saffron text-slate-900'
                                                : 'bg-zinc-800 text-zinc-400 hover:text-white'
                                                }`}
                                        >
                                            {path.target_role}
                                        </button>
                                    ))}
                                </div>
                            )}

                            {/* Timeline */}
                            <div className="relative pl-4 md:pl-0">
                                {/* Vertical Line */}
                                <div className="absolute left-[27px] md:left-[39px] top-4 bottom-10 w-0.5 bg-zinc-800 hidden md:block"></div>

                                <div className="space-y-8">
                                    {currentPath.steps.map((step, index) => {
                                        // Determine status dynamically for the UI demo
                                        const pathCompletedSteps = completedSteps[currentPath._id] || [];

                                        const isCompleted = pathCompletedSteps.includes(step.id);
                                        const isPreviousCompleted = index === 0 || pathCompletedSteps.includes(currentPath.steps[index - 1].id);
                                        const currentStatus = isCompleted ? 'completed' : isPreviousCompleted ? 'active' : 'locked';

                                        return (
                                            <div key={step.id} className="relative flex items-start gap-6">

                                                {/* Icon Node */}
                                                <div className="relative z-10 flex items-center justify-center w-12 h-12 md:w-20 md:h-20 shrink-0">
                                                    {getStatusIcon(currentStatus)}
                                                </div>

                                                {/* Content Card */}
                                                <div className={`flex-1 p-6 rounded-xl border transition-all ${currentStatus === 'active'
                                                    ? 'bg-zinc-900/80 border-brand-saffron/50 shadow-[0_0_15px_rgba(249,115,22,0.1)]'
                                                    : 'bg-brand-card border-zinc-800'
                                                    }`}>
                                                    <div className="flex flex-col md:flex-row md:items-center justify-between mb-4 gap-2">
                                                        <h3 className={`text-xl font-bold ${currentStatus === 'locked' ? 'text-zinc-500' : 'text-white'}`}>
                                                            Phase {step.id}: {step.title}
                                                        </h3>

                                                        <div className="flex items-center gap-3">
                                                            <span className="text-sm font-medium text-zinc-400 bg-zinc-800/50 px-3 py-1 rounded-full w-fit">
                                                                {step.duration}
                                                            </span>
                                                            {/* 🔥 The Interactive Button 🔥 */}
                                                            {currentStatus === 'active' && (
                                                                <button
                                                                    onClick={() => handleMarkAsDone(currentPath._id, step.id, currentPath.steps.length)}
                                                                    className="text-xs font-bold px-3 py-1 bg-brand-saffron text-slate-900 rounded hover:bg-brand-amber transition"
                                                                >
                                                                    Mark as Done
                                                                </button>
                                                            )}
                                                        </div>
                                                    </div>

                                                    <p className={`mb-4 ${currentStatus === 'locked' ? 'text-zinc-600' : 'text-zinc-400'}`}>
                                                        {step.description}
                                                    </p>

                                                    <div className="flex flex-wrap gap-2">
                                                        {step.skills.map((skill, sIdx) => (
                                                            <span
                                                                key={sIdx}
                                                                className={`px-3 py-1.5 rounded-lg text-sm font-medium border ${currentStatus === 'completed' ? 'bg-green-500/10 text-green-400 border-green-500/20' :
                                                                    currentStatus === 'active' ? 'bg-brand-saffron/10 text-brand-saffron border-brand-saffron/20' :
                                                                        'bg-zinc-800/30 text-zinc-600 border-zinc-800'
                                                                    }`}
                                                            >
                                                                {skill}
                                                            </span>
                                                        ))}
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
}