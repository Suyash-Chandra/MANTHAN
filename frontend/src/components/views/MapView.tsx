import { useState } from 'react';
import { MapPin, Image as ImageIcon } from 'lucide-react';
import type { Detection } from './AnalyzeView';

export function MapView({ detections }: { detections: Detection[] }) {
  // Group detections by image_id
  const uploads = detections.reduce((acc, d) => {
    const id = d.image_id || d.detection_id.split('-')[1]; // Fallback to parsing detection_id if image_id is missing
    if (!acc[id]) acc[id] = [];
    acc[id].push(d);
    return acc;
  }, {} as Record<string, Detection[]>);

  const uploadIds = Object.keys(uploads);
  const [selectedId, setSelectedId] = useState<string | null>(uploadIds.length > 0 ? uploadIds[0] : null);

  if (uploadIds.length === 0) {
    return (
      <div className="map-empty">
        <MapPin size={32} />
        <h3>No Data</h3>
        <p>Upload a sonar image to generate demo geospatial metadata.</p>
      </div>
    );
  }

  // Ensure selectedId is valid if detections change
  const currentId = selectedId && uploads[selectedId] ? selectedId : uploadIds[0];
  const activeDetections = uploads[currentId];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: '20px', height: '600px' }}>
      {/* Sidebar List of Uploads */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', overflowY: 'auto', paddingRight: '10px' }}>
        <h3 style={{ fontSize: '14px', color: 'var(--text-muted)', marginBottom: '4px', marginTop: 0, textTransform: 'uppercase', letterSpacing: '1px' }}>
          Recent Uploads
        </h3>
        {uploadIds.map((id) => (
          <button
            key={id}
            onClick={() => setSelectedId(id)}
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
              padding: '16px',
              background: id === currentId ? 'rgba(6, 182, 212, 0.1)' : 'var(--bg-panel)',
              border: `1px solid ${id === currentId ? 'var(--accent-cyan)' : 'var(--border-color)'}`,
              borderRadius: '6px',
              textAlign: 'left',
              transition: 'all 0.2s'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: id === currentId ? 'var(--accent-cyan)' : 'var(--text-main)', fontWeight: id === currentId ? 'bold' : 'normal' }}>
              <ImageIcon size={16} />
              <span className="mono">Image {id.slice(0, 6)}</span>
            </div>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              {uploads[id].length} Anomaly Marker{uploads[id].length !== 1 ? 's' : ''}
            </span>
          </button>
        ))}
      </div>

      {/* Map Area for Selected Upload */}
      <div style={{ position: 'relative', width: '100%', height: '100%', background: '#0a151c', border: '1px solid var(--border-color)', borderRadius: '6px', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: 16, left: 16, zIndex: 10, background: 'rgba(0,0,0,0.8)', padding: '12px 16px', borderRadius: '4px', border: '1px solid var(--border-color)', backdropFilter: 'blur(4px)' }}>
          <h4 style={{ margin: '0 0 4px 0', color: 'var(--text-main)' }}>Thunder Bay Survey</h4>
          <p className="mono" style={{ margin: 0, fontSize: '11px', color: 'var(--accent-cyan)' }}>
            Viewing: Image {currentId.slice(0, 6)} ({activeDetections.length} targets)
          </p>
        </div>
        
        <iframe 
          width="100%" 
          height="100%" 
          frameBorder="0" 
          scrolling="no" 
          src="https://www.openstreetmap.org/export/embed.html?bbox=-83.1,44.9,-82.9,45.1&layer=mapnik" 
          style={{ filter: 'invert(1) hue-rotate(180deg) opacity(0.5)' }}
        ></iframe>

        <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
          {activeDetections.map(d => { 
            if (!d.longitude || !d.latitude) return null; 
            const x = ((d.longitude) - -83.05) / 0.1 * 100; 
            const y = ((d.latitude) - 44.95) / 0.1 * 100; 
            return (
              <div 
                key={d.detection_id} 
                style={{
                  position: 'absolute', 
                  left: `${Math.max(5, Math.min(95, x))}%`, 
                  top: `${Math.max(5, Math.min(95, y))}%`, 
                  transform: 'translate(-50%, -50%)', 
                  zIndex: 20, 
                  pointerEvents: 'auto',
                  cursor: 'help'
                }} 
                title={`${d.class_name}\n${d.latitude} N, ${d.longitude} W\nStatus: ${d.status}`}
              >
                <MapPin 
                  size={36} 
                  color={d.status === 'CONFIRMED' ? 'var(--accent-cyan)' : d.status === 'REJECTED' ? 'var(--accent-danger)' : 'var(--accent-warning)'} 
                  style={{ filter: 'drop-shadow(0 4px 12px rgba(0,0,0,0.9))' }} 
                />
              </div>
            ); 
          })}
        </div>
      </div>
    </div>
  );
}
