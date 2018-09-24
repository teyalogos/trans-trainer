$(document).ready(function () {
    namespace = '/voice';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    // updates progress bar
    function updateProgress(width, text) {
        $("#progressBar").text(text + " " + width + "%");
        $("#progressBar").css("width", width + "%");
    }

    // handles message from server to update progress bar
    socket.on('progress', function (msg) {
        updateProgress(msg.width, msg.text);
    });

    // notify user that the file selected is invalid or valid
    socket.on('filestatus', function (msg) {
        $("#fileInput").attr('class', "custom-file-input " + msg.data);

        // change progress bar if the file is invalid
        if(msg.data == 'is-invalid') {
            $("#progressBar").attr('class', "progress-bar bg-danger");
            updateProgress(100, "Please select a WAV file");
        }
    });

    // handles message received from server containing the prediction results
    socket.on('prediction', function (msg) {
        // update displays
        var label = msg.prediction > 0.5 ? "female" : "male";
        $("#predictionDisplay").text(label);

        var percentage = 0;
        if(label == "female") {
            percentage = msg.prediction * 100;
        } else {
            percentage = (msg.prediction * 100) - 100;
            percentage *= -1;
        }
        $("#predictionProbability").text(percentage.toString() + '%');

        var meanfreq = msg.data[0];
        var sd = msg.data[1];
        var medianfreq = msg.data[2];
        var mode = msg.data[10];
        $("#meanfreq").text(meanfreq);
        $("#medianfreq").text(medianfreq);
        $("#mode").text(mode);
        $("#sd").text(sd);

        // display stats container
        $("#statsContainer").collapse("show");

        // change progress bar color to indicate success
        $("#progressBar").attr('class', "progress-bar bg-success");
    });

    // handles file selection
    $('#fileInput').on('change', function () {
        // make sure we display the filename correctly
        // get the file name
        var path = $(this).val();
        var fileName = path.replace(/^C:\\fakepath\\/, "")
        // replace the "Choose a file" label
        $(this).next('.custom-file-label').html(fileName);

        // Reset progress Bar
        updateProgress("0", "");
        $("#progressBar").attr('class', "progress-bar progress-bar-striped progress-bar-animated bg-info");

        // display stats container
        $("#statsContainer").collapse("hide");
    });
});
