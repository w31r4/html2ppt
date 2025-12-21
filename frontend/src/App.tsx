import { Routes, Route, Navigate } from 'react-router-dom';
import HomePage from './pages/HomePage';
import OutlinePage from './pages/OutlinePage';
import GeneratingPage from './pages/GeneratingPage';
import ResultPage from './pages/ResultPage';
import SettingsPage from './pages/SettingsPage';
import Layout from './components/Layout';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/outline/:sessionId" element={<OutlinePage />} />
        <Route path="/generating/:sessionId" element={<GeneratingPage />} />
        <Route path="/result/:sessionId" element={<ResultPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}

export default App;