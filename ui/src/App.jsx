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
  
  // Format based on keywords to add visual "beginner-friendly" icons
  const paragraphs = text.split('\n').filter(p => p.trim());
  
  return (
    <div className="explanation-text">
      {paragraphs.map((para, i) => {
        let icon = null;
        if (para.toLowerCase().includes('what does this file do')) icon = <Box size={18} color="var(--accent-color)" />;
        if (para.toLowerCase().includes('author says')) icon = <Info size={18} color="#0284c7" />;
        if (para.toLowerCase().includes('it has') || para.toLowerCase().includes('functions')) icon = <Zap size={18} color="#f59e0b" />;
        if (para.toLowerCase().includes('external tool')) icon = <Settings size={18} color="#6366f1" />;
        if (para.toLowerCase().includes('think of this like')) icon = <Sparkles size={18} color="#d946ef" />;

        return (
          <p key={i} style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
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
  const [mode, setMode] = useState('beginner'); // Default to beginner for hosting
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
    setSidebarOpen(false); // Close sidebar on mobile select

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
        style={{ position: 'fixed', top: '20px', left: '20px', zIndex: 60, background: 'white', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '8px', display: 'flex', alignItems: 'center' }}
        className="lg:hidden"
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
           <p style={{fontSize: '10px', color: 'var(--text-tertiary)', lineHeight: 1.4}}>Parsing local project files with advanced AST mappings.</p>
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
            style={{maxWidth: '1200px', margin: '0 auto', width: '100%', paddingBottom: '40px'}}
          >
            {/* Header */}
            <div style={{display: 'flex', flexDirection: 'column', gap: '24px', marginBottom: '48px'}}>
               <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'flex-end', gap: '20px' }}>
                  <div style={{ flex: 1, minWidth: '300px' }}>
                    <h2 style={{fontSize: 'clamp(2rem, 5vw, 2.5rem)', fontWeight: 800, letterSpacing: '-0.04em'}}>{selectedFile.name}</h2>
                    <div style={{display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '8px'}}>
                      <Badge>{selectedFile.path}</Badge>
                      {analysis?.metrics?.total_lines && <Badge color="var(--accent-color)">{analysis.metrics.total_lines} LOC</Badge>}
                    </div>
                  </div>
                  <div style={{display: 'flex', gap: '4px', background: '#f3f4f6', padding: '4px', borderRadius: '10px'}}>
                    {['beginner', 'developer', 'fun:pirate'].map(m => (
                      <button 
                        key={m}
                        onClick={() => setMode(m)}
                        style={{
                          padding: '8px 16px', borderRadius: '7px', fontSize: '11px', fontWeight: 700, border: 'none', cursor: 'pointer',
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
                <div className="col-8 white-panel" style={{padding: '0', position: 'relative', overflow: 'hidden', minHeight: '340px', background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)', display: 'flex', alignItems: 'center'}}>
                   <div style={{padding: '48px', flex: 1, position: 'relative', zIndex: 1}}>
                      <div className="metric-label" style={{color: '#0369a1', marginBottom: '16px'}}>Source Context</div>
                      <h3 style={{fontSize: '2rem', marginBottom: '12px'}}>Structural Insight</h3>
                      <p style={{color: '#334155', maxWidth: '300px', lineHeight: 1.6, fontSize: '15px'}}>
                        Analyzing <strong>{analysis?.metrics?.function_count || 0} functions</strong> and <strong>{analysis?.metrics?.class_count || 0} structures</strong> in this module.
                      </p>
                      <button 
                        className="btn-premium btn-primary" 
                        style={{marginTop: '24px', background: '#0369a1'}}
                        onClick={() => setShowTrace(true)}
                      >
                         View Deep Trace
                      </button>
                   </div>
                   <div style={{position: 'absolute', right: '10px', bottom: '-20px', width: '400px', height: '400px', opacity: loading ? 0.3 : 1, transition: 'opacity 0.5s'}} className="hidden sm:block">
                      <img src="/illustration.png" alt="Illustration" style={{width: '100%', height: '100%', objectFit: 'contain'}} />
                   </div>
                   {loading && (
                      <div style={{position: 'absolute', inset: 0, background: 'rgba(255,255,255,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 10}}>
                         <div className="premium-loader" />
                      </div>
                   )}
                </div>

                {/* Score Panel */}
                <div className="col-4 white-panel" style={{padding: '32px', textAlign: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
                      <div className="metric-label" style={{marginBottom: '20px'}}>Health Index</div>
                      <div style={{position: 'relative', width: '140px', height: '140px', margin: '0 auto 20px'}}>
                         <svg width="140" height="140" viewBox="0 0 120 120" style={{transform: 'rotate(-90deg)'}}>
                           <circle cx="60" cy="60" r="54" fill="none" stroke="#f3f4f6" strokeWidth="8"/>
                           <circle cx="60" cy="60" r="54" fill="none" stroke={ (analysis?.scores?.maintainability || 0) > 70 ? "#10b981" : "var(--accent-color)" } strokeWidth="8" strokeDasharray="339.3" 
                              strokeDashoffset={339.3 - (339.3 * (analysis?.scores?.maintainability || 0) / 100)}
                              style={{transition: 'stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1)'}}
                           />
                         </svg>
                         <div style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '36px', fontWeight: 900}}>
                            {analysis?.scores?.maintainability || 0}<span style={{fontSize: '16px', fontWeight: 600, color: 'var(--text-tertiary)'}}>%</span>
                         </div>
                      </div>
                      <div style={{fontSize: '13px', color: (analysis?.scores?.maintainability || 0) > 70 ? '#10b981' : 'var(--accent-color)', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em'}}>
                        {analysis?.scores?.maintainability_label || 'COMPUTING'}
                      </div>
                </div>

                {/* Metrics */}
                <div className="col-8 white-panel metrics-row">
                    <div className="metric-item">
                      <Layers size={20} color="#6b7280" style={{marginBottom: '12px'}} />
                      <div className="metric-value">{analysis?.metrics?.total_lines || 0}</div>
                      <div className="metric-label">LOC</div>
                    </div>
                    <div style={{width: '1px', height: '40px', background: 'var(--border-color)'}} className="hidden sm:block" />
                    <div className="metric-item">
                      <Code2 size={20} color="#6b7280" style={{marginBottom: '12px'}} />
                      <div className="metric-value">{analysis?.metrics?.function_count || analysis?.complexity?.functions?.length || 0}</div>
                      <div className="metric-label">Methods</div>
                    </div>
                    <div style={{width: '1px', height: '40px', background: 'var(--border-color)'}} className="hidden sm:block" />
                    <div className="metric-item">
                      <AlertTriangle size={20} color="#f59e0b" style={{marginBottom: '12px'}} />
                      <div className="metric-value">{analysis?.smells?.length || 0}</div>
                      <div className="metric-label">Smells</div>
                    </div>
                    <div style={{width: '1px', height: '40px', background: 'var(--border-color)'}} className="hidden sm:block" />
                    <div className="metric-item">
                      <BookOpen size={20} color="#6b7280" style={{marginBottom: '12px'}} />
                      <div className="metric-value">{Math.round((analysis?.metrics?.comment_ratio || 0) * 100)}%</div>
                      <div className="metric-label">Docs</div>
                    </div>
                </div>

                {/* Complexity Card */}
                <div className="col-4 white-panel" style={{padding: '32px', textAlign: 'center', borderTop: '4px solid var(--accent-color)'}}>
                      <div className="metric-label" style={{marginBottom: '10px'}}>Complexity</div>
                      <div style={{fontSize: '4rem', fontWeight: 900, color: 'var(--text-primary)', letterSpacing: '-0.06em', transition: 'all 0.5s'}}>
                        {analysis?.complexity?.average_complexity || 0}
                      </div>
                      <div style={{fontSize: '11px', color: 'var(--text-tertiary)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em'}}>
                        {analysis?.complexity?.overall_label || 'STABLE'}
                      </div>
                </div>

                {/* AI Explanation */}
                <div className="col-7">
                  <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px'}}>
                    <Sparkles size={16} color="var(--accent-color)" />
                    <span className="metric-label" style={{color: 'var(--text-primary)'}}>AI Semantic Report</span>
                  </div>
                  <div className="white-panel" style={{padding: 'clamp(20px, 5vw, 48px)', minHeight: '440px', position: 'relative'}}>
                     <div style={{position: 'absolute', top: '24px', right: '24px', opacity: 0.1}} className="hidden sm:block">
                        <Zap size={48} />
                     </div>
                    <ReadableExplanation text={explanation} />
                    {!explanation && !loading && <p style={{color: 'var(--text-tertiary)', fontStyle: 'italic'}}>Waiting for engine explanation...</p>}
                  </div>
                </div>

                {/* Side Insights */}
                <div className="col-5 dashboard-grid" style={{gap: '32px'}}>
                  <div className="col-12">
                     <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px'}}>
                        <Shield size={16} color="var(--text-primary)" />
                        <span className="metric-label" style={{color: 'var(--text-primary)'}}>Risk Factors</span>
                     </div>
                     <div style={{display: 'flex', flexDirection: 'column', gap: '16px'}}>
                        {analysis?.smells?.length > 0 ? analysis.smells.slice(0, 4).map((smell, i) => (
                          <div key={i} className="glass-card" style={{padding: '24px'}}>
                             <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '8px'}}>
                                <span style={{fontSize: '12px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em', color: smell.severity === 'high' ? 'var(--danger)' : 'var(--text-primary)'}}>
                                  {smell.kind.replace(/_/g, ' ')}
                                </span>
                                <span className="badge">L{smell.lineno}</span>
                             </div>
                             <p style={{fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.5}}>{smell.message}</p>
                          </div>
                        )) : (
                          <div className="white-panel" style={{padding: '48px', textAlign: 'center', borderStyle: 'dashed'}}>
                             <Activity size={32} color="#10b981" style={{opacity: 0.3, marginBottom: '16px'}} />
                             <p style={{fontSize: '13px', fontWeight: 700, color: '#10b981', letterSpacing: '0.05em'}}>ARCHITECTURE OPTIMIZED</p>
                          </div>
                        )}
                     </div>
                  </div>

                  <div className="white-panel" style={{padding: '32px', background: 'linear-gradient(to bottom right, #ffffff, #f9fafb)', position: 'relative', overflow: 'hidden'}}>
                     <h4 style={{fontSize: '16px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px'}}>
                        <Compass size={20} color="var(--accent-color)" /> Insight Detail
                     </h4>
                     <p style={{fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.7, position: 'relative', zIndex: 1}}>
                        Our specialized <strong>Engine v1.2</strong> identified structural patterns using recursive descent parsing. 
                        The maintainability score is computed relative to the Weighted Micro-Function Complexity.
                     </p>
                     <div style={{position: 'absolute', right: '-20px', bottom: '-20px', opacity: 0.03}} className="hidden md:block">
                        <BarChart3 size={120} />
                     </div>
                  </div>
                </div>

              </div>
            )}
          </motion.div>
        ) : (
          <motion.div 
            initial={{opacity: 0, scale: 0.98}} animate={{opacity: 1, scale: 1}}
            style={{height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: '20px'}}
          >
             <div style={{position: 'relative', width: 'clamp(200px, 40vw, 500px)', height: 'clamp(200px, 30vw, 400px)', marginBottom: '32px'}}>
                <img src="/illustration.png" alt="Logo" style={{width: '100%', height: '100%', objectFit: 'contain', filter: 'drop-shadow(0 20px 40px rgba(0,0,0,0.05))'}} />
             </div>
             <h2 style={{fontSize: 'clamp(2rem, 5vw, 3.5rem)', fontWeight: 800, marginBottom: '24px', letterSpacing: '-0.05em'}}>Understand everything.</h2>
             <p style={{color: 'var(--text-secondary)', maxWidth: '560px', margin: '0 auto', fontSize: 'clamp(1rem, 2vw, 1.25rem)', fontWeight: 400, lineHeight: 1.7}}>
               Choose a source file from the explorer to perform deep structural analysis and generate AI human-language explanations.
             </p>
             <button onClick={() => fileInputRef.current?.click()} className="btn-premium btn-primary" style={{marginTop: '40px', padding: '14px 32px', fontSize: '16px', borderRadius: '12px'}}>
                Analyze New File
             </button>
          </motion.div>
        )}
        </AnimatePresence>
      </div>

      {/* Deep Trace Modal */}
      <Modal isOpen={showTrace} onClose={() => setShowTrace(false)} title="Deep Trace Analysis">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div style={{ background: '#f8fafc', padding: '20px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <Search size={16} color="var(--accent-color)" />
              <span className="metric-label">Raw AST Mapping</span>
            </div>
            <pre style={{ fontSize: '12px', color: '#334155', overflowX: 'auto', padding: '12px', background: 'white', borderRadius: '8px', border: '1px solid var(--border-color)', lineHeight: 1.5 }}>
              {JSON.stringify(analysis, null, 2)}
            </pre>
          </div>
          
          <div className="dashboard-grid">
             <div className="col-6 white-panel" style={{ padding: '20px' }}>
                <h4 style={{ fontSize: '14px', marginBottom: '12px' }}>Semantic Nodes</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                   {analysis?.complexity?.functions?.map((f, i) => (
                     <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                        <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>{f.name}</span>
                        <span style={{ fontWeight: 700 }}>{f.complexity} CPX</span>
                     </div>
                   ))}
                </div>
             </div>
             <div className="col-6 white-panel" style={{ padding: '20px' }}>
                <h4 style={{ fontSize: '14px', marginBottom: '12px' }}>Logical Flow</h4>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                  Structural integrity verified via {analysis?.metrics?.total_lines} lines of recursive analysis.
                </p>
             </div>
          </div>
        </div>
      </Modal>

      <style>{`
          .premium-loader { width: 40px; height: 40px; border: 2px solid #f3f4f6; border-top-color: var(--text-primary); border-radius: 50%; animation: spin 0.6s linear infinite; }
          @keyframes spin { to { transform: rotate(360deg); } }
          
          @media (max-width: 1023px) {
            .lg\\:hidden { display: flex !important; }
            .hidden.sm\\:block { display: none !important; }
          }
          @media (min-width: 1024px) {
            .lg\\:hidden { display: none !important; }
          }
          @media (max-width: 639px) {
            .hidden.sm\\:block { display: none !important; }
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
