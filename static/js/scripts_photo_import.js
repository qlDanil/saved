function customResult(resultElement, result) {
    $(resultElement).append(
        $('<p>').text('Сохраненные фотографии Вконтакте успешно импортированы!')
    );
}

$(function () {
    var progressUrl = $("#Url").attr("data-url");
    CeleryProgressBar.initProgressBar(progressUrl, {
        onResult: customResult,
        pollInterval: 200,
    });
});