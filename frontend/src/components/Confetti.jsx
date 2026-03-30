/**
 * JOBPILOT — Confetti burst for celebrations
 */
import { useEffect, useState } from 'react'

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#f43f5e']

export default function Confetti({ trigger }) {
  const [particles, setParticles] = useState([])

  useEffect(() => {
    if (!trigger) return
    const p = Array.from({ length: 30 }, (_, i) => ({
      id: i,
      x: 50 + (Math.random() - 0.5) * 60,
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
      delay: Math.random() * 0.3,
      duration: 0.8 + Math.random() * 0.6,
      size: 4 + Math.random() * 4,
      rotation: Math.random() * 360,
    }))
    setParticles(p)
    const timer = setTimeout(() => setParticles([]), 2000)
    return () => clearTimeout(timer)
  }, [trigger])

  if (!particles.length) return null

  return (
    <div className="fixed inset-0 pointer-events-none z-[100]">
      {particles.map(p => (
        <div key={p.id} className="absolute" style={{
          left: `${p.x}%`,
          top: '40%',
          width: p.size,
          height: p.size,
          backgroundColor: p.color,
          borderRadius: Math.random() > 0.5 ? '50%' : '2px',
          animation: `confetti-fall ${p.duration}s ease-out ${p.delay}s forwards`,
          transform: `rotate(${p.rotation}deg)`,
        }} />
      ))}
    </div>
  )
}
