import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import api from '../api/client'
import toast from 'react-hot-toast'

export default function ClientModal({ isOpen, onClose, client, inboundId, inboundProtocol, onSaved }) {
  const isEdit = !!client
  const [form, setForm] = useState({
    email: '', traffic_limit_gb: 0, expiry_days: 30,
    password: '', is_active: true, reset_traffic: false
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (client) {
      setForm({
        email: client.email,
        traffic_limit_gb: Math.floor(client.traffic_limit_bytes / 1024**3),
        expiry_days: 30,
        password: client.password || '',
        is_active: client.is_active,
        reset_traffic: false
      })
    } else {
      setForm({
        email: '', traffic_limit_gb: 0, expiry_days: 30,
        password: '', is_active: true, reset_traffic: false
      })
    }
  }, [client, isOpen])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      if (isEdit) {
        await api.put(`/clients/${client.id}`, {
          traffic_limit_gb: form.traffic_limit_gb,
          is_active: form.is_active,
          reset_traffic: form.reset_traffic
        })
        toast.success('Client updated')
      } else {
        await api.post(`/clients/inbound/${inboundId}`, {
          email: form.email,
          traffic_limit_gb: form.traffic_limit_gb,
          expiry_days: form.expiry_days,
          password: ['trojan', 'shadowsocks'].includes(inboundProtocol) ? form.password : undefined
        })
        toast.success('Client created')
      }
      onSaved()
      onClose()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-surface rounded-2xl w-full max-w-md border border-slate-700">
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <h3 className="text-xl font-bold text-white">
            {isEdit ? 'Edit Client' : 'Add Client'}
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Email</label>
            <input
              type="text"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              disabled={isEdit}
              placeholder="user@example.com"
              className="w-full bg-dark border border-slate-600 rounded-xl px-4 py-3 text-white disabled:opacity-50"
              required
            />
          </div>

          {['trojan', 'shadowsocks'].includes(inboundProtocol) && !isEdit && (
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Password</label>
              <input
                type="text"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                placeholder="Leave empty for auto-generate"
                className="w-full bg-dark border border-slate-600 rounded-xl px-4 py-3 text-white"
              />
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Traffic (GB)</label>
              <input
                type="number"
                min="0"
                value={form.traffic_limit_gb}
                onChange={(e) => setForm({ ...form, traffic_limit_gb: parseInt(e.target.value) || 0 })}
                className="w-full bg-dark border border-slate-600 rounded-xl px-4 py-3 text-white"
              />
              <p className="text-xs text-slate-500 mt-1">0 = unlimited</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                {isEdit ? 'Extend (days)' : 'Expiry (days)'}
              </label>
              <input
                type="number"
                min="1"
                value={form.expiry_days}
                onChange={(e) => setForm({ ...form, expiry_days: parseInt(e.target.value) || 30 })}
                disabled={isEdit}
                className="w-full bg-dark border border-slate-600 rounded-xl px-4 py-3 text-white disabled:opacity-50"
              />
            </div>
          </div>

          {isEdit && (
            <>
              <div className="flex items-center justify-between py-2">
                <span className="text-sm text-slate-300">Active</span>
                <button
                  type="button"
                  onClick={() => setForm({ ...form, is_active: !form.is_active })}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    form.is_active ? 'bg-green-500' : 'bg-slate-600'
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    form.is_active ? 'translate-x-6' : 'translate-x-1'
                  }`} />
                </button>
              </div>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.reset_traffic}
                  onChange={(e) => setForm({ ...form, reset_traffic: e.target.checked })}
                  className="w-4 h-4 rounded"
                />
                <span className="text-sm text-slate-300">Reset used traffic</span>
              </label>
            </>
          )}

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 rounded-xl border border-slate-600 text-slate-300 hover:bg-slate-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-3 rounded-xl bg-primary hover:bg-indigo-600 text-white font-medium disabled:opacity-50"
            >
              {loading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
