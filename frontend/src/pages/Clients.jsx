import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Plus, Pencil, Trash2, QrCode, Link2, ArrowLeft } from 'lucide-react'
import api from '../api/client'
import ClientModal from '../components/ClientModal'
import QRCodeModal from '../components/QRCodeModal'
import toast from 'react-hot-toast'

export default function Clients() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [inbound, setInbound] = useState(null)
  const [clients, setClients] = useState([])
  const [modalOpen, setModalOpen] = useState(false)
  const [qrOpen, setQrOpen] = useState(false)
  const [selected, setSelected] = useState(null)
  const [qrData, setQrData] = useState({ link: '', title: '' })
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    try {
      const [ibRes, clRes] = await Promise.all([
        api.get('/inbounds'),
        api.get(`/inbounds/${id}/clients`)
      ])
      const ib = ibRes.data.find(i => i.id === parseInt(id))
      setInbound(ib)
      setClients(clRes.data)
    } catch (err) {
      toast.error('Failed to load')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [id])

  const handleDelete = async (clientId) => {
    if (!confirm('Delete this client?')) return
    try {
      await api.delete(`/clients/${clientId}`)
      toast.success('Deleted')
      fetchData()
    } catch {
      toast.error('Failed')
    }
  }

  const handleShowQR = async (clientId, email) => {
    try {
      const res = await api.get(`/clients/${clientId}/links`)
      setQrData({ link: res.data.link, title: email })
      setQrOpen(true)
    } catch {
      toast.error('Failed to get link')
    }
  }

  const formatBytes = (bytes) => {
    if (!bytes) return '0 GB'
    return `${(bytes / 1024**3).toFixed(2)} GB`
  }

  const progressPercent = (used, total) => {
    if (!total) return 0
    return Math.min(100, (used / total) * 100)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/inbounds')}
          className="p-2 rounded-lg bg-surface border border-slate-700 hover:bg-slate-800"
        >
          <ArrowLeft size={20} />
        </button>
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-white">{inbound?.tag || 'Clients'}</h2>
          <p className="text-slate-400 text-sm mt-1">
            {inbound?.protocol.toUpperCase()} : {inbound?.port}
          </p>
        </div>
        <button
          onClick={() => { setSelected(null); setModalOpen(true) }}
          className="flex items-center gap-2 bg-primary hover:bg-indigo-600 text-white px-6 py-3 rounded-xl font-medium"
        >
          <Plus size={20} /> Add Client
        </button>
      </div>

      <div className="bg-surface rounded-2xl border border-slate-700/50 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-slate-800/50 text-slate-400 text-sm">
                <th className="px-6 py-4 text-left font-medium">Email</th>
                <th className="px-6 py-4 text-left font-medium">Traffic Used</th>
                <th className="px-6 py-4 text-left font-medium">Expires</th>
                <th className="px-6 py-4 text-left font-medium">Status</th>
                <th className="px-6 py-4 text-right font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {loading ? (
                <tr><td colSpan={5} className="px-6 py-12 text-center text-slate-400">Loading...</td></tr>
              ) : clients.length === 0 ? (
                <tr><td colSpan={5} className="px-6 py-12 text-center text-slate-400">No clients yet</td></tr>
              ) : clients.map(client => {
                const percent = progressPercent(client.used_traffic_bytes, client.traffic_limit_bytes)
                const expired = client.expiry_time && new Date(client.expiry_time) < new Date()
                
                return (
                  <tr key={client.id} className="hover:bg-slate-800/30">
                    <td className="px-6 py-4">
                      <div className="font-medium text-white">{client.email}</div>
                      <div className="text-xs text-slate-500 font-mono mt-1">
                        {client.uuid_str.slice(0, 8)}...
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-white">{formatBytes(client.used_traffic_bytes)}</div>
                      <div className="text-xs text-slate-400 mb-1">
                        / {formatBytes(client.traffic_limit_bytes)}
                      </div>
                      <div className="w-32 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${percent > 80 ? 'bg-red-500' : 'bg-primary'}`}
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-300">
                      {client.expiry_time ? new Date(client.expiry_time).toLocaleDateString() : 'Never'}
                    </td>
                    <td className="px-6 py-4">
                      {expired ? (
                        <span className="text-xs px-2 py-1 rounded-full bg-red-500/20 text-red-400">Expired</span>
                      ) : client.is_active ? (
                        <span className="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">Active</span>
                      ) : (
                        <span className="text-xs px-2 py-1 rounded-full bg-slate-500/20 text-slate-400">Disabled</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleShowQR(client.id, client.email)}
                          className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-primary"
                          title="Show QR"
                        >
                          <QrCode size={16} />
                        </button>
                        <button
                          onClick={async () => {
                            const res = await api.get(`/clients/${client.id}/links`)
                            await navigator.clipboard.writeText(res.data.link)
                            toast.success('Link copied')
                          }}
                          className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-primary"
                          title="Copy Link"
                        >
                          <Link2 size={16} />
                        </button>
                        <button
                          onClick={() => { setSelected(client); setModalOpen(true) }}
                          className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white"
                        >
                          <Pencil size={16} />
                        </button>
                        <button
                          onClick={() => handleDelete(client.id)}
                          className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-red-400"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      <ClientModal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); setSelected(null) }}
        client={selected}
        inboundId={parseInt(id)}
        inboundProtocol={inbound?.protocol}
        onSaved={fetchData}
      />

      <QRCodeModal
        isOpen={qrOpen}
        onClose={() => setQrOpen(false)}
        link={qrData.link}
        title={qrData.title}
      />
    </div>
  )
}
