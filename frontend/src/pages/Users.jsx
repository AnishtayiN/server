import { useEffect, useState } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import { useStore } from '../store/useStore'
import UserModal from '../components/UserModal'
import api from '../api/client'
import toast from 'react-hot-toast'

export default function Users() {
  const { users, fetchUsers, loading } = useStore()
  const [modalOpen, setModalOpen] = useState(false)
  const [creating, setCreating] = useState(false)

  useEffect(() => { fetchUsers() }, [fetchUsers])

  const handleCreate = async (form) => {
    setCreating(true)
    try {
      await api.post('/users', form)
      toast.success('Admin created')
      setModalOpen(false)
      fetchUsers()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error')
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this admin?')) return
    try {
      await api.delete(`/users/${id}`)
      toast.success('Deleted')
      fetchUsers()
    } catch {
      toast.error('Failed to delete')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Admins</h2>
          <p className="text-slate-400 text-sm mt-1">Manage panel administrators</p>
        </div>
        <button
          onClick={() => setModalOpen(true)}
          className="flex items-center gap-2 bg-primary hover:bg-indigo-600 text-white px-6 py-3 rounded-xl font-medium"
        >
          <Plus size={20} /> New Admin
        </button>
      </div>

      <div className="bg-surface rounded-2xl border border-slate-700/50 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-slate-800/50 text-slate-400 text-sm">
                <th className="px-6 py-4 text-left font-medium">Username</th>
                <th className="px-6 py-4 text-left font-medium">Status</th>
                <th className="px-6 py-4 text-left font-medium">Created</th>
                <th className="px-6 py-4 text-right font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {loading ? (
                <tr><td colSpan={4} className="px-6 py-12 text-center text-slate-400">Loading...</td></tr>
              ) : users.length === 0 ? (
                <tr><td colSpan={4} className="px-6 py-12 text-center text-slate-400">No admins found</td></tr>
              ) : users.map(user => (
                <tr key={user.id} className="hover:bg-slate-800/30">
                  <td className="px-6 py-4 font-medium text-white">{user.username}</td>
                  <td className="px-6 py-4">
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      user.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                    }`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-300 text-sm">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleDelete(user.id)}
                      className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-red-400"
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <UserModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleCreate}
        loading={creating}
      />
    </div>
  )
}
