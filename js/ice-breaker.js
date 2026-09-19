const QUESTIONS = [
  "What's the most iconic piece of your cowboy-disco look tonight: boots, hat, fringe, or sequins?",
  "If you had to give yourself a cowboy or disco stage name tonight, what would it be?",
  "What's the funniest thing you've ever witnessed on a dance floor?",
  "You walk into a bar with a disco ball and a mechanical bull. Which one gets your attention first?",
  "What's a completely normal thing that secretly makes you want to start dancing?",
  "If you could bring one musician—country or disco—to perform at this party, who are you picking?",
  "What's the weirdest fashion combination you've ever worn and somehow pulled off?",
  "You have to enter the party dramatically: horseback, limousine, roller skates, or carried in like royalty—which are you choosing?",
  "What song could come on right now that would make you immediately abandon the conversation and hit the dance floor?",
  "What's the dumbest way you've ever injured yourself while \"having a good time\"?",
  "If tonight had an official cocktail named after you, what would it be called?",
  "If you could throw absolutely any themed party next, what would it be?",
  "What's the most unhinged late-night food combination you've eaten after a night out?",
  "Who here would you trust with complete control of the aux cord?",
  "What's one trend you're happy stayed in the past—and one you'd personally bring back?",
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
