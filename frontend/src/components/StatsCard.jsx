export default function StatsCard({ title, value, icon: Icon, color = 'primary' }) {
  const colorClasses = {
    primary: 'bg-indigo-500/20 text-indigo-400',
    green: 'bg-green-500/20 text-green-400',
    purple: 'bg-purple-500/20 text-purple-400',
    orange: 'bg-orange-500/20 text-orange-400',
    red: 'bg-red-500/20 text-red-400',
    blue: 'bg-blue-500/20 text-blue-400',
  }
  
  const colorClass = colorClasses[color] || colorClasses.primary
  
  return (
    <div className="bg-surface rounded-2xl p-6 border border-slate-700/50 hover:border-primary/30 transition-colors">
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm text-slate-400 font-medium">{title}</span>
        <div className={`w-10 h-10 rounded-xl ${colorClass} flex items-center justify-center`}>
          <Icon size={20} />
        </div>
      </div>
      <p className="text-3xl font-bold text-white">{value}</p>
    </div>
  )
}
