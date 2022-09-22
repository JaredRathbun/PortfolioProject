// get all folders in our .directory-list
var allFolders = $(".directory-list li > ul");

allFolders.each(function () {
    // add the folder class to the parent <li>
    var folderAndName = $(this).parent();
    folderAndName.addClass("folder");

    // backup this inner <ul>
    var backupOfThisFolder = $(this);
    // then delete it
    $(this).remove();
    // add an <a> tag to whats left ie. the folder name
    folderAndName.wrapInner("<a href='#' /  style=\'color: black; text-decoration: none;\'>");
    // then put the inner <ul> back
    folderAndName.append(backupOfThisFolder);

    // now add a slideToggle to the <a> we just added
    folderAndName.find("a").click(function (e) {
        $(this).siblings("ul").slideToggle("slow");
        e.preventDefault();
    });

});

function getFileCode(btn) {
    let endpoint = btn.id;

    fetch(endpoint)
        .then((res) => res = res.json())
        .then((json) => {
            const code_div = document.getElementById('code-div');
            if (json.code_present) {
                code_div.style.removeProperty('display');
                code_div.style.removeProperty('justify-content');
                code_div.style.removeProperty('align-items');
            } else {
                code_div.style.setProperty('display', 'flex');
                code_div.style.setProperty('justify-content', 'center');
                code_div.style.setProperty('align-items', 'center');
            }

            code_div.innerHTML = json.code;
        });
}


function getRawContent(rawEndpoint) {
    fetch(rawEndpoint).then((res) => res = res.json()).then((json) => {
        const code_div = document.getElementById('code-div');
        if (json.content_loaded) {
            code_div.style.removeProperty('display');
            code_div.style.removeProperty('justify-content');
            code_div.style.removeProperty('align-items');
        } else {
            code_div.style.setProperty('display', 'flex');
            code_div.style.setProperty('justify-content', 'center');
            code_div.style.setProperty('align-items', 'center');
        }

        code_div.innerHTML = json.raw_code;
    });
}

function downloadFile(endpoint, token) {
    fetch(endpoint, {
        method: 'GET',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
    }).then((res) => {
        if (res.status == 401) {
            alert('Error: Invalid API Token. Hint: Generate a new token by clicking "My Account" > "API Token"');
            return null;
        } else if (res.status == 400) {
            alert('Error: Invalid information.');
            return null;
        } else if (res.status == 500) {
            alert('Error: Server Error');
            return null;
        }

        return res.formData();
    }).then((data) => {
        if (data != null) {
            const a = document.createElement('a');
            a.href = URL.createObjectURL(data.get('file'));
            a.download = data.get('filename');
            a.click();
        }
    });
}

function downloadProject(btn) {
    const btn_id = btn.id;
    const splitArray = btn_id.split('*');
    let endpoint = splitArray[0];
    let token = splitArray[1];

    fetch(endpoint, {
        method: 'GET',
        headers: {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
    }).then((res) => {
        if (res.status == 401) {
            alert('Error: Invalid API Token. Hint: Generate a new token by clicking "My Account" > "API Token"');
            return null;
        } else if (res.status == 400) {
            alert('Error: Invalid information.');
            return null;
        } else if (res.status == 500) {
            alert('Error: Server Error');
            return null;
        }

        return res.formData();
    }).then((data) => {
        if (data != null) {
            const a = document.createElement('a');
            a.href = URL.createObjectURL(data.get('file'));
            a.download = data.get('filename');
            a.click();
        }
    });
}

function populateComments() {
    let commentsIssuesDiv = document
        .getElementById('comments-issues-div-container').childNodes[1]
    // Clear the div of any contents.
    commentsIssuesDiv.innerHTML = "";
    fetch(`/projects/comments/${commentsIssuesDiv.id}`)
        .then((res) => res = res.json())
        .then((data) => {
            if (data.length > 0) {
                for (let comment of data) {
                    let div = document.createElement('div');
                    div.setAttribute('class', 'comment');

                    let usernameAndDateDiv = document.createElement('div');
                    usernameAndDateDiv.setAttribute('class', 'name-date');
                    let username = document.createElement('h3');
                    username.textContent = comment.username;
                    let date = document.createElement('p');
                    date.textContent = new Date(comment.date).toString();

                    let seperator = document.createElement('hr');
                    seperator.setAttribute('class', 'hr-seperator');

                    usernameAndDateDiv.appendChild(username);
                    usernameAndDateDiv.appendChild(date);
                    usernameAndDateDiv.appendChild(seperator);
                    div.appendChild(usernameAndDateDiv);

                    let text = document.createElement('div');
                    text.textContent = comment.text;
                    text.style.margin = "10px";
                    text.style.overflowWrap = "anywhere";
                    div.appendChild(text);

                    commentsIssuesDiv.appendChild(div);
                }
            } else {
                let div = document.createElement('div');
                div.setAttribute('class', 'no-content-center');
                let h = document.createElement('h4');
                h.textContent = 'It looks like there are no comments for this project. Add a new one now!';
                div.appendChild(h);
                commentsIssuesDiv.appendChild(div);
            }
        });
}

function populateBugs() {
    let commentsIssuesDiv = document
        .getElementById('comments-issues-div-container').childNodes[1]
    // Clear the div of any contents.
    commentsIssuesDiv.innerHTML = "";

    fetch(`/projects/bugs/${commentsIssuesDiv.id}`)
        .then((res) => res = res.json())
        .then((data) => {
            if (data.length > 0) {
                for (let bug of data) {
                    let div = document.createElement('div');
                    div.setAttribute('class', 'bug');

                    let usernameAndDateDiv = document.createElement('div');
                    usernameAndDateDiv.setAttribute('class', 'name-date');
                    let username = document.createElement('h3');
                    username.textContent = bug.username;
                    let date = document.createElement('p');
                    date.textContent = new Date(bug.date).toString();

                    let seperator = document.createElement('hr');
                    seperator.setAttribute('class', 'hr-seperator');

                    usernameAndDateDiv.appendChild(username);
                    usernameAndDateDiv.appendChild(date);
                    usernameAndDateDiv.appendChild(seperator);
                    div.appendChild(usernameAndDateDiv);

                    let bugName = document.createElement('h5');
                    bugName.textContent = bug.bug_name;
                    bugName.style.margin = "10px";
                    div.appendChild(bugName);

                    let bugDesc = document.createElement('div');
                    bugDesc.textContent = bug.bug_desc;
                    bugDesc.style.margin = "10px";
                    bugDesc.style.overflowWrap = "anywhere";
                    div.appendChild(bugDesc);

                    commentsIssuesDiv.appendChild(div);
                }
            } else {
                let div = document.createElement('div');
                div.setAttribute('class', 'no-content-center');
                let h = document.createElement('h4');
                h.textContent = 'It looks like there are no bugs for this project!';
                div.appendChild(h);
                commentsIssuesDiv.appendChild(div);
            }
        });
}

function popBugForm() {
    Swal.fire({
        title: '<h4>Create a Bug</h4>',
        html: `
            <input class="form-control" type="text" id="bug-name" style="color: black !important; width: 100%" placeholder="Enter Bug Name"></input>
            <textarea class="form-control" id="bug-desc" placeholder="Enter bug description" style="margin-top: 10px; width: 100%"></textarea>
        `,
        confirmButtonText: 'Create Bug',
        showCancelButton: true,

        preConfirm: () => {
            const bugName = Swal.getPopup().querySelector('#bug-name').value
            const bugDesc = Swal.getPopup().querySelector('#bug-desc').value;

            return { bugName: bugName, bugDesc: bugDesc };
        }
    }).then((result) => {
        let projectId = document
            .getElementById('comments-issues-div-container').childNodes[1].id;

        fetch(`/projects/bugs/add/${projectId}`, {
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST',
            body: JSON.stringify({
                bug_name: result.value.bugName,
                bug_desc: result.value.bugDesc
            })
        }).then((res) => {
            // If the insertion of the bug was successful, pop up a success msg.
            if (res.status == 200) {
                Swal.fire('Bug Successfully Submitted',
                    'Click \'OK\' to return to the project.', 'success');
                populateBugs();
            } else {
                // If the insertion failed, pop up a failure message.
                Swal.fire('Unable to create bug.',
                    'Please try again later.', 'error');
            }
        })
    });
}

function popCommentForm() {
    Swal.fire({
        title: '<h4>Add a Comment</h4>',
        html: `
            <textarea class="form-control" id="comment" placeholder="Enter comment" style="margin-top: 10px; width: 100%"></textarea>
        `,
        confirmButtonText: 'Add Comment',
        showCancelButton: true,

        preConfirm: () => {
            const comment = Swal.getPopup().querySelector('#comment').value;

            return { comment: comment };
        }
    }).then((result) => {
        let projectId = document
            .getElementById('comments-issues-div-container').childNodes[1].id;
        fetch('/projects/comments/add/' + projectId, {
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST',
            body: JSON.stringify({comment: result.value.comment})
        }).then((res) => {
            // If the insertion of the bug was successful, pop up a success msg.
            if (res.status == 200) {
                Swal.fire('Comment successfully added.',
                    'Click \'OK\' to return to the project.', 'success');
                populateComments();
            } else {
                // If the insertion failed, pop up a failure message.
                Swal.fire('Unable to add Comment.',
                    'Please try again later.', 'error');
            }
        })
    });
}

/**
 * Inverts the button that is currently active.
 */
function invertButtons() {
    let commentsBtn = document.getElementById('comments-btn');
    let bugsBtn = document.getElementById('bugs-btn');

    commentsBtn.disabled = !commentsBtn.disabled;
    bugsBtn.disabled = !bugsBtn.disabled;
}