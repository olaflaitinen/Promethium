import { useEffect, useState } from 'react';
// @ts-ignore
import Plot from 'react-plotly.js';

interface SeismicViewerProps {
    dataUrl?: string; // URL to fetch JSON/binary seismic data
}

export const InteractiveSeismicViewer = ({ dataUrl }: SeismicViewerProps) => {
    // Mock data for visualization if no URL provided
    const [plotData, setPlotData] = useState<any[]>([]);

    useEffect(() => {
        if (!dataUrl) {
            // Generate synthetic wiggle trace for demo
            const x = Array.from({ length: 100 }, (_, i) => i);
            const y = x.map(i => Math.sin(i * 0.1) * Math.exp(-i * 0.01));
            setPlotData([{
                z: [y, y.map(v => v * -1), y], // Fake 2D slice
                type: 'heatmap',
                colorscale: 'Greys'
            }]);
        }
    }, [dataUrl]);

    return (
        <div style={{ width: '100%', height: '100%' }}>
            <Plot
                data={plotData}
                layout={{
                    autosize: true,
                    title: 'Seismic Data View',
                    xaxis: { title: 'Trace Number' },
                    yaxis: { title: 'Time Sample', autorange: 'reversed' },
                    paper_bgcolor: '#1e293b',
                    plot_bgcolor: '#1e293b',
                    font: { color: '#f8fafc' }
                }}
                useResizeHandler={true}
                style={{ width: "100%", height: "100%" }}
            />
        </div>
    );
};
