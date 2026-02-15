import { useState, useEffect } from 'react';
import axios from 'axios';

function GraphRawView() {
    const [graph, setGraph] = useState({ nodes: [], edges: [] });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        axios.get('http://localhost:8000/api/v1/graph')
            .then(res => setGraph(res.data))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div>Loading Graph Data...</div>;

    return (
        <div className="view-container">
            <h3>Graph DB (Raw Data)</h3>
            <div className="flex-tables">
                <div className="table-wrapper">
                    <h4>Nodes</h4>
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Type</th>
                                <th>Tier</th>
                            </tr>
                        </thead>
                        <tbody>
                            {graph.nodes.map(n => (
                                <tr key={n.name}>
                                    <td>{n.name}</td>
                                    <td>{n.type}</td>
                                    <td>{n.tier}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                <div className="table-wrapper">
                    <h4>Edges (Dependencies)</h4>
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Source</th>
                                <th>Target</th>
                                <th>Criticality</th>
                            </tr>
                        </thead>
                        <tbody>
                            {graph.edges.map((e, idx) => (
                                <tr key={idx}>
                                    <td>{e.source}</td>
                                    <td>{e.target}</td>
                                    <td>{e.criticality}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

export default GraphRawView;
