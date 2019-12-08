
let dieButtons, playButtons, selected;

dieButtons = [];
playButtons = [];
to_throw = [0, 1, 2, 3, 4];

function DieButton (button, index) {
  this.button = button;
  this.selected = false;
  this.value = parseInt(this.button.value);
  this.index = index;

  this.selectDeselect = function() {
    this.selected = !this.selected;
    if (!to_throw.includes(this.index)) {
      to_throw.push(this.index);
      console.log("adding index: " + this.index);
    }
    else {
      console.log("removing index: " + this.index);
      console.log("removing: " + to_throw.indexOf(this.index));
      to_throw.splice(to_throw.indexOf(this.index), 1);
    }
    console.log("to throw: " + to_throw);
    console.log("Select-deselect");
  }


  this.update = function() {
    if (this.selected) {
      this.button.classList.add("selected");
    }
    else {
      this.button.classList.remove("selected");
    }
  }
}

DieButton.prototype.toString = function() {
  return "{<DieButton>selected: " + this.selected + ", value: " + this.value + "}";
}



function PlayButton (name) {
  this.name = name;
  this.button = document.getElementById(name + "-button");
  console.log(this.button);
}

PlayButton.prototype.update = function() {
  this.button.value = '[' + to_throw + ']';
  console.log("updating button: " + this.name);
  console.log(this.button.value);
}

PlayButton.prototype.toString = function() {
  return "{<PlayButton> name: " + this.name + ", button: " + this.button + "}";
}

function main() {
  console.log("Inside main");
  initialize();
  dieButtons.forEach(
    function(button) {
      setOnClickListener(button);
    }
  );
}

function setOnClickListener(button) {
  button.button.onclick = function() {
    button.selectDeselect();
    update();
  }
}

function initialize() {
  console.log("Inside initialize");
  document.querySelectorAll(".die-button").forEach(
    function(button, index) {
      dieButtons.push(new DieButton(button, index));
      console.log("Adding die button to list: " + button.name)
    }
  );

  document.querySelectorAll(".play-button").forEach(
    function(button) {
      playButtons.push(new PlayButton(button.name));
      console.log("Adding play button to list: " + button.name)
    }
  );

  update();
}

function update() {
  dieButtons.forEach(
    function(button) {
      button.update();
    }
  );
  playButtons.forEach(
    function(button) {
      button.update();
    }
  );
}

window.onload = function() {
    console.log("window loaded");
    main();
  }
