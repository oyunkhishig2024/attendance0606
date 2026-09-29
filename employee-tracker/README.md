# Employee Tracker

Implementation of `Employee_Tracker_Specification_v3.pdf`, scoped to the
**pivotal vertical slice** the spec itself recommends building first
(§11.1/§11.2, milestones M0–M2 plus most of M3): tenancy + RBAC, branch
geofences, the geofence check-in loop, scheduling, absence-reason logging,
and attendance review, with the mandatory tenant-isolation gate green.

The full spec is a 16-week, two-engineer build (a multi-tenant SaaS backend
plus a native iOS/Android app with anti-fraud, consent PDFs, and platform
administration). That can't be delivered in one sitting, and this
environment has no Android/iOS device, simulator, or App Store access to
validate a native build against. What follows is what's actually built,
verified, and what's explicitly deferred.

## What's built

### Backend (`backend/`) — FastAPI + MongoDB (Motor)

- Middleware chain per spec §5.8: request_id → CORS → rate_limit → auth →
  role_gate → tenant_scope → handler → audit_write.
- Auth: signup (creates org + Admin + default "Стандарт" schedule), login,
  `/auth/me`, change-password, delete-account (Apple compliance path).
  bcrypt cost 12, JWT HS256, 12h lifetime.
- Tenant CRUD: users, locations (branches, soft-delete), employees, shift
  templates (schedules, with activation toggle + affected-employee count +
  default-schedule delete protection), holidays.
- **The pivotal geofence check-in loop** (`app/services/checkin.py`):
  server-recomputed Haversine distance, schedule resolution hierarchy
  (Employee → Department → Branch → Org default), holiday/non-workday `off`
  status, idempotent one-check-in-per-day, stale-capture rejection, and
  anti-fraud flagging (device fingerprint mismatch, mock-location flag) —
  flags, never blocks, per spec §8.3.
- Public surface: `/public/employee/{token}`, `/public/checkin/{token}`,
  `/public/consent/{token}` — opaque tokens, rate-limited, `Cache-Control:
  no-store`.
- Attendance list with filters, `/reports/org-day` summary.
- **Absence-reason logging** (`app/routers/reasons.py`, `app/reasons_catalog.py`):
  the 15 preset Mongolian reason types (§1.2 item 9 — the spec names the
  capability but doesn't enumerate them; these are a reasonable generic HR
  set), multi-employee/date-range writes (one `reason_logs` row per
  employee spanning the range), and per-day attendance status flipped to
  `reason` **without** clobbering an existing check-in's time/distance
  (§3.5) — or a fresh `reason` record created if the employee hadn't
  checked in at all that day.
- **Employee month grid** (`app/services/month_grid.py`,
  `GET /employees/{id}/month-grid`) — spec §4.5's `employee_month_grid`
  derived read model: assembles attendance + holidays + resolved schedule
  so every day in a month is explained (`off`/holiday, `off`/rest day,
  `absent` for a past no-show, `pending` for today/future) rather than
  appearing as a gap.
- Platform (SystemAdmin): organization provisioning/suspend/reactivate,
  aggregate-only analytics, audit logs.
- Error shape, RBAC, tenant isolation, and account-state flags (`disabled`,
  `must_change_password`, org `suspended`) match spec §2 and §5.1 exactly.

**Tests** (`backend/tests/`, 36 passing): the **mandatory tenant-isolation
gate** (§7.4 — two orgs, every id-addressed route, id substitution, never a
403/404-violating leak), the **role matrix** (§7.5 — Manager read-only
everywhere, HR denied on tenant-user writes and the default schedule,
tenant roles 403 on `/platform/*`, SystemAdmin 403 on tenant routes), the
highest-value unit tests from §7.2 (Haversine boundary behaviour at exactly
the radius, status resolution at exactly `shift_start + grace_minutes`,
holiday/non-workday handling, all four schedule precedence combinations
plus the deactivation fallback), reason-logging behaviour (role gating,
invalid reason key rejected, check-in preservation), and the month-grid's
four day-classification cases.

Writing these tests caught two real bugs before they shipped: `DELETE
/users/{id}` and `DELETE /holidays/{id}` returned `{"ok": true}` for another
tenant's id instead of 404 (no data leaked, but wrong status), and Manager
was wrongly denied read access to `/shifts` and `/holidays` (spec §2.2 grants
Manager `R`; the route only allowed Admin/HR). Both are fixed.

Run it:
```
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest                      # 36 passed
uvicorn app.main:app --reload   # MONGO_URL defaults to an in-process mongomock;
                                 # set a real MONGO_URL in .env for production
```

### Mobile (`mobile/`) — Expo Router / React Native

Matching spec §9/§10's design tokens and file layout: `theme.ts`
(Blueberry `#243b8f` / Cream Soda `#fff0c9`), `login`, `signup`,
`change-password`, a two-tab bottom bar (Хяналт/Ирц — Staff/Analytics/More
are deferred, see below), the dashboard (`(app)/index.tsx`, reading
`/reports/org-day`), and the two public flows — `consent/[token].tsx` and
**`checkin/[token].tsx`**, which implements the full permission lifecycle
from spec §8.1/§8.2 (rationale → foreground one-shot `Accuracy.High` fix →
accuracy gate with retry → server-authoritative result, never a generic
"failed").

Also now built: the **attendance-review screen** (`(app)/attendance.tsx` —
date navigator, status filter chips including "Флагтай", a list joined
against the employees cache for display names), the **employee detail
screen** (`employee/[id].tsx` — a real 7-column month grid coloured by
`lib/status.ts`, month stepper, flag markers), and the **reason-logging
form** (`reasons/log.tsx` — reason-type chips from the 15-item catalogue,
a date range, multi-employee selection via `EmployeeMultiSelect`,
preselecting the employee when opened from their detail page). Both new
screens are gated behind `useRole().can("employees.write")` for the
write action, matching Manager's read-only capability matrix row.

`npm install` succeeds and `npx tsc --noEmit` is clean. It has **not** been
run on a device, simulator, or `expo start` — there's no Android SDK, iOS
toolchain, or display in this environment, and `expo install`'s
compatibility check is blocked by this container's network policy (only
`registry.npmjs.org` is reachable, not `exp.host`). Treat this as a
type-checked scaffold, not a runtime-verified app.

## Deferred (out of this slice)

Everything the spec places at M4 and later, or that needs a device/store
account to validate meaningfully:

- **Rest of M3**: the "why this status?" explainer surfaced inline on a
  status pill (the month grid's `explanation` field already carries the
  data — `holiday`/`rest_day`/`pending` — it's just not rendered as
  human-readable copy in the UI yet); the `staff.tsx`/`analytics.tsx` tabs.
- **M4**: consent PDF generation (ReportLab/svglib), QR rendering/scanning,
  impossible-travel heuristic, flagged-review queue UI.
- **M5**: platform admin UI screens (the API routes exist; there's no
  `(platform)/` app yet).
- **M6**: E2E suite (Detox/Maestro), device matrix pass, privacy manifest /
  Data Safety form, performance pass — all require real devices.
- Any actual Android/iOS build (APK/AAB/IPA) — needs the Android SDK and a
  macOS+Xcode toolchain this environment doesn't have.

## Assumptions and deviations worth flagging

- `employees.work_days[]` (a per-employee override) is applied as an
  override of which days count as a workday for status resolution; the
  resolved schedule's own `start_time`/`grace_minutes` still govern timing.
  The spec lists the field but doesn't fully specify its interaction with
  schedule resolution.
- §5.5's table shows only Admin/HR columns for `/shifts` and `/holidays`
  GET, but §2.2's capability matrix explicitly grants Manager `R` on both.
  Implemented per §2.2 (the more detailed, authoritative source) — see the
  role-matrix test.
- §5.5 shows "409 if default" under HR's column for `DELETE /shifts/{id}`,
  while §2.2 lists "Organization default schedule" as HR: denied entirely.
  Implemented as: HR gets 403 (not 409) on any write to the default
  schedule; the default is never deletable by anyone (409) — see
  `app/routers/shifts.py`.
- No end-of-day batch job marks a no-show `absent` in real time; the spec
  doesn't specify when such a job would run. `/reports/org-day` (today's
  live summary) still reports a no-show as `not_checked_in` rather than
  guessing `absent` before the day is over. The month grid (a look *back*
  at a past employee, not today's live board) computes `absent` for a past
  workday with no record on the fly at read time — the two views ask
  different questions and answer them differently on purpose.
- The consent screen is one screen with the acknowledge-then-submit order
  enforced, not the full 4-step wizard with back-navigation from §9.4.
