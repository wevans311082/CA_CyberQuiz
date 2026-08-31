# Browser reliability suite

The Playwright suite has two layers:

- The framework and entry-surface smoke test runs without application services and is suitable for every pull request.
- The live multi-user test is opt-in and uses one facilitator plus two independent player browser contexts against a real exercise.

## Local smoke test

```powershell
npx playwright install chromium
npm run dev -- --host 127.0.0.1
$env:E2E_BASE_URL = 'http://127.0.0.1:3000'
npm run test:e2e -- --grep "framework guide"
```

The test runs in desktop Chromium and mobile Chromium. Playwright retains traces, screenshots, and video for failures.

## Live exercise test

Start the normal backend, Redis, Postgres, and frontend stack, then provide a facilitator-authenticated storage state and a disposable exercise:

```powershell
$env:E2E_BASE_URL = 'http://127.0.0.1:3000'
$env:E2E_GAME_PIN = '123456'
$env:E2E_GAME_ID = '<exercise-id>'
$env:E2E_HOST_TOKEN = '<host-token>'
$env:E2E_STORAGE_STATE = '<path-to-playwright-storage-state.json>'
npm run test:e2e -- --grep "live multi-user"
```

The live test is intentionally skipped when these variables are absent. It must run against disposable data and must not use a production exercise. The next reliability increment is to seed this fixture automatically in CI, then extend the journey with timer synchronisation, role acceptance, branch decisions, scoring/bonuses, projector presentation, and policy spotlight assertions.
