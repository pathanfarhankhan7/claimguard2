import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'

const data = [
  { name: 'High Suspicion', value: 12 },
  { name: 'Medium Suspicion', value: 37 },
  { name: 'Low Suspicion', value: 51 },
]

export function DashboardPage() {
  return (
    <div style={{padding:24}}>
      <h1>Dashboard</h1>
      <p>Understand Claims. Detect Patterns. Investigate Smarter.</p>
      <div style={{height:260, maxWidth:500}}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" outerRadius={90}>
              <Cell fill="#ef4444" /><Cell fill="#f59e0b" /><Cell fill="#22c55e" />
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
