import { useEffect } from 'react'
import { Users, Activity, HardDrive, Cpu, Radio } from 'lucide-react'
import StatsCard from '../components/StatsCard'
import { useStore } from '../store/useStore'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer
} from 'recharts'

const mockTrafficData = [
  { name: 'Mon', traffic: 40 },
  { name: 'Tue', traffic: 65 },
  { name: 'Wed', traffic: 55 },
  { name: 'Thu', traffic: 80 },
  { name: 'Fri', traffic: 70 },
  { name: 'Sat', traffic: 90 },
  { name: 'Sun', traffic: 75 },
]

export default function Dashboard() {
  const { stats, fetchStats } = useStore()

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 30000)
    return () => clearInterval(interval)
  }, [fetchStats])

  const formatBytes = (bytes) => {
    if (!bytes) return '0 GB'
    const gb = bytes / 1024**3
    return `${gb.toFixed(1)} GB`
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Dashboard</h2>
        <p className="text-slate-400 text-sm mt-1">Overview of your proxy server</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard title="Total Clients" value={stats?.total_users ?? '-'} icon={Users} color="primary" />
        <StatsCard title="Active Clients" value={stats?.active_users ?? '-'} icon={Activity} color="green" />
        <StatsCard title="Total Inbounds" value={stats?.total_inbounds ?? '-'} icon={Radio} color="purple" />
        <StatsCard title="CPU Usage" value={`${stats?.cpu_percent?.toFixed(0) ?? 0}%`} icon={Cpu} color="orange" />
      </div>

      <div className="bg-surface rounded-2xl p-6 border border-slate-700/50">
        <h3 className="text-lg font-semibold text-white mb-6">Weekly Traffic Overview</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={mockTrafficData}>
              <defs>
                <linearGradient id="colorTraffic" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '12px'
                }}
              />
              <Area
                type="monotone"
                dataKey="traffic"
                stroke="#6366f1"
                strokeWidth={2}
                fill="url(#colorTraffic)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
