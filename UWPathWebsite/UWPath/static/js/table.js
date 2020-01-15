const terms = ["1A", "1B", "2A", "2B", "3A", "3B", "4A", "4B", "5A", "5B"];

/* Custom Dragula JS */
window.onload = function() {
  dragula([
    document.getElementById("required"),
    document.getElementById("1A"),
    document.getElementById("1B"),
    document.getElementById("2A"),
    document.getElementById("2B"),
    document.getElementById("3A"),
    document.getElementById("3B"),
    document.getElementById("4A"),
    document.getElementById("4B"),
    document.getElementById("5A"),
    document.getElementById("5B"),
    document.getElementById("trash")
  ]).on('drop', function (el, target, source) {
      const course = $(el).text().trim();
      const term = $(target).attr("id");
      const sourceId = $(source).attr("id");
      const draggedId = el.id;

      if (term === "trash") {
          emptyTrash();
      }
      else if (term === "required"){
          //no operations if courses are dragged back to required courses
          // need to change in future because all course needs to be validated again
          document.getElementById(draggedId).style.color = "darkslateblue"; //back to original color
          return
      }
      else if (!(course.endsWith("*") || course.includes(","))) {
          /* This else statement is not implemented. It just passes through. */
          var list_of_courses_taken = getTaken(term);
          var current_term_courses = getCurrent(term);
          $.ajax({
              url: 'http://127.0.0.1:8000/api/meets_prereqs/get/' + course,
              type: 'get', // This is the default though, you don't actually need to always mention it
              data: {list_of_courses_taken: list_of_courses_taken, current_term_courses: current_term_courses},
              async: false,
              success: function(data) {
                  var can_take = data.can_take;
                  console.log(can_take);
                  // Do something
                  if (can_take){
                    document.getElementById(draggedId).style.color = "green";
                  }
                  else {
                    document.getElementById(draggedId).style.color = "red";
                  }
              },
              error: function(data) {
                  document.getElementById(draggedId).style.color = "grey";
                  // alert("Error: cannot determine if course can be taken.")
              }
          });
      }
      else {
          // Do something when course is not a real course code.
          //Hao Wei: I think this returns error above
      }
  });
};


/* Vanilla JS to add a new task */
function addTask() {
    /* Get task text from input */
    const inputTask = document.getElementById("taskText").value.toUpperCase();
    var id = inputTask + "(" + Math.round(Math.random() * 100 )  +")"; //generate random number to prevent unique id
    id = id.replace(" ", "");
    // check if inputTask has whitespace
    if (/\S/.test(inputTask)) {
        /* Add task to the 'Required' column */
        $.ajax({
            url: 'http://127.0.0.1:8000/api/course-info/get/' + inputTask,
            type: 'get', // This is the default though, you don't actually need to always mention it
            success: function (data) {
                document.getElementById("required").innerHTML +=
                    "<li class='task' id='" + id + "'>" + "<p>" + inputTask + "</p></li>";
            },
            error: function (data) {
                document.getElementById("required").innerHTML +=
                    "<li class='task' id='" + id + "'>" + "<p>" + inputTask + " *</p></li>";
            }
        });
        /* Clear task text from input after adding task */
        document.getElementById("taskText").value = "";
    }
}

/* Vanilla JS to delete tasks in 'Trash' column */
function emptyTrash() {
  /* Clear tasks from 'Trash' column */
  document.getElementById("trash").innerHTML = "";
}

function getTaken(term) {
    var taken = [];
    var arrayLength = terms.indexOf(term);

    for (var i = 0; i < arrayLength; i++) {
        var term_courses = document.getElementById(terms[i]).getElementsByTagName("li");

        term_courses = Array.from(term_courses).map(function(c) {
            return $(c).text().trim().split(", ");
        });

        // merges split arrays into one flattened array
        term_courses = [].concat.apply([], term_courses);

        // concat to taken
        taken = taken.concat(term_courses);
    }
    return taken;
}

function getCurrent(term) {
    var term_courses = document.getElementById(term).getElementsByTagName("li");
    term_courses = Array.from(term_courses).map(function(c) {
        return $(c).text().trim().split(", ");
    });
    // merges split arrays into one flattened array
    term_courses = [].concat.apply([], term_courses);
    return term_courses;
}
