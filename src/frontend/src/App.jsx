import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'
import ForceGraph2D from 'react-force-graph-2d'
import VectorView from './VectorView';
import MetricsView from './MetricsView';
import GraphRawView from './GraphRawView';
import ChatWindow from './ChatWindow';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [serviceName, setServiceName] = useState('');
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showChat, setShowChat] = useState(false);

  // Dummy graph data for visualization until we fetch real graph
  // eslint-disable-next-line no-unused-vars
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });

  // Fetch graph data on mount
  useEffect(() => {
    axios.get('http://localhost:8000/api/v1/graph')
      .then(res => {
        // Transform for visualization
        const nodes = res.data.nodes.map(n => ({ id: n.name, ...n, group: n.type === 'Database' ? 2 : 1 }));
        const links = res.data.edges.map(e => ({ source: e.source, target: e.target, ...e }));
        setGraphData({ nodes, links });
      })
      .catch(err => console.error("Failed to fetch graph:", err));
  }, []);

  const fetchRecommendation = async () => {
    if (!serviceName) return;
    setLoading(true);
    setError(null);
    setRecommendation(null);
    setShowChat(false);

    try {
      const response = await axios.get(`http://localhost:8000/api/v1/recommend/${serviceName}`);
      setRecommendation(response.data);
      setShowChat(true); // Switch to chat view on success
    } catch (err) {
      console.error(err);
      setError("Failed to fetch recommendation. Service might not exist or backend is down.");
    } finally {
      setLoading(false);
    }
  };

  const renderDashboard = () => (
    <div className="main-content">
      <div className="left-panel">
        {!showChat ? (
          <>
            <div className="input-group">
              <label>Select Service:</label>
              <input
                type="text"
                value={serviceName}
                onChange={(e) => setServiceName(e.target.value)}
                placeholder="e.g., PaymentService"
              />
              <button onClick={fetchRecommendation} disabled={loading}>
                {loading ? 'Analyzing...' : 'Get Recommendation'}
              </button>
            </div>

            {error && <div className="error">{error}</div>}

            <div className="intro-text" style={{ marginTop: '2rem', color: '#666' }}>
              <p>Enter a service name above to generate SLO recommendations and start a chat with the AI agent.</p>
            </div>
          </>
        ) : (
          <ChatWindow
            serviceName={serviceName}
            initialRecommendation={recommendation?.reasoning}
            onBack={() => setShowChat(false)}
          />
        )}
      </div>

      <div className="right-panel">
        <h3>Service Topology</h3>
        <div className="graph-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#ffffff' }}>
          <ForceGraph2D
            graphData={graphData}
            nodeLabel="id"
            nodeAutoColorBy="group"
            linkDirectionalArrowLength={6}
            linkDirectionalArrowRelPos={1}
            linkColor={() => '#999999'}
            linkWidth={1.5}
            nodeRelSize={6}
          />
        </div>
      </div>
    </div>
  );

  return (
    <div className="container">
      <header>
        <h1>SLO Recommender Agent</h1>
        <p>AI-driven reliability targets based on topology, metrics, and runbooks.</p>
      </header>

      <div className="tabs">
        <button
          className={`tab-button ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button
          className={`tab-button ${activeTab === 'vectors' ? 'active' : ''}`}
          onClick={() => setActiveTab('vectors')}
        >
          Vector DB (Runbooks)
        </button>
        <button
          className={`tab-button ${activeTab === 'metrics' ? 'active' : ''}`}
          onClick={() => setActiveTab('metrics')}
        >
          Metrics DB (Time Series)
        </button>
        <button
          className={`tab-button ${activeTab === 'graph' ? 'active' : ''}`}
          onClick={() => setActiveTab('graph')}
        >
          Graph DB (Raw Data)
        </button>
      </div>

      <div className="view-content">
        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'vectors' && <VectorView />}
        {activeTab === 'metrics' && <MetricsView />}
        {activeTab === 'graph' && <GraphRawView />}
      </div>
    </div>
  )
}

export default App
