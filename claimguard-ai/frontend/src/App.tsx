import { Link, Route, Routes } from 'react-router-dom'
import { DashboardPage } from './pages/DashboardPage'
import { AnalyzePage } from './pages/AnalyzePage'

const Placeholder = ({ title }: { title: string }) => <div className="p-6"><h1>{title}</h1><p>ClaimGuard AI provides AI-assisted claim analysis and investigation support. AI predictions are not definitive determinations of fraud, liability, or coverage.</p></div>

export function App() {
  const pages = ['login','register','dashboard','analyze','claims','documents','similar-claims','clusters','policy-ai','investigation-ai','knowledge-graph','nlp-insights','model-lab','datasets','reports','settings']
  return (
    <div style={{display:'grid', gridTemplateColumns:'220px 1fr', minHeight:'100vh'}}>
      <aside style={{padding:16, borderRight:'1px solid #e5e7eb'}}>
        <h2>ClaimGuard AI</h2>
        <nav style={{display:'flex', flexDirection:'column', gap:8}}>{pages.map(p => <Link key={p} to={`/${p}`}>{p}</Link>)}</nav>
      </aside>
      <main>
        <Routes>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/analyze" element={<AnalyzePage />} />
          {pages.filter(p => !['dashboard','analyze'].includes(p)).map(p => <Route key={p} path={`/${p}`} element={<Placeholder title={p} />} />)}
          <Route path="*" element={<DashboardPage />} />
        </Routes>
      </main>
    </div>
  )
}
