/**
 * JOBPILOT — Keyboard Shortcuts
 * Global keyboard shortcuts with help modal.
 */
import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { X } from 'lucide-react'

const SHORTCUTS = [
  { keys: ['g', 'd'], label: 'Go to Dashboard', action: 'nav:/' },
  { keys: ['g', 'j'], label: 'Go to Jobs', action: 'nav:/jobs' },
  { keys: ['g', 'a'], label: 'Go to Applications', action: 'nav:/applications' },
  { keys: ['g', 'r'], label: 'Go to Resumes', action: 'nav:/resumes' },
  { keys: ['g', 's'], label: 'Go to Settings', action: 'nav:/settings' },
  { keys: ['/'], label: 'Focus search', action: 'focus:search' },
  { keys: ['?'], label: 'Show shortcuts', action: 'help' },
  { keys: ['Esc'], label: 'Close modal / clear', action: 'escape' },
]

export function useKeyboardShortcuts() {
  const navigate = useNavigate()
  const [showHelp, setShowHelp] = useState(false)
  // `pending` tracks the first key of a two-key chord (e.g. 'g' in g+d).
  // After pressing 'g', we wait up to 1 second for a second key. If no second
  // key arrives within 1s, pending resets to null (the setTimeout clears it).
  const [pending, setPending] = useState(null)

  const handleKey = useCallback((e) => {
    // Don't trigger shortcuts while the user is typing in a form field
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return

    const key = e.key

    if (key === '?') { e.preventDefault(); setShowHelp(true); return }

    // ── Two-key chord: g → d/j/a/r/s ──
    // When pending='g', the next keypress completes the chord and navigates.
    if (pending === 'g') {
      setPending(null)
      const routes = { d: '/dashboard', j: '/jobs', a: '/applications', r: '/resumes', s: '/settings' }
      if (routes[key]) { e.preventDefault(); navigate(routes[key]) }
      return
    }

    if (key === 'g') {
      setPending('g')
      // Auto-cancel the chord if no second key arrives within 1 second
      setTimeout(() => setPending(null), 1000)
      return
    }

    if (key === '/') {
      e.preventDefault()
      document.querySelector('[aria-label="Search jobs"]')?.focus()
    }
  }, [pending, navigate])

  useEffect(() => {
    document.addEventListener('keydown', handleKey)
    return () => document.removeEventListener('keydown', handleKey)
  }, [handleKey])

  return { showHelp, setShowHelp }
}

export function ShortcutsHelp({ onClose }) {
  useEffect(() => {
    const h = (e) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', h)
    return () => document.removeEventListener('keydown', h)
  }, [onClose])

  return (
    <div className="fixed inset-0 bg-black/40 z-[70] flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white dark:bg-surface-800 rounded-xl w-full max-w-sm p-5 shadow-2xl" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white">Keyboard Shortcuts</h2>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-surface-700"><X className="w-4 h-4 text-gray-400" /></button>
        </div>
        <div className="space-y-1.5">
          {SHORTCUTS.map(s => (
            <div key={s.label} className="flex items-center justify-between py-1.5">
              <span className="text-sm text-gray-600 dark:text-surface-300">{s.label}</span>
              <div className="flex gap-1">
                {s.keys.map(k => (
                  <kbd key={k} className="px-2 py-0.5 bg-gray-100 dark:bg-surface-700 text-gray-700 dark:text-surface-300 text-xs font-mono rounded border border-gray-200 dark:border-surface-600">{k}</kbd>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
