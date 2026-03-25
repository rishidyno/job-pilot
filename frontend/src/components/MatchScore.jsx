/**
 * JOBPILOT — MatchScore Component
 * Circular progress ring with dark mode.
 */
import { scoreColor } from '../utils/helpers'

export default function MatchScore({ score, size = 48 }) {
  const radius = (size - 6) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - ((score || 0) / 100) * circumference
  const colors = scoreColor(score)
  // Extract just the text color class (first class)
  const textClass = colors.split(' ').filter(c => c.startsWith('text-')).join(' ')

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke="currentColor"
          className="text-gray-200 dark:text-surface-700" strokeWidth="3" />
        <circle cx={size/2} cy={size/2} r={radius} fill="none" strokeWidth="3" strokeLinecap="round"
          stroke="currentColor" strokeDasharray={circumference} strokeDashoffset={offset}
          className={`score-ring ${textClass}`} />
      </svg>
      <span className={`absolute text-xs font-bold ${textClass}`}>
        {score ?? '?'}
      </span>
    </div>
  )
}
