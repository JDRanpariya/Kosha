import { useUIStore } from '@/stores/uiStore'
import { cn } from '@/lib/utils'

function Section({ title, children }: { title: string; children: React.ReactNode }) {
    return (
        <div className="mb-8">
            <h2 className="text-[10px] font-medium tracking-[0.12em] uppercase text-ink-faint mb-3">{title}</h2>
            <div className="card-kosha divide-y divide-border">{children}</div>
        </div>
    )
}

function SettingRow({ label, description, children }: { label: string; description?: string; children: React.ReactNode }) {
    return (
        <div className="flex items-center justify-between gap-6 px-4 py-3.5">
            <div className="min-w-0">
                <p className="text-[13px] text-ink">{label}</p>
                {description && <p className="text-[11px] text-ink-faint mt-0.5">{description}</p>}
            </div>
            <div className="shrink-0">{children}</div>
        </div>
    )
}

export function SettingsPage() {
    const { theme, toggleTheme } = useUIStore()

    return (
        <div className="px-5 pt-7 pb-16 max-w-xl">
            <div className="mb-7 fade-up">
                <p className="text-[9.5px] font-medium tracking-[0.15em] uppercase text-ink-faint mb-1">Preferences</p>
                <h1 className="font-serif text-[26px] font-normal text-ink">Settings</h1>
            </div>

            <Section title="Appearance">
                <SettingRow label="Theme" description="Warm light or warm dark — both designed for reading">
                    <select value={theme}
                        onChange={e => { if (e.target.value !== theme) toggleTheme() }}
                        className="h-8 px-2.5 rounded-md border border-border bg-parchment-mid text-[12px] text-ink outline-none focus:border-ink-faint transition-colors">
                        <option value="light">Light</option>
                        <option value="dark">Dark</option>
                    </select>
                </SettingRow>
            </Section>

            <div className="card-kosha px-4 py-4 opacity-60">
                <p className="text-[11px] font-medium text-ink-mid mb-1">Coming next</p>
                <p className="text-[11px] text-ink-faint">
                    Digest schedule, notification preferences, Obsidian export,
                    and a profile page showing what the AI has learned about your interests.
                </p>
            </div>
        </div>
    )
}
