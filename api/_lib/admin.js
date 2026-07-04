export function isModerationEnabled() {
  return Boolean(String(process.env.GALLERY_ADMIN_CODE || "").trim());
}

export function verifyAdminCode(request) {
  const expected = String(process.env.GALLERY_ADMIN_CODE || "").trim();
  if (!expected) {
    return false;
  }
  const header = String(request.headers.get("x-admin-code") || "").trim();
  const url = new URL(request.url);
  const query = String(url.searchParams.get("code") || "").trim();
  return header === expected || query === expected;
}

export function getVoteCloseTime() {
  const configured = String(process.env.VOTE_CLOSE_TIME || "").trim();
  return configured || "2026-08-15T21:00:00-07:00";
}

export function isVoteClosed() {
  return Date.now() >= new Date(getVoteCloseTime()).getTime();
}
