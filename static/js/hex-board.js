
function drawBoard(n, state, last, player, mover) {
  // Only the current player is allowed to resign.
  if (player == mover) {
    resign = document.getElementById('resign');
    if (resign) { resign.disabled = false; }
  }
  // Define some constants.
  var r = 18, // radius of each hex
      sqrt3 = 1.7320508075688772,
      slope = -0.57735026918962584,
      w = 6 + (3 * n - 1) * r,
      h = 6 + n * r * sqrt3,
      board = Raphael('hex-board', w, h);
  // Draw the outline of the board, the coloured edges.
  board.path(["M", 0, h/2-6, "L", w/2, 0]).attr({"stroke": "red",  "stroke-width": 12});
  board.path(["M", w/2, 0, "L", w, h/2-6]).attr({"stroke": "blue", "stroke-width": 12});
  board.path(["M", w, h/2+6, "L", w/2, h]).attr({"stroke": "red",  "stroke-width": 12});
  board.path(["M", w/2, h, "L", 0, h/2+6]).attr({"stroke": "blue", "stroke-width": 12});
  // Function to draw the (animated) hexes.
  function hex(cx, cy, r, params) {
    var rby2 = r / 2;
    return board.path(
        ["M", cx - r, cy,
        "L", cx - rby2, cy - (sqrt3 * rby2),
        "L", cx + rby2, cy - (sqrt3 * rby2),
        "L", cx + r, cy,
        "L", cx + rby2, cy + (sqrt3 * rby2),
        "L", cx - rby2, cy + (sqrt3 * rby2),
        "z"]).attr(params);
  }
  // Function to record the move and activate the "Make this move" link.
  function showMakeMove(i, j) {
    var coords = document.getElementById('coords');
        button = document.getElementById('make-move');
    if (coords) { coords.value = i.toString() + " " + j.toString(); }
    if (button) { button.disabled = false; }
  }
  // Define the shade colour for prospective moves.
  if (player == "r") { shade = "rgb(255, 127, 127)"; }
  if (player == "b") { shade = "rgb(127, 127, 255)"; }
  // More constants.
  var hoffset = 3 + n * r * sqrt3 / 2,
      woffset = 3,
      tiles = board.set(), // collection of all hexes
      potential = null;    // hex selected for move
  // Function to draw and decorate each hex.
  function process(i, j) {
    var cx = woffset + r * (1 + i * 1.5 + j * 1.5),
        cy = hoffset + r * (i * sqrt3 / 2 + slope * j * 1.5),
        c = "white",
        s = state.charAt(n * i + j);
    if (s == "r") { c = "red"; }
    if (s == "b") { c = "blue"; }
    // Draw and colour the hex appropriately.
    var t = hex(cx, cy, r, {"fill": c, "stroke": "black", "stroke-width": 3});
    if (last == n * i + j) { board.circle(cx, cy, 5).attr({"stroke-width": 3}); }
    // Add the animation if the hex is white.
    if (c == "white") {
      t.mouseover(function () {
        t.toFront();
        t.attr("fill", shade);
        t.animate({scale: [1.1, 1.1, cx, cy]}, 500, "elastic");
      }).mouseout(function () {
        t.animate({scale: [1, 1, cx, cy]}, 500, "elastic");
        if (t != potential) { t.attr("fill", "white"); }
      }).mouseup(function () {
        if (player == mover) {
          if (potential) { potential.attr("fill", "white"); }
          t.attr("fill", shade);
          potential = t;
          showMakeMove(i, j);
        }
      });
    }
    tiles.push(t);
  }
  for (var i=0; i<n; i++) {
    for (var j=0; j<n; j++) {
      process(i, j); // Javascript is silly.
    }
  }
  return tiles;
}

function openChannel(token) {
  channel = new goog.appengine.Channel(token);
  socket = channel.open();
  socket.onopen    = function ()  {};
  socket.onclose   = function ()  {};
  socket.onerror   = function ()  {};
  socket.onmessage = function (m) {
    if (m.data == "reload") { location.reload(true); }
  };
}
