import React, { useState, useEffect } from 'react';
import { 
  FileCode, Activity, AlertTriangle, Cpu, ChevronRight, 
  Terminal, BarChart3, LayoutDashboard, Settings, Info,
  Code2, Sparkles, BookOpen, Layers, RefreshCw, XCircle, UploadCloud,
  Zap, Compass, Shield, Menu, X, Box, Search
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// --- Simplified Components ---

const Badge = ({ children, color = "var(--text-secondary)" }) => (
  <span className="badge" style={{ border: `1px solid ${color}22`, color }}>
    {children}
  </span>
);

const Modal = ({ isOpen, onClose, title, children }) => (
  <AnimatePresence>
    {isOpen && (
      <motion.div 
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
        style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}
        onClick={onClose}
      >
        <motion.div 
          initial={{ scale: 0.95, y: 20 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.95, y: 20 }}
          style={{ background: 'white', width: '100%', maxWidth: '800px', borderRadius: '16px', overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)' }}
          onClick={e => e.stopPropagation()}
        >
          <div style={{ padding: '24px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>{title}</h3>
            <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-tertiary)' }}><X size={24} /></button>
          </div>
          <div style={{ padding: '32px', maxHeight: '70vh', overflowY: 'auto' }}>
            {children}
          </div>
        </motion.div>
      </motion.div>
    )}
  </AnimatePresence>
);

const ErrorState = ({ message, onRetry }) => (
  <div style={{
    height: '60vh', display: 'flex', flexDirection: 'column', 
    alignItems: 'center', justifyContent: 'center', gap: '32px', textAlign: 'center'
  }}>
    <div style={{
      width: '80px', height: '80px', borderRadius: '50%', background: '#fee2e2',
      display: 'flex', alignItems: 'center', justifyContent: 'center'
    }}>
      <XCircle size={40} color="var(--danger)" />
    </div>
    <div>
      <h3 style={{fontSize: '1.75rem', marginBottom: '8px'}}>Analysis Interrupted</h3>
      <p style={{color: 'var(--text-secondary)', maxWidth: '400px', margin: '0 auto', fontSize: '15px'}}>{message}</p>
    </div>
    <button className="btn-premium btn-primary" onClick={onRetry} style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
      <RefreshCw size={18} /> Retry Engine
    </button>
  </div>
);

// Helper to format AI text with modern icons/metaphors
const ReadableExplanation = ({ text }) => {
  if (!text) return null;
  
  // Split by double newline to detect sections, then process paragraphs
  const paragraphs = text.split('\n').filter(p => p.trim());
  
  return (
    <div className="explanation-text">
      {paragraphs.map((para, i) => {
        // If it's a separator line from backend
        if (para === '---') return <div key={i} className="hr" />;

        let icon = null;
        const lowPara = para.toLowerCase();
        
        // Only add icon if the line doesn't ALREADY start with an emoji (prevent doubling)
        const hasEmoji = /^[\u2700-\u27bf]|[\u1f300-\u1f64f]|[\u1f680-\u1f6ff]|[\u1f1e0-\u1f1ff]/.test(para);

        if (!hasEmoji) {
          if (lowPara.includes('mini-command')) icon = <Zap size={18} color="var(--accent-color)" />;
          if (lowPara.includes('blueprint')) icon = <Box size={18} color="#0284c7" />;
          if (lowPara.includes('helper')) icon = <Sparkles size={18} color="#f59e0b" />;
          if (lowPara.includes('note from the creator')) icon = <Info size={18} color="#6366f1" />;
          if (lowPara.includes('big picture')) icon = <LayoutDashboard size={18} color="#0d9488" />;
        }

        return (
          <p key={i} style={{ display: 'flex', gap: '14px', alignItems: 'flex-start', wordBreak: 'break-word' }}>
            {icon && <span style={{ marginTop: '4px', flexShrink: 0 }}>{icon}</span>}
            <span dangerouslySetInnerHTML={{ __html: para.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />
          </p>
        );
      })}
    </div>
  );
};

function App() {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [explanation, setExplanation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState('beginner'); 
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showTrace, setShowTrace] = useState(false);
  const fileInputRef = React.useRef(null);

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = () => {
    fetch('/api/files')
      .then(res => res.json())
      .then(data => setFiles(Array.isArray(data) ? data : []))
      .catch(err => {
        console.error("Failed to load files", err);
        setError("Could not connect to the CodeExplain Engine.");
      });
  };

  const handleSelectFile = async (file) => {
    setLoading(true);
    setError(null);
    setAnalysis(null);
    setExplanation('');
    setSelectedFile(file);
    setSidebarOpen(false);

    try {
      const contentRes = await fetch(`/api/file-content?path=${encodeURIComponent(file.path)}`);
      if (!contentRes.ok) throw new Error("Failed to read file content.");
      const contentData = await contentRes.json();
      setFileContent(contentData.content || '');

      const analyzeRes = await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source: contentData.content,
          filename: file.name,
          source_path: file.path
        })
      });
      
      const analyzeData = await analyzeRes.json();
      if (!analyzeRes.ok) throw new Error(analyzeData.detail || "Analysis engine error.");
      setAnalysis(analyzeData);

      const explainRes = await fetch('/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source: contentData.content,
          filename: file.name,
          source_path: file.path,
          mode: mode
        })
      });
      
      const explainData = await explainRes.json();
      if (!explainRes.ok) throw new Error(explainData.detail || "Explanation engine error.");
      setExplanation(explainData.explanation || 'No explanation generated.');

    } catch (err) {
      console.error("Operation failed", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch('/api/upload', { method: 'POST', body: formData });
      if (!res.ok) throw new Error("Upload failed.");
      const data = await res.json();
      await handleSelectFile(data);
      fetchFiles();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  useEffect(() => {
    if (selectedFile && !loading && !error) {
       const fetchExplanation = async () => {
         setLoading(true);
         try {
           const res = await fetch('/explain', {
             method: 'POST',
             headers: { 'Content-Type': 'application/json' },
             body: JSON.stringify({
               source: fileContent,
               filename: selectedFile.name,
               source_path: selectedFile.path,
               mode: mode
             })
           });
           const data = await res.json();
           if (res.ok) setExplanation(data.explanation || '');
         } catch (e) { console.error(e); }
         setLoading(false);
       };
       fetchExplanation();
    }
  }, [mode]);

  return (
    <div className="app-container">
      {/* Sidebar Mobile Toggle */}
      <button 
        onClick={() => setSidebarOpen(!sidebarOpen)}
        style={{ position: 'fixed', top: '20px', left: '20px', zIndex: 60, background: 'white', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '10px', display: 'flex', alignItems: 'center', boxShadow: 'var(--shadow-md)' }}
        className="lg-toggle"
      >
        {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Sidebar Overlay */}
      {sidebarOpen && <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.2)', zIndex: 45 }} onClick={() => setSidebarOpen(false)} />}

      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="logo-container">
            <img src="/logo.png" alt="CodeExplain" className="sidebar-logo" />
            <div>
              <h1 style={{fontSize: '1.2rem', fontWeight: 800}}>CodeExplain</h1>
              <span style={{fontSize: '10px', color: 'var(--text-tertiary)', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase'}}>Autonomous AI</span>
            </div>
          </div>
        </div>

        <div className="file-list">
          <div style={{padding: '0 16px', marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <span style={{fontSize: '11px', fontWeight: 700, color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.1em'}}>Explorer</span>
            <button 
              onClick={() => fileInputRef.current?.click()}
              style={{
                background: 'white', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '6px',
                padding: '4px 8px', fontSize: '10px', fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px',
                boxShadow: 'var(--shadow-sm)'
              }}
            >
              <UploadCloud size={12} /> UPLOAD
            </button>
            <input type="file" ref={fileInputRef} style={{ display: 'none' }} onChange={handleFileUpload} accept=".py,.js,.jsx,.ts,.tsx" />
          </div>

          {files.length > 0 ? files.map(file => (
            <button
              key={file.path}
              onClick={() => handleSelectFile(file)}
              className={`file-item ${selectedFile?.path === file.path ? 'active' : ''}`}
            >
              <FileCode size={16} color={selectedFile?.path === file.path ? 'var(--accent-color)' : 'var(--text-secondary)'} />
              <span style={{overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}}>{file.name}</span>
              {selectedFile?.path === file.path && <ChevronRight size={14} style={{marginLeft: 'auto'}} />}
            </button>
          )) : (
            <div style={{ padding: '40px 20px', textAlign: 'center', color: 'var(--text-tertiary)' }}>
              <p style={{ fontSize: '12px' }}>No files found in project root.</p>
            </div>
          )}
        </div>

        <div style={{padding: '24px', borderTop: '1px solid var(--border-color)', margin: '0 12px 12px'}}>
           <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px'}}>
              <div style={{width: '6px', height: '6px', borderRadius: '50%', background: error ? 'var(--danger)' : '#10b981'}} />
              <span style={{fontSize: '11px', fontWeight: 700}}>{error ? 'Engine Fault' : 'Ready'}</span>
           </div>
           <p style={{fontSize: '10px', color: 'var(--text-tertiary)', lineHeight: 1.4}}>Engine v1.2 — Story-Mode Active. (Run <code>npm build</code> to sync changes).</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <AnimatePresence mode="wait">
        {selectedFile ? (
          <motion.div 
            key={selectedFile.path}
            initial={{opacity: 0, x: 20}}
            animate={{opacity: 1, x: 0}}
            exit={{opacity: 0, x: -20}}
            transition={{duration: 0.4, ease: [0.22, 1, 0.36, 1]}}
            style={{maxWidth: '1200px', margin: '0 auto', width: '100%', paddingBottom: '60px'}}
          >
            {/* Header */}
            <div style={{display: 'flex', flexDirection: 'column', gap: '24px', marginBottom: '48px', paddingTop: '40px'}}>
               <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'flex-end', gap: '24px' }}>
                  <div style={{ flex: 1, minWidth: '280px' }}>
                    <h2 style={{fontSize: 'clamp(2rem, 5vw, 3rem)', fontWeight: 800, letterSpacing: '-0.04em', lineHeight: 1.1}}>{selectedFile.name}</h2>
                    <div style={{display: 'flex', flexWrap: 'wrap', gap: '12px', marginTop: '12px'}}>
                      <Badge>{selectedFile.path}</Badge>
                      {analysis?.metrics?.total_lines && <Badge color="var(--accent-color)">{analysis.metrics.total_lines} LINES OF CODE</Badge>}
                    </div>
                  </div>
                  <div style={{display: 'flex', gap: '4px', background: '#f3f4f6', padding: '4px', borderRadius: '12px', height: 'fit-content'}}>
                    {['beginner', 'developer', 'fun:pirate'].map(m => (
                      <button 
                        key={m}
                        onClick={() => setMode(m)}
                        style={{
                          padding: '10px 18px', borderRadius: '9px', fontSize: '11px', fontWeight: 700, border: 'none', cursor: 'pointer',
                          background: mode === m ? 'white' : 'transparent',
                          color: mode === m ? 'black' : 'var(--text-secondary)',
                          boxShadow: mode === m ? 'var(--shadow-sm)' : 'none',
                          transition: 'all 0.2s'
                        }}
                      >
                        {m.split(':')[1]?.toUpperCase() || m.toUpperCase()}
                      </button>
                    ))}
                  </div>
               </div>
            </div>

            {error ? (
              <ErrorState message={error} onRetry={() => handleSelectFile(selectedFile)} />
            ) : (
              <div className="dashboard-grid">
                
                {/* Hero Illustration Card */}
                <div className="col-8 white-panel" style={{padding: '0', position: 'relative', overflow: 'hidden', minHeight: '380px', background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)', display: 'flex', alignItems: 'center'}}>
                   <div style={{padding: 'clamp(32px, 6vw, 64px)', flex: 1, position: 'relative', zIndex: 1}}>
                      <div className="metric-label" style={{color: '#0369a1', marginBottom: '20px'}}>Source Context</div>
                      <h3 style={{fontSize: '2.5rem', marginBottom: '16px', lineHeight: 1.1}}>Structural Insight</h3>
                      <p style={{color: '#334155', maxWidth: '340px', lineHeight: 1.7, fontSize: '16px'}}>
                        Our engine detected <strong>{analysis?.metrics?.function_count || 0} functions</strong> and <strong>{analysis?.metrics?.class_count || 0} structures</strong> in this specific module.
                      </p>
                      <button 
                        className="btn-premium btn-primary" 
                        style={{marginTop: '32px', background: '#0369a1', padding: '12px 28px'}}
                        onClick={() => setShowTrace(true)}
                      >
                         View Deep Trace
                      </button>
                   </div>
                   <div style={{position: 'absolute', right: '10px', bottom: '-20px', width: '420px', height: '420px', opacity: loading ? 0.3 : 1, transition: 'opacity 0.5s'}} className="hero-img">
                      <img src="/illustration.png" alt="Illustration" style={{width: '100%', height: '100%', objectFit: 'contain'}} />
                   </div>
                   {loading && (
                      <div style={{position: 'absolute', inset: 0, background: 'rgba(255,255,255,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 10}}>
                         <div className="premium-loader" />
                      </div>
                   )}
                </div>

                {/* Score Panel */}
                <div className="col-4 white-panel" style={{padding: '48px 32px', textAlign: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
                      <div className="metric-label" style={{marginBottom: '24px'}}>Health Index</div>
                      <div style={{position: 'relative', width: '160px', height: '160px', margin: '0 auto 24px'}}>
                         <svg width="160" height="160" viewBox="0 0 120 120" style={{transform: 'rotate(-90deg)'}}>
                           <circle cx="60" cy="60" r="54" fill="none" stroke="#f3f4f6" strokeWidth="8"/>
                           <circle cx="60" cy="60" r="54" fill="none" stroke={ (analysis?.scores?.maintainability || 0) > 70 ? "#10b981" : "var(--accent-color)" } strokeWidth="8" strokeDasharray="339.3" 
                              strokeDashoffset={339.3 - (339.3 * (analysis?.scores?.maintainability || 0) / 100)}
                              style={{transition: 'stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1)'}}
                           />
                         </svg>
                         <div style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '42px', fontWeight: 900}}>
                            {analysis?.scores?.maintainability || 0}<span style={{fontSize: '18px', fontWeight: 600, color: 'var(--text-tertiary)'}}>%</span>
                         </div>
                      </div>
                      <div style={{fontSize: '14px', color: (analysis?.scores?.maintainability || 0) > 70 ? '#10b981' : 'var(--accent-color)', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.1em'}}>
                        {analysis?.scores?.maintainability_label || 'COMPUTING'}
                      </div>
                </div>

                {/* Metrics */}
                <div className="col-8 white-panel metrics-row">
                    <div className="metric-item">
                      <Layers size={22} color="#6b7280" style={{marginBottom: '14px'}} />
                      <div className="metric-value">{analysis?.metrics?.total_lines || 0}</div>
                      <div className="metric-label">LOC</div>
                    </div>
                    <div style={{width: '1px', height: '50px', background: 'var(--border-color)'}} className="metric-sep" />
                    <div className="metric-item">
                      <Code2 size={22} color="#6b7280" style={{marginBottom: '14px'}} />
                      <div className="metric-value">{analysis?.metrics?.function_count || analysis?.complexity?.functions?.length || 0}</div>
                      <div className="metric-label">Methods</div>
                    </div>
                    <div style={{width: '1px', height: '50px', background: 'var(--border-color)'}} className="metric-sep" />
                    <div className="metric-item">
                      <AlertTriangle size={22} color="#f59e0b" style={{marginBottom: '14px'}} />
                      <div className="metric-value">{analysis?.smells?.length || 0}</div>
                      <div className="metric-label">Smells</div>
                    </div>
                    <div style={{width: '1px', height: '50px', background: 'var(--border-color)'}} className="metric-sep" />
                    <div className="metric-item">
                      <BookOpen size={22} color="#6b7280" style={{marginBottom: '14px'}} />
                      <div className="metric-value">{Math.round((analysis?.metrics?.comment_ratio || 0) * 100)}%</div>
                      <div className="metric-label">Docs</div>
                    </div>
                </div>

                {/* Complexity Card */}
                <div className="col-4 white-panel" style={{padding: '40px 32px', textAlign: 'center', borderTop: '6px solid var(--accent-color)'}}>
                      <div className="metric-label" style={{marginBottom: '12px'}}>Complexity</div>
                      <div style={{fontSize: '5rem', fontWeight: 900, color: 'var(--text-primary)', letterSpacing: '-0.06em', lineHeight: 0.9, transition: 'all 0.5s'}}>
                        {analysis?.complexity?.average_complexity || 0}
                      </div>
                      <div style={{fontSize: '12px', color: 'var(--text-tertiary)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.15em', marginTop: '16px'}}>
                        {analysis?.complexity?.overall_label || 'STABLE'}
                      </div>
                </div>

                {/* AI Explanation */}
                <div className="col-7">
                  <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px'}}>
                    <Sparkles size={18} color="var(--accent-color)" />
                    <span className="metric-label" style={{color: 'var(--text-primary)', fontSize: '13px'}}>AI Narrative Report</span>
                  </div>
                  <div className="white-panel" style={{padding: 'clamp(24px, 6vw, 64px)', minHeight: '500px', position: 'relative'}}>
                    <ReadableExplanation text={explanation} />
                    {!explanation && !loading && <div style={{ textAlign: 'center', padding: '100px 0' }}><p style={{color: 'var(--text-tertiary)', fontStyle: 'italic'}}>Select a file to generate a narrative story...</p></div>}
                  </div>
                </div>

                {/* Side Insights Column - Responsive & Robust */}
                <div className="col-5" style={{ display: 'flex', flexDirection: 'column', gap: '32px', minWidth: 0, overflowX: 'hidden' }}>
                  
                  {/* Risks */}
                  <div style={{ width: '100%' }}>
                     <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px'}}>
                        <Shield size={18} color="var(--text-primary)" />
                        <span className="metric-label" style={{color: 'var(--text-primary)', fontSize: '13px'}}>Risk Factors</span>
                     </div>
                     <div style={{display: 'flex', flexDirection: 'column', gap: '20px'}}>
                        {analysis?.smells?.length > 0 ? analysis.smells.slice(0, 4).map((smell, i) => (
                          <div key={i} className="glass-card" style={{padding: '24px'}}>
                             <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '10px'}}>
                                <span style={{fontSize: '13px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em', color: smell.severity === 'high' ? 'var(--danger)' : 'var(--text-primary)'}}>
                                  {smell.kind.replace(/_/g, ' ')}
                                </span>
                                <Badge>L{smell.lineno}</Badge>
                             </div>
                             <p style={{fontSize: '15px', color: 'var(--text-secondary)', lineHeight: 1.6}}>{smell.message}</p>
                          </div>
                        )) : (
                          <div className="white-panel" style={{padding: '64px 32px', textAlign: 'center', borderStyle: 'dashed'}}>
                             <Activity size={40} color="#10b981" style={{opacity: 0.3, marginBottom: '20px'}} />
                             <p style={{fontSize: '14px', fontWeight: 700, color: '#10b981', letterSpacing: '0.05em'}}>ARCHITECTURE OPTIMIZED</p>
                          </div>
                        )}
                     </div>
                  </div>

                  {/* Insight Detail Card */}
                  <div className="white-panel" style={{padding: '40px 32px', background: 'linear-gradient(to bottom right, #ffffff, #f9fafb)', position: 'relative', overflow: 'hidden', minWidth: '0'}}>
                     <h4 style={{fontSize: '18px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px'}}>
                        <Compass size={22} color="var(--accent-color)" /> Insight Detail
                     </h4>
                     <p style={{fontSize: '15px', color: 'var(--text-secondary)', lineHeight: 1.8, position: 'relative', zIndex: 1}}>
                        Our specialized <strong>Engine v1.2</strong> identified structural patterns using recursive descent parsing. 
                        The maintainability score is computed relative to the Weighted Micro-Function Complexity.
                     </p>
                     <div style={{position: 'absolute', right: '-20px', bottom: '-20px', opacity: 0.05}} className="hidden md:block">
                        <BarChart3 size={140} />
                     </div>
                  </div>
                </div>

              </div>
            )}
          </motion.div>
        ) : (
          <motion.div 
            initial={{opacity: 0, scale: 0.98}} animate={{opacity: 1, scale: 1}}
            style={{height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: '40px'}}
          >
             <div style={{position: 'relative', width: 'clamp(240px, 45vw, 560px)', height: 'clamp(240px, 35vw, 440px)', marginBottom: '40px'}}>
                <img src="/illustration.png" alt="Logo" style={{width: '100%', height: '100%', objectFit: 'contain', filter: 'drop-shadow(0 30px 60px rgba(0,0,0,0.06))'}} />
             </div>
             <h2 style={{fontSize: 'clamp(2.5rem, 6vw, 4rem)', fontWeight: 800, marginBottom: '24px', letterSpacing: '-0.05em', lineHeight: 1}}>Understand everything.</h2>
             <p style={{color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto', fontSize: 'clamp(1.1rem, 2vw, 1.4rem)', fontWeight: 400, lineHeight: 1.8}}>
               Upload or choose a source file to see it transformed into a simple, human story you can actually understand.
             </p>
             <button onClick={() => fileInputRef.current?.click()} className="btn-premium btn-primary" style={{marginTop: '48px', padding: '16px 40px', fontSize: '18px', borderRadius: '14px'}}>
                Analyze New File
             </button>
          </motion.div>
        )}
        </AnimatePresence>
      </div>

      {/* Deep Trace Modal */}
      <Modal isOpen={showTrace} onClose={() => setShowTrace(false)} title="Deep Trace Analysis">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
          <div style={{ background: '#f8fafc', padding: '24px', borderRadius: '14px', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <Search size={18} color="var(--accent-color)" />
              <span className="metric-label" style={{ fontSize: '13px' }}>Raw AST Mapping</span>
            </div>
            <pre style={{ fontSize: '12px', color: '#334155', overflowX: 'auto', padding: '16px', background: 'white', borderRadius: '10px', border: '1px solid var(--border-color)', lineHeight: 1.6, maxHeight: '300px' }}>
              {JSON.stringify(analysis, null, 2)}
            </pre>
          </div>
          
          <div className="dashboard-grid">
             <div className="col-6 white-panel" style={{ padding: '32px' }}>
                <h4 style={{ fontSize: '15px', marginBottom: '16px' }}>Semantic Nodes</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                   {(analysis?.complexity?.functions || []).length > 0 ? analysis.complexity.functions.map((f, i) => (
                     <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                        <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>{f.name}</span>
                        <span style={{ fontWeight: 800 }}>{f.complexity} CPX</span>
                     </div>
                   )) : <p style={{ color: 'var(--text-tertiary)', fontSize: '13px' }}>No specific nodes found.</p>}
                </div>
             </div>
             <div className="col-6 white-panel" style={{ padding: '32px' }}>
                <h4 style={{ fontSize: '15px', marginBottom: '16px' }}>Logical Flow</h4>
                <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  Structural integrity verified via <strong>{analysis?.metrics?.total_lines || 0} lines</strong> of recursive analysis.
                </p>
             </div>
          </div>
        </div>
      </Modal>

      <style>{`
          .premium-loader { width: 44px; height: 44px; border: 3px solid #f3f4f6; border-top-color: var(--text-primary); border-radius: 50%; animation: spin 0.6s linear infinite; }
          @keyframes spin { to { transform: rotate(360deg); } }
          
          .lg-toggle { display: none; }
          @media (max-width: 1023px) {
            .lg-toggle { display: flex !important; }
            .hero-img { display: none !important; }
            .metric-sep { display: none !important; }
            .main-content { padding-top: 80px !important; }
          }
          
          .hidden.md\\:block { display: none; }
          @media (min-width: 768px) {
            .hidden.md\\:block { display: block; }
          }
      `}</style>
    </div>
  );
}

export default App;
