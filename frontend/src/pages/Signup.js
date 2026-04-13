import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Target, Mail, Lock, User, Loader2, AlertCircle } from 'lucide-react';

export default function Signup() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // 🔥 SEND DATA TO SECURE PYTHON BACKEND 🔥
      const res = await axios.post('https://skillpulse-api-2026.onrender.com/api/auth/signup', {
        name,
        email,
        password,
        role: 'Student' // Default role for now
      });

      if (res.data.success) {
        // Redirect to login page after successful registration
        navigate('/login');
      }
    } catch (err) {
      console.error(err);
      // Catch the "Email already registered" error from backend
      setError(err.response?.data?.error || 'Failed to create account. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-brand-dark flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-brand-card p-8 rounded-2xl border border-zinc-800 shadow-2xl">
        
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 bg-brand-saffron/10 rounded-full flex items-center justify-center mb-4 border border-brand-saffron/20">
            <Target className="text-brand-saffron" size={32} />
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Create an Account</h1>
          <p className="text-zinc-400 text-sm">Join SkillPulse to get your AI career roadmap.</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg flex items-start gap-3">
            <AlertCircle size={20} className="shrink-0 mt-0.5" />
            <p className="text-sm font-medium">{error}</p>
          </div>
        )}

        <form onSubmit={handleSignup} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">Full Name</label>
            <div className="relative">
              <User className="absolute left-3 top-3 text-zinc-500" size={20} />
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-brand-dark border border-zinc-700 rounded-lg text-white focus:outline-none focus:border-brand-saffron transition-colors"
                placeholder="Suraj Wakchaure"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 text-zinc-500" size={20} />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-brand-dark border border-zinc-700 rounded-lg text-white focus:outline-none focus:border-brand-saffron transition-colors"
                placeholder="you@example.com"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 text-zinc-500" size={20} />
              <input
                type="password"
                required
                minLength="6"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-brand-dark border border-zinc-700 rounded-lg text-white focus:outline-none focus:border-brand-saffron transition-colors"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 mt-2 bg-brand-saffron text-slate-900 font-bold rounded-lg hover:bg-brand-amber transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? <><Loader2 className="animate-spin" size={20} /> Creating Account...</> : 'Sign Up'}
          </button>
        </form>

        <p className="mt-6 text-center text-zinc-400 text-sm">
          Already have an account? <Link to="/login" className="text-brand-saffron hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}