function populate_inner(step){
	inputs=$("#step"+step+" .input_val").children("select option:selected");
	if (inputs){
		inputs.each(function(x){
			selected = new Array();
			for (var i = 0; i < this.options.length; i++){
				if (this.options[ i ].selected){
					selected.push(this.options[ i ].text);
				}
			}
			$("#inner"+step).html(selected.toString());
		});	
	}
	inputs = $("#step"+step+" .input_val").children("input");
	if (inputs){
		inputs.each(function(x){
			$("#inner"+step).html($(this).val().toString());
		});	
	}
}
function init_stepper(){
	current_step = 1;
	amount_steps = $(".step").length;
	$("#step_header").html($("#heading"+current_step).val());
	$("#step"+current_step).show();
	$("#next_step").click(function(){
		next_step = current_step + 1;
		if (next_step <= amount_steps){
			populate_inner(current_step);
			$(".step").hide();
			$("#step"+next_step).show();
			$("#step_header").html($("#heading"+next_step).val());
			current_step = next_step;
		}else{
			populate_inner(current_step);
		}
	});
	$("#previous_step").click(function(){
		previous_step = current_step - 1;
		if (previous_step >= 1){
			populate_inner(current_step);
			$(".step").hide();
			$("#step"+previous_step).show();
			$("#step_header").html($("#heading"+previous_step).val());
			current_step = previous_step;
		}else{
			populate_inner(current_step);
		}
	});
	$(".edit_button").click(function(){
		step = $(this).attr("id").substring(4);
		$(".step").hide();
		$("#step"+step).show();
		$("#step_header").html($("#heading"+step).val());
	});
	$(".input_val select, .input_val input").change(function(){
		step_name = $(this).parent().parent().attr("id");
		step_id = step_name.substring(4);
		$("#step_header").html($("#heading"+step_id).val());
		populate_inner(step_id);
	});
}