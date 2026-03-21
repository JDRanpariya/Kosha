import { useState } from 'react'
import { useUIStore } from '@/stores/uiStore'
import { cn } from '@/lib/utils'

// ── Section wrapper ───────────────────────────────────────────────────────

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-8">
      <h2 className="text-[10px] font-medium tracking-[0.12em] uppercase text-ink-faint mb-3">
        {title}
      </h2>
      <div className="card-kosha divide-y divide-border">
        {children}
      </div>
    </div>
  )
}

// ── Setting row ───────────────────────────────────────────────────────────

function SettingRow({
  label,
  description,
  children,
}: {
  label: string
  description?: string
  children: React.ReactNode
}) {
  return (
    <div className="flex items-center justify-between gap-6 px-4 py-3.5">
      <div className="min-w-0">
        <p className="text-[13px] text-ink">{label}</p>
        {description && (
          <p className="text-[11px] text-ink-faint mt-0.5">{description}</p>
        )}
      </div>
      <div className="shrink-0">{children}</div>
    </div>
  )
}

// ── Toggle ────────────────────────────────────────────────────────────────

function Toggle({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={cn(
        'relative w-9 h-5 rounded-full border transition-colors duration-200',
        checked
          ? 'bg-sage border-sage'
          : 'bg-parchment-deep border-border',
      )}
    >
      <span className={cn(
        'absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform duration-200',
        checked && 'translate-x-4',
      )} />
    </button>
  )
}

// ── Select ────────────────────────────────────────────────────────────────

function Select({
  value,
  options,
  onChange,
}: {
  value: string
  options: { value: string; label: string }[]
  onChange: (v: string) => void
}) {
  return (
    <select
      value={value}
      onChange={e => onChange(e.target.value)}
      className="h-8 px-2.5 rounded-md border border-border bg-parchment-mid text-[12px] text-ink outline-none focus:border-ink-faint transition-colors"
    >
      {options.map(o => (
        <option key={o.value} value={o.value}>{o.label}</option>
      ))}
    </select>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────

export function SettingsPage() {
  const { theme, toggleTheme } = useUIStore()

  // Local settings state — in Phase 2 these would be persisted to backend
  const [digestSchedule, setDigestSchedule] = useState('daily')
  const [digestTime, setDigestTime] = useState('08:00')
  const [obsidianPath, setObsidianPath] = useState('')
  const [obsidianEnabled, setObsidianEnabled] = useState(false)
  const [notifications, setNotifications] = useState(false)

  return (
    <div className="px-5 pt-7 pb-16 max-w-xl">

      <div className="mb-7 fade-up">
        <p className="text-[9.5px] font-medium tracking-[0.15em] uppercase text-ink-faint mb-1">
          Preferences
        </p>
        <h1 className="font-serif text-[26px] font-normal text-ink">
          Settings
        </h1>
      </div>

      {/* ── Appearance ── */}
      <Section title="Appearance">
        <SettingRow
          label="Theme"
          description="Warm light or warm dark — both designed for reading"
        >
          <Select
            value={theme}
            options={[
              { value: 'light', label: 'Light' },
              { value: 'dark',  label: 'Dark'  },
            ]}
            onChange={v => { if (v !== theme) toggleTheme() }}
          />
        </SettingRow>
      </Section>

      {/* ── Digest ── */}
      <Section title="Digest">
        <SettingRow
          label="Schedule"
          description="How often to compile a new digest from your sources"
        >
          <Select
            value={digestSchedule}
            options={[
              { value: 'daily',  label: 'Daily'  },
              { value: 'weekly', label: 'Weekly' },
            ]}
            onChange={setDigestSchedule}
          />
        </SettingRow>

        <SettingRow
          label="Delivery time"
          description="When the digest is ready each day"
        >
          <input
            type="time"
            value={digestTime}
            onChange={e => setDigestTime(e.target.value)}
            className="h-8 px-2.5 rounded-md border border-border bg-parchment-mid text-[12px] text-ink outline-none focus:border-ink-faint transition-colors"
          />
        </SettingRow>

        <SettingRow
          label="Notifications"
          description="Alert when a new digest is ready"
        >
          <Toggle checked={notifications} onChange={setNotifications} />
        </SettingRow>
      </Section>

      {/* ── Obsidian ── */}
      <Section title="Obsidian integration">
        <SettingRow
          label="Enable export"
          description="Save annotated items to your Obsidian vault"
        >
          <Toggle checked={obsidianEnabled} onChange={setObsidianEnabled} />
        </SettingRow>

        {obsidianEnabled && (
          <SettingRow
            label="Vault path"
            description="Folder where Kosha notes will be written"
          >
            <input
              type="text"
              value={obsidianPath}
              onChange={e => setObsidianPath(e.target.value)}
              placeholder="~/Documents/Obsidian/Inbox"
              className="w-52 h-8 px-2.5 rounded-md border border-border bg-parchment-mid text-[11px] text-ink placeholder:text-ink-faint outline-none focus:border-ink-faint transition-colors"
            />
          </SettingRow>
        )}
      </Section>

      {/* ── Phase 2 preview — honest placeholder ── */}
      <div className="card-kosha px-4 py-4 opacity-60">
        <p className="text-[11px] font-medium text-ink-mid mb-1">Coming in Phase 2</p>
        <p className="text-[11px] text-ink-faint">
          "My profile" — see what the AI has learned about your interests,
          correct its understanding, and explore how your curiosity has evolved over time.
        </p>
      </div>
    </div>
  )
}
