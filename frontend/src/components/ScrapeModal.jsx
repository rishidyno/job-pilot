/**
 * Portal selector modal — dark mode, responsive.
 */
import { useState, useEffect, useRef } from 'react'

const ALL_PORTALS = ['linkedin', 'indeed', 'glassdoor', 'google', 'naukri']

export default function ScrapeModal({ onScrape, onClose }) {
  const [selected, setSelected] = useState(new Set(ALL_PORTALS))
  const modalRef = useRef(null)

  useEffect(() => {
    const handleKey = (e) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', handleKey)
    modalRef.current?.focus()
    return () => document.removeEventListener('keydown', handleKey)
  }, [onClose])

  const toggle = (p) => setSelected(prev => {
    const next = new Set(prev)
    next.has(p) ? next.delete(p) : next.add(p)
    return next
  })

  return (
    <div className="fixed inset-0 glass-overlay z-50 flex items-end sm:items-center justify-center p-0 sm:p-4"
      onClick={onClose} role="dialog" aria-modal="true" aria-label="Select portals to scrape">
      <div ref={modalRef} tabIndex={-1}
        className="bg-white dark:bg-surface-800 rounded-t-2xl sm:rounded-xl w-full sm:max-w-sm p-5 sm:p-6 outline-none"
        onClick={e => e.stopPropagation()}>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">Select Portals</h3>
        <p className="text-xs text-gray-500 dark:text-surface-400 mb-4">Choose which job sites to scrape</p>
        <div className="space-y-1 mb-5">
          {ALL_PORTALS.map(p => (
            <label key={p} className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-50 dark:hover:bg-surface-700 cursor-pointer">
              <input type="checkbox" checked={selected.has(p)} onChange={() => toggle(p)}
                className="w-4 h-4 rounded border-gray-300 dark:border-surface-600 text-brand-600 focus:ring-brand-500 dark:bg-surface-700" />
              <span className="text-sm text-gray-700 dark:text-surface-300 capitalize">{p}</span>
            </label>
          ))}
        </div>
        <div className="flex items-center justify-between">
          <button onClick={() => setSelected(prev => prev.size === ALL_PORTALS.length ? new Set() : new Set(ALL_PORTALS))}
            className="text-xs text-brand-600 dark:text-brand-400 hover:underline">
            {selected.size === ALL_PORTALS.length ? 'Deselect All' : 'Select All'}
          </button>
          <div className="flex gap-2">
            <button onClick={onClose}
              className="px-4 py-2 text-sm border border-gray-200 dark:border-surface-600 rounded-lg hover:bg-gray-50 dark:hover:bg-surface-700 text-gray-700 dark:text-surface-300">
              Cancel
            </button>
            <button onClick={() => onScrape([...selected])} disabled={selected.size === 0}
              className="px-4 py-2 text-sm bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 font-medium">
              Scrape ({selected.size})
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
