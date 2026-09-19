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

  var stage = document.getElementById("ice-breaker-stage");
  var grid = document.getElementById("ice-breaker-grid");
  var nextBtn = document.getElementById("ice-breaker-next");
  var shuffleBtn = document.getElementById("ice-breaker-shuffle");
  var shuffleStatus = document.getElementById("ice-breaker-status");

  var deck = QUESTIONS.slice();
  var index = 0;

  function haptic() {
    if (navigator.vibrate) {
      navigator.vibrate(12);
    }
  }

  function renderStage() {
    if (!stage) {
      return;
    }

    var question = deck[index];
    stage.innerHTML =
      '<article class="ice-breaker-card ice-breaker-card--solo">' +
      '<span class="ice-breaker-card__number" aria-hidden="true">' +
      (index + 1) +
      " / " +
      deck.length +
      '</span><p class="ice-breaker-card__text">' +
      question +
      "</p></article>";
  }

  function setStatus(message) {
    if (shuffleStatus) {
      shuffleStatus.textContent = message || "";
    }
  }

  function nextQuestion() {
    index = (index + 1) % deck.length;
    renderStage();
    haptic();
    setStatus("");
  }

  function shuffleQuestions() {
    for (var i = deck.length - 1; i > 0; i -= 1) {
      var j = Math.floor(Math.random() * (i + 1));
      var temp = deck[i];
      deck[i] = deck[j];
      deck[j] = temp;
    }
    index = 0;
    renderStage();
    haptic();
    setStatus("Deck shuffled — " + deck.length + " prompts ready.");
  }

  if (grid) {
    grid.classList.add("is-hidden");
    grid.setAttribute("aria-hidden", "true");
  }

  renderStage();

  if (nextBtn) {
    nextBtn.addEventListener("click", nextQuestion);
  }

  if (shuffleBtn) {
    shuffleBtn.addEventListener("click", shuffleQuestions);
  }
})();
