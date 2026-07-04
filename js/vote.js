(function () {
  "use strict";

  var config = window.CDP || {};
  var dateTbd = Boolean(config.PARTY_DATE_TBD || !config.VOTE_CLOSE_TIME);
  var VOTE_KEY = "cdp-best-outfit-vote";
  var DEVICE_KEY = "cdp-device-id";

  function getDeviceId() {
    var id = localStorage.getItem(DEVICE_KEY);
    if (!id) {
      id = "d-" + Date.now() + "-" + Math.random().toString(36).slice(2, 11);
      localStorage.setItem(DEVICE_KEY, id);
    }
    return id;
  }
  var closeTime = config.VOTE_CLOSE_TIME;
  var maxNumber = config.VOTE_MAX_NUMBER ? config.VOTE_MAX_NUMBER : 99;

  var form = document.getElementById("vote-form");
  var status = document.getElementById("vote-status");
  var resultsEl = document.getElementById("vote-results");
  var resultsList = document.getElementById("vote-results-list");
  var resultsTotal = document.getElementById("vote-results-total");
  var submitBtn = document.getElementById("vote-submit");
  var winnerEl = document.getElementById("vote-winner");
  var winnerName = document.getElementById("vote-winner-name");
  var winnerCount = document.getElementById("vote-winner-count");
  var voteOpenNote = document.getElementById("vote-open-note");
  var numberInput = document.getElementById("vote-number");

  if (numberInput) {
    numberInput.max = String(maxNumber);
  }

  function formatContestant(item) {
    if (item.number != null) {
      return "#" + item.number;
    }
    return item.nominee || "Unknown";
  }

  function setStatus(message, type) {
    if (!status) {
      return;
    }
    status.textContent = message;
    status.className = "form-note" + (type ? " form-note--" + type : "");
  }

  function formatCloseTime() {
    if (!closeTime) {
      return "party night";
    }
    return new Date(closeTime).toLocaleString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  }

  function applyClosedState(data) {
    if (!data.closed) {
      if (voteOpenNote) {
        voteOpenNote.textContent = "Voting closes " + formatCloseTime() + ".";
        voteOpenNote.classList.remove("is-hidden");
      }
      return;
    }

    if (voteOpenNote) {
      voteOpenNote.classList.add("is-hidden");
    }

    if (form) {
      form.classList.add("is-closed");
    }

    if (submitBtn) {
      submitBtn.disabled = true;
    }

    if (winnerEl && data.winner) {
      winnerName.textContent = formatContestant(data.winner);
      winnerCount.textContent =
        data.winner.count + (data.winner.count === 1 ? " vote" : " votes");
      winnerEl.classList.remove("is-hidden");
    }

    setStatus("Voting is closed for the night.", "success");
  }

  function renderResults(data) {
    if (!resultsEl || !resultsList || !resultsTotal) {
      return;
    }

    applyClosedState(data);
    resultsList.innerHTML = "";
    var results = data.results || [];

    if (results.length === 0) {
      resultsTotal.textContent = data.closed
        ? "No votes were cast."
        : "No votes yet — cast the first one!";
      resultsEl.classList.remove("is-hidden");
      return;
    }

    resultsTotal.textContent = data.closed
      ? "Final results — " +
        (data.totalVotes === 1 ? "1 vote" : data.totalVotes + " votes")
      : data.totalVotes === 1
        ? "1 vote counted"
        : data.totalVotes + " votes counted";

    results.forEach(function (item, index) {
      var row = document.createElement("li");
      row.className = "vote-result" + (data.closed && index === 0 ? " vote-result--winner" : "");
      row.innerHTML =
        '<span class="vote-result__rank">' +
        (index + 1) +
        '</span><span class="vote-result__name">' +
        formatContestant(item) +
        '</span><span class="vote-result__count">' +
        item.count +
        (item.count === 1 ? " vote" : " votes") +
        "</span>";
      resultsList.appendChild(row);
    });

    resultsEl.classList.remove("is-hidden");
  }

  function loadResults() {
    return fetch("/api/vote")
      .then(function (response) {
        return response.json();
      })
      .then(renderResults)
      .catch(function () {
        if (resultsTotal) {
          resultsTotal.textContent = "Live results unavailable offline.";
        }
      });
  }

  if (localStorage.getItem(VOTE_KEY) && form) {
    form.classList.add("is-voted");
    if (!form.classList.contains("is-closed")) {
      setStatus("You already voted — thanks!", "success");
    }
    if (submitBtn && !form.classList.contains("is-closed")) {
      submitBtn.disabled = true;
    }
  }

  if (form && status) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();

      if (form.classList.contains("is-closed")) {
        setStatus("Voting is closed for the night.", "error");
        return;
      }

      if (localStorage.getItem(VOTE_KEY)) {
        setStatus("You already voted on this device.", "error");
        return;
      }

      var voter = form.voter.value.trim();
      var number = parseInt(form.number.value, 10);

      if (!voter) {
        setStatus("Please enter your name.", "error");
        return;
      }

      if (!Number.isInteger(number) || number < 1 || number > maxNumber) {
        setStatus("Enter a contestant number between 1 and " + maxNumber + ".", "error");
        return;
      }

      submitBtn.disabled = true;
      setStatus("Recording your vote…");

      fetch("/api/vote", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ voter: voter, number: number, deviceId: getDeviceId() }),
      })
        .then(function (response) {
          return response.json().then(function (data) {
            if (!response.ok) {
              throw new Error(data.error || "Vote failed.");
            }
            return data;
          });
        })
        .then(function (data) {
          localStorage.setItem(VOTE_KEY, new Date().toISOString());
          form.classList.add("is-voted");
          setStatus(data.message || "Vote recorded — thanks!", "success");
          return loadResults();
        })
        .catch(function (error) {
          setStatus(error.message || "Something went wrong. Please try again.", "error");
          if (!form.classList.contains("is-closed")) {
            submitBtn.disabled = false;
          }
        });
    });
  }

  loadResults();
  setInterval(loadResults, 15000);
})();
