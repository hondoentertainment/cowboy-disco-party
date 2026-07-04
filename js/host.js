(function () {
  "use strict";

  var STORAGE_KEY = "cdp-host-checklist";
  var adminCode = sessionStorage.getItem("cdp-admin-code") || "";

  var codeForm = document.getElementById("host-code-form");
  var codeInput = document.getElementById("host-code");
  var dashboard = document.getElementById("host-dashboard");
  var status = document.getElementById("host-status");
  var systemStatus = document.getElementById("host-system-status");
  var voteStatus = document.getElementById("host-vote-status");
  var voteLeaderboard = document.getElementById("host-vote-leaderboard");
  var checklist = document.getElementById("host-checklist");
  var shareMessage = document.getElementById("host-share-message");
  var copyInviteBtn = document.getElementById("host-copy-invite");

  var defaultItems = [
    "Set GALLERY_ADMIN_CODE in Vercel for host tools (poll results)",
    "Print party kit: invitations, QR, signs, labels, number tags (/party-kit.html)",
    "Post QR sign at the entrance",
    "Hang the Cowboy Disco Saloon sign on the door",
    "Copy and send guest invite text (below)",
    "Test gallery upload on phone over cellular",
    "Test Best Outfit vote by contestant number on phone",
    "Open photo slideshow on the TV (/slideshow.html)",
    "Open Ice Breakers full-screen for warm-ups",
    "Review party-night run-of-show (/party-night.html)",
  ];

  function setStatus(message, type) {
    if (!status) {
      return;
    }
    status.textContent = message;
    status.className = "form-note" + (type ? " form-note--" + type : "");
  }

  function formatContestant(item) {
    if (item.number != null) {
      return "#" + item.number;
    }
    return item.nominee || "Unknown";
  }

  function loadChecks() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    } catch (error) {
      return {};
    }
  }

  function saveChecks(checks) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(checks));
  }

  function renderChecklist() {
    if (!checklist) {
      return;
    }

    var checks = loadChecks();
    checklist.innerHTML = "";

    defaultItems.forEach(function (label, index) {
      var id = "host-check-" + index;
      var item = document.createElement("label");
      item.className = "host-check";
      item.innerHTML =
        '<input type="checkbox" id="' +
        id +
        '"' +
        (checks[id] ? " checked" : "") +
        ">" +
        "<span>" +
        label +
        "</span>";
      checklist.appendChild(item);
    });

    checklist.querySelectorAll("input").forEach(function (input) {
      input.addEventListener("change", function () {
        var next = loadChecks();
        next[input.id] = input.checked;
        saveChecks(next);
      });
    });
  }

  function renderLeaderboard(results) {
    if (!voteLeaderboard) {
      return;
    }

    var top = (results || []).slice(0, 3);
    if (!top.length) {
      voteLeaderboard.classList.add("is-hidden");
      voteLeaderboard.innerHTML = "";
      return;
    }

    voteLeaderboard.innerHTML = "";
    top.forEach(function (item, index) {
      var row = document.createElement("li");
      row.textContent =
        (index + 1) + ". " + formatContestant(item) + " — " + item.count + (item.count === 1 ? " vote" : " votes");
      voteLeaderboard.appendChild(row);
    });
    voteLeaderboard.classList.remove("is-hidden");
  }

  function loadSystemStatus() {
    if (!systemStatus) {
      return;
    }

    fetch("/api/status")
      .then(function (response) {
        return response.json();
      })
      .then(function (data) {
        var parts = [];
        parts.push("Gallery uploads publish instantly.");
        parts.push(
          data.voteClosed
            ? "Voting is closed."
            : "Voting open until " +
                new Date(data.voteCloseTime).toLocaleString("en-US", {
                  weekday: "short",
                  hour: "numeric",
                  minute: "2-digit",
                }) +
                "."
        );
        systemStatus.textContent = parts.join(" ");
      })
      .catch(function () {
        systemStatus.textContent = "Could not load system status.";
      });
  }

  function loadVoteStatus() {
    if (!voteStatus) {
      return;
    }

    fetch("/api/vote")
      .then(function (response) {
        return response.json();
      })
      .then(function (data) {
        if (data.closed && data.winner) {
          voteStatus.innerHTML =
            "<strong>Voting closed.</strong> Winner: <strong>" +
            formatContestant(data.winner) +
            "</strong> (" +
            data.winner.count +
            (data.winner.count === 1 ? " vote" : " votes") +
            ")";
          renderLeaderboard(data.results);
          return;
        }

        if (data.closed) {
          voteStatus.textContent = "Voting is closed. No votes were cast.";
          renderLeaderboard([]);
          return;
        }

        voteStatus.textContent =
          "Voting open — " +
          (data.totalVotes === 1 ? "1 vote" : data.totalVotes + " votes") +
          " so far. Closes " +
          new Date(data.closesAt).toLocaleString("en-US", {
            weekday: "short",
            hour: "numeric",
            minute: "2-digit",
          }) +
          ".";
        renderLeaderboard(data.results);
      })
      .catch(function () {
        voteStatus.textContent = "Vote status unavailable.";
      });
  }

  if (shareMessage) {
    shareMessage.textContent =
      window.CDP && window.CDP.SHARE_MESSAGE
        ? window.CDP.SHARE_MESSAGE
        : "Cowboy Disco Party: https://cowboy-disco-party.vercel.app";
  }

  if (copyInviteBtn) {
    copyInviteBtn.addEventListener("click", function () {
      var message = shareMessage ? shareMessage.textContent : "";
      if (!message || !navigator.clipboard) {
        return;
      }
      navigator.clipboard.writeText(message).then(function () {
        copyInviteBtn.textContent = "Copied!";
        setTimeout(function () {
          copyInviteBtn.textContent = "Copy invite text";
        }, 2000);
      });
    });
  }

  if (codeForm && codeInput) {
    if (adminCode) {
      codeInput.value = adminCode;
      if (dashboard) {
        dashboard.classList.remove("is-hidden");
      }
    }

    codeForm.addEventListener("submit", function (event) {
      event.preventDefault();
      adminCode = codeInput.value.trim();
      if (!adminCode) {
        setStatus("Enter the host admin code.", "error");
        return;
      }

      fetch("/api/poll?admin=1&code=" + encodeURIComponent(adminCode))
        .then(function (response) {
          return response.json().then(function (data) {
            if (!response.ok) {
              throw new Error(data.error || "Invalid admin code.");
            }
            return data;
          });
        })
        .then(function () {
          sessionStorage.setItem("cdp-admin-code", adminCode);
          if (dashboard) {
            dashboard.classList.remove("is-hidden");
          }
          setStatus("Host dashboard unlocked.", "success");
          loadSystemStatus();
          loadVoteStatus();
        })
        .catch(function (error) {
          setStatus(error.message, "error");
        });
    });
  }

  renderChecklist();
  loadSystemStatus();
  loadVoteStatus();
  setInterval(loadVoteStatus, 30000);
  setInterval(loadSystemStatus, 60000);
})();
