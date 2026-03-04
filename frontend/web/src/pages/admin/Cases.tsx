import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { FileText } from 'lucide-react'

export default function Cases() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Cases / Audit</h1>
        <p className="text-muted-foreground mt-1">
          View triage cases and audit trail. Filter by date, severity, hospital.
        </p>
      </div>
      <Card className="border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Case list
          </CardTitle>
          <CardDescription>
            Case list and filters will go here. Connect to your admin/audit API when ready.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border border-dashed border-border/60 p-8 text-center text-sm text-muted-foreground">
            No cases loaded. Configure your audit API to fetch triage cases.
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
