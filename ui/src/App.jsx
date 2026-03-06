import React, { useState, useEffect } from 'react';
import { 
  FileCode, Activity, AlertTriangle, Cpu, ChevronRight, 
  Terminal, BarChart3, LayoutDashboard, Settings, Info,
  Code2, Sparkles, BookOpen, Layers, RefreshCw, XCircle, UploadCloud
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// --- Components ---

const Badge = ({ children, color = "var(--text-secondary)" }) => (
  <span style={{
    background: 'rgba(255,255,255,0.05)', 
    padding: '2px 8px', 
    borderRadius: '4px', 
    fontSize: '10px', 
    fontFamily: 'var(--font-mono)',
    color: color,
    border: `1px solid ${color}33`
  }}>
    {children}
  </span>
);

const ErrorState = ({ message, onRetry }) => (
  <div style={{
    height: '60vh', display: 'flex', flexDirection: 'column', 
    alignItems: 'center', justifyContent: 'center', gap: '24px', textAlign: 'center'
  }}>
    <XCircle size={64} color="var(--danger)" opacity={0.5} />
    <div>
      <h3 style={{fontSize: '1.5rem', fontWeight: 700, marginBottom: '8px'}}>Analysis Failed</h3>
      <p style={{color: 'var(--text-secondary)', maxWidth: '400px', margin: '0 auto'}}>{message}</p>
    </div>
    <button 
      onClick={onRetry}
      style={{
        padding: '10px 24px', borderRadius: '8px', background: 'white', color: 'black',
        fontWeight: 700, border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px'
      }}
    >
      <RefreshCw size={18} /> Retry Analysis
    </button>
  </div>
);

function App() {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [explanation, setExplanation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState('developer');
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
        setError("Could not connect to the CodeExplain Engine. Please ensure the server is running.");
      });
  };

  const handleSelectFile = async (file) => {
    setLoading(true);
    setError(null);
    setAnalysis(null);
    setExplanation('');
    setSelectedFile(file);

    try {
      // 1. Get File Content
      const contentRes = await fetch(`/api/file-content?path=${encodeURIComponent(file.path)}`);
      if (!contentRes.ok) throw new Error("Failed to read file content.");
      const contentData = await contentRes.json();
      setFileContent(contentData.content || '');

      // 2. Run Analysis
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

      // 3. Run Explanation
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

      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error("File upload failed. Ensure the backend is running.");
      
      const data = await res.json();
      await handleSelectFile(data);
      fetchFiles(); // refresh explorer
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  // Re-run explanation when mode changes
  useEffect(() => {
    if (selectedFile && !loading && !error) {
       // Simple re-fetch of explanation only
       const fetchExplanation = async () => {
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
         } catch (e) {
          console.error("Failed to fetch explanation", e);
         }
       };
       fetchExplanation();
    }
  }, [mode]);

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar glass-panel">
        <div className="sidebar-header">
          <div className="logo-container">
            <div className="logo-box">
              <Terminal size={24} color="black" />
            </div>
            <div>
              <h1 style={{fontSize: '1.25rem', fontWeight: 700, letterSpacing: '-0.025em'}}>CodeExplain</h1>
              <span style={{fontSize: '10px', color: 'var(--text-secondary)', fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase'}}>AI Engine v1.2</span>
            </div>
          </div>
        </div>

        <div className="file-list">
          <div style={{padding: '0 16px', marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <span style={{fontSize: '10px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.1em'}}>Project Explorer</span>
            
            <button 
              onClick={() => fileInputRef.current?.click()}
              style={{
                background: 'rgba(245,144,38,0.1)', color: 'var(--accent-color)', 
                border: '1px solid rgba(245,144,38,0.2)', borderRadius: '4px',
                padding: '4px 8px', fontSize: '10px', fontWeight: 700, cursor: 'pointer',
                display: 'flex', alignItems: 'center', gap: '4px'
              }}
            >
              <UploadCloud size={12} /> UPLOAD
            </button>
            <input 
              type="file" 
              ref={fileInputRef} 
              style={{ display: 'none' }} 
              onChange={handleFileUpload} 
              accept=".py,.js,.jsx,.ts,.tsx"
            />
          </div>
          {files.length > 0 ? files.map(file => (
            <button
              key={file.path}
              onClick={() => handleSelectFile(file)}
              className={`file-item ${selectedFile?.path === file.path ? 'active' : ''}`}
            >
              <FileCode size={18} />
              <span style={{fontSize: '14px', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}}>{file.name}</span>
            </button>
          )) : (
             <div style={{padding: '20px', textAlign: 'center', opacity: 0.5}}>
                <p style={{fontSize: '12px'}}>No source files found.</p>
             </div>
          )}
        </div>

        <div style={{padding: '16px', background: 'rgba(255,255,255,0.03)', borderTop: '1px solid var(--border-color)', margin: '8px', borderRadius: '12px'}}>
           <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px'}}>
              <div style={{width: '8px', height: '8px', borderRadius: '50%', background: error ? 'var(--danger)' : '#10b981'}} />
              <span style={{fontSize: '12px', fontWeight: 600}}>{error ? 'Engine Error' : 'Engine Connected'}</span>
           </div>
           <p style={{fontSize: '10px', color: '#64748b'}}>Multi-language AST parser active.</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <AnimatePresence mode="wait">
        {selectedFile ? (
          <motion.div 
            key={selectedFile.path}
            initial={{opacity: 0, y: 10}}
            animate={{opacity: 1, y: 0}}
            exit={{opacity: 0, y: -10}}
            style={{maxWidth: '1200px', margin: '0 auto', width: '100%'}}
          >
            {/* Header */}
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '32px'}}>
              <div>
                <h2 style={{fontSize: '2.25rem', fontWeight: 800, letterSpacing: '-0.02em'}}>{selectedFile.name}</h2>
                <div style={{display: 'flex', gap: '8px', marginTop: '4px'}}>
                   <Badge>{selectedFile.path}</Badge>
                   {analysis?.metrics?.total_lines && <Badge color="var(--accent-color)">{analysis.metrics.total_lines} lines</Badge>}
                </div>
              </div>
              <div style={{display: 'flex', gap: '8px', background: 'rgba(255,255,255,0.03)', padding: '4px', borderRadius: '24px', border: '1px solid var(--border-color)'}}>
                {['developer', 'beginner', 'fun:pirate'].map(m => (
                  <button 
                    key={m}
                    onClick={() => setMode(m)}
                    style={{
                      padding: '8px 16px', borderRadius: '20px', fontSize: '11px', fontWeight: 700, border: 'none', cursor: 'pointer',
                      background: mode === m ? 'var(--accent-color)' : 'transparent',
                      color: mode === m ? 'black' : 'var(--text-secondary)',
                      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                    }}
                  >
                    {m.split(':')[1]?.toUpperCase() || m.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            {error ? (
              <ErrorState message={error} onRetry={() => handleSelectFile(selectedFile)} />
            ) : loading ? (
              <div className="glass-panel" style={{height: '60vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '20px'}}>
                 <div className="loader" />
                 <p style={{color: 'var(--text-secondary)', fontWeight: 500, letterSpacing: '0.05em'}} className="animate-pulse">MAP-REDUCE SEMANTICS...</p>
                 <style>{`
                    .loader { width: 48px; height: 48px; border: 3px solid rgba(245,144,38,0.1); border-top-color: var(--accent-color); border-radius: 50%; animation: spin 0.8s cubic-bezier(0.4, 0, 0.2, 1) infinite; }
                    @keyframes spin { to { transform: rotate(360deg); } }
                    .animate-pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
                    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .5; } }
                 `}</style>
              </div>
            ) : (
              <div className="dashboard-grid">
                
                {/* Score Panel */}
                <div className="col-4 dashboard-grid" style={{gap: '16px'}}>
                   <div className="col-12 glass-panel" style={{padding: '24px', textAlign: 'center', position: 'relative', overflow: 'hidden'}}>
                      <div className="metric-label" style={{marginBottom: '16px'}}>Maintainability Index</div>
                      <div style={{position: 'relative', width: '120px', height: '120px', margin: '0 auto 16px'}}>
                         <svg width="120" height="120" viewBox="0 0 120 120" style={{transform: 'rotate(-90deg)'}}>
                           <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="10"/>
                           <circle cx="60" cy="60" r="52" fill="none" stroke={ (analysis?.scores?.maintainability || 0) > 70 ? "#10b981" : "#f59e0b" } strokeWidth="10" strokeDasharray="326.7" 
                              strokeDashoffset={326.7 - (326.7 * (analysis?.scores?.maintainability || 0) / 100)}
                              style={{transition: 'stroke-dashoffset 1s ease-out'}}
                           />
                         </svg>
                         <div style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '28px', fontWeight: 800}}>
                           {analysis?.scores?.maintainability || 0}
                         </div>
                      </div>
                      <div style={{fontSize: '11px', color: (analysis?.scores?.maintainability || 0) > 70 ? '#10b981' : '#f59e0b', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.1em'}}>
                        {analysis?.scores?.maintainability_label || 'COMPUTING...'}
                      </div>
                   </div>
                   <div className="col-12 glass-panel" style={{padding: '24px', textAlign: 'center', borderLeft: '4px solid var(--accent-color)'}}>
                      <div className="metric-label" style={{marginBottom: '8px'}}>Cyclomatic Complexity</div>
                      <div style={{fontSize: '3rem', fontWeight: 900, color: 'var(--accent-color)', letterSpacing: '-0.05em'}}>
                        {analysis?.complexity?.average_complexity || 0}
                      </div>
                      <div style={{fontSize: '11px', color: 'var(--accent-color)', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.1em'}}>
                        {analysis?.complexity?.overall_label || 'LOW RISK'}
                      </div>
                   </div>
                </div>

                {/* Metrics Stats */}
                <div className="col-8 glass-panel metrics-row" style={{padding: '0 40px'}}>
                    <div className="metric-item">
                      <Layers size={22} color="var(--text-secondary)" style={{marginBottom: '10px'}} />
                      <div className="metric-value">{analysis?.metrics?.total_lines || 0}</div>
                      <div className="metric-label">LOC</div>
                    </div>
                    <div style={{width: '1px', height: '48px', background: 'rgba(255,255,255,0.08)'}} />
                    <div className="metric-item">
                      <Code2 size={22} color="var(--text-secondary)" style={{marginBottom: '10px'}} />
                      <div className="metric-value">{analysis?.metrics?.function_count || analysis?.complexity?.functions?.length || 0}</div>
                      <div className="metric-label">Methods</div>
                    </div>
                    <div style={{width: '1px', height: '48px', background: 'rgba(255,255,255,0.08)'}} />
                    <div className="metric-item">
                      <Sparkles size={22} color="var(--text-secondary)" style={{marginBottom: '10px'}} />
                      <div className="metric-value">{analysis?.smells?.length || 0}</div>
                      <div className="metric-label">Smells</div>
                    </div>
                    <div style={{width: '1px', height: '48px', background: 'rgba(255,255,255,0.08)'}} />
                    <div className="metric-item">
                      <BookOpen size={22} color="var(--text-secondary)" style={{marginBottom: '10px'}} />
                      <div className="metric-value">{Math.round((analysis?.metrics?.comment_ratio || 0) * 100)}%</div>
                      <div className="metric-label">Docs</div>
                    </div>
                </div>

                {/* Explanation Card */}
                <div className="col-7">
                  <div style={{display: 'flex', alignItems: 'center', gap: '8px', padding: '0 8px', marginBottom: '16px'}}>
                    <Info size={16} color="var(--accent-color)" />
                    <span className="metric-label">AI Semantic Explanation</span>
                  </div>
                  <div className="glass-panel" style={{padding: '40px', minHeight: '440px', position: 'relative', overflow: 'hidden'}}>
                    <div style={{position: 'absolute', top: -20, right: -20, opacity: 0.03, pointerEvents: 'none'}}>
                      <BarChart3 size={240} />
                    </div>
                    <div style={{fontSize: '1.25rem', fontWeight: 300, lineHeight: 1.7, color: '#f1f5f9', position: 'relative'}}>
                       {(explanation || '').split('\n').filter(p => p.trim()).map((para, i) => (
                         <p key={i} style={{marginBottom: '20px'}}>{para}</p>
                       ))}
                    </div>
                  </div>
                </div>

                {/* Sidebar Cards */}
                <div className="col-5 dashboard-grid" style={{gap: '24px'}}>
                  {/* Code Smells */}
                  <div className="col-12">
                    <div style={{display: 'flex', alignItems: 'center', gap: '8px', padding: '0 8px', marginBottom: '16px'}}>
                      <AlertTriangle size={16} color="#f59e0b" />
                      <span className="metric-label">Architecture Alerts</span>
                    </div>
                    <div style={{display: 'flex', flexDirection: 'column', gap: '12px'}}>
                      {analysis?.smells && analysis.smells.length > 0 ? (
                        analysis.smells.slice(0, 5).map((smell, i) => (
                          <div key={i} className="glass-card" style={{padding: '16px', display: 'flex', gap: '16px', borderLeft: `3px solid ${smell.severity === 'high' ? '#ef4444' : '#f59e0b'}`}}>
                             <div style={{flex: 1}}>
                               <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '4px'}}>
                                  <span style={{fontSize: '12px', fontWeight: 700, color: 'white', textTransform: 'uppercase', letterSpacing: '0.05em'}}>
                                    {smell.kind.replace(/_/g, ' ')}
                                  </span>
                                  <span style={{fontSize: '10px', color: '#64748b', fontFamily: 'var(--font-mono)'}}>LINE {smell.lineno}</span>
                               </div>
                               <p style={{fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.4}}>{smell.message}</p>
                             </div>
                          </div>
                        ))
                      ) : (
                        <div className="glass-card" style={{padding: '40px', textAlign: 'center', background: 'rgba(16,185,129,0.03)', border: '1px dashed rgba(16,185,129,0.2)'}}>
                           <Sparkles size={28} color="#10b981" style={{margin: '0 auto 12px', opacity: 0.4}} />
                           <p style={{fontSize: '11px', color: '#10b981', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em'}}>Architecture is Pristine</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Quick Insight */}
                  <div className="col-12 glass-panel" style={{padding: '24px', background: 'linear-gradient(135deg, rgba(245,144,38,0.05) 0%, transparent 100%)'}}>
                     <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px'}}>
                        <Activity size={20} color="var(--accent-color)" />
                        <h4 style={{fontSize: '14px', fontWeight: 700}}>Analysis Insight</h4>
                     </div>
                     <p style={{fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5}}>
                        This {selectedFile.name.endsWith('.py') ? 'Python module' : 'Source file'} has been processed using the 
                        <strong> Universal Parser Pipeline</strong>. Deep structural analysis detected 
                        <strong> {analysis?.complexity?.functions?.length || 0}</strong> entry points.
                     </p>
                  </div>
                </div>

              </div>
            )}
          </motion.div>
        ) : (
          <motion.div 
            initial={{opacity: 0}} animate={{opacity: 1}}
            style={{height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: '48px'}}
          >
             <div style={{position: 'relative', marginBottom: '40px'}}>
                <div style={{position: 'absolute', inset: -20, filter: 'blur(50px)', background: 'rgba(245,144,38,0.15)', borderRadius: '50%'}} />
                <Terminal size={140} color="rgba(245,144,38,0.2)" />
             </div>
             <h2 style={{fontSize: '3rem', fontWeight: 800, marginBottom: '20px', letterSpacing: '-0.03em', color: 'white'}}>Insight into every block.</h2>
             <p style={{color: 'var(--text-secondary)', maxWidth: '480px', margin: '0 auto', fontSize: '1.25rem', fontWeight: 300, lineHeight: 1.6}}>
               Select a source file from the project explorer to begin deep structural analysis and AI human-language explanation.
             </p>
             <div style={{marginTop: '40px', display: 'flex', gap: '16px'}}>
                <div style={{padding: '12px 24px', borderRadius: '12px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-color)', fontSize: '12px', fontWeight: 600}}>
                   <span style={{color: 'var(--accent-color)'}}>82</span> Unit Tests Active
                </div>
                <div style={{padding: '12px 24px', borderRadius: '12px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-color)', fontSize: '12px', fontWeight: 600}}>
                   Engine v1.2.0 <span style={{color: '#10b981'}}>Online</span>
                </div>
             </div>
          </motion.div>
        )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App;
