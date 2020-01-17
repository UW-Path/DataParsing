// TODO - This will be dependent on how many terms the user specifies.
const terms = ["1A", "1B", "2A", "2B", "3A", "3B", "4A", "4B"];

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
  ]).on('drop', function (el, target) {
      const term = $(target).attr("id");
      let draggedId = el.id;

      if (term === "trash") {
          let term_index = 0;
          emptyTrash();
          checkSchedule(term_index)
      }
      else if (term === "required"){
          // no operations if courses are dragged back to required courses
          // need to change in future because all course needs to be validated again
          document.getElementById(draggedId).style.color = "darkslateblue"; // back to original color
      }
      else {
          debugger
          let term_index = terms.indexOf(term);
          checkSchedule(term_index);
      }
  });
};


function checkSchedule(term_index) {
    var num_terms = terms.length;
    var list_of_courses_taken = getTaken(term_index);

    for (var i = term_index; i < num_terms; i++) {
        var current_term_courses = getCurrent(i);
        var current_term_courses_text = current_term_courses[1];
        current_term_courses = current_term_courses[0];
        var arrayLen = current_term_courses.length;

        if (arrayLen) {
            for (var j = 0; j < arrayLen; j++) {
                var course_li = current_term_courses[j];
                let course = course_li.innerText.trim();

                if (!(course.endsWith("*") || course.includes(","))) {
                    draggedId = course_li.id;
                    $.ajax({
                        url: 'http://127.0.0.1:8000/api/meets_prereqs/get/' + course,
                        type: 'get',
                        data: {
                            list_of_courses_taken: list_of_courses_taken,
                            current_term_courses: current_term_courses_text
                        },
                        async: false,
                        success: function (data) {
                            debugger
                            var can_take = data.can_take;

                            // Do something
                            if (can_take) {
                                document.getElementById(draggedId).style.color = "green";
                            } else {
                                document.getElementById(draggedId).style.color = "red";
                            }
                        },
                        error: function () {
                            debugger
                            document.getElementById(draggedId).style.color = "grey";
                            // alert("Error: cannot determine if course can be taken.")
                        }
                    });
                }
            }

            list_of_courses_taken = list_of_courses_taken.concat(current_term_courses_text);
        }
    }
}

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


function getTaken(term_index) {
    var taken = [];

    for (var i = 0; i < term_index; i++) {
        var term_courses = getCurrent(i)[1];
        taken = taken.concat(term_courses);
    }
    return taken;
}

function getCurrent(term_index) {
    var term_courses = document.getElementById(terms[term_index]).getElementsByTagName("li");
    var term_courses_text = Array.from(term_courses).map(function(c) {
        return $(c).text().trim().split(", ");
    });
    // merges split arrays into one flattened array
    term_courses_text = [].concat.apply([], term_courses_text);
    return [term_courses, term_courses_text];
}
