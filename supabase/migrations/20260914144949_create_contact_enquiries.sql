/*
# Create contact_enquiries table (single-tenant, no auth)

1. New Tables
- `contact_enquiries`
- `id` (uuid, primary key)
- `name` (text, not null) — visitor's name
- `email` (text, not null) — visitor's reply email
- `message` (text, not null) — the enquiry message
- `request_id` (uuid, not null) — idempotency key from the browser
- `created_at` (timestamptz, default now())
2. Security
- Enable RLS on `contact_enquiries`.
- Allow anon + authenticated INSERT only (public contact form, no sign-in).
- No SELECT/UPDATE/DELETE for anon — only the database owner can read enquiries.
- Add unique constraint on request_id to prevent duplicate submissions.
*/

CREATE TABLE IF NOT EXISTS contact_enquiries (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  email text NOT NULL,
  message text NOT NULL,
  request_id uuid NOT NULL,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE contact_enquiries ENABLE ROW LEVEL SECURITY;

CREATE UNIQUE INDEX IF NOT EXISTS contact_enquiries_request_id_key ON contact_enquiries(request_id);

DROP POLICY IF EXISTS "anon_insert_enquiries" ON contact_enquiries;
CREATE POLICY "anon_insert_enquiries"
ON contact_enquiries FOR INSERT
TO anon, authenticated
WITH CHECK (true);
