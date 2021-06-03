var socket = undefined;
var state_refresh_interval = undefined;
var page_params = new URLSearchParams(window.location.search);

var app = new Vue({
    el: "#logs-card",
    data: {
        state: "unknown",
        websocket: "unknown",
        logs: []
    },
    mounted() {
        websocket_connect();
//        state_refresh();
    },
    updated() {
        var item = $("#logs-body");
        item.scrollTop(item.prop("scrollHeight"));
    }
    }
    );

function websocket_connect() {
    test_id = page_params.get('test_id')
    project_id = page_params.get('project_id')
    $.ajax({
        url: `/api/v1/security/${project_id}/get_url?task_id=${test_id}`,
        cache: false,
        contentType: false,
        processData: false,
        method: 'GET',
        success: function(data){
            var full_ws_url = data['websocket_url']
            console.log(full_ws_url)
            socket = new WebSocket(full_ws_url);
            socket.onmessage = on_websocket_message;
            socket.onopen = on_websocket_open;
            socket.onclose = on_websocket_close;
            socket.onerror = on_websocket_error;
    }})
}

function on_websocket_message(message) {
    if (message.type != "message") {
        console.log("Unknown message");
        console.log(message);
        return;
    }

    var data = JSON.parse(message.data);

    data.streams.forEach(function(stream_item) {
        stream_item.values.forEach(function(message_item) {
            app.logs.push(message_item[1]);
        });
    });
}

function on_websocket_open(message) {
    app.websocket = "connected";
}

function on_websocket_close(message) {
    app.websocket = "disconnected";
    setTimeout(websocket_connect, 1 * 1000);
//    clearInterval(websocket_connect)
}

function on_websocket_error(message) {
    app.websocket = "errored";
    socket.close();
}

//function state_refresh() {
//    if (state_refresh_interval != undefined) {
//        clearInterval(state_refresh_interval);
//        state_refresh_interval = undefined;
//        }
//    try {
//        do_refresh_state();
//    } catch(error) {
//        console.log("Error during state refresh");
//        console.error(error);
//    }
//        state_refresh_interval = setInterval(state_refresh, 5 * 1000);
//    }

//function do_refresh_state() {
//    axios
//    .get("{{ url_for('tasks.task_state', key=task_key) }}")
//    .then(response => {
//    app.state = response.data.state;
//    });
//}
