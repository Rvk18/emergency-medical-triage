# MedTriage AI — Admin Web App

Admin dashboard only. Healthcare worker and user (patient) flows live on the **mobile app** (`frontend/mobile-android`).

## Stack

- React 18 + TypeScript
- Vite
- React Router 6
- **Tailwind CSS** + **shadcn/ui** (from `.agents` stitch/shadcn-ui skill): Button, Card, Input, Label; Lucide icons

## Run

```bash
npm install
npm run dev
```

Open http://localhost:3000 — sign in (any email/password for demo) to reach the admin shell.

## Admin sections (placeholders)

- **Dashboard** — Overview (cases today, users, hospitals)
- **Users** — Healthcare workers / RMPs (list, invite, deactivate)
- **Hospitals** — Facilities, beds, specialists
- **Cases / Audit** — Triage cases, filters, audit trail
- **Settings** — App config, feature flags

Wire these to your admin API when ready.
