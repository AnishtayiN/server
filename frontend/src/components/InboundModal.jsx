import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import api from '../api/client'
import toast from 'react-hot-toast'

const PROTOCOLS = ['vless', 'vmess', 'trojan', 'shadowsocks']
const NETWORKS = ['tcp', 'ws', 'grpc', 'http']
const SECURITIES = ['tls', 'reality', 'none']

export default function InboundModal({ isOpen, onClose, inbound, onSaved }) {
  const isEdit = !!inbound
  const [form, setForm] = useState({
    tag: '', protocol: 'vless', port: 443, network: 'tcp',
    security: 'tls', sni: '', flow: 'xtls-rprx-vision',
    settings: {}, stream_settings: {}
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (inbound) {
      setForm(inbound)
    } else {
      setForm({
        tag: '', protocol: 'vless', port: 443, network: 'tcp',
        security: 'tls', sni: '', flow: 'xtls-rprx-vision',
        settings: {}, stream_settings: {}
      })
    }
  }, [inbound, isOpen])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      if (isEdit) {
        await api.put(`/inbounds/${inbound.id}`, form)
        toast.success('Inbound updated')
      } else {
        await api.post('/inbounds', form)
        toast.success('Inbound created')
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
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-surface rounded-2xl w-full max-w-2xl border border-slate-700 my-8">
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <h3 className="text-xl font-bold text-white">
            {isEdit ? 'Edit Inbound' : 'Create Inbound'}
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5 max-h-[70vh] overflow-y-auto">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Tag</label>
              <input
                type="text"
                value={form.tag}
                onChange={(e) => setForm({ ...form, tag: e.target.value })}
                disabled={isEdit}
                placeholder="vless-reality"
                className="w-full bg-dark border border-slate-600 rounded-xl px-4 py-3 text-white disabled:opacity-50"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Port</label>
              <input
                type="number"
                value={form.port}
                onChange={(e) => setForm({ ...form, port: parseInt(e.target.value) })}
                className="w-full bg-dark border border-slate-600 rounded-xl px-4 py-3 text-white"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Protocol</label>
              <select
                value={form.protocol}
                onChange={(e) => setForm({ ...form, protocol: e.target.value })}
                className="w-full bg-dark border border-slate-600 rounded-xl px-4 py-3 text-white"
              >
                {PROTOCOLS.map(p => <option key={p} value={p}>{p.toUpperCase()}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Network</label>
              <select
                value={form.network}
                onChange={(e) => setForm({ ...form, network: e.target.value })}
                className="w-full bg-dark border border-slate-600 rounded-xl px-4 py-3 text-white"
              >
                {NETWORKS.map(n => <option key={n} value={n}>{n.toUpperCase()}</option>)}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Security</label>
              <select
                value={form.security}
                onChange={(e) => setForm({ ...form, security: e.target.value })}
                className="w-full bg-dark border border-slate-600 rounded-xl px-4 py-3 text-white"
              >
                {SECURITIES.map(s => <option key={s} value={s}>{s.toUpperCase()}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">SNI</label>
              <input
                type="text"
                value={form.sni}
                onChange={(e) => setForm({ ...form, sni: e.target.value })}
                placeholder="example.com"
                className="w-full bg-dark border border-slate-600 rounded-xl px-4 py-3 text-white"
              />
            </div>
          </div>

          {form.protocol === 'vless' && (
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Flow</label>
              <select
                value={form.flow || ''}
                onChange={(e) => setForm({ ...form, flow: e.target.value })}
                className="w-full bg-dark border border-slate-600 rounded-xl px-4 py-3 text-white"
              >
                <option value="">None</option>
                <option value="xtls-rprx-vision">xtls-rprx-vision</option>
                <option value="xtls-rprx-vision-udp443">xtls-rprx-vision-udp443</option>
              </select>
            </div>
          )}

          {form.network === 'ws' && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">WS Path</label>
                <input
                  type="text"
                  value={form.stream_settings?.path || ''}
                  onChange={(e) => setForm({
                    ...form,
                    stream_settings: { ...form.stream_settings, path: e.target.value }
                  })}
                  placeholder="/ws"
                  className="w-full bg-dark border border-slate-600 rounded-xl px-4 py-3 text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">WS Host</label>
                <input
                  type="text"
                  value={form.stream_settings?.host || ''}
                  onChange={(e) => setForm({
                    ...form,
                    stream_settings: { ...form.stream_settings, host: e.target.value }
                  })}
                  placeholder="example.com"
                  className="w-full bg-dark border border-slate-600 rounded-xl px-4 py-3 text-white"
                />
              </div>
            </div>
          )}

          {form.network === 'grpc' && (
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">gRPC Service Name</label>
              <input
                type="text"
                value={form.stream_settings?.service_name || ''}
                onChange={(e) => setForm({
                  ...form,
                  stream_settings: { ...form.stream_settings, service_name: e.target.value }
                })}
                placeholder="grpc"
                className="w-full bg-dark border border-slate-600 rounded-xl px-4 py-3 text-white"
              />
            </div>
          )}

          {form.security === 'reality' && (
            <div className="bg-dark/50 rounded-xl p-4 space-y-4">
              <h4 className="text-sm font-semibold text-primary">REALITY Settings</h4>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Public Key</label>
                <input
                  type="text"
                  value={form.settings?.public_key || ''}
                  onChange={(e) => setForm({
                    ...form,
                    settings: { ...form.settings, public_key: e.target.value }
                  })}
                  className="w-full bg-dark border border-slate-600 rounded-lg px-3 py-2 text-white font-mono text-xs"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Short ID</label>
                <input
                  type="text"
                  value={form.settings?.short_id || ''}
                  onChange={(e) => setForm({
                    ...form,
                    settings: { ...form.settings, short_id: e.target.value }
                  })}
                  className="w-full bg-dark border border-slate-600 rounded-lg px-3 py-2 text-white font-mono text-xs"
                />
              </div>
            </div>
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
