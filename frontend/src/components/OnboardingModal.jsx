/**
 * JOBPILOT — Onboarding Modal
 * Guides new users through setup after registration.
 */
import { useState } from 'react'
import { Rocket, FileText, Settings, Search, ArrowRight, Check, X } from 'lucide-react'

const STEPS = [
  {
    icon: Rocket,
    title: 'Welcome to JobPilot!',
    desc: 'Your AI-powered job hunting engine. Let\'s get you set up in 3 quick steps.',
    color: 'text-brand-600 dark:text-brand-400',
    bg: 'bg-brand-50 dark:bg-brand-950/30',
  },
  {
    icon: FileText,
    title: 'Add Your Resume',
    desc: 'Go to Resume Manager and paste your LaTeX resume. The AI uses this to tailor versions for each job.',
    color: 'text-indigo-600 dark:text-indigo-400',
    bg: 'bg-indigo-50 dark:bg-indigo-950/30',
    link: '/resumes',
    linkLabel: 'Go to Resumes',
  },
  {
    icon: Settings,
    title: 'Configure Your Profile',
    desc: 'Set your target roles, locations, and skills in Settings. Also edit the AI rules and candidate profile.',
    color: 'text-purple-600 dark:text-purple-400',
    bg: 'bg-purple-50 dark:bg-purple-950/30',
    link: '/settings',
    linkLabel: 'Go to Settings',
  },
  {
    icon: Search,
    title: 'Start Scraping Jobs',
    desc: 'Hit "Scrape Now" on the Dashboard to find jobs from LinkedIn, Naukri, Indeed, and more. Add portal credentials in .env for best results.',
    color: 'text-emerald-600 dark:text-emerald-400',
    bg: 'bg-emerald-50 dark:bg-emerald-950/30',
    link: '/',
    linkLabel: 'Go to Dashboard',
  },
]

export default function OnboardingModal({ onClose }) {
  const [step, setStep] = useState(0)
  const current = STEPS[step]
  const Icon = current.icon
  const isLast = step === STEPS.length - 1

  return (
    <div className="fixed inset-0 bg-black/50 z-[70] flex items-center justify-center p-4"
      role="dialog" aria-modal="true" aria-label="Welcome onboarding">
      <div className="bg-white dark:bg-surface-800 rounded-2xl w-full max-w-md overflow-hidden shadow-2xl">
        {/* Progress bar */}
        <div className="h-1 bg-gray-100 dark:bg-surface-700">
          <div className="h-full bg-brand-500 transition-all duration-500 ease-out"
            style={{ width: `${((step + 1) / STEPS.length) * 100}%` }} />
        </div>

        <div className="p-6 sm:p-8">
          {/* Close */}
          <div className="flex justify-end -mt-2 -mr-2 mb-2">
            <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-surface-700" aria-label="Skip onboarding">
              <X className="w-4 h-4 text-gray-400" />
            </button>
          </div>

          {/* Icon */}
          <div className={`w-14 h-14 rounded-2xl ${current.bg} flex items-center justify-center mx-auto mb-5`}>
            <Icon className={`w-7 h-7 ${current.color}`} />
          </div>

          {/* Content */}
          <h2 className="text-xl font-bold text-gray-900 dark:text-white text-center mb-2">{current.title}</h2>
          <p className="text-sm text-gray-500 dark:text-surface-400 text-center leading-relaxed max-w-xs mx-auto">{current.desc}</p>

          {/* Step dots */}
          <div className="flex items-center justify-center gap-1.5 mt-6 mb-6">
            {STEPS.map((_, i) => (
              <div key={i} className={`h-1.5 rounded-full transition-all duration-300 ${
                i === step ? 'w-6 bg-brand-500' : i < step ? 'w-1.5 bg-brand-300 dark:bg-brand-700' : 'w-1.5 bg-gray-200 dark:bg-surface-600'
              }`} />
            ))}
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            {step > 0 && (
              <button onClick={() => setStep(s => s - 1)}
                className="flex-1 py-2.5 text-sm border border-gray-200 dark:border-surface-600 rounded-lg hover:bg-gray-50 dark:hover:bg-surface-700 text-gray-600 dark:text-surface-300 font-medium">
                Back
              </button>
            )}
            <button onClick={() => isLast ? onClose() : setStep(s => s + 1)}
              className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-brand-600 text-white text-sm font-semibold rounded-lg hover:bg-brand-700 active:scale-[0.98] transition-transform">
              {isLast ? <><Check className="w-4 h-4" /> Get Started</> : <>Next <ArrowRight className="w-4 h-4" /></>}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
