# frontend (Vue 2 skeleton)

Stack: Vue CLI + Vue 2 + Vue Router 3 + Vuex 3 + Element UI + Axios.

## Quick start
- `npm install`
- `npm run serve` (set `VUE_APP_API_BASE_URL` in `.env.local` to point at the backend)

## Structure
- `src/api`: Axios wrappers with auth + signed URL handling.
- `src/store`: Vuex modules (datasets, files, metrics, reports).
- `src/views`: Pages for upload, metrics, reports, admin tools.
- `src/components`: Reusable UI components.
- `src/router`: Route definitions and guards.

## Next
- Add signed URL download/upload flows once backend endpoints are ready.
