import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileText, Users, Building2 } from 'lucide-react'

const stats = [
  { label: 'Cases today', value: '—', icon: FileText, desc: 'Triage assessments' },
  { label: 'Healthcare workers', value: '—', icon: Users, desc: 'Active RMPs' },
  { label: 'Hospitals', value: '—', icon: Building2, desc: 'Registered facilities' },
]

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          Overview of cases, users, and hospitals.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {stats.map(({ label, value, icon: Icon, desc }) => (
          <Card key={label} className="border-border/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {label}
              </CardTitle>
              <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{value}</div>
              <p className="text-xs text-muted-foreground mt-1">{desc}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
