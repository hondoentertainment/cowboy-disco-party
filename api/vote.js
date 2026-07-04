import { list, put } from "@vercel/blob";
import { getVoteCloseTime, isVoteClosed } from "./_lib/admin.js";

const DEFAULT_MAX_NUMBER = 99;

function normalizeName(value) {
  return String(value || "")
    .trim()
    .replace(/\s+/g, " ")
    .slice(0, 80);
}

function getMaxNumber() {
  const parsed = Number.parseInt(process.env.VOTE_MAX_NUMBER || "", 10);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : DEFAULT_MAX_NUMBER;
}

function parseContestantNumber(value) {
  const number = Number.parseInt(String(value ?? "").trim(), 10);
  if (!Number.isInteger(number)) {
    return null;
  }
  return number;
}

function getVoteTarget(vote) {
  if (vote.number != null) {
    const number = parseContestantNumber(vote.number);
    if (number != null) {
      return { number };
    }
  }

  const legacyNumber = parseContestantNumber(vote.nominee);
  if (legacyNumber != null) {
    return { number: legacyNumber };
  }

  const nominee = normalizeName(vote.nominee);
  if (nominee) {
    return { nominee };
  }

  return null;
}

function targetKey(target) {
  return target.number != null ? "n:" + target.number : "l:" + target.nominee;
}

function compareTargets(a, b) {
  if (a.number != null && b.number != null) {
    return a.number - b.number;
  }

  return String(a.nominee || a.number).localeCompare(String(b.nominee || b.number));
}

function normalizeVoterKey(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, " ");
}

async function loadVotes() {
  const { blobs } = await list({ prefix: "votes/", limit: 1000 });
  const votes = await Promise.all(
    blobs
      .filter(function (blob) {
        return blob.pathname.endsWith(".json");
      })
      .map(async function (blob) {
        const response = await fetch(blob.url);
        if (!response.ok) {
          return null;
        }
        return response.json();
      })
  );
  return votes.filter(Boolean);
}

function buildResults(valid) {
  const tally = {};

  valid.forEach(function (vote) {
    const target = getVoteTarget(vote);
    if (!target) {
      return;
    }

    const key = targetKey(target);
    if (!tally[key]) {
      tally[key] =
        target.number != null
          ? { number: target.number, count: 0 }
          : { nominee: target.nominee, count: 0 };
    }
    tally[key].count += 1;
  });

  const results = Object.values(tally).sort(function (a, b) {
    return b.count - a.count || compareTargets(a, b);
  });

  const winner = results.length > 0 ? results[0] : null;
  return { results, winner };
}

export async function GET() {
  try {
    const valid = await loadVotes();
    const { results, winner } = buildResults(valid);
    const closed = isVoteClosed();

    return Response.json({
      results,
      totalVotes: valid.length,
      closed,
      closesAt: getVoteCloseTime(),
      winner: closed ? winner : null,
    });
  } catch (error) {
    console.error("Vote results failed:", error);
    return Response.json({
      results: [],
      totalVotes: 0,
      closed: isVoteClosed(),
      closesAt: getVoteCloseTime(),
      winner: null,
    });
  }
}

export async function POST(request) {
  if (isVoteClosed()) {
    return Response.json({ error: "Voting is closed for the night." }, { status: 403 });
  }

  try {
    const body = await request.json();
    const voter = normalizeName(body.voter);
    const number = parseContestantNumber(body.number);
    const deviceId = String(body.deviceId || "").trim().slice(0, 64);
    const maxNumber = getMaxNumber();

    if (!voter) {
      return Response.json({ error: "Please enter your name." }, { status: 400 });
    }

    if (number == null || number < 1 || number > maxNumber) {
      return Response.json(
        { error: "Enter a contestant number between 1 and " + maxNumber + "." },
        { status: 400 }
      );
    }

    const existing = await loadVotes();
    const voterKey = normalizeVoterKey(voter);
    const duplicate = existing.find(function (vote) {
      if (deviceId && vote.deviceId === deviceId) {
        return true;
      }
      return normalizeVoterKey(vote.voter) === voterKey;
    });

    if (duplicate) {
      return Response.json(
        { error: "That name already voted tonight — one vote per guest." },
        { status: 409 }
      );
    }

    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
    const vote = {
      id,
      voter,
      number,
      deviceId: deviceId || null,
      votedAt: new Date().toISOString(),
    };

    await put(`votes/${id}.json`, JSON.stringify(vote), {
      access: "public",
      contentType: "application/json",
    });

    return Response.json({ ok: true, message: "Vote recorded for #" + number + " — thanks!" });
  } catch (error) {
    console.error("Vote submission failed:", error);
    return Response.json({ error: "Could not record your vote. Please try again." }, { status: 500 });
  }
}
