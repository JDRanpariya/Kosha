import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
    'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors',
    {
        variants: {
            variant: {
                // Was: bg-primary text-primary-foreground — renders sage green
                default: 'border-transparent bg-parchment-deep text-ink-mid',
                secondary: 'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
                destructive: 'border-transparent bg-destructive text-destructive-foreground',
                outline: 'border-border text-ink-mid',
                // Add a sage variant for intentional accent use
                accent: 'border-transparent bg-sage-light text-sage-dark font-medium',
            },
        },
        defaultVariants: { variant: 'default' },
    }
)

export interface BadgeProps
    extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> { }

function Badge({ className, variant, ...props }: BadgeProps) {
    return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { Badge, badgeVariants }
