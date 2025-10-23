🗂️ Product Backlog – LessonGen (AI Lesson Plan Generator)
Epic 1: User Management & Access
Feature 1.1 – Authentication & Authorization

User Stories

As a teacher, I want to sign in using my school Google account so that I can securely access my lessons.

Acceptance Criteria: Google OAuth 2.0; token stored securely; session timeout after inactivity.

Priority: High

As an admin, I want to create and manage school/district accounts so that I can onboard multiple teachers.

Acceptance Criteria: CRUD for users, role-based permissions (teacher, coach, admin).

Priority: High

As a teacher, I want to update my profile and preferred subjects/grades to personalize lesson generation.

Acceptance Criteria: Editable profile; preferences persist across sessions.

Priority: Medium

Epic 2: Lesson Plan Generation (Core AI Engine)
Feature 2.1 – Lesson Creation Wizard

User Stories

As a teacher, I want to enter a topic, grade, and duration to generate a new lesson plan instantly.

Acceptance Criteria: Input form (topic, subject, grade, duration, standard optional).

Priority: High

As a teacher, I want the AI to generate a full lesson plan with objectives, materials, and activities.

Acceptance Criteria: Plan includes five sections (Objective, Materials, Flow, Assessment, Differentiation).

Priority: High

As a teacher, I want to preview the lesson before saving it to my library.

Acceptance Criteria: Preview screen with formatted markdown view.

Priority: High

Feature 2.2 – Standards Alignment

User Stories

As a teacher, I want the AI to automatically align my lesson to the appropriate standard (e.g., NGSS 5-LS2-1).

Acceptance Criteria: Suggest relevant standards based on subject and grade.

Priority: High

As a curriculum coordinator, I want to filter all lessons by standard code for auditing alignment.

Acceptance Criteria: Filter lessons by framework, subject, grade, and code.

Priority: Medium

As a teacher, I want to manually override the suggested standard.

Acceptance Criteria: Dropdown with searchable standards list.

Priority: Medium

Feature 2.3 – AI Generation Parameters

User Stories

As a teacher, I want to specify learning goals or keywords to guide the AI’s focus.

Acceptance Criteria: “Focus” text field affects generated lesson objectives.

Priority: Medium

As a teacher, I want to choose between different teaching styles (inquiry-based, direct instruction, project-based).

Acceptance Criteria: Radio button selection modifies AI output tone.

Priority: Medium

As an admin, I want to log every AI generation job for monitoring and analytics.

Acceptance Criteria: Each gen_job record includes user_id, parameters, timestamps, and result link.

Priority: High

Epic 3: Lesson Editing & Management
Feature 3.1 – WYSIWYG Lesson Editor

User Stories

As a teacher, I want to edit AI-generated content before publishing.

Acceptance Criteria: Markdown editor with sectioned layout and real-time preview.

Priority: High

As a teacher, I want to save multiple versions of a lesson to track revisions.

Acceptance Criteria: Version history in sidebar with timestamps.

Priority: High

As a teacher, I want to restore a previous version of a lesson.

Acceptance Criteria: “Restore” button sets current_version_id.

Priority: Medium

As a teacher, I want autosave to prevent losing edits.

Acceptance Criteria: Edits persist every 30 seconds or on section change.

Priority: High

Feature 3.2 – Lesson Library

User Stories

As a teacher, I want to view all my saved lessons in one dashboard.

Acceptance Criteria: Grid view with title, grade, subject, and last updated.

Priority: High

As a teacher, I want to organize lessons by unit, topic, or tag.

Acceptance Criteria: Custom tags, drag-and-drop reordering.

Priority: Medium

As an admin, I want to view and filter lessons created by my teachers.

Acceptance Criteria: Admin view with filters by school, grade, subject.

Priority: Medium

Epic 4: Unit Planning & Pacing
Feature 4.1 – Unit Builder

User Stories

As a teacher, I want to group lessons into a unit.

Acceptance Criteria: Create “Unit” → add existing lessons or generate new ones.

Priority: Medium

As a teacher, I want to reorder lessons within a unit to match pacing.

Acceptance Criteria: Drag-and-drop ordering in unit_items.

Priority: Medium

As a teacher, I want to export an entire unit as a pacing guide (PDF or DOCX).

Acceptance Criteria: One-click export, with lesson titles, objectives, and duration.

Priority: Medium

Epic 5: Differentiation & Accessibility
Feature 5.1 – Student Adaptation

User Stories

As a teacher, I want to request an adapted version of a lesson for ELL or IEP students.

Acceptance Criteria: “Differentiate” button generates modified copy with accommodations.

Priority: Medium

As a teacher, I want enrichment extensions for gifted learners.

Acceptance Criteria: “Extension” field appended under lesson flow.

Priority: Medium

As a teacher, I want to generate bilingual lesson plans (English/French).

Acceptance Criteria: Language toggle regenerates or translates content.

Priority: Low (Phase 2)

Epic 6: LMS & Export Integration
Feature 6.1 – LMS Push

User Stories

As a teacher, I want to send a lesson directly to Google Classroom or Canvas.

Acceptance Criteria: OAuth integration; confirmation message after push.

Priority: High

As an admin, I want to track which lessons have been exported to the LMS.

Acceptance Criteria: lms_pushes table updates with success/failure status.

Priority: Medium

Feature 6.2 – Export & Share

As a teacher, I want to export lessons as PDF, DOCX, or Google Doc.

Acceptance Criteria: File downloads must include header metadata (grade, standard).

Priority: High

As a teacher, I want to share a read-only link to a lesson with colleagues.

Acceptance Criteria: Share token generated with expiration option.

Priority: Medium

Epic 7: Analytics & Insights
Feature 7.1 – User Analytics

As an admin, I want to view metrics on how many lessons were generated, edited, or exported.

Acceptance Criteria: Dashboard pulling from events and metrics_daily.

Priority: Medium

As a teacher, I want to see how much time I’ve saved using the generator.

Acceptance Criteria: Simple “Time Saved” metric (avg time per manual lesson vs. AI).

Priority: Medium

Epic 8: Security, Compliance & Infrastructure
Feature 8.1 – Compliance & Privacy

As an admin, I want assurance that student data is protected under FERPA/COPPA.

Acceptance Criteria: Data retention policies, encryption, clear privacy notice.

Priority: High

As a teacher, I want to know my lessons are private unless I explicitly share them.

Acceptance Criteria: Default visibility='private'; confirmation on publish.

Priority: High

Epic 9: AI Feedback & Continuous Improvement
Feature 9.1 – Quality Feedback Loop

As a teacher, I want to rate the AI-generated lesson (1–5 stars).

Acceptance Criteria: Rating saved to lesson_versions; AI fine-tuning feedback collected.

Priority: Low (Phase 2)

As an admin, I want to view which standards produce low-rated lessons to improve content.

Acceptance Criteria: Aggregated feedback by standard_id.

Priority: Low

🏁 Priority Summary (MVP vs. Future)
Priority	Scope	Example Stories
MVP (Phase 1–2)	Core generation, editing, standards, export, SSO	Epics 1–3, 6.1
Phase 3 (Enhancement)	Units, differentiation, analytics	Epics 4–5, 7
Phase 4 (Scaling)	Feedback, collaboration, marketplace	Epic 9 + Future Enhancements
🔮 Future Backlog Candidates

Collaborative co-planning (multi-user editing sessions)

Teacher marketplace (share/sell lessons)

Student view integration (interactive mode)

Voice-to-lesson generator (“Generate lesson from spoken prompt”)

API for district LMS import/export pipelines
