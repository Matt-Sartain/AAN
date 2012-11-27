// JavaScript Document
function GetChartData(){	
	var d1 = [];
	var d2 = [];
	var ticksArr = [];
	
	$.ajax({
		type: "POST",
		url: "/advertiser/get_chart_data/",
		dataType: "json",
		async: false,
		success: function(data){
			$.each(data.items, function(i,item){
				if(ticksArr.join().indexOf(item.DateIn*1000) < 0){
					ticksArr.push([item.DateIn*1000]);
				}
				if(item.DataType == "impressions"){
					d1.push([item.DateIn*1000,item.DataValue]);
				}
				if (item.DataType == "amount"){
					d2.push([item.DateIn*1000,item.DataValue]);
				}
			});
		}
	});
	if(ticksArr.length > 9){
		ticksArr = null;
	}
	return [d1,d2,ticksArr];	
}
function UpdateCharts(){	
	var charts = GetChartData();
	var d1 = charts[0];
	var d2 = charts[1];
	var ticksArr = charts[2];
	
	var doubleGraph_data = [ 
								{ 
									data: d2,
									bars: { show: true } 
								}, 
								{ 
									data: d1, 
									lines: { show: true }, 
									yaxis: 2 
								}
							];
	var doubleGragh_options = { 
									xaxis: { mode: "time",  timeformat: "%b %d", ticks: ticksArr }, 
									yaxis: { min: null },
									grid: { hoverable: true, clickable: true },
									points: { show: true, fill: true, fillColor: "#000000" },
									colors: ["#0000FF","#FF0000"]
								};
	if(d1.length > 0|| d2.length > 0){
		$.plot($("#doubleHolder"), doubleGraph_data, doubleGragh_options);
	}
}
function showTooltip(x, y, contents) {
	$('<div id="tooltip">' + contents + '</div>').css( {
		position: 'absolute',
		display: 'block',
		top: y + 5,
		left: x + 5,
		border: '1px solid #fdd',
		padding: '2px',
		'background-color': '#e5e5e5',
		opacity: 0.80
	}).appendTo("body").fadeIn(200);
}
// now connect the two 
$(function () {
    $("#doubleHolder").bind("plotselected", function (event, ranges) {
		var charts = GetChartData();
		var d1 = charts[0];
		var d2 = charts[1];
		var ticksArr = charts[2];

		var doubleGraph_data = [ { data: d2, label: "amount" }, { data: d1, label: "impressions", yaxis: 2 }];
		var doubleGragh_options = { 
									xaxis: { mode: "time",  timeformat: "%b %d", ticks: ticksArr }, 
									yaxis: { min: null },
									points: { show: true, fill: true, fillColor: "#000000" },
									lines: { show: true },
									grid: { hoverable: true, clickable: true },
									colors: ["#0000FF","#FF0000"]
								};
		$.plot($("#doubleHolder"), doubleGraph_data, doubleGragh_options);
    });
	var previousPoint=0;
	$("#doubleHolder").bind("plothover", function (event, pos, item) {
		if(item){
			$("#tooltip").remove();
			var y = item.datapoint[1];
			showTooltip(item.pageX, item.pageY,	"Value of: " + y);
		} else {
			$("#tooltip").remove();
			previousPoint = null;            
		}

	});
});