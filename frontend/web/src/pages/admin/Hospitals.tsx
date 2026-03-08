import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Building2 } from 'lucide-react'

export default function Hospitals() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Hospitals</h1>
        <p className="text-muted-foreground mt-1">
          Manage facilities, beds, and on-call specialists.
        </p>
      </div>
      <Card className="border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Facilities
          </CardTitle>
          <CardDescription>
            Edit capacity and specialist availability. Connect to your admin API when ready.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border border-dashed border-border/60 p-8 text-center text-sm text-muted-foreground">
            No hospitals loaded. Configure your admin API to list and edit facilities.
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
