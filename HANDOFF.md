# Natillera Digital — Project Handoff / Status

**Last updated:** 2026-07-07. Written so work can resume on a different machine with zero prior context.

## Architecture (3 separate deploy targets, same repo)

```
natillera-beta/  (github.com/leonardoq-ops/natillera-beta, branch main)
├── index.html, login.html, dashboard.html, css/, js/, assets/   -> static marketing site
│                                                                     GitHub Pages, natilleradigital.com
├── app/          -> Streamlit dashboards (engine + member/admin UI)
│                     deployed on Streamlit Community Cloud
├── api/          -> FastAPI proof-upload service
│                     deployed on Google Cloud Run (southamerica-east1)
└── cloudbuild.yaml -> explicit build/push/deploy pipeline for api/ (Cloud Build trigger uses this)
```

`_config.yml` excludes both `app/` and `api/` from the Jekyll/GitHub Pages build so they don't interfere with the static site.

## Live URLs

- Static site: **natilleradigital.com** (GitHub Pages)
- Streamlit dashboards: **https://leonardoq-ops-natillera-beta-appstreamlit-app-6gh9ll.streamlit.app/**
- Proof API (Cloud Run): **https://natillera-beta-954802059162.southamerica-east1.run.app** (confirmed healthy via `/health`)

## External accounts / where secrets live (never committed to git)

- **Turso** (SQLite-compatible DB, shared by both `app/` and `api/`): database `natillera-prod-leonardoq-ops`, region `aws-us-east-2`. URL + auth token live in (a) Streamlit Cloud → app settings → Secrets, and (b) Cloud Run → service → Variables & Secrets. **Both must have the identical, current (non-revoked) token** — this has been a recurring source of confusion; the token was rotated multiple times during setup.
- **Google Cloud project**: `proyecto-natillera-digital` (org `natilleradigital.com`). Org policy `iam.disableServiceAccountKeyCreation` is enforced — **no JSON key files can ever be created**. Drive auth uses Application Default Credentials instead (see `api/google_drive_utils.py`), satisfied by attaching the service account directly to the Cloud Run service (Security tab).
- **Service account**: `natillera-proof-uploader@proyecto-natillera-digital.iam.gserviceaccount.com` — attached to the Cloud Run service; must also have Editor access on the Drive folder below.
- **Google Drive folder**: "Natillera Digital - Pruebas de Pago", ID `17GgQQoZLVqLNFFGH1GfH2tLB0USSjs1M`, shared with the service account above.
- **Artifact Registry repo**: `natillera-repo` (southamerica-east1, Docker format) — where Cloud Build pushes images.
- **Cloud Build service account**: the default compute one, `954802059162-compute@developer.gserviceaccount.com`, granted extra roles: Logs Writer, Cloud Run Admin, Service Account User, Artifact Registry Writer.
- **Shared secret between the two services**: `UPLOAD_API_KEY` — must be the identical string in both Streamlit secrets and Cloud Run env vars (this is our own app-level API key check, not a Google credential).
- **`COWORK_WEBHOOK_URL`**: not yet obtained from the user; currently unset, and the code handles that gracefully (no-op notification).

## What's built and verified working (locally, fully tested)

- `app/natillera_engine/`: full calc engine per CALC_ENGINE_SPEC v1.1 (compounding, GMF, retefuente, VNR, early_exit, mora, reserve, huella, reduced risk validators, ledger with SHA-256 hash chain, `EventType.VERIFICACION` + `proof_status.py` for the upload/verify flow). 25 passing pytest tests.
- `app/db/`: SQLite/Turso persistence layer, append-only ledger enforced by DB triggers, `DbLedger` mirrors the in-memory `Ledger`'s interface.
- `app/auth/`: argon2 hashing, member login by email+PIN, admin by password, session-state only (no localStorage). Critical gotcha already fixed: `st.navigation()` must run on **every** script execution including pre-login, or Streamlit's classic auto-discovered `pages/` sidebar leaks every admin page to unauthenticated visitors.
- `app/ui/theme.py`: Natillera Aesthetics Guide (Navy/Oro Muisca/Teal palette, Fraunces/DM Sans/DM Mono fonts, card/badge styling) injected via a single `<style>` block. Gotcha already fixed: a `<script>`-based counter animation for THE NUMBER was tried and removed — `st.markdown(unsafe_allow_html=True)` inserts via `innerHTML`, and browsers never execute `<script>` tags inserted that way, so it silently never ran.
- `api/`: FastAPI service with `/api/upload-proof` and `/api/verify-proof`, sharing `app/natillera_engine` and `app/db` verbatim via the Dockerfile's build (COPYs them from repo root into the image — no code duplication). API-key protected via `X-API-Key` header. 4 passing pytest tests.
- Full local end-to-end test (Streamlit + FastAPI + shared SQLite) confirmed working: member uploads proof -> admin verifies -> member's dashboard badge updates. Confirmed via automated browser testing.

## Cloud Build / Cloud Run deployment gotchas already solved (don't repeat these)

1. Cloud Run's "Continuously deploy from repository" wizard's "Dockerfile" build-type UI was unreliable at applying a custom Dockerfile path/directory — kept reverting to looking for `Dockerfile` at repo root. **Fixed by using an explicit `cloudbuild.yaml`** (Configuration Type = "Cloud Build configuration file") instead of the wizard's Dockerfile mode.
2. Cloud Build requires `options.logging` (e.g. `CLOUD_LOGGING_ONLY`) whenever a custom/explicit service account is specified for the build - otherwise trigger creation fails with an "invalid argument" error.
3. `gcr.io` now requires `artifactregistry.repositories.createOnPush` to auto-create a repo on first push (Google migrated it onto Artifact Registry under the hood). **Fixed by pushing to an explicitly pre-created Artifact Registry repo** (`natillera-repo`) instead.
4. The gcloud CLI builder image must be `gcr.io/cloud-builders/gcloud`, **not** `gcr.io/google.com/cloudsdk/cloud-sdk` (the latter hits an unrelated Artifact Registry permission wall pulling from Google's internal mirror).
5. The default Compute Engine service account needs Logs Writer, Cloud Run Admin, Service Account User, and Artifact Registry Writer roles added manually (IAM & Admin -> IAM) - none of these are granted by default.

Current `cloudbuild.yaml` (3 steps: docker build -> docker push -> gcloud run deploy) is confirmed working — the last build completed with no errors and the service is live and healthy.

## OPEN ISSUE — currently blocking (this is where we left off)

**Symptom**: On the live Streamlit app, clicking the "Ingresar" (login) button does nothing at all — no network activity, no state change. This reproduces even for both member and admin login tabs.

**Diagnosis so far**:
- Streamlit Cloud server logs show a clean startup, dependencies installed fine, no Python tracebacks, multiple successful "Updated app!" redeploys matching our pushes. The app process itself is healthy.
- A cookie-aware `curl` test confirms the server responds correctly with real HTML over plain HTTPS (the redirect dance through `/-/login` and `share.streamlit.io/-/auth/app` is normal Streamlit Cloud session bootstrapping, not a bug — an earlier diagnosis blaming "restricted visibility" was wrong; a follow-up cookie-jar-aware curl retest got a clean `200`).
- Browser DevTools Network tab (filtered to "WS") showed **zero WebSocket connections attempted at all**, which is consistent with something blocking the WS upgrade specifically, since plain HTTP works fine.
- One early screenshot showed the user was testing from *inside* Streamlit Cloud's own "Manage app" dashboard (an embedded/sandboxed iframe preview, not the real public page) — that was corrected, but the issue persisted even from what should have been the real public URL in a plain tab.
- Not yet conclusively tested: mobile data / different network (to rule out a work VPN or router-level firewall blocking WebSocket upgrades specifically), and an incognito window (to rule out a browser extension).

**Next steps to try, in order**:
1. Open the app URL in an **incognito/private window** (rules out extensions).
2. Try on a **different network** entirely (phone hotspot/mobile data) — if it suddenly works, the block is on the current network (VPN/firewall), not the app.
3. Go through the full configuration checklist below to rule out any secrets/settings mismatch as a contributing factor (unlikely given the symptom is WS-specific, but cheap to verify):
   - Streamlit Cloud: main file path = `app/streamlit_app.py`, visibility = public, all 4 secrets present and non-placeholder.
   - Cloud Run: region `southamerica-east1`, revision healthy, all 5 env vars present, service account attached, unauthenticated invocations allowed.
   - Turso: identical URL+token in both places, token not stale/revoked.
   - Drive folder shared with the service account.
4. If a different network fixes it: the app itself is fine, it's a local network restriction — nothing left to fix in code.
5. If a different network does NOT fix it: this becomes a genuine Streamlit-Cloud-side or app-side bug worth deeper investigation (check for any reverse proxy/CDN in front, or try re-deploying).

## Remaining task list (not yet done)

- Resolve the WebSocket/login issue above.
- Once login works: full live end-to-end smoke test (real member login, real proof upload through Google Drive, real admin verification, badge updates) — this has only been verified locally so far, not against the live deployed services.
- Seed the real pilot members (currently only one test member exists in the real Turso DB: `ana@example.com` / PIN `1234`; admin password was also set but is a generated string not documented anywhere for security - whoever has it should keep it, or reset it via `scripts/seed_members.py --set-admin-password` if lost).
- Wire the real `COWORK_WEBHOOK_URL` once the user obtains it from that external tool, and redeploy `api/`.
- Consider pinning `streamlit` in `app/requirements.txt` (currently unpinned at `>=1.36`, so Cloud installed the newest `1.59.0` - not confirmed related to the WS issue, but unpinned versions mean silent behavior drift on every redeploy).
