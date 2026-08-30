// The editor depends on browser-only DOM APIs (CKEditor/Pikaso).
// Keep the route's existing server load for auth/data, but render the editor on the client.
export const ssr = false;
