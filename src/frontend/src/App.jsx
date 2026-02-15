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
            nodeCanvasObject={(node, ctx, globalScale) => {
              const label = node.id;
              const fontSize = 12 / globalScale;
              ctx.font = `${fontSize}px Sans-Serif`;

              // Determine color based on group (1=Service, 2=Database)
              const color = node.group === 2 ? '#ef4444' : '#3b82f6'; // Red for DB, Blue for Service

              // Draw Node Circle
              ctx.beginPath();
              ctx.arc(node.x, node.y, 6, 0, 2 * Math.PI, false);
              ctx.fillStyle = color;
              ctx.fill();

              // Draw Text Label Background
              const textWidth = ctx.measureText(label).width;
              const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);

              ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
              ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y + 8, ...bckgDimensions);

              // Draw Text Label
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillStyle = '#1f2937';
              ctx.fillText(label, node.x, node.y + 8 + fontSize / 2);
            }}
            linkCanvasObjectMode={() => 'after'}
            linkCanvasObject={(link, ctx, globalScale) => {
              const start = link.source;
              const end = link.target;

              // Only draw if we have coordinates
              if (typeof start !== 'object' || typeof end !== 'object') return;

              const textPos = Object.assign({}, ...['x', 'y'].map(c => ({
                [c]: start[c] + (end[c] - start[c]) / 2
              })));

              const label = 'calls';
              const fontSize = 10 / globalScale;
              ctx.font = `${fontSize}px Sans-Serif`;

              ctx.save();
              ctx.translate(textPos.x, textPos.y);
              // Calculate angle
              const angle = Math.atan2(end.y - start.y, end.x - start.x);
              ctx.rotate(angle);

              // Draw Label Background
              const textWidth = ctx.measureText(label).width;
              const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);
              ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
              ctx.fillRect(-bckgDimensions[0] / 2, -bckgDimensions[1] / 2, ...bckgDimensions);

              // Draw Label Text
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillStyle = '#6b7280';
              ctx.fillText(label, 0, 0);

              ctx.restore();
            }}
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
