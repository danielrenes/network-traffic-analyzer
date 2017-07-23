$(document).ready(function() {
  var sent_length = chartSent.data.datasets[0].data.length;
  var recv_length = chartRecv.data.datasets[0].data.length;

  var refresh_chart = function() {
    $.ajax({
      url: $SCRIPT_ROOT + "/refresh",
      type: "GET",
      data: {
        "last_index_sent": sent_length,
        "last_index_recv": recv_length
      },
      datatype: "json"
    }).done(function(data) {
      sent_refresh = data["sent"];
      recv_refresh = data["recv"];

      for (let i = 0; i < sent_refresh.length; i++) {
        chartSent.data.labels[sent_length] = sent_refresh[i]["ip"];
        chartSent.data.datasets[0].data[sent_length] = sent_refresh[i]["num_packets"];
        sent_length++;
      }

      for (let i = 0; i < recv_refresh.length; i++) {
        chartRecv.data.labels[sent_length] = recv_refresh[i]["ip"];
        chartRecv.data.datasets[0].data[recv_length] = recv_refresh[i]["num_packets"];
        recv_length++;
      }

      chartSent.update();
      chartRecv.update();
    });
  };

  setInterval(function() {
    refresh_chart();
  }, 10000);
});
