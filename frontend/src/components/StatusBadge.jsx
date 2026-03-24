/**
 * JOBPILOT — StatusBadge Component
 * Colored pill showing job/application status.
 */

import { statusColor, capitalize } from '../utils/helpers'

export default function StatusBadge({ status }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColor(status)}`}>
      {capitalize(status)}
    </span>
  )
}
