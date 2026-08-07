import { useState } from 'react'
import { Save, Server, Shield, Globe } from 'lucide-react'

export default function Settings() {
  const [settings, setSettings] = useState({
    domain: '', panel_path: '', reality_public_key: '', telegram_bot_token: ''
  })
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Settings</h2>
        <p className="text-slate-400 text-sm mt-1">Configure your proxy server</p>
      </div>

      <div className="bg-surface rounded-2xl p-6 border border-slate-700/50">
        <div className="flex items-center gap-3 mb-6">
          <Server className="text-primary" size={22} />
          <h3 className="text-lg font-semibold text-white">Server Settings</h3>
        </div>

        <div className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Domain</label>
            <input
              type="text"
              value={settings.domain}
              onChange={(e) => setSettings({ ...settings, domain: e.target.value })}
              placeholder="example.com"
              className="w-full bg-dark border border-slate-600 rounded-xl px-4 py-3 text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Panel Secret Path</label>
            <input
              type="text"
              value={settings.panel_path}
              onChange={(e) => setSettings({ ...settings, panel_path: e.target.value })}
              placeholder="/p-abc123/"
              className="w-full bg-dark border border-slate-600 rounded-xl px-4 py-3 text-white"
            />
          </div>
        </div>
      </div>

      <div className="bg-surface rounded-2xl p-6 border border-slate-700/50">
        <div className="flex items-center gap-3 mb-6">
          <Shield className="text-green-400" size={22} />
          <h3 className="text-lg font-semibold text-white">Security</h3>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">REALITY Public Key</label>
          <input
            type="text"
            value={settings.reality_public_key}
            onChange={(e) => setSettings({ ...settings, reality_public_key: e.target.value })}
            placeholder="pbk..."
            className="w-full bg-dark border border-slate-600 rounded-xl px-4 py-3 text-white font-mono text-sm"
          />
        </div>
      </div>

      <div className="bg-surface rounded-2xl p-6 border border-slate-700/50">
        <div className="flex items-center gap-3 mb-6">
          <Globe className="text-purple-400" size={22} />
          <h3 className="text-lg font-semibold text-white">Integrations</h3>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Telegram Bot Token</label>
          <input
            type="password"
            value={settings.telegram_bot_token}
            onChange={(e) => setSettings({ ...settings, telegram_bot_token: e.target.value })}
            placeholder="123456789:ABC..."
            className="w-full bg-dark border border-slate-600 rounded-xl px-4 py-3 text-white"
          />
        </div>
      </div>

      <button
        onClick={handleSave}
        className="flex items-center gap-2 bg-primary hover:bg-indigo-600 text-white px-8 py-3 rounded-xl font-medium"
      >
        <Save size={20} />
        {saved ? 'Saved!' : 'Save Settings'}
      </button>
    </div>
  )
}
