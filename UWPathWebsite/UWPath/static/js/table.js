// TODO - This will be dependent on how many terms the user specifies.
var terms = ["1A", "1B", "2A", "2B", "3A", "3B", "4A", "4B"]; //Add 5A 5B for Double Degrees
var dragger = dragula([]);
// same as first func
function initDragula() {
    dragger.destroy();
    dragger = dragula([
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
        document.getElementById("6A"),
        document.getElementById("6B"),
        document.getElementById("7A"),
        document.getElementById("7B"),
        document.getElementById("8A"),
        document.getElementById("8B"),
        document.getElementById("9A"),
        document.getElementById("9B"),
        document.getElementById("10A"),
        document.getElementById("10B"),
        document.getElementById("trash")
    ]);

    dragger.on('drop', function (el, target, source) {
        const term = $(target).attr("id");
        const src = $(source).attr("id");
        let draggedId = el.id;
        let termIndex = 0;

        if (term === "trash") {
            emptyTrash();
            checkSchedule(termIndex);
        } else if (term === "required") {
            // no operations if courses are dragged back to required courses
            // need to change in future because all course needs to be validated again
            document.getElementById(draggedId).style.color = "darkslateblue"; // back to original color
            checkSchedule(termIndex);
        } else {
            if (src === "required") {
                //only check schedule for course after term has been dropped
                termIndex = terms.indexOf(term);
            } else {
                //src is Term Number
                termIndex = Math.min(terms.indexOf(src), terms.indexOf(term));
            }
            // else needs to check all schedule again`
            checkSchedule(termIndex);
        }
    });
}


/* Custom Dragula JS */
window.onload = function(){
    this.initDragula();
};

function checkSchedule(term_index) {
    const numTerms = terms.length;
    let listOfCoursesTaken = getTaken(term_index);

    for (let i = term_index; i < numTerms; i++) {
        let currentTermCourses = getCurrent(i);
        const currentTermCoursesText = currentTermCourses[1];
        currentTermCourses = currentTermCourses[0];
        let arrayLen = currentTermCourses.length;

        if (arrayLen) {
            for (let j = 0; j < arrayLen; j++) {
                let course_li = currentTermCourses[j];
                let course = course_li.innerText.trim();

                if (!(course.endsWith("*") || course.includes(","))) {
                    draggedId = course_li.id;
                    $.ajax({
                        url: 'http://127.0.0.1:8000/api/meets_prereqs/get/' + course,
                        type: 'get',
                        data: {
                            list_of_courses_taken: listOfCoursesTaken,
                            current_term_courses: currentTermCoursesText
                        },
                        async: false,
                        success: function (data) {
                            let can_take = data.can_take;
                            // Do something
                            if (can_take) {
                                document.getElementById(draggedId).style.color = "green";
                            } else {
                                document.getElementById(draggedId).style.color = "red";
                            }
                        },
                        error: function () {
                            document.getElementById(draggedId).style.color = "grey";
                            // alert("Error: cannot determine if course can be taken.")
                        }
                    });
                }
            }
            listOfCoursesTaken = listOfCoursesTaken.concat(currentTermCoursesText);
        }
    }
}

/* Vanilla JS to add a new task */
function addTask() {
    /* Get task text from input */
    const inputTask = document.getElementById("taskText").value.toUpperCase();
    let id = inputTask + "(" + Math.round(Math.random() * 100) + ")"; //generate random number to prevent unique id
    id = id.replace(" ", "");
    // check if inputTask has whitespace
    if (/\S/.test(inputTask)) {
        /* Add task to the 'Required' column */
        $.ajax({
            url: 'http://127.0.0.1:8000/api/course-info/get/' + inputTask,
            type: 'get', // This is the default though, you don't actually need to always mention it
            success: function (data) {
                document.getElementById("required").innerHTML +=
                    "<li class='task' id='" + id + "' onclick='popupWindow(\"" + id + "\",-1)'>" + "<p>" + inputTask + "</p></li>";
            },
            error: function (data) {
                document.getElementById("required").innerHTML +=
                    "<li class='task' id='" + id + "' onclick='popupWindow(\"" + id + "\",-1)'>" + "<p>" + inputTask + " *</p></li>";
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

function addTerm() {
    var ul = document.getElementById("table");
    var li = document.createElement("li");
    var children = ul.children.length + 2;
    li.classList.add('column');
    if (children % 8 === 2 || children % 8 === 3) {
        li.classList.add('oneA-column');
    } else if (children % 8 === 4 || children % 8 === 5) {
        li.classList.add('twoA-column');
    } else if (children % 8 === 6 || children % 8 === 7) {
        li.classList.add('threeA-column');
    } else {
        li.classList.add('fourA-column');
    }
    var term = (children % 2) ? "B" : "A";
    term = Math.floor(children / 2).toString() + term;
    terms = terms.concat(term);
    li.innerHTML = "<div class='column-header'><h4>" + term + "</h4></div><ul class='task-list' id=" + term + "></ul>";
    ul.appendChild(li);
    initDragula();
}

function getTaken(term_index) {
    let taken = [];

    for (let i = 0; i < term_index; i++) {
        let term_courses = getCurrent(i)[1];
        taken = taken.concat(term_courses);
    }
    return taken;
}

function getCurrent(term_index) {
    let el = document.getElementById(terms[term_index]);
    let termCourses = el.getElementsByTagName("li");
    let termCoursesText = Array.from(termCourses).map(function (c) {
        let id = c.id;
        c.onclick = function() {popupWindow(id, term_index);};
        return $(c).text().trim().split(", ");
    });
    // merges split arrays into one flattened array
    termCoursesText = [].concat.apply([], termCoursesText);
    return [termCourses, termCoursesText];
}

function filter_courses(start, end, code) {
    let course_title = {};
    $.ajax({
        url: 'http://127.0.0.1:8000/api/course-info/filter',
        type: 'get',
        data: {
            start: start,
            end: end,
            code: code
        },
        async: false,
        success: function (data) {
            let i;
            for (i = 0; i < data.length; i++) {
                course_title[data[i].course_code] = data[i].course_name;
            }
        },
        error: function (xhr, status, error) {
            var err = eval("(" + xhr.responseText + ")");
            alert(err.Message);
        }
    });
    return course_title;
}

function getListOfCourses(course_text) {
    let courses = {};
    let number_regex = /[1-9][0-9][0-9]/g;
    let range_regex = /[A-Z]+\s?[1-9][0-9][0-9][A-Z]?-[A-Z]+\s?[1-9][0-9][0-9][A-Z]?/g;
    let level_regex = /[A-Z]+ [1-9]00-/g;
    let course_regex = /[A-Z]+\s?[1-9][0-9][0-9][A-Z]?/g;
    let code_regex = /[A-Z]+/;

    let course, start, end, code, i;

    // Generate courses from range
    let range_courses = course_text.match(range_regex);
    if (range_courses) {
        for (i = 0; i < range_courses.length; i++) {
            course = range_courses[i].match(course_regex);
            start = course[0].match(number_regex)[0];
            end = course[1].match(number_regex)[0];
            code = course[0].match(code_regex)[0];
            let filtered_courses = filter_courses(start, end, code);
            courses = Object.assign({}, courses, filtered_courses);
        }
        course_text = course_text.replace(range_regex, "");
    }

    // Generate courses from level
    let level_courses = course_text.match(level_regex);
    if (level_courses) {
        for (i = 0; i < level_courses.length; i++) {
            course = level_courses[i].match(course_regex);
            start = course[0].match(number_regex)[0];
            end = 1000;
            code = course[0].match(code_regex)[0];
            if (code == "MATH") {
                let codes = ["ACTSC", "AMATH", "CO", "CS", "MATBUS", "MATH", "PMATH", "STAT"];
                let j;
                for (j = 0; j < codes.length; j++) {
                    let filtered_courses = filter_courses(start, end, codes[j]);
                    courses = Object.assign({}, courses, filtered_courses);
                }
            } else {
                let filtered_courses = filter_courses(start, end, code);
                courses = Object.assign({}, courses, filtered_courses);
            }
        }
        course_text = course_text.replace(level_regex, "");
    }

    // Generate courses from courses
    let other_courses = course_text.match(course_regex);
    if (other_courses) {
        let filtered_courses = filter_courses(0, 1000, other_courses.toString());
        courses = Object.assign({}, courses, filtered_courses);
        course_text = course_text.replace(course_regex, "");
    }

    if (course_text === "English List I") {
        let filtered_courses = ["EMLS 101R", "EMLS 102R", "EMLS 129R", "ENGL 129R", "ENGL 109", "SPCOM 100", "SPCOM 223"];
        filtered_courses = filter_courses(0, 1000, filtered_courses.toString());
        courses = Object.assign({}, courses, filtered_courses);
    } else if (course_text === "English List II") {
        let filtered_courses = ["EMLS 101R", "EMLS 102R", "EMLS 129R", "ENGL 129R", "ENGL 109", "SPCOM 100", "SPCOM 223",
            "EMLS 103R", "EMLS 104R", "EMLS 110R", "ENGL 108B", "ENGL 108D", "ENGL 119", "ENGL 208B", "ENGL 209",
            "ENGL 210E", "ENGL 210F", "ENGL 378", "MTHEL 300", "SPCOM 225", "SPCOM 227", "SPCOM 228"];
        filtered_courses = filter_courses(0, 1000, filtered_courses.toString());
        courses = Object.assign({}, courses, filtered_courses);
    } else if (course_text === "MATH") {
        codes = ["ACTSC", "AMATH", "CO", "CS", "MATBUS", "MATH", "PMATH", "STAT"];
        let filtered_courses = filter_courses(100, 1000, codes.toString());
        courses = Object.assign({}, courses, filtered_courses);
    } else if (course_text === "NON-MATH") {
        codes = ["ACTSC", "AMATH", "CO", "CS", "MATBUS", "MATH", "PMATH", "STAT"];
        let filtered_courses = filter_courses(100, 1000, "~" + codes.toString());
        courses = Object.assign({}, courses, filtered_courses);
    } else if (course_text === "Elective") {
        let filtered_courses = filter_courses(100, 1000, "none");
        courses = Object.assign({}, courses, filtered_courses);
    } else {
        // Generate courses from code
        let code_courses = course_text.match(code_regex);
        if (code_courses) {
            for (i = 0; i < code_courses.length; i++) {
                let filtered_courses = filter_courses(100, 1000, code_courses[i]);
                courses = Object.assign({}, courses, filtered_courses);
            }
            course_text = course_text.replace(code_regex, "");
        }
    }

    return courses;
}

function closePopup() {
    let popup1 = document.getElementById("popup-1");
    popup1.style.display = "none";
}

function replaceCourse(element, course) {
    let el = document.getElementById(element);
    el.innerHTML = "<p>" + course + "</p>";
    checkSchedule(0);
    closePopup();
}

function changeHeaderColor(can_take) {
    let header = document.getElementsByClassName("card-header");
    if (header.length) {
        if (can_take > 0) {
            header[0].style.backgroundColor = "#c8e6c9";
        } else if (!can_take) {
            header[0].style.backgroundColor = "#ffccbc";
        }
    }
}

function generateCourseHTML(course, term_index, isScrollable = false, element = "", codes = []) {
    let can_take = -1;
    if (term_index >= 0) {
        let listOfCoursesTaken = getTaken(term_index);
        let currentTermCoursesText = getCurrent(term_index)[1];
        if (codes.length){
            currentTermCoursesText = currentTermCoursesText.filter( function( el ) {
                return !codes.includes( el );
            } );
        }
        $.ajax({
            url: 'http://127.0.0.1:8000/api/meets_prereqs/get/' + course,
            type: 'get',
            data: {
                list_of_courses_taken: listOfCoursesTaken,
                current_term_courses: currentTermCoursesText
            },
            async: false,
            success: function (data) {
                if (data.can_take) {
                    can_take = 1;
                } else {
                    can_take = 0;
                }
            }
        });
    }

    let uwFlowLink = "https://uwflow.com/course/" + course.replace(" ", "");
    // isScrollable check if the course is within a list of courses to choose from
    // for single courses
    let html = "";
    if (isScrollable) {
        html += "<button class='btn btn-primary' id='select-course' style='float: right;'" +
            "onclick='replaceCourse(\"" + element + "\",\"" + course + "\")'>Select</button><div>";
    }
    else html += "<div class='card-header'><a class=\"close\" id='close-popup-1' onclick=\"closePopup()\">×</a>";
    html += "<h3>" + course + "</h3></div>";

    $.ajax({
        url: 'http://127.0.0.1:8000/api/course-info/get/' + course,
        type: 'get',
        async: false,
        success: function (data) {
            let id = data.course_id;
            let name = data.course_name;
            let credit = data.credit;
            let info = data.info;
            let online = data.online;
            let prereqs = data.prereqs;
            let coreqs = data.coreqs;
            let antireqs = data.antireqs;
            if (isScrollable) html += "<div>";
            else html += "<div class='card-body'><div id=\"container\" style='overflow-y: scroll; min-height: 44vh;'>";
            html += "<br style='font-size: 14px'><b>" + name + "</b> (" + credit + ") ID:" + id + " "
                + "</br><a href='" + uwFlowLink + "'target='_blank'>UWFlow</a>";
            html += "</p><div id='wrapper' style='max-height: 170px; overflow-y: initial'>" + info;
            if (online) {
                html += "<br><i>Available online.</i>";
            }
            html += "</br>";
            if (prereqs) {
                html += "</br><b>Prereq: </b>" + prereqs;
            } if (coreqs) {
                html += "</br><b>Coreq: </b>" + coreqs;
            } if (antireqs) {
                html += "</br><b>Antireq: </b>" + antireqs;
            }
            html += "</div></div>";
            if (!isScrollable) html += "</div>";
        },
        error: function () {
            html += "<large-p>ERROR</large-p>";
        }
    });
    return [html, can_take];
}

function generateScrollHTML(courses, codes, course_text, term_index, element) {
    let html = "<div class='card-header'><a class=\"close\" id='close-popup-1' onclick=\"closePopup()\">×</a>";
    html += "<h3 style=\"white-space:nowrap;overflow:hidden;text-overflow: ellipsis;max-width: 75ch; padding: 0.1rem;\">" + course_text + "</h3></div>";
    html += "<div class='card-body' style='padding-bottom: 0em'>";
    html += '<div id="container"><div id="left"><div id="wrapper" style="overflow-y: initial"><ul>';
    for (let i = 0; i < codes.length; i++) {
        html += '<li style="white-space:nowrap;overflow:hidden;text-overflow: ellipsis;max-width: 45ch;cursor: pointer" class="bold" onclick="replaceCourseHTML(\'' +
            codes[i] + "','" + element + '\',' + term_index.toString() + ',[\'' + codes.join("', '") + '\'])"><a style="color: #007bff">' + codes[i] + "</a>: " + courses[codes[i]] + '</li>';
    }
    html += '</ul></div></div>';
    let response = generateCourseHTML(codes[0], term_index,true, element, codes);
    let inner = response[0];
    let can_take = response[1];
    html += '<div id="right">' + inner + '</div></div><br>';
    html += "</div>";
    return [html, can_take];
}

function replaceCourseHTML(course, element, term_index, codes=[]) {
    let el = document.getElementById("right");
    let response = generateCourseHTML(course, term_index, true, element, codes);

    el.innerHTML = response[0];
    changeHeaderColor(response[1]);
}

function popupWindow(str, term_index) {
    let el = document.getElementById(str);
    let course_text = el.innerText;
    let courses = getListOfCourses(course_text);
    let codes = Object.keys(courses).sort();

    let content = document.getElementsByClassName("popup-content")[0];
    let html = "";
    let can_take = -1;
    if (codes.length === 1) {
        let response = generateCourseHTML(codes[0], term_index);
        html = response[0];
        can_take = response[1];
    }
    else {
        let response = generateScrollHTML(courses, codes, course_text, term_index, str);
        html = response[0];
        can_take = response[1];
    }
    content.innerHTML = html;
    changeHeaderColor(can_take);
    document.getElementById("popup-1").style.display = "block";
    document.getElementById("popup-1").style.width = "98%";
}

function breathCheck() {
    const numTerms = terms.length;
    let taken = getTaken(numTerms);
    $.ajax({
        url: 'http://127.0.0.1:8000/api/breath_met/',
        type: 'get',
        data: {
            list_of_courses_taken: taken
        },
        async: false,
        success: function (data) {
            let breadth = document.getElementById("breadth");
            if (data.breadth_met) {
                breadth.style.backgroundColor = "green";
            } else {
                breadth.style.backgroundColor = "red";
            }
        },
        error: function () {
            debugger;
        }
    });
}
