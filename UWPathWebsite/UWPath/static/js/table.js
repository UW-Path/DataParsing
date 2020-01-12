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
  ]).on('drop', function (el) {
    emptyTrash()
  });
};


/* Vanilla JS to add a new task */
function addTask() {
  debugger
  /* Get task text from input */
  var inputTask = document.getElementById("taskText").value.toUpperCase();

  /* Add task to the 'Required' column */
  $.ajax({
    url: 'http://127.0.0.1:8000/api/course-info/get/' + inputTask,
    type: 'get', // This is the default though, you don't actually need to always mention it
    success: function(data) {
        document.getElementById("required").innerHTML +=
            "<li class='task'><p>" + inputTask + "</p></li>";
    },
      error: function(data) {
        document.getElementById("required").innerHTML +=
            "<li class='task'><p>" + inputTask + " *</p></li>";
    }
});
  /* Clear task text from input after adding task */
  document.getElementById("taskText").value = "";
}

/* Vanilla JS to delete tasks in 'Trash' column */
function emptyTrash() {
  /* Clear tasks from 'Trash' column */
  document.getElementById("trash").innerHTML = "";
}
