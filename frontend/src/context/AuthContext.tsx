import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../api/client';

export interface User {
  id: number;
  email: string;
  name?: string;
  full_name: string;
  role_target?: string;
  experience_level?: string;
  bio?: string;
  skills: string[];
  llm_preference: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (
    email: string,
    password: string,
    fullName: string,
    roleTarget?: string,
    experienceLevel?: string
  ) => Promise<void>;
  loginWithDemo: () => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('career_coach_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchUser = async () => {
    try {
      const res = await apiClient.get('/auth/me');
      setUser(res.data);
    } catch (err) {
      console.error('Failed to fetch user:', err);
      setUser(null);
      localStorage.removeItem('career_coach_token');
      setToken(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchUser();
    } else {
      setIsLoading(false);
    }
  }, [token]);

  const loginWithDemo = async () => {
    setIsLoading(true);
    const demoEmail = 'demo.candidate@careercoach.ai';
    const demoPass = 'CareerCoach2026!';
    try {
      const res = await apiClient.post('/auth/login', {
        email: demoEmail,
        password: demoPass,
      });
      localStorage.setItem('career_coach_token', res.data.access_token);
      setToken(res.data.access_token);
      await fetchUser();
    } catch {
      // Register demo user if not existing
      try {
        const regRes = await apiClient.post('/auth/register', {
          email: demoEmail,
          password: demoPass,
          full_name: 'Alex Morgan',
          role_target: 'Senior Full Stack Software Engineer',
          experience_level: '4-7 years',
        });
        localStorage.setItem('career_coach_token', regRes.data.access_token);
        setToken(regRes.data.access_token);
        await fetchUser();
      } catch (e) {
        console.error('Demo registration failed:', e);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const res = await apiClient.post('/auth/login', { email, password });
    localStorage.setItem('career_coach_token', res.data.access_token);
    setToken(res.data.access_token);
    await fetchUser();
  };

  const register = async (
    email: string,
    password: string,
    fullName: string,
    roleTarget?: string,
    experienceLevel?: string
  ) => {
    const res = await apiClient.post('/auth/register', {
      email,
      password,
      full_name: fullName,
      role_target: roleTarget || 'Full Stack Software Engineer',
      experience_level: experienceLevel || '1-3 years',
    });
    localStorage.setItem('career_coach_token', res.data.access_token);
    setToken(res.data.access_token);
    await fetchUser();
  };

  const logout = () => {
    localStorage.removeItem('career_coach_token');
    setToken(null);
    setUser(null);
  };

  const refreshUser = async () => {
    await fetchUser();
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        register,
        loginWithDemo,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
