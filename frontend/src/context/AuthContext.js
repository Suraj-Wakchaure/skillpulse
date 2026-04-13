import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  // Check if a user is already logged in when the app loads
  useEffect(() => {
    const storedUser = localStorage.getItem('skillpulse_user');
    const storedToken = localStorage.getItem('skillpulse_token');
    
    if (storedUser && storedToken) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const login = (userData, token) => {
    setUser(userData);
    localStorage.setItem('skillpulse_user', JSON.stringify(userData));
    localStorage.setItem('skillpulse_token', token);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('skillpulse_user');
    localStorage.removeItem('skillpulse_token');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);