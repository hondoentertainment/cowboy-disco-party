const QUESTIONS = [
  "What's the most iconic piece of your cowboy-disco look tonight — boots, hat, or sequins?",
  "Two-step or hustle — which are you leading on the dance floor first?",
  "What's the most embarrassing thing that's ever happened to you at a country bar or disco?",
  "If this room had a disco ball and a mechanical bull, which would you ride first?",
  "What's a totally normal thing that secretly makes you want to line dance?",
  "Which song would you pick for the group boot-scoot finale — country or disco?",
  "What's the weirdest fashion combo you've ever worn and still pulled off?",
  "If someone here challenged you to a hat toss, buckle shine, or mirror-ball stare-down, which are you accepting?",
  "What's your signature move when the DJ drops a surprise country-disco mashup?",
  "What's the dumbest way you've ever injured yourself while \"having a good time\"?",
  "Saddle brown, disco gold, or electric blue — what's your power color tonight?",
  "If you could throw a party with any theme imaginable, what would it be?",
  "What's the most unhinged late-night snack combo you've ever eaten after dancing?",
  "Who at this party would you trust to call the next line dance?",
  "What's one trend you're glad stayed in the past — and one you're bringing back tonight?",
];

(function () {
  "use strict";

  var grid = document.getElementById("ice-breaker-grid");
  var shuffleBtn = document.getElementById("ice-breaker-shuffle");
  var shuffleStatus = document.getElementById("ice-breaker-status");

  function renderQuestions(questions) {
    if (!grid) {
      return;
    }

    grid.innerHTML = "";
    questions.forEach(function (question, index) {
      var item = document.createElement("li");
      item.className = "ice-breaker-card";
      item.innerHTML =
        '<span class="ice-breaker-card__number" aria-hidden="true">' +
        (index + 1) +
        '</span><p class="ice-breaker-card__text">' +
        question +
        "</p>";
      grid.appendChild(item);
    });
  }

  function shuffleQuestions() {
    var shuffled = QUESTIONS.slice();
    for (var i = shuffled.length - 1; i > 0; i -= 1) {
      var j = Math.floor(Math.random() * (i + 1));
      var temp = shuffled[i];
      shuffled[i] = shuffled[j];
      shuffled[j] = temp;
    }
    renderQuestions(shuffled);
    if (shuffleStatus) {
      shuffleStatus.textContent = "Deck shuffled — " + shuffled.length + " fresh prompts ready.";
    }
  }

  renderQuestions(QUESTIONS);

  if (shuffleBtn) {
    shuffleBtn.addEventListener("click", shuffleQuestions);
  }
})();
