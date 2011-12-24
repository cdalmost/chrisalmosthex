
var boardSizeIndex = 0;

var boardSizes = ["14", "11", "19"];

function rotateBoardSize() {
  boardSizeIndex = (boardSizeIndex + 1) % boardSizes.length;
  var size = boardSizes[boardSizeIndex];
  document.forms["newGame"].elements["size"].value = size;
  var link = document.getElementById('sizeLink');
  if (link) { link.innerHTML = size + 'x' + size; }
}

function validateNewGame() {
  var p1 = document.forms["newGame"].elements["p1"].value,
      p2 = document.forms["newGame"].elements["p2"].value,
      e1 = document.forms["newGame"].elements["e1"].value,
      e2 = document.forms["newGame"].elements["e2"].value;

  if (p1 && p2) {
    var email = /^([A-Za-z0-9_\-\.\+%])+\@([A-Za-z0-9_\-\.%])+\.([A-Za-z]{2,4})$/;
    if (email.test(e1) && email.test(e2)) {
      return true;
    }
    else {
      alert("Are you sure about those email addresses?")
      return false;
    }
  }
  else {
    alert("Neither name may be empty.");
    return false;
  }
}
