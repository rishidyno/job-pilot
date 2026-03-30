/**
 * JOBPILOT — Public Landing Page
 * Animated homepage with floating orbs, scroll reveals, glassmorphism.
 */
import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Rocket, Search, FileText, BarChart3, Briefcase, Zap, Shield, Github, Linkedin, ArrowRight, ChevronDown } from 'lucide-react'

/* ── Scroll-triggered fade-in ── */
function Reveal({ children, className = '', delay = 0 }) {
  const ref = useRef(null)
  const [visible, setVisible] = useState(false)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setVisible(true); obs.disconnect() } }, { threshold: 0.15 })
    obs.observe(el)
    return () => obs.disconnect()
  }, [])
  return (
    <div ref={ref} className={`transition-all duration-700 ease-out ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'} ${className}`}
      style={{ transitionDelay: `${delay}ms` }}>
      {children}
    </div>
  )
}

/* ── Animated counter ── */
function Counter({ target, suffix = '' }) {
  const [count, setCount] = useState(0)
  const ref = useRef(null)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const obs = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) {
        let start = 0
        const step = Math.max(1, Math.floor(target / 40))
        const timer = setInterval(() => { start += step; if (start >= target) { setCount(target); clearInterval(timer) } else setCount(start) }, 30)
        obs.disconnect()
      }
    }, { threshold: 0.5 })
    obs.observe(el)
    return () => obs.disconnect()
  }, [target])
  return <span ref={ref}>{count}{suffix}</span>
}

/* ── Typing effect ── */
function TypeWriter({ words, className }) {
  const [idx, setIdx] = useState(0)
  const [text, setText] = useState('')
  const [deleting, setDeleting] = useState(false)
  useEffect(() => {
    const word = words[idx % words.length]
    const timer = setTimeout(() => {
      if (!deleting) {
        setText(word.slice(0, text.length + 1))
        if (text.length + 1 === word.length) setTimeout(() => setDeleting(true), 1500)
      } else {
        setText(word.slice(0, text.length - 1))
        if (text.length === 0) { setDeleting(false); setIdx(i => i + 1) }
      }
    }, deleting ? 40 : 80)
    return () => clearTimeout(timer)
  }, [text, deleting, idx, words])
  return <span className={className}>{text}<span className="animate-pulse">|</span></span>
}

const FEATURES = [
  { icon: Search, title: 'Multi-Portal Scraping', desc: 'LinkedIn, Indeed, Glassdoor, Google Jobs, Naukri — one click, no login needed.', color: 'from-blue-500 to-cyan-400' },
  { icon: FileText, title: 'AI Resume Tailoring', desc: 'Your LaTeX resume rewritten for each job — truthful, ATS-optimized, one page.', color: 'from-purple-500 to-pink-400' },
  { icon: BarChart3, title: 'Smart Job Matching', desc: 'AI scores every job against your profile. Skill match highlighting built in.', color: 'from-amber-500 to-orange-400' },
  { icon: Briefcase, title: 'Application Tracking', desc: 'Kanban board, status updates, timeline — from scrape to offer.', color: 'from-emerald-500 to-teal-400' },
  { icon: Zap, title: 'Keyboard-First UX', desc: '6 themes, keyboard shortcuts, dark mode, responsive — built for power users.', color: 'from-rose-500 to-red-400' },
  { icon: Shield, title: 'Self-Hosted & Private', desc: 'Your data stays on your machine. No third-party analytics. MIT licensed.', color: 'from-indigo-500 to-violet-400' },
]

const STEPS = [
  { num: '01', title: 'Scrape', desc: 'Pull jobs from 5+ portals with smart keyword expansion' },
  { num: '02', title: 'Tailor', desc: 'AI rewrites your resume for each job description' },
  { num: '03', title: 'Track', desc: 'Kanban board tracks every application to offer' },
]

const STATS = [
  { value: 5, suffix: '+', label: 'Job Portals' },
  { value: 6, suffix: '', label: 'Themes' },
  { value: 35, suffix: '+', label: 'API Endpoints' },
  { value: 100, suffix: '%', label: 'Open Source' },
]

export default function Home() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white overflow-x-hidden">

      {/* ══════ HERO ══════ */}
      <section className="relative min-h-screen flex flex-col items-center justify-center px-6 py-20">
        {/* Floating gradient orbs */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute w-[600px] h-[600px] -top-40 -left-40 bg-blue-600/20 rounded-full blur-[120px] animate-float-slow" />
          <div className="absolute w-[500px] h-[500px] -bottom-20 -right-20 bg-purple-600/20 rounded-full blur-[100px] animate-float-medium" />
          <div className="absolute w-[300px] h-[300px] top-1/3 right-1/4 bg-emerald-600/10 rounded-full blur-[80px] animate-float-fast" />
        </div>

        {/* Content */}
        <div className="relative z-10 text-center max-w-3xl mx-auto">
          <div className="flex items-center justify-center gap-2.5 mb-6 animate-fade-in">
            <Rocket className="w-10 h-10 text-blue-400" />
            <span className="text-3xl sm:text-4xl font-bold">
              Job<span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Pilot</span>
            </span>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-bold leading-tight mb-6 animate-fade-in-up">
            <span className="bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
              Your AI-Powered
            </span>
            <br />
            <TypeWriter words={['Job Hunting Copilot', 'Resume Tailor', 'Application Tracker', 'Career Autopilot']} className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent" />
          </h1>

          <p className="text-lg sm:text-xl text-gray-400 max-w-xl mx-auto mb-10 animate-fade-in-up-delay">
            Scrape jobs from 5+ portals. Tailor your resume with AI. Track every application. All from one dashboard.
          </p>

          <div className="flex items-center justify-center gap-4 animate-fade-in-up-delay-2">
            <button onClick={() => navigate('/login')}
              className="group px-8 py-3.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-blue-500/25 transition-all duration-300 hover:scale-105 active:scale-95 flex items-center gap-2">
              Get Started <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
            <a href="https://github.com/rishidyno/job-pilot" target="_blank" rel="noopener noreferrer"
              className="px-6 py-3.5 border border-gray-700 text-gray-300 font-medium rounded-xl hover:border-gray-500 hover:text-white transition-all duration-300 flex items-center gap-2">
              <Github className="w-4 h-4" /> GitHub
            </a>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 animate-bounce">
          <ChevronDown className="w-6 h-6 text-gray-600" />
        </div>
      </section>

      {/* ══════ FEATURES ══════ */}
      <section className="relative px-6 py-24 max-w-6xl mx-auto">
        <Reveal>
          <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4">
            Everything you need to <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">land your next role</span>
          </h2>
          <p className="text-gray-400 text-center max-w-lg mx-auto mb-16">Built for developers who want to automate the boring parts of job hunting.</p>
        </Reveal>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {FEATURES.map((f, i) => (
            <Reveal key={f.title} delay={i * 100}>
              <div className="group relative p-6 rounded-2xl border border-gray-800/50 bg-gray-900/30 backdrop-blur-sm hover:border-gray-700 hover:bg-gray-800/40 transition-all duration-500 hover:-translate-y-1 hover:shadow-xl hover:shadow-black/20">
                <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                  <f.icon className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-base font-semibold text-white mb-2">{f.title}</h3>
                <p className="text-sm text-gray-400 leading-relaxed">{f.desc}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ══════ HOW IT WORKS ══════ */}
      <section className="px-6 py-24 max-w-4xl mx-auto">
        <Reveal>
          <h2 className="text-3xl sm:text-4xl font-bold text-center mb-16">
            Three steps to <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">autopilot</span>
          </h2>
        </Reveal>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
          {STEPS.map((s, i) => (
            <Reveal key={s.num} delay={i * 150}>
              <div className="text-center">
                <div className="text-5xl font-black bg-gradient-to-b from-gray-600 to-gray-800 bg-clip-text text-transparent mb-4">{s.num}</div>
                <h3 className="text-xl font-bold text-white mb-2">{s.title}</h3>
                <p className="text-sm text-gray-400">{s.desc}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ══════ STATS ══════ */}
      <section className="px-6 py-20">
        <div className="max-w-4xl mx-auto grid grid-cols-2 sm:grid-cols-4 gap-8">
          {STATS.map((s, i) => (
            <Reveal key={s.label} delay={i * 100}>
              <div className="text-center">
                <div className="text-4xl sm:text-5xl font-black text-white mb-1">
                  <Counter target={s.value} suffix={s.suffix} />
                </div>
                <p className="text-sm text-gray-500">{s.label}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ══════ BUILT BY ══════ */}
      <section className="px-6 py-24">
        <Reveal>
          <div className="max-w-lg mx-auto text-center">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mx-auto mb-6 text-3xl font-bold">
              R
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Built by Rishi Raj</h2>
            <p className="text-gray-400 mb-6">SDE-1 at Amazon · IIIT Lucknow · Because job hunting should be automated.</p>
            <div className="flex items-center justify-center gap-3">
              <a href="https://github.com/rishidyno/" target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-2 px-5 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-sm text-gray-300 hover:text-white hover:border-gray-500 transition-all duration-300 hover:scale-105">
                <Github className="w-4 h-4" /> GitHub
              </a>
              <a href="https://www.linkedin.com/in/rishidyno/" target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-2 px-5 py-2.5 bg-[#0a66c2]/10 border border-[#0a66c2]/30 rounded-xl text-sm text-blue-400 hover:text-blue-300 hover:border-[#0a66c2]/50 transition-all duration-300 hover:scale-105">
                <Linkedin className="w-4 h-4" /> LinkedIn
              </a>
            </div>
          </div>
        </Reveal>
      </section>

      {/* ══════ CTA FOOTER ══════ */}
      <section className="px-6 py-24">
        <Reveal>
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Ready to <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">automate</span> your job search?
            </h2>
            <p className="text-gray-400 mb-8">Free. Open source. Self-hosted. Your data stays yours.</p>
            <button onClick={() => navigate('/login')}
              className="group px-10 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl text-lg hover:shadow-lg hover:shadow-blue-500/25 transition-all duration-300 hover:scale-105 active:scale-95 flex items-center gap-2 mx-auto">
              Create Free Account <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </Reveal>
      </section>

      {/* ══════ FOOTER ══════ */}
      <footer className="border-t border-gray-800/50 px-6 py-8">
        <div className="max-w-4xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <Rocket className="w-4 h-4" />
            <span>JobPilot — MIT License</span>
          </div>
          <div className="flex items-center gap-4">
            <a href="https://github.com/rishidyno/job-pilot" target="_blank" rel="noopener noreferrer" className="hover:text-gray-400 transition-colors">GitHub</a>
            <a href="https://www.linkedin.com/in/rishidyno/" target="_blank" rel="noopener noreferrer" className="hover:text-gray-400 transition-colors">LinkedIn</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
