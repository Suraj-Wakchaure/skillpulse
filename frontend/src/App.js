import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import SkillGap from './pages/SkillGap'; // 🔥 IMPORT ADDED HERE
import TopSkills from './pages/TopSkills';
import Trending from './pages/Trending';
import LearningPath from './pages/LearningPath';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-brand-dark text-slate-100 font-sans selection:bg-brand-saffron selection:text-white">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/skill-gap" element={<SkillGap />} /> {/* 🔥 ROUTE ADDED HERE */}
            <Route path="/dashboard/skills" element={<TopSkills />} />
            <Route path="/dashboard/trends" element={<Trending />} />
            <Route path="/dashboard/path" element={<LearningPath />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;