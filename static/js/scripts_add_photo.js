function handleFileSelect(evt) {
    var file = evt.target.files[0];

    if (file.type.match('image.*')) {
        var reader = new FileReader();

        reader.onload = (function (theFile) {
            return function (e) {
                document.getElementById('preview').innerHTML = ['<img class="thumb" src="', e.target.result,
                    '" title="', escape(theFile.name), '"/>'].join('');
            };
        })(file);

        reader.readAsDataURL(file);
    }
}
document.getElementsByClassName('form-image')[0].addEventListener('change', handleFileSelect, false);