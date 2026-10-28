import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { DemoBanner } from './components/DemoBanner';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { InstitutionDashboard } from './pages/InstitutionDashboard';
import { SubmitApplicationPage } from './pages/SubmitApplicationPage';
import { ApplicationDetailPage } from './pages/ApplicationDetailPage';
import { OfficerReviewPage } from './pages/OfficerReviewPage';
import { AdminDashboard } from './pages/AdminDashboard';
import { VerificationStudioPage } from './pages/VerificationStudioPage';
import { api } from './services/api';
import { User, ApplicationItem } from './types';

export function App() {
  const [user, setUser] = useState<User | null>(null);
  const [currentPath, setCurrentPath] = useState<string>('/');
  const [selectedAppId, setSelectedAppId] = useState<number | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loadingInitial, setLoadingInitial] = useState(true);

  // Initialize Auth from local storage / API
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedUser = localStorage.getItem('verifyai_user');
        if (storedUser) {
          setUser(JSON.parse(storedUser));
        }
        const me = await api.getMe();
        setUser(me);
        localStorage.setItem('verifyai_user', JSON.stringify(me));
      } catch (e) {
        // Not authenticated
      } finally {
        setLoadingInitial(false);
      }
    };
    initAuth();
  }, []);

  const handleLoginSuccess = (loggedInUser: User) => {
    setUser(loggedInUser);
    if (loggedInUser.role === 'review_officer') {
      setCurrentPath('/officer');
    } else if (loggedInUser.role === 'system_admin') {
      setCurrentPath('/admin');
    } else {
      setCurrentPath('/dashboard');
    }
  };

  const handleLogout = () => {
    api.clearToken();
    setUser(null);
    setCurrentPath('/');
    setSelectedAppId(null);
  };

  const handleNavigate = (path: string) => {
    if (path.startsWith('/applications/')) {
      const parts = path.split('/');
      const id = parseInt(parts[2], 10);
      if (!isNaN(id)) {
        setSelectedAppId(id);
        setCurrentPath('/application-detail');
        return;
      }
    }
    if (path === '/applications') {
      setCurrentPath('/dashboard');
      return;
    }
    setCurrentPath(path);
  };

  // Quick 1-click Scenario Switcher for SIH Judges
  const handleSelectScenario = async (scenarioId: string) => {
    try {
      const apps = await api.getApplications();
      let targetApp: ApplicationItem | undefined;

      if (scenarioId === 'scenario-1') {
        targetApp = apps.find(a => a.reference_id.includes('APEX'));
      } else if (scenarioId === 'scenario-2') {
        targetApp = apps.find(a => a.reference_id.includes('BHARATI'));
      } else if (scenarioId === 'scenario-3') {
        targetApp = apps.find(a => a.reference_id.includes('GLOBAL'));
      }

      if (targetApp) {
        setSelectedAppId(targetApp.id);
        // If current user is review officer, open in officer console
        if (user?.role === 'review_officer') {
          setCurrentPath('/officer');
        } else {
          setCurrentPath('/application-detail');
        }
      } else {
        alert('Scenario application loaded in registry. Please sign in or reset demo database.');
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleQuickLoginFromLanding = async (role: string) => {
    try {
      if (role === 'review_officer') {
        const res = await api.login('officer@aicte.gov.in', 'Officer@123');
        handleLoginSuccess(res.user);
      } else if (role === 'institution_admin') {
        const res = await api.login('institution@verifyai.gov.in', 'Admin@123');
        handleLoginSuccess(res.user);
      } else if (role === 'system_admin') {
        const res = await api.login('sysadmin@aicte.gov.in', 'SysAdmin@123');
        handleLoginSuccess(res.user);
      }
    } catch (e: any) {
      alert('Login error: ' + e.message);
    }
  };

  // Render Page Content
  const renderContent = () => {
    if (currentPath === '/') {
      return (
        <LandingPage
          onNavigate={handleNavigate}
          onQuickLogin={handleQuickLoginFromLanding}
        />
      );
    }

    if (currentPath === '/verification-studio' || currentPath === '/benchmark') {
      return <VerificationStudioPage />;
    }

    if (currentPath === '/login' || !user) {
      return (
        <LoginPage
          onLoginSuccess={handleLoginSuccess}
          onNavigate={handleNavigate}
        />
      );
    }

    if (currentPath === '/apply') {
      return (
        <SubmitApplicationPage
          user={user}
          onNavigate={handleNavigate}
          onApplicationCreated={(id) => {
            setSelectedAppId(id);
            setCurrentPath('/application-detail');
          }}
        />
      );
    }

    if (currentPath === '/application-detail' && selectedAppId) {
      return (
        <ApplicationDetailPage
          applicationId={selectedAppId}
          user={user}
          onBack={() => setCurrentPath(user.role === 'review_officer' ? '/officer' : '/dashboard')}
        />
      );
    }

    if (currentPath === '/officer') {
      return (
        <OfficerReviewPage
          user={user}
          onNavigate={handleNavigate}
          selectedAppId={selectedAppId}
        />
      );
    }

    if (currentPath === '/admin' || currentPath === '/admin/rules' || currentPath === '/analytics') {
      return (
        <AdminDashboard
          user={user}
          onNavigate={handleNavigate}
        />
      );
    }

    // Default Institution Dashboard
    return (
      <InstitutionDashboard
        user={user}
        onNavigate={handleNavigate}
        onViewApplication={(id) => {
          setSelectedAppId(id);
          setCurrentPath('/application-detail');
        }}
      />
    );
  };

  return (
    <div className="min-h-screen bg-slatebg flex flex-col font-sans">
      {/* SIH Judge Demo Bar */}
      <DemoBanner
        onSelectScenario={handleSelectScenario}
        onDataReset={() => {
          if (currentPath !== '/') {
            handleNavigate(currentPath);
          }
        }}
      />

      {/* Top Navigation */}
      <Navbar
        user={user}
        onLogout={handleLogout}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        onNavigate={handleNavigate}
      />

      {/* App Body */}
      {currentPath === '/' || currentPath === '/login' || !user ? (
        <div className="flex-1">{renderContent()}</div>
      ) : (
        <div className="flex-1 flex max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 gap-6">
          <Sidebar
            user={user}
            currentPath={currentPath}
            onNavigate={handleNavigate}
            isOpen={sidebarOpen}
            onCloseMobile={() => setSidebarOpen(false)}
          />
          <main className="flex-1 min-w-0">{renderContent()}</main>
        </div>
      )}
    </div>
  );
}

export default App;
