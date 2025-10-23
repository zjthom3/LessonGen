Core ERD (high level)

Tenanting & Org

tenants 1—* districts 1—* schools 1—* users

Curriculum & Standards

standards_frameworks 1—* standards

lessons 1—* lesson_versions — lesson_standards (to standards)

units 1—* unit_items (lesson or resource)

Content & Assets

lessons 1—* lesson_versions 1—* lesson_blocks

assets — lesson_versions (via lesson_assets)

rubrics, assessments, questions, answer_options

AI & Workflow

gen_jobs → produces lesson_versions

editor_sessions, audit_logs

Distribution & LMS

lms_connections 1—* lms_pushes

shares (internal/external sharing/links)

Analytics

events (track usage), metrics_daily

Entities & Tables
1) Multitenancy & Identity
-- Tenants → Districts → Schools → Users (RBAC via user_roles)
CREATE TABLE tenants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  plan TEXT NOT NULL DEFAULT 'district',
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE districts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE schools (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  district_id UUID NOT NULL REFERENCES districts(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  grade_bands TEXT[] DEFAULT '{}', -- e.g. {'K-5','6-8'}
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  school_id UUID REFERENCES schools(id) ON DELETE SET NULL,
  district_id UUID REFERENCES districts(id) ON DELETE SET NULL,
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  email CITEXT UNIQUE NOT NULL,
  full_name TEXT NOT NULL,
  auth_provider TEXT NOT NULL, -- 'google','microsoft','classlink','password'
  role TEXT NOT NULL DEFAULT 'teacher', -- teacher, coach, admin, district_admin
  locale TEXT NOT NULL DEFAULT 'en-US',
  disabled BOOLEAN NOT NULL DEFAULT FALSE,
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE user_roles (
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role TEXT NOT NULL, -- extra scoped roles/permissions
  scope JSONB NOT NULL DEFAULT '{}',
  PRIMARY KEY (user_id, role)
);

2) Standards & Alignment
CREATE TABLE standards_frameworks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT NOT NULL, -- 'CCSS', 'NGSS', 'TEKS', 'QC', etc.
  name TEXT NOT NULL,
  jurisdiction TEXT, -- 'US','CA-QC', etc.
  language TEXT NOT NULL DEFAULT 'en',
  metadata JSONB NOT NULL DEFAULT '{}'
);

CREATE UNIQUE INDEX ux_framework_code ON standards_frameworks(code, jurisdiction);

CREATE TABLE standards (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  framework_id UUID NOT NULL REFERENCES standards_frameworks(id) ON DELETE CASCADE,
  code TEXT NOT NULL,  -- e.g., 'NGSS 5-LS2-1'
  grade_band TEXT,     -- 'K-2','3-5','6-8','9-12'
  subject TEXT,        -- 'Math','Science'
  description TEXT NOT NULL,
  tags TEXT[] DEFAULT '{}',
  metadata JSONB NOT NULL DEFAULT '{}'
);

CREATE INDEX ix_standards_lookup ON standards (framework_id, subject, grade_band);

3) Curriculum Objects (Units, Lessons, Versions)
CREATE TABLE units (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  subject TEXT NOT NULL,
  grade_level TEXT NOT NULL, -- 'K', '1', ..., '12'
  duration_days INT,
  description TEXT,
  visibility TEXT NOT NULL DEFAULT 'private', -- private, org, public
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE lessons (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  subject TEXT NOT NULL,
  grade_level TEXT NOT NULL,
  language TEXT NOT NULL DEFAULT 'en',
  status TEXT NOT NULL DEFAULT 'draft', -- draft, published, archived
  current_version_id UUID, -- FK set after first version insert
  visibility TEXT NOT NULL DEFAULT 'private', -- private, org, public
  tags TEXT[] DEFAULT '{}',
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Optimistic, immutable versioning (write-once); link back to lessons.current_version_id
CREATE TABLE lesson_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lesson_id UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
  version_no INT NOT NULL, -- 1,2,3...
  objective TEXT,
  duration_minutes INT,
  differentiation JSONB NOT NULL DEFAULT '[]', -- strategies array
  assessments JSONB NOT NULL DEFAULT '[]', -- summaries/references to assessment ids
  accommodations JSONB NOT NULL DEFAULT '[]', -- IEP/ELL etc
  teacher_script_md TEXT, -- markdown
  materials JSONB NOT NULL DEFAULT '[]', -- [{type:'url|file|text', label, value}]
  flow JSONB NOT NULL DEFAULT '[]', -- [{phase:'Engage', minutes:5, content_md:'...'}]
  locale TEXT NOT NULL DEFAULT 'en-US',
  ai_model TEXT, -- provenance
  source JSONB NOT NULL DEFAULT '{}', -- e.g., {prompt_id, settings}
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  published_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX ux_lesson_versions ON lesson_versions(lesson_id, version_no);

-- Unit composition (ordered)
CREATE TABLE unit_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  unit_id UUID NOT NULL REFERENCES units(id) ON DELETE CASCADE,
  position INT NOT NULL,
  item_type TEXT NOT NULL, -- 'lesson' | 'resource'
  lesson_id UUID REFERENCES lessons(id) ON DELETE SET NULL,
  resource_ref JSONB, -- other resource pointers
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Alignment: many-to-many
CREATE TABLE lesson_standards (
  lesson_version_id UUID NOT NULL REFERENCES lesson_versions(id) ON DELETE CASCADE,
  standard_id UUID NOT NULL REFERENCES standards(id) ON DELETE CASCADE,
  PRIMARY KEY (lesson_version_id, standard_id)
);

Optional: Structured Blocks for fine-grained editing
CREATE TABLE lesson_blocks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lesson_version_id UUID NOT NULL REFERENCES lesson_versions(id) ON DELETE CASCADE,
  block_type TEXT NOT NULL, -- 'objective','engage','explore','explain','elaborate','evaluate','materials'
  sequence INT NOT NULL,
  content_md TEXT NOT NULL,
  est_minutes INT,
  metadata JSONB NOT NULL DEFAULT '{}'
);

4) Assessments & Questions (Re-usable)
CREATE TABLE rubrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  criteria JSONB NOT NULL, -- [{criterion, levels:[{name,desc,points}], weight}]
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE assessments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  type TEXT NOT NULL, -- 'exit_ticket','quiz','project'
  grading_schema JSONB NOT NULL DEFAULT '{}',
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
  prompt_md TEXT NOT NULL,
  q_type TEXT NOT NULL, -- 'mcq','short','rubric','truefalse'
  difficulty TEXT, -- 'easy','medium','hard'
  metadata JSONB NOT NULL DEFAULT '{}',
  position INT NOT NULL
);

CREATE TABLE answer_options (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
  label TEXT, -- 'A','B','C'
  content_md TEXT NOT NULL,
  is_correct BOOLEAN,
  feedback_md TEXT
);

5) Assets & Files
CREATE TABLE assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  uploaded_by UUID REFERENCES users(id),
  storage_uri TEXT NOT NULL, -- s3://... / gcs://...
  filename TEXT NOT NULL,
  mime_type TEXT NOT NULL,
  size_bytes BIGINT,
  checksum TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  metadata JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE lesson_assets (
  lesson_version_id UUID NOT NULL REFERENCES lesson_versions(id) ON DELETE CASCADE,
  asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
  purpose TEXT, -- 'handout','slide','image','worksheet'
  PRIMARY KEY (lesson_version_id, asset_id)
);

6) AI Generation & Editing Workflow
CREATE TABLE gen_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id),
  input JSONB NOT NULL,  -- {grade, subject, topic, standards[], duration, constraints}
  status TEXT NOT NULL DEFAULT 'queued', -- queued,running,succeeded,failed
  model TEXT NOT NULL,
  temperature NUMERIC(3,2) DEFAULT 0.2,
  top_p NUMERIC(3,2) DEFAULT 1.0,
  max_tokens INT,
  result_lesson_version_id UUID REFERENCES lesson_versions(id),
  error TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE editor_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lesson_version_id UUID NOT NULL REFERENCES lesson_versions(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id),
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  ended_at TIMESTAMPTZ,
  diff JSONB NOT NULL DEFAULT '[]' -- CRDT/ops log if needed
);

7) Sharing, LMS, and Publishing
CREATE TABLE shares (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resource_type TEXT NOT NULL, -- 'lesson','unit'
  resource_id UUID NOT NULL,
  visibility TEXT NOT NULL DEFAULT 'private', -- private, org, public, link
  link_token TEXT UNIQUE, -- for link sharing
  expires_at TIMESTAMPTZ,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE lms_connections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  district_id UUID REFERENCES districts(id),
  school_id UUID REFERENCES schools(id),
  provider TEXT NOT NULL, -- 'google_classroom','canvas','schoology'
  oauth JSONB NOT NULL,   -- tokens
  scope JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE lms_pushes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lesson_version_id UUID NOT NULL REFERENCES lesson_versions(id) ON DELETE CASCADE,
  lms_connection_id UUID NOT NULL REFERENCES lms_connections(id) ON DELETE CASCADE,
  status TEXT NOT NULL DEFAULT 'pending', -- pending,posted,failed
  target JSONB NOT NULL, -- {course_id, topic_id, due_date, attachments[]}
  response JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

8) Compliance, Auditing, Analytics
CREATE TABLE audit_logs (
  id BIGSERIAL PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  actor_user_id UUID REFERENCES users(id),
  action TEXT NOT NULL, -- 'create_lesson','publish_version','share_link'
  resource_type TEXT NOT NULL,
  resource_id UUID NOT NULL,
  before JSONB,
  after JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE events (
  id BIGSERIAL PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id),
  name TEXT NOT NULL, -- 'lesson_generate','lesson_export','lms_push'
  properties JSONB NOT NULL DEFAULT '{}',
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE metrics_daily (
  d DATE NOT NULL,
  tenant_id UUID NOT NULL,
  metric TEXT NOT NULL, -- 'gen_count','active_users','exports'
  value BIGINT NOT NULL,
  PRIMARY KEY (d, tenant_id, metric)
);

Key Design Notes

Immutable versions: lesson_versions are append-only; lessons.current_version_id points to the latest, giving auditability and easy rollback.

Flexible content: Markdown for authoring (teacher_script_md, lesson_blocks.content_md), with structured arrays (flow, materials) in JSONB for UI rendering and exports.

Standards alignment: Many-to-many via lesson_standards; supports multiple frameworks and cross-jurisdiction use.

Org-aware visibility: visibility fields allow private / org / public / link publishing.

LMS decoupling: lms_connections store tokens/scopes; lms_pushes retain payloads & responses for retries/diagnostics.

Analytics: event firehose + rolled-up metrics_daily for dashboards.

Multi-tenant security: every core object carries tenant_id for row-level security (RLS) in PostgreSQL.

Helpful Indexes (performance quick wins)
CREATE INDEX ix_lessons_tenant_subject_grade ON lessons(tenant_id, subject, grade_level);
CREATE INDEX ix_lesson_versions_lesson_created ON lesson_versions(lesson_id, created_at DESC);
CREATE INDEX ix_events_tenant_name_time ON events(tenant_id, name, occurred_at DESC);
CREATE INDEX ix_assets_tenant_filename ON assets(tenant_id, filename);
CREATE INDEX ix_standards_textsearch ON standards USING GIN (to_tsvector('english', description));
CREATE INDEX ix_lessons_tags_gin ON lessons USING GIN (tags);

Common Queries (sanity checks)
-- 1) Fetch latest published version for a lesson
SELECT lv.*
FROM lessons l
JOIN lesson_versions lv ON lv.id = l.current_version_id
WHERE l.id = $1 AND l.status = 'published';

-- 2) Search lessons by subject/grade + standard code
SELECT DISTINCT l.*
FROM lessons l
JOIN lesson_versions lv ON lv.lesson_id = l.id
JOIN lesson_standards ls ON ls.lesson_version_id = lv.id
JOIN standards s ON s.id = ls.standard_id
WHERE l.tenant_id = $tenant
  AND l.subject = 'Science'
  AND l.grade_level = '5'
  AND s.code ILIKE '%5-LS2-1%';

-- 3) Get unit outline with lesson titles & latest versions
SELECT ui.position, l.title, lv.version_no
FROM unit_items ui
LEFT JOIN lessons l ON l.id = ui.lesson_id
LEFT JOIN lesson_versions lv ON lv.id = l.current_version_id
WHERE ui.unit_id = $unit
ORDER BY ui.position;

Minimal API Alignment (for later)

POST /gen-jobs → create generation request

GET /lessons/:id → includes current_version & aligned standards

POST /lessons/:id/versions → save edited version (new version_no)

POST /lms/push → push a lesson_version with lms_connection_id
