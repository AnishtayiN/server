import { useEffect, useState } from 'react'
import { Plus, Pencil, Trash2, Users, Server } from 'lucide-react'
import api from '../api/client'
import InboundModal from '../components/InboundModal'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

export default function Inbounds() {
  const [inbounds, setInbounds] = useState([])
  const [modalOpen, setModalOpen] = useState(false)
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const fetchInbounds = async () => {
    try {
      const res = await api.get('/inbounds')
      setInbounds(res.data)
    } catch (err) {
      toast.error('Failed to load inbounds')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchInbounds() }, [])

  const handleDelete = async (id) => {
    if (!confirm('Delete this inbound and all its clients?')) return
    try {
      await api.delete(`/inbounds/${id}`)
      toast.success('Deleted')
      fetchInbounds()
    } catch {
      toast.error('Delete failed')
    }
  }

  const protocolColors = {
    vless: 'bg-blue-500/20 text-blue-400',
    vmess: 'bg-purple-500/20 text-purple-400',
    trojan: 'bg-green-500/20 text-green-400',
    shadowsocks: 'bg-orange-500/20 text-orange-400'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Inbounds</h2>
          <p className="text-slate-400 text-sm mt-1">Manage proxy listeners and protocols</p>
        </div>
        <button
          onClick={() => { setSelected(null); setModalOpen(true) }}
          className="flex items-center gap-2 bg-primary hover:bg-indigo-600 text-white px-6 py-3 rounded-xl font-medium"
        >
          <Plus size={20} /> New Inbound
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {loading ? (
          <div className="col-span-full text-center py-12 text-slate-400">Loading...</div>
        ) : inbounds.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <Server className="mx-auto text-slate-600 mb-4" size={48} />
            <p className="text-slate-400">No inbounds yet. Create your first one!</p>
          </div>
        ) : inbounds.map(ib => (
          <div
            key={ib.id}
            className="bg-surface rounded-2xl p-6 border border-slate-700/50 hover:border-primary/30 transition-all"
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="font-bold text-white text-lg">{ib.tag}</h3>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${protocolColors[ib.protocol]}`}>
                    {ib.protocol.toUpperCase()}
                  </span>
                  <span className="text-xs text-slate-400">:{ib.port}</span>
                </div>
              </div>
              <div className={`w-2 h-2 rounded-full ${ib.is_active ? 'bg-green-400' : 'bg-red-400'}`} />
            </div>

            <div className="space-y-2 mb-4 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">Network</span>
                <span className="text-slate-200 uppercase">{ib.network}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Security</span>
                <span className="text-slate-200 uppercase">{ib.security}</span>
              </div>
              {ib.sni && (
                <div className="flex justify-between">
                  <span className="text-slate-400">SNI</span>
                  <span className="text-slate-200 truncate ml-2">{ib.sni}</span>
                </div>
              )}
              <div className="flex justify-between items-center pt-2 border-t border-slate-700">
                <span className="text-slate-400 flex items-center gap-1">
                  <Users size={14} /> Clients
                </span>
                <span className="font-bold text-primary">{ib.clients_count || 0}</span>
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => navigate(`/inbounds/${ib.id}/clients`)}
                className="flex-1 py-2 rounded-lg bg-primary/20 text-primary hover:bg-primary/30 text-sm font-medium"
              >
                Clients
              </button>
              <button
                onClick={() => { setSelected(ib); setModalOpen(true) }}
                className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white"
              >
                <Pencil size={16} />
              </button>
              <button
                onClick={() => handleDelete(ib.id)}
                className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-red-400"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>

      <InboundModal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); setSelected(null) }}
        inbound={selected}
        onSaved={fetchInbounds}
      />
    </div>
  )
}
