import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Target, LayoutDashboard, Trophy, TrendingUp, BrainCircuit, Map, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const navItems = [
    { name: 'Overview', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Top Skills', path: '/dashboard/skills', icon: Trophy },
    { name: 'Trending', path: '/dashboard/trends', icon: TrendingUp },
    { name: 'My Skill Gap', path: '/skill-gap', icon: Target, isPrimary: true },
    { name: 'Learning Path', path: '/dashboard/path', icon: Map },
  ];

  return (
    <div className="w-64 bg-brand-card border-r border-slate-800 h-screen fixed left-0 top-0 flex flex-col">
      {/* Header / Logo */}
      <div className="h-20 flex items-center px-6 border-b border-slate-800">
        <Link to="/" className="flex items-center gap-2">
          <Target className="text-brand-saffron" size={28} />
          <span className="text-xl font-extrabold tracking-tight text-white">Skill<span className="text-brand-saffron">Pulse</span></span>
        </Link>
      </div>

      {/* User Profile Snippet */}
      <div className="p-6 border-b border-slate-800 flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-brand-saffron to-brand-amber flex items-center justify-center text-slate-900 font-bold text-lg">
          {user?.name?.charAt(0) || 'U'}
        </div>
        <div className="overflow-hidden">
          <p className="text-white font-medium truncate">{user?.name || 'User'}</p>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 overflow-y-auto py-6 px-4 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.name}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium transition-all duration-200 ${
                item.isPrimary 
                  ? 'bg-brand-saffron/10 text-brand-saffron border border-brand-saffron/20 hover:bg-brand-saffron/20 mt-4 mb-2' 
                  : isActive 
                    ? 'bg-slate-800 text-white' 
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              <item.icon size={20} />
              {item.name}
            </Link>
          );
        })}
      </div>

      {/* Footer / Logout */}
      <div className="p-4 border-t border-slate-800">
        <button 
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 w-full rounded-lg font-medium text-slate-400 hover:text-red-400 hover:bg-red-400/10 transition-all duration-200"
        >
          <LogOut size={20} />
          Log Out
        </button>
      </div>
    </div>
  );
}