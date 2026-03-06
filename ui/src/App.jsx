import React, { useState, useEffect } from 'react';
import { 
  FileCode, Activity, AlertTriangle, Cpu, ChevronRight, 
  Terminal, BarChart3, LayoutDashboard, Settings, Info,
  Code2, Sparkles, BookOpen, Layers, RefreshCw, XCircle, UploadCloud,
  Zap, Compass, Shield, Menu, X, Box, Search
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// --- Takra 3D Components ---

const FloatingSculpture = () => (
  <div className="bg-sculpture">
    <motion.div 
      className="floating-shape"
      animate={{ y: [0, -30, 0], rotate: [0, 45, 0] }}
      transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
      style={{ width: '300px', height: '300px', top: '10%', left: '-50px' }}
    />
    <motion.div 
      className="floating-shape"
      animate={{ y: [0, 40, 0], rotate: [0, -30, 0] }}
      transition={{ duration: 12, repeat: Infinity, ease: "easeInOut", delay: 2 }}
      style={{ width: '400px', height: '400px', bottom: '5%', right: '-100px' }}
    />
  </div>
);

const Badge = ({ children, color = "var(--text-secondary)" }) => (
  <span className="badge" style={{ border: `1px solid ${color}22`, color, background: 'white', fontWeight: 700, borderRadius: '8px' }}>
    {children}
  </span>
);

const Modal = ({ isOpen, onClose, title, children }) => (
  <AnimatePresence>
    {isOpen && (
      <motion.div 
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
        style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.1)', backdropFilter: 'blur(8px)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}
        onClick={onClose}
      >
        <motion.div 
          initial={{ scale: 0.9, y: 40 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.9, y: 40 }}
          transition={{ type: "spring", damping: 25, stiffness: 300 }}
          className="modal-3d"
          style={{ width: '100%', maxWidth: '900px', borderRadius: '32px', overflow: 'hidden' }}
          onClick={e => e.stopPropagation()}
        >
          <div style={{ padding: '32px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 800 }}>{title}</h3>
            <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-tertiary)' }}><X size={28} /></button>
          </div>
          <div style={{ padding: '40px', maxHeight: '75vh', overflowY: 'auto' }}>
            {children}
          </div>
        </motion.div>
      </motion.div>
    )}
  </AnimatePresence>
);

const MetricBox = ({ icon: Icon, value, label, color = "#6b7280" }) => (
  <motion.div 
    className="metric-item"
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ type: "spring", damping: 20 }}
  >
    <div style={{ width: '44px', height: '44px', background: 'white', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px', boxShadow: 'var(--shadow-3d-sm)', border: '1px solid var(--border-color)' }}>
      <Icon size={20} color={color} />
    </div>
    <div className="metric-value">{value}</div>
    <div className="metric-label">{label}</div>
  </motion.div>
);

const ReadableExplanation = ({ text }) => {
  if (!text) return null;
  const paragraphs = text.split('\n').filter(p => p.trim());
  return (
    <div className="explanation-text">
      {paragraphs.map((para, i) => {
        if (para === '---') return <div key={i} className="hr" />;
        let icon = null;
        const lowPara = para.toLowerCase();
        const hasEmoji = /^[\u2700-\u27bf]|[\u1f300-\u1f64f]|[\u1f680-\u1f6ff]|[\u1f1e0-\u1f1ff]/.test(para);
        if (!hasEmoji) {
          if (lowPara.includes('mini-command') || lowPara.includes('instruction')) icon = <Zap size={20} color="var(--accent-color)" />;
          if (lowPara.includes('blueprint') || lowPara.includes('class')) icon = <Box size={20} color="#0284c7" />;
          if (lowPara.includes('helper') || lowPara.includes('job')) icon = <Sparkles size={20} color="#f59e0b" />;
          if (lowPara.includes('note') || lowPara.includes('author')) icon = <Info size={20} color="#6366f1" />;
          if (lowPara.includes('picture') || lowPara.includes('chapter')) icon = <LayoutDashboard size={20} color="#0d9488" />;
        }
        return (
          <p key={i} style={{ display: 'flex', gap: '18px', alignItems: 'flex-start' }}>
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

  useEffect(() => { fetchFiles(); }, []);

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
      const contentData = await contentRes.json();
      setFileContent(contentData.content || '');
      const analyzeRes = await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: contentData.content, filename: file.name, source_path: file.path })
      });
      const analyzeData = await analyzeRes.json();
      setAnalysis(analyzeData);
      const explainRes = await fetch('/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: contentData.content, filename: file.name, source_path: file.path, mode: mode })
      });
      const explainData = await explainRes.json();
      setExplanation(explainData.explanation || '');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <FloatingSculpture />

      {/* Sidebar Mobile Toggle */}
      <button 
        onClick={() => setSidebarOpen(!sidebarOpen)}
        style={{ position: 'fixed', top: '24px', left: '24px', zIndex: 60, background: 'white', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '12px', display: 'flex', alignItems: 'center', boxShadow: 'var(--shadow-3d-md)' }}
        className="lg-toggle"
      >
        {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Sidebar Overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.05)', backdropFilter: 'blur(4px)', zIndex: 45 }} 
            onClick={() => setSidebarOpen(false)} 
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="logo-container">
            <motion.img 
              src="/logo.png" 
              alt="CodeExplain" 
              className="sidebar-logo" 
              animate={{ rotateY: [0, 360] }}
              transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
            />
            <div>
              <h1 style={{fontSize: '1.3rem', fontWeight: 800}}>CodeExplain</h1>
              <span style={{fontSize: '10px', color: 'var(--text-tertiary)', fontWeight: 800, letterSpacing: '0.15em', textTransform: 'uppercase'}}>Autonomous AI</span>
            </div>
          </div>
        </div>

        <div className="file-list">
          <div style={{padding: '0 20px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <span style={{fontSize: '11px', fontWeight: 800, color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.15em'}}>Project Engine</span>
          </div>

          <div style={{ padding: '0 12px 24px' }}>
            <button 
              onClick={() => fileInputRef.current?.click()}
              className="btn-premium"
              style={{ width: '100%', justifyContent: 'center', marginBottom: '32px', background: 'white' }}
            >
              <UploadCloud size={16} /> NEW ANALYSIS
            </button>
            <input type="file" ref={fileInputRef} style={{ display: 'none' }} onChange={(e) => {}} accept=".py,.js,.jsx,.ts,.tsx" />

            {files.map(file => (
              <button
                key={file.path}
                onClick={() => handleSelectFile(file)}
                className={`file-item ${selectedFile?.path === file.path ? 'active' : ''}`}
              >
                <FileCode size={18} color={selectedFile?.path === file.path ? 'var(--accent-color)' : 'var(--text-secondary)'} />
                <span style={{overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}}>{file.name}</span>
              </button>
            ))}
          </div>
        </div>

        <div style={{padding: '32px', background: 'rgba(255,255,255,0.4)', borderRadius: '24px', margin: '0 16px 16px', border: '1px solid var(--border-color)'}}>
           <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px'}}>
              <div style={{width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', boxShadow: '0 0 10px #10b98155'}} />
              <span style={{fontSize: '12px', fontWeight: 800}}>Takra Engine v1.2</span>
           </div>
           <p style={{fontSize: '11px', color: 'var(--text-secondary)', lineHeight: 1.5}}>Ready for 3D structural mapping.</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <AnimatePresence mode="wait">
        {selectedFile ? (
          <motion.div 
            key={selectedFile.path}
            initial={{opacity: 0, y: 30}}
            animate={{opacity: 1, y: 0}}
            exit={{opacity: 0, y: -30}}
            transition={{ type: "spring", damping: 25 }}
            style={{maxWidth: '1300px', margin: '0 auto', width: '100%', paddingBottom: '100px'}}
          >
            {/* Header */}
            <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'flex-end', gap: '32px', marginBottom: '60px', paddingTop: '20px'}}>
               <div style={{ flex: 1, minWidth: '300px' }}>
                 <motion.h2 layoutId="title" style={{fontSize: 'clamp(2.5rem, 6vw, 4rem)', fontWeight: 800, letterSpacing: '-0.05em', lineHeight: 1}}>{selectedFile.name}</motion.h2>
                 <div style={{display: 'flex', flexWrap: 'wrap', gap: '16px', marginTop: '20px'}}>
                   <Badge>{selectedFile.path}</Badge>
                   {analysis?.metrics?.total_lines && <Badge color="var(--accent-color)">{analysis.metrics.total_lines} SOURCE LINES</Badge>}
                 </div>
               </div>
               <div style={{display: 'flex', gap: '6px', background: '#f5f5f5', padding: '6px', borderRadius: '18px', boxShadow: 'var(--bevel-light)'}}>
                 {['beginner', 'developer', 'fun:pirate'].map(m => (
                   <button 
                     key={m}
                     onClick={() => setMode(m)}
                     style={{
                       padding: '12px 24px', borderRadius: '14px', fontSize: '11px', fontWeight: 800, border: 'none', cursor: 'pointer',
                       background: mode === m ? 'white' : 'transparent',
                       color: mode === m ? 'black' : 'var(--text-tertiary)',
                       boxShadow: mode === m ? 'var(--shadow-3d-sm)' : 'none',
                       transition: 'all 0.3s cubic-bezier(0.2, 0, 0, 1)'
                     }}
                   >
                     {m.split(':')[1]?.toUpperCase() || m.toUpperCase()}
                   </button>
                 ))}
               </div>
            </div>

            <div className="dashboard-grid">
              
              {/* Hero Card - Sculptural */}
              <div className="col-8 white-panel" style={{minHeight: '440px', display: 'flex', alignItems: 'center', background: 'radial-gradient(circle at top left, #fff, #fafafa)'}}>
                 <div style={{padding: 'clamp(40px, 8vw, 80px)', flex: 1, position: 'relative', zIndex: 1}}>
                    <div className="metric-label" style={{color: 'var(--accent-color)', marginBottom: '24px'}}>Abstract Mapping</div>
                    <h3 style={{fontSize: '3rem', marginBottom: '24px', lineHeight: 1}}>Structural Sculpting</h3>
                    <p style={{color: 'var(--text-secondary)', maxWidth: '400px', lineHeight: 1.8, fontSize: '17px'}}>
                       Observed <strong>{analysis?.metrics?.function_count || 0} logical behaviors</strong> and <strong>{analysis?.metrics?.class_count || 0} core templates</strong>.
                    </p>
                    <button 
                      className="btn-premium btn-primary" 
                      style={{marginTop: '40px', padding: '16px 36px', fontSize: '15px'}}
                      onClick={() => setShowTrace(true)}
                    >
                       View Engine Trace
                    </button>
                 </div>
                 <div style={{position: 'absolute', right: '0', bottom: '-40px', width: '500px', height: '500px'}} className="hero-img">
                    <img src="/illustration.png" alt="Illustration" style={{width: '100%', height: '100%', objectFit: 'contain'}} />
                 </div>
              </div>

              {/* Health Score - Takra 3D */}
              <div className="col-4 white-panel" style={{display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '60px 40px'}}>
                    <div className="metric-label" style={{marginBottom: '40px'}}>Calculated Health</div>
                    <div style={{position: 'relative', width: '200px', height: '200px'}}>
                       <motion.div 
                         style={{ position: 'absolute', inset: 0, borderRadius: '50%', background: 'white', border: '1px solid var(--border-color)', boxShadow: 'var(--shadow-3d-lg), var(--bevel-heavy)'}}
                         animate={{ scale: [1, 1.02, 1] }} transition={{ duration: 4, repeat: Infinity }}
                       />
                       <svg width="200" height="200" viewBox="0 0 120 120" style={{transform: 'rotate(-90deg)', position: 'relative', zIndex: 1}}>
                         <circle cx="60" cy="60" r="50" fill="none" stroke="#f8f8f8" strokeWidth="6"/>
                         <motion.circle cx="60" cy="60" r="50" fill="none" stroke="var(--accent-color)" strokeWidth="6" strokeDasharray="314" 
                            initial={{ strokeDashoffset: 314 }}
                            animate={{ strokeDashoffset: 314 - (314 * (analysis?.scores?.maintainability || 0) / 100) }}
                            transition={{ duration: 2, ease: "easeOut" }}
                         />
                       </svg>
                       <div style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '56px', fontWeight: 900, letterSpacing: '-0.05em'}}>
                          {analysis?.scores?.maintainability || 0}
                       </div>
                    </div>
                    <div style={{fontSize: '14px', color: 'var(--text-primary)', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.2em', marginTop: '32px'}}>
                      {analysis?.scores?.maintainability_label || 'COMPUTING'}
                    </div>
              </div>

              {/* Metrics Bar */}
              <div className="col-8 white-panel metrics-row" style={{ height: 'auto', padding: '40px' }}>
                  <MetricBox icon={Layers} value={analysis?.metrics?.total_lines || 0} label="Lines" />
                  <MetricBox icon={Code2} value={analysis?.metrics?.function_count || 0} label="Tricks" />
                  <MetricBox icon={AlertTriangle} value={analysis?.smells?.length || 0} label="Flaws" color="var(--danger)" />
                  <MetricBox icon={BookOpen} value={`${Math.round((analysis?.metrics?.comment_ratio || 0) * 100)}%`} label="Story" />
              </div>

              {/* Complexity Card */}
              <div className="col-4 white-panel" style={{padding: '50px 40px', textAlign: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
                    <div className="metric-label" style={{marginBottom: '16px'}}>Complexity Scale</div>
                    <div style={{fontSize: '6rem', fontWeight: 900, color: 'var(--text-primary)', letterSpacing: '-0.08em', lineHeight: 0.8}}>
                      {analysis?.complexity?.average_complexity || 0}
                    </div>
                    <div style={{fontSize: '13px', color: 'var(--text-tertiary)', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.2em', marginTop: '24px'}}>
                      {analysis?.complexity?.overall_label || 'READY'}
                    </div>
              </div>

              {/* Narrative Explainer */}
              <div className="col-7">
                <div style={{display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '24px', paddingLeft: '8px'}}>
                  <Sparkles size={20} color="var(--accent-color)" />
                  <span className="metric-label" style={{color: 'var(--text-primary)', fontSize: '13px'}}>Human Narrative Report</span>
                </div>
                <div className="white-panel" style={{padding: 'clamp(40px, 8vw, 80px)', minHeight: '600px', background: '#fff'}}>
                  <ReadableExplanation text={explanation} />
                </div>
              </div>

              {/* Sculptural Sidebar Insights */}
              <div className="col-5" style={{ display: 'flex', flexDirection: 'column', gap: '40px' }}>
                <div>
                   <div style={{display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '24px', paddingLeft: '8px'}}>
                      <Shield size={20} color="var(--text-primary)" />
                      <span className="metric-label" style={{color: 'var(--text-primary)', fontSize: '13px'}}>Risk Factor Analysis</span>
                   </div>
                   <div style={{display: 'flex', flexDirection: 'column', gap: '24px'}}>
                      {analysis?.smells?.map((smell, i) => (
                        <motion.div 
                          key={i} className="glass-card" 
                          whileHover={{ scale: 1.02 }}
                          style={{padding: '32px', background: 'white', boxShadow: 'var(--shadow-3d-md), var(--bevel-light)'}}
                        >
                           <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '16px'}}>
                              <span style={{fontSize: '14px', fontWeight: 900, textTransform: 'uppercase', color: smell.severity === 'high' ? 'var(--danger)' : 'var(--text-primary)'}}>
                                {smell.kind.replace(/_/g, ' ')}
                              </span>
                              <Badge>LINE {smell.lineno}</Badge>
                           </div>
                           <p style={{fontSize: '16px', color: 'var(--text-secondary)', lineHeight: 1.7}}>{smell.message}</p>
                        </motion.div>
                      ))}
                   </div>
                </div>

                <div className="white-panel" style={{padding: '48px 40px', background: 'linear-gradient(135deg, #ffffff, #fdfdfd)', border: '1px solid var(--border-color)', boxShadow: 'var(--shadow-3d-lg)'}}>
                   <h4 style={{fontSize: '20px', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '12px'}}>
                      <Compass size={24} color="var(--accent-color)" /> Sculptural Context
                   </h4>
                   <p style={{fontSize: '16px', color: 'var(--text-secondary)', lineHeight: 1.8}}>
                      Crafted via <strong>Engine Alpha</strong>, identifying cross-module patterns using high-precision AST sculpting. 
                      Maintainability is weighted against geometric code density.
                   </p>
                </div>
              </div>

            </div>
          </motion.div>
        ) : (
          <motion.div 
            initial={{opacity: 0}} animate={{opacity: 1}}
            style={{height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: '60px'}}
          >
             <motion.div 
               animate={{ y: [0, -20, 0] }} transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
               style={{position: 'relative', width: 'clamp(300px, 50vw, 600px)', height: 'clamp(260px, 40vw, 500px)', marginBottom: '60px'}}
             >
                <img src="/illustration.png" alt="Logo" style={{width: '100%', height: '100%', objectFit: 'contain', filter: 'drop-shadow(0 40px 80px rgba(0,0,0,0.08))'}} />
             </motion.div>
             <h2 style={{fontSize: 'clamp(3rem, 8vw, 5rem)', fontWeight: 800, marginBottom: '32px', letterSpacing: '-0.06em', lineHeight: 0.95}}>Understand <br/> Everything.</h2>
             <p style={{color: 'var(--text-secondary)', maxWidth: '640px', margin: '0 auto', fontSize: 'clamp(1.2rem, 2.5vw, 1.6rem)', fontWeight: 500, lineHeight: 1.7}}>
                Upload source files to generate 3D semantic mappings and narrative-driven code clarity.
             </p>
          </motion.div>
        )}
        </AnimatePresence>
      </div>

      <Modal isOpen={showTrace} onClose={() => setShowTrace(false)} title="Takra Engine Trace">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '40px' }}>
          <div style={{ background: '#fafafa', padding: '32px', borderRadius: '24px', border: '1px solid var(--border-color)', boxShadow: 'var(--bevel-light)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
              <Search size={22} color="var(--accent-color)" />
              <span className="metric-label" style={{ fontSize: '14px' }}>Deep AST Geometry</span>
            </div>
            <pre style={{ fontSize: '13px', color: '#1a1a1a', overflowX: 'auto', padding: '24px', background: 'white', borderRadius: '16px', border: '1px solid var(--border-color)', lineHeight: 1.8, maxHeight: '400px' }}>
              {JSON.stringify(analysis, null, 2)}
            </pre>
          </div>
        </div>
      </Modal>

      <style>{`
          .lg-toggle { display: none; }
          @media (max-width: 1023px) {
            .lg-toggle { display: flex !important; }
            .hero-img { display: none !important; }
            .main-content { padding-top: 100px !important; }
            .sidebar { position: fixed; z-index: 50; transform: translateX(-100%); width: 100%; max-width: 320px; }
            .sidebar.open { transform: translateX(0); }
          }
      `}</style>
    </div>
  );
}

export default App;
