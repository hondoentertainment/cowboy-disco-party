(function (global) {
  "use strict";

  global.CDP = {
    BRAND_NAME: "Cowboy Disco Party",
    BRAND_VENUE: "Cowboy Disco Saloon",
    BRAND_TAGLINE: "Where Studio 54 meets the Wild West — rhinestone, mirror-ball light, and two-step under the Seattle skyline.",
    BRAND_DATE_LABEL: "Sep 19, 2026 · 6:00 PM",
    SITE_URL: "https://cowboy-disco-party.vercel.app",
    // Partiful event page — set to the full event URL (e.g. "https://partiful.com/e/XXXX")
    // to reveal "RSVP on Partiful" buttons sitewide. Leave empty to keep them hidden.
    PARTIFUL_URL: "https://partiful.com/e/94zFEZVg5w39NBaw2eih?c=1gmpxVwQ",
    // Spotify party playlist — set to the playlist URL to reveal the
    // "Hear the Party Playlist" button in the schedule section.
    SPOTIFY_PLAYLIST_URL: "",
    // Ambient country-disco loop. Set to an audio file path (e.g.
    // "/assets/party-loop.mp3") to reveal the sound toggle. Playback is
    // always opt-in — it never autoplays, and the choice is remembered.
    AMBIENT_AUDIO_URL: "",
    PARTY_DATE_TBD: false,
    PARTY_DATE: "2026-09-19T18:00:00-07:00",
    PARTY_END: "2026-09-19T22:00:00-07:00",
    VOTE_CLOSE_TIME: "2026-09-19T21:00:00-07:00",
    VOTE_MAX_NUMBER: 99,
    VOTE_TAG_COUNT: 30,
    // The invite page appends "RSVP: <PARTIFUL_URL>" automatically when set,
    // so the Partiful link lives in exactly one place.
    SHARE_MESSAGE:
      "You're invited to Cowboy Disco — where Studio 54 meets the Wild West. Saturday, Sep 19, 2026 at 6:00 PM · Cowboy Disco Saloon at Green Lake Village East, 427 NE 72nd St, Seattle. Party details, photos & votes: https://cowboy-disco-party.vercel.app",
    OG_IMAGE: "https://cowboy-disco-party.vercel.app/assets/og-card.jpg",
  };
})(window);
