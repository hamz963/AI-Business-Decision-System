import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { DashboardView } from './components/DashboardView';
import { DatasetsView } from './components/DatasetsView';
import { ScenariosView } from './components/ScenariosView';
import { DecisionsView } from './components/DecisionsView';
import { AIAnalystView } from './components/AIAnalystView';
import { ForecastingView } from './components/ForecastingView';
import { dashboardApi, datasetsApi, decisionsApi } from './services/api';
import { ExecutiveDashboardData, Dataset, Decision } from './types';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState<ExecutiveDashboardData | null>(null);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [activeDatasetId, setActiveDatasetId] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInitialData();
  }, [activeDatasetId]);

  const loadInitialData = async () => {
    try {
      const [dash, dsets, decs] = await Promise.all([
        dashboardApi.getExecutive(activeDatasetId).catch(() => null),
        datasetsApi.list().catch(() => []),
        decisionsApi.list().catch(() => [])
      ]);

      if (dash) setDashboardData(dash);
      if (dsets) {
        setDatasets(dsets);
        if (!activeDatasetId && dsets.length > 0) {
          setActiveDatasetId(dsets[0].id);
        }
      }
      if (decs) setDecisions(decs);
    } catch (err) {
      console.error('Error loading platform state:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadInitialData();
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 font-sans">
      {/* Left Navigation */}
      <Sidebar currentTab={currentTab} setCurrentTab={setCurrentTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header currentTab={currentTab} datasetName={dashboardData?.dataset_name} />

        <main className="flex-1 overflow-y-auto p-8 bg-slate-950">
          {loading && !dashboardData ? (
            <div className="h-full flex flex-col items-center justify-center space-y-3">
              <div className="w-8 h-8 rounded-full border-2 border-sky-500 border-t-transparent animate-spin"></div>
              <p className="text-xs font-mono text-slate-400">Initializing Decision Intelligence Engine...</p>
            </div>
          ) : (
            <>
              {currentTab === 'dashboard' && dashboardData && (
                <DashboardView data={dashboardData} onNavigate={setCurrentTab} />
              )}

              {currentTab === 'datasets' && (
                <DatasetsView 
                  datasets={datasets} 
                  onRefresh={handleRefresh}
                  activeDatasetId={activeDatasetId}
                  onSelectDataset={setActiveDatasetId}
                />
              )}

              {currentTab === 'scenarios' && (
                <ScenariosView activeDatasetId={activeDatasetId} />
              )}

              {currentTab === 'decisions' && (
                <DecisionsView decisions={decisions} onRefresh={handleRefresh} />
              )}

              {currentTab === 'ai-analyst' && (
                <AIAnalystView activeDatasetId={activeDatasetId} onNavigate={setCurrentTab} />
              )}

              {currentTab === 'forecasting' && (
                <ForecastingView activeDatasetId={activeDatasetId} />
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
