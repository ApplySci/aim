function checkUrl() {
    if (this.value.trim() === '') {
        document.getElementById('url_status').innerHTML = '';
        return;
    }

    fetch(this.value, { mode: 'no-cors' })
        .then(response => {
            // If we get here, the resource exists, even if we can't access it due to CORS
            document.getElementById('url_status').innerHTML = '<span style="color:green;">✔️</span>';
        })
        .catch(() => {
            // This catch will only trigger for network errors, not CORS issues
            document.getElementById('url_status').innerHTML = '<span style="color:red;">❌</span>';
        });
}

function checkImg() {
    if (this.value.trim() === '') {
        document.getElementById('icon_status').innerHTML = '';
        return;
    }

    var img = new Image();
    img.src = this.value;
    img.onload = function() {
        document.getElementById('icon_status').innerHTML = '<img src="' + img.src + '" width="50" height="50">';
    }
    img.onerror = function() {
        document.getElementById('icon_status').innerHTML = '<span style="color:red;">❌</span>';
    }
}

function setupValidation() {
    var urlField = document.getElementById('url');
    var iconField = document.getElementById('url_icon');

    urlField.addEventListener('change', checkUrl);
    urlField.addEventListener('input', checkUrl);
    iconField.addEventListener('change', checkImg);
    iconField.addEventListener('input', checkImg);
    checkUrl.call(urlField);
    checkImg.call(iconField);
}

document.addEventListener('DOMContentLoaded', setupValidation);
