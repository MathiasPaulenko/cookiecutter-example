function create_chart(chart_id, labels, values, colors, total_value){
    if ($("#"+chart_id).length) {
      var areaData = {
        labels: labels,
        datasets: [{
            data: values,
            backgroundColor: colors,
            borderColor: "rgba(0,0,0,0)"
          }
        ]
      };
      var areaOptions = {
        responsive: true,
        maintainAspectRatio: false,
        segmentShowStroke: false,
        cutout: "70%",
        elements: {
          arc: {
              borderWidth: 4
          }
        },
        tooltips: {
          enabled: true
        },
        plugins: {
          legend: {
            position: "top", // by default it's top
          },
        },
      }

      var chartPlugins = [
        {
            afterDraw: function(chart) {
              var width = chart.width,
                  height = chart.height,
                  ctx = chart.ctx;

              ctx.restore();
              var fontSize = 3.125;
              ctx.font = "500 " + fontSize + "em sans-serif";
              ctx.textBaseline = "middle";
              ctx.fillStyle = "#666";

              var text = total_value,
                  textX = Math.round((width - ctx.measureText(text).width) / 2),
                  textY = height / 2;
              ctx.fillText(text, textX, textY+20);
              ctx.save();
            }
        },
      ]

      var chartCanvas = $("#"+chart_id).get(0).getContext("2d");
      var chart = new Chart(chartCanvas, {
        type: 'doughnut',
        data: areaData,
        options: areaOptions,
        plugins: chartPlugins
      });
    }
}