function removeClass(btn) {
    console.log(btn.id);

    if (confirm('Are you sure you want to remove this' +
        'class? The class and all project in the class will be permanently deleted.')) {
            fetch(btn.id, {
                method: 'POST'
            }).then(function (res) {
                if (res.status == 200) { 
                    location.reload();
                } else {
                    alert('Unable to delete. Please try again later.');
                }
            }).catch(function (err) {
                
            });
    }
}