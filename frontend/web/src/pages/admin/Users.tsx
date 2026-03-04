import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Users as UsersIcon } from 'lucide-react'

export default function Users() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Users</h1>
        <p className="text-muted-foreground mt-1">
          Manage healthcare workers and RMPs.
        </p>
      </div>
      <Card className="border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <UsersIcon className="h-5 w-5" />
            User list
          </CardTitle>
          <CardDescription>
            Invite, deactivate, and view activity. Connect to your admin API when ready.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border border-dashed border-border/60 p-8 text-center text-sm text-muted-foreground">
            No users loaded. Configure your admin API to fetch and manage users.
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
