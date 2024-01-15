let bar_chart;
async function update_execution_chart(from_date, to_date){
    // Send the get request to get a json with the date labels, passed and failed executions.
    const res = await fetch("/api/v1/executions/?from_date=" + from_date + "&to_date="+to_date);
        const obj = await res.json();
        bar_chart.data.labels = obj.labels;
        bar_chart.data.datasets[0].data = obj.passed;
        bar_chart.data.datasets[1].data = obj.failed;
        bar_chart.update();
}
$(document).ready(()=>{
    // Get the today date.
    let today = new Date();
    let dd = today.getDate().toString();
    let mm = today.getMonth()+1;
    let yyyy = today.getFullYear();

    if (mm.toString().length < 2)
        mm = '0' + mm;
    if (dd.length < 2)
        dd = '0' + dd;

    let past_day = new Date();
    past_day.setDate(past_day.getDate() - 5);
    let past_dd = past_day.getDate().toString();
    let past_mm = past_day.getMonth()+1;
    let past_yyyy = past_day.getFullYear();

    if (past_mm.toString().length < 2)
        past_mm = '0' + past_mm;
    if (past_dd.length < 2)
        past_dd = '0' + past_dd;

    // Update the chart with the available data with the data of today and the last 5 days
    update_execution_chart(`${past_yyyy}-${past_mm}-${past_dd}`, `${yyyy}-${mm}-${dd}`);

    // Add the event listeners
    $("#from_date").change(async (element) => {
        let from_date = $("#from_date").val();
        let to_date = $("#to_date").val();
        update_execution_chart(from_date, to_date)

    });
    $("#to_date").change(async (element) => {
        let from_date = $("#from_date").val();
        let to_date = $("#to_date").val();
        update_execution_chart(from_date, to_date)
    });
});

function create_bar_chart(chart_id, labels, values, colors){
   if ($("#"+chart_id).length) {
      let data = {
        labels: [
        ],
        datasets: [
        {
            label: "Passed",
            data: [],
            backgroundColor: colors[0],
            borderColor: "rgba(0,0,0,0)"
        },
        {
            label: "Failed",
            data: [],
            backgroundColor: colors[1],
            borderColor: "rgba(0,0,0,0)"
        },
        ]
      };
      let options = {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: 'Passed / Failed executions'
          }
        }
      }

      var chartCanvas = $("#"+chart_id).get(0).getContext("2d");
      bar_chart = new Chart(chartCanvas, {
        type: 'bar',
        data: data,
        options: options,
      });
    }
}