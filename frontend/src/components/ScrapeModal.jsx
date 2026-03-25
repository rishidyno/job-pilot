/**
 * Portal selector modal — reusable across Dashboard and Jobs pages.
 */
import { useState } from 'react'

const ALL_PORTALS = ['linkedin', 'naukri', 'wellfound', 'instahyre', 'indeed', 'glassdoor']

export default function ScrapeModal({ onScrape, onClose }) {
  const [selected, setSelected] = useState(new Set(ALL_PORTALS))

  const toggle = (p) => setSelected(prev => {
    const next = new Set(prev)
    next.has(p) ? next.delete(p) : next.add(p)
    return next
  })

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white rounded-xl w-full max-w-sm p-6" onClick={e => e.stopPropagation()}>
        <h3 className="text-lg font-semibold text-gray-900 mb-1">Select Portals to Scrape</h3>
        <p className="text-xs text-gray-500 mb-4">Choose which job sites to scrape from</p>
        <div className="space-y-2 mb-5">
          {ALL_PORTALS.map(p => (
            <label key={p} className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input type="checkbox" checked={selected.has(p)} onChange={() => toggle(p)}
                className="w-4 h-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500" />
              <span className="text-sm text-gray-700 capitalize">{p}</span>
            </label>
          ))}
        </div>
        <div className="flex items-center justify-between">
          <button onClick={() => setSelected(prev => prev.size === ALL_PORTALS.length ? new Set() : new Set(ALL_PORTALS))}
            className="text-xs text-brand-600 hover:underline">
            {selected.size === ALL_PORTALS.length ? 'Deselect All' : 'Select All'}
          </button>
          <div className="flex gap-2">
            <button onClick={onClose}
              className="px-4 py-2 text-sm border border-gray-200 rounded-lg hover:bg-gray-50">Cancel</button>
            <button onClick={() => onScrape([...selected])} disabled={selected.size === 0}
              className="px-4 py-2 text-sm bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50">
              Scrape {selected.size} Portal{selected.size !== 1 ? 's' : ''}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
