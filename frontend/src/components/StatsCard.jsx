export default function StatsCard({ title, value, icon: Icon, color = 'primary' }) {
  return (
    <div className="bg-surface rounded-2xl p-6 border border-slate-700/50 hover:border-primary/30 transition-colors">
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm text-slate-400 font-medium">{title}</span>
        <div className={`w-10 h-10 rounded-xl bg-${color}/20 flex items-center justify-center`}>
          <Icon size={20} className={`text-${color}`} />
        </div>
      </div>
      <p className="text-3xl font-bold text-white">{value}</p>
    </div>
  )
}
