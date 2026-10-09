/*
# Add business, service, and website columns to contact_enquiries

1. Modified Tables
- `contact_enquiries`
  - Added `business` (text) — visitor's business name (optional at DB level, validated client-side)
  - Added `service` (text) — the selected service type (e.g. "New website", "SEO")
  - Added `website` (text) — visitor's current website URL if provided (nullable)

2. Notes
- These columns are additive — no existing data is lost.
- The existing INSERT policy (anon + authenticated, WITH CHECK true) already covers the new columns.
- All new columns are nullable so the insert won't fail if a field is omitted.
*/

ALTER TABLE contact_enquiries
  ADD COLUMN IF NOT EXISTS business text,
  ADD COLUMN IF NOT EXISTS service text,
  ADD COLUMN IF NOT EXISTS website text;