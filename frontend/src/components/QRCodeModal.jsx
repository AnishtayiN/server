import { QRCodeSVG } from 'qrcode.react'
import { X, Copy, Check } from 'lucide-react'
import { useState } from 'react'
import toast from 'react-hot-toast'

export default function QRCodeModal({ isOpen, onClose, link, title }) {
  const [copied, setCopied] = useState(false)

  if (!isOpen) return null

  const handleCopy = async () => {
    await navigator.clipboard.writeText(link)
    setCopied(true)
    toast.success('Copied to clipboard')
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-surface rounded-2xl p-8 w-full max-w-md border border-slate-700 shadow-2xl">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-white">{title}</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        <div className="bg-white p-6 rounded-2xl flex items-center justify-center mb-6">
          <QRCodeSVG value={link} size={240} level="H" />
        </div>

        <div className="relative">
          <input
            type="text"
            value={link}
            readOnly
            className="w-full bg-dark border border-slate-600 rounded-xl px-4 py-3 pr-12 text-sm text-slate-300 font-mono"
          />
          <button
            onClick={handleCopy}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
          >
            {copied ? <Check size={18} className="text-green-400" /> : <Copy size={18} />}
          </button>
        </div>
      </div>
    </div>
  )
}
