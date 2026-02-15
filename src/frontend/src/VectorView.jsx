import { useState, useEffect } from 'react';
import axios from 'axios';

function VectorView() {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        axios.get('http://localhost:8000/api/v1/vectors')
            .then(res => setDocuments(res.data.documents))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div>Loading Vector Data...</div>;

    return (
        <div className="view-container">
            <h3>Vector DB (Runbooks)</h3>
            <table className="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Service</th>
                        <th>Type</th>
                        <th>Content (Snippet)</th>
                    </tr>
                </thead>
                <tbody>
                    {documents.map(doc => (
                        <tr key={doc.id}>
                            <td>{doc.id}</td>
                            <td>{doc.metadata?.service || 'N/A'}</td>
                            <td>{doc.metadata?.type || 'N/A'}</td>
                            <td title={doc.text}>{doc.text.substring(0, 100)}...</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default VectorView;
