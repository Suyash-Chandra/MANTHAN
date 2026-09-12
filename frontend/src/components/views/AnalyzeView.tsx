import { useEffect, useRef, useState } from 'react';
import { Check, Crosshair, FileUp, RotateCcw, ScanLine, X, ChevronLeft, ChevronRight } from 'lucide-react';
export type Detection = { detection_id: string; class_name: string; confidence: number; anomaly_score: number; priority: string; bbox: [number, number, number, number]; estimated_dimensions: string; shadow_length_px: number | null; status: string; geolocation_status: string; inference_mode: string; latitude?: number; longitude?: number; };
type Props = { api: string; onDetection: (item: Detection) => void; onReview: (item: Detection, action: string) => void };
export function AnalyzeView({ api, onDetection, onReview }: Props) {
  const [image, setImage] = useState<string | null>(null);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('LOAD A SIDE-SCAN SONAR IMAGE');
  const [scanProgress, setScanProgress] = useState(0);
  const [scanPhase, setScanPhase] = useState('');
  const input = useRef<HTMLInputElement>(null);
  const img = useRef<HTMLImageElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const detection = detections[selectedIndex] || null;

  function draw() {
    const source = img.current;
    const target = canvas.current;
    if (!source || !target) return;
    const box = target.getBoundingClientRect();
    const scale = Math.min(box.width / source.naturalWidth, box.height / source.naturalHeight);
    target.width = box.width * devicePixelRatio;
    target.height = box.height * devicePixelRatio;
    const ctx = target.getContext('2d');
    if (!ctx) return;
    ctx.scale(devicePixelRatio, devicePixelRatio);
    const w = source.naturalWidth * scale, h = source.naturalHeight * scale;
    const x = (box.width - w) / 2, y = (box.height - h) / 2;
    ctx.drawImage(source, x, y, w, h);

    if (detections.length > 0) {
      detections.forEach((d, i) => {
        const [a, b, c, dy] = d.bbox;
        const isSelected = i === selectedIndex;
        // Draw glow effect for selected
        if (isSelected) {
          ctx.shadowColor = '#e9b968';
          ctx.shadowBlur = 12;
        }
        ctx.strokeStyle = isSelected ? '#e9b968' : '#00ffd0';
        ctx.lineWidth = isSelected ? 2.5 : 1.5;
        ctx.strokeRect(x + a * scale, y + b * scale, (c - a) * scale, (dy - b) * scale);
        ctx.shadowBlur = 0;
        // Label background
        const confLabel = d.confidence >= 0.65 ? 'HIGH' : 'GOOD';
        
        const label = `${d.class_name}  [${confLabel}]`;
        const labelW = ctx.measureText(label).width + 14;
        if (isSelected) {
          ctx.fillStyle = 'rgba(233, 185, 104, 0.9)';
          ctx.fillRect(x + a * scale, y + b * scale - 20, labelW, 20);
          ctx.fillStyle = '#081015';
          ctx.font = 'bold 11px monospace';
          ctx.fillText(label, x + a * scale + 6, y + b * scale - 6);
        } else {
          ctx.fillStyle = 'rgba(0, 255, 208, 0.7)';
          ctx.fillRect(x + a * scale, y + b * scale - 18, labelW, 18);
          ctx.fillStyle = '#081015';
          ctx.font = '10px monospace';
          ctx.fillText(label, x + a * scale + 6, y + b * scale - 5);
        }
      });
    }
  }

  useEffect(() => {
    draw();
    window.addEventListener('resize', draw);
    return () => window.removeEventListener('resize', draw);
  }, [image, detections, selectedIndex]);

  async function upload(file: File) {
    if (!file.type.startsWith('image/')) {
      setMessage('UNSUPPORTED FILE — USE PNG, JPEG, OR TIFF');
      return;
    }
    setImage(URL.createObjectURL(file));
    setDetections([]);
    setSelectedIndex(0);
    setBusy(true);
    setScanProgress(0);
    setScanPhase('INITIALIZING SCAN');

    // Animated scan phases
    const phases = [
      { pct: 10, label: 'LOADING SONAR IMAGE DATA' },
      { pct: 25, label: 'APPLYING CLAHE ENHANCEMENT' },
      { pct: 40, label: 'RUNNING SPECKLE NOISE REDUCTION' },
      { pct: 55, label: 'FEEDING INTO YOLOv8 NEURAL NETWORK' },
      { pct: 70, label: 'EXTRACTING ANOMALY CANDIDATES' },
      { pct: 85, label: 'COMPUTING GEOSPATIAL METADATA' },
      { pct: 95, label: 'FINALIZING DETECTION REPORT' },
    ];
    let phaseIdx = 0;
    const interval = setInterval(() => {
      if (phaseIdx < phases.length) {
        setScanProgress(phases[phaseIdx].pct);
        setScanPhase(phases[phaseIdx].label);
        setMessage(phases[phaseIdx].label);
        phaseIdx++;
      }
    }, 400);

    try {
      const form = new FormData();
      form.append('file', file);
      const r = await fetch(`${api}/api/analyze`, { method: 'POST', body: form });
      const body = await r.json() as { detections?: Detection[]; detail?: string };
      if (!r.ok) throw new Error(body.detail);
      clearInterval(interval);
      setScanProgress(100);
      setScanPhase('ANALYSIS COMPLETE');

      const next = body.detections;
      if (next && next.length > 0) {
        setDetections(next);
        setSelectedIndex(0);
        next.forEach(d => onDetection(d));
        setMessage(`✓ IDENTIFIED ${next.length} ANOMAL${next.length > 1 ? 'IES' : 'Y'} — REVIEW REQUIRED`);
      } else {
        setMessage('NO ANOMALIES DETECTED IN THIS SCAN.');
      }
    } catch (error) {
      clearInterval(interval);
      setScanProgress(0);
      setScanPhase('');
      setMessage(`ANALYSIS FAILED — ${error instanceof Error ? error.message : 'LOCAL API UNAVAILABLE'}`);
    } finally {
      setBusy(false);
      setTimeout(() => { setScanProgress(0); setScanPhase(''); }, 3000);
    }
  }

  return <section className="analyze">
    <header className="analyze-head">
      <div>
        <p className="eyebrow">ANALYZE / INSPECTION WORKSPACE</p>
        <h2>Sonar interpretation bay</h2>
      </div>
      <div className="toolbox">
        <button onClick={() => input.current?.click()}><FileUp size={15}/> UPLOAD SURVEY</button>
        <span>AI ENGINE</span>
      </div>
    </header>

    <div className="workspace">
      <div className="viewer">
        <div className="viewer-top">
          <span className={busy ? 'pulse' : ''}><ScanLine size={15}/> {message}</span>
          <span className="mono">RAW INPUT · 0—30m RANGE</span>
        </div>

        <div className="sonar-stage" onClick={() => !image && input.current?.click()}>
          {image ? <>
            <img ref={img} src={image} onLoad={draw}/>
            <canvas ref={canvas}/>
            {/* Scanning overlay animation */}
            {busy && <div className="scan-overlay">
              <div className="scan-line-anim"/>
              <div className="scan-info">
                <div className="scan-spinner"/>
                <span className="scan-phase">{scanPhase}</span>
                <div className="scan-bar-track">
                  <div className="scan-bar-fill" style={{ width: `${scanProgress}%` }}/>
                </div>
                <span className="scan-pct">{scanProgress}%</span>
              </div>
            </div>}
          </> : <div className="drop">
            <Crosshair size={40}/>
            <strong>SONAR VIEWPORT</strong>
            <p>Drop or browse a local image to start a traceable demo workflow.</p>
          </div>}
        </div>

        <div className="range">
          <span>PORT</span><i/><span>0m</span><i/><span>10m</span><i/><span>20m</span><i/><span>30m</span><i/><span>STARBOARD</span>
        </div>
      </div>

      <aside className="intel">
        <p className="eyebrow">DETECTION INTELLIGENCE</p>
        {detection ? <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className="id">{detection.detection_id}</div>
            {detections.length > 1 && <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <button onClick={() => setSelectedIndex(s => Math.max(0, s - 1))} disabled={selectedIndex === 0} style={{ padding: '4px', background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', cursor: 'pointer' }}><ChevronLeft size={16}/></button>
              <span style={{ fontSize: '12px' }}>{selectedIndex + 1} of {detections.length}</span>
              <button onClick={() => setSelectedIndex(s => Math.min(detections.length - 1, s + 1))} disabled={selectedIndex === detections.length - 1} style={{ padding: '4px', background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', cursor: 'pointer' }}><ChevronRight size={16}/></button>
            </div>}
          </div>
          <h3>{detection.class_name}</h3>
          <div className="demo-callout">{detection.inference_mode === 'YOLOv8_AI' ? <>YOLOv8 AI DETECTION<br/><small>Neural network inference</small></> : <>SYNTHETIC DEMO CANDIDATE<br/><small>Contour-based heuristic inference</small></>}</div>
          <dl>
            <div><dt>Status</dt><dd style={{ color: detection.status === 'CONFIRMED' ? 'var(--accent-cyan)' : detection.status === 'REJECTED' ? 'var(--accent-orange)' : 'var(--text)' }}>{detection.status}</dd></div>
            <div><dt>Confidence</dt><dd>{detection.confidence ? (detection.confidence >= 0.65 ? 'HIGH' : 'GOOD') : 'Unavailable'}</dd></div>
            <div><dt>Anomaly score</dt><dd>{detection.anomaly_score ? `${detection.anomaly_score}/100` : 'Not assessed'}</dd></div>
            <div><dt>Dimensions</dt><dd>{detection.estimated_dimensions || 'Unavailable'}</dd></div>
            <div><dt>Shadow</dt><dd>{detection.shadow_length_px ? `${detection.shadow_length_px} px` : 'Not assessed'}</dd></div>
            <div><dt>Location</dt><dd>{detection.geolocation_status || `${detection.latitude || 'Unavailable'} N, ${detection.longitude || 'Unavailable'} W`}</dd></div>
          </dl>
          <div className="review">
            <button onClick={() => {onReview(detection,'CONFIRM'); setDetections(d => {const n=[...d]; n[selectedIndex]={...n[selectedIndex], status:'CONFIRMED'}; return n;});}}><Check size={14}/> CONFIRM</button>
            <button onClick={() => {onReview(detection,'REJECT'); setDetections(d => {const n=[...d]; n[selectedIndex]={...n[selectedIndex], status:'REJECTED'}; return n;});}}><X size={14}/> REJECT</button>
            <button onClick={() => {onReview(detection,'RECOVERY_QUEUE'); setDetections(d => {const n=[...d]; n[selectedIndex]={...n[selectedIndex], status:'RECOVERY_QUEUE'}; return n;});}}><RotateCcw size={14}/> RECOVERY QUEUE</button>
          </div>
        </> : <div className="no-selection">No candidate selected.<br/><small>Results are only created after upload.</small></div>}
      </aside>
    </div>

    <input ref={input} type="file" accept="image/png,image/jpeg,image/tiff" hidden onChange={(e) => { const f = e.target.files?.[0]; if (f) void upload(f); }}/>
  </section>;
}
