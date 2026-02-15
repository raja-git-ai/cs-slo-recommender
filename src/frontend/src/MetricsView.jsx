import { useState, useEffect } from 'react';
import axios from 'axios';

function MetricsView() {
    const [metrics, setMetrics] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        axios.get('http://localhost:8000/api/v1/metrics/all?limit=50')
            .then(res => setMetrics(res.data.metrics))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div>Loading Metrics Data...</div>;

    return (
        <div className="view-container">
            <h3>Metrics DB (Latest 50)</h3>
            <table className="data-table">
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Service</th>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    {metrics.map((m, idx) => (
                        <tr key={idx}>
                            <td>{m.timestamp}</td>
                            <td>{m.service_name}</td>
                            <td>{m.metric_name}</td>
                            <td>{m.value.toFixed(2)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default MetricsView;
