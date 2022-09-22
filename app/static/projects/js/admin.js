function sendCreateProject() {
    const classIDSelect = document.getElementById('project-class-id');
    const classID = classIDSelect.options[classIDSelect.selectedIndex].text
        .split(' - ')[0];
    

    const title = document.getElementById('project-name').value;
    const desc = document.getElementById('project-desc').value;
    const zipFile = document.getElementById('project-zip').files.item(0);
    const iconImage = document.getElementById('project-icon').files.item(0);

    const formData = new FormData();
    formData.append('parent_class', classID);
    formData.append('project_name', title);
    formData.append('project_desc', desc);
    formData.append('icon_image', iconImage);
    formData.append('project_zip', zipFile);
    formData.append('tags', []);

    const request = new XMLHttpRequest();
    request.open('POST', '/projects/upload');
    request.send(formData);
}

function sendCreateClass() {
    const classID = document.getElementById('class-id').value;
    const title = document.getElementById('class-title').value;
    const desc = document.getElementById('class-desc').value;
    const iconImage = document.getElementById('class-icon').files.item(0);

    const formData = new FormData();
    formData.append('id', classID);
    formData.append('class_title', title);
    formData.append('desc', desc);
    formData.append('icon_image', iconImage);

    const request = new XMLHttpRequest();
    request.open('POST', '/classes/create-class');
    request.send(formData);
}