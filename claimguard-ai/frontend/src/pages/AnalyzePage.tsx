import { useState } from 'react'
import axios from 'axios'

export function AnalyzePage() {
  const [text, setText] = useState('')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const onAnalyze = async () => {
    setLoading(true)
    try {
      const res = await axios.post('http://localhost:8000/api/claims/analyze', { text })
      setResult(res.data.data)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{padding:24}}>
      <h1>Analyze Claim</h1>
      <textarea value={text} onChange={e => setText(e.target.value)} rows={8} style={{width:'100%'}} placeholder="Paste insurance claim narrative..." />
      <button onClick={onAnalyze} disabled={loading || !text}>{loading ? 'Analyzing...' : 'Analyze Claim'}</button>
      {result && <pre style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  )
}
