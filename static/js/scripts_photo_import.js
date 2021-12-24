function customResult(resultElement, result) {
    $(resultElement).append(
        $('<p>').text('The import process is complete')
    );
}

function processSuccess(progressBarElement, progressBarMessageElement, result) {
			var success_url = $("#SucUrl").attr("data-url");
			window.location.replace(success_url)
		}

$(function () {
    var progressUrl = $("#Url").attr("data-url");
    CeleryProgressBar.initProgressBar(progressUrl, {
        onResult: customResult,
        onSuccess: processSuccess,
        pollInterval: 200,
    });
});