var input, input_box, fields;
/* // prefilled variables
	attr_value	// holds the matching value
	attr_id		// holds the attribute id
	attr_type	// holds the input type
*/
$(document).ready(function(){
	console.log("ready");
	input_box = $("#field-value");
	fields = $("#field-type");
	update_value_type();
	$("#field-type").on("change", function(){
	    attr_id = $("#field-type option:selected").val();
	    attr_type = $("#field-type option:selected").attr("data-type");
	    update_value_type();
	});

	$("#admin-ss-form").submit(function(e) {
		e.preventDefault();

		var params = $("#admin-ss-form").serializeJSON(true);

		CTFd.fetch("/api/v1/split_scores/settings", {
			method: "POST",
			credentials: "same-origin",
			headers: {
				Accept: "application/json",
				"Content-Type": "application/json"
			},
			body: JSON.stringify(params)
		})
		.then(function(response) {
			return response.json();
		})
		.then(function(response) {
			if (response.success) {
				window.location = script_root + "/admin/splitscoreboard";
			} else {
				$("#admin-ss-form > #results").empty();
				Object.keys(response.errors).forEach(function(key, index) {
					$("#admin-ss-form > #results").append(
						ezbadge({
							type: "error",
							body: response.errors[key]
						})
					);
					var i = $("#admin-ss-form").find("input[name={0}]".format(key));	
					var input = $(i);
					
					input.addClass("input-filled-invalid");
					input.removeClass("input-filled-valid");
				});
			}
		});
	});
});

function update_value_type(){
	if( input != undefined)
		input.off();
	input_box.empty()
	switch(attr_type.toLowerCase()){
		case "number":
			input_box.html('<label for="value">Where value matches:</label><input type="number" class="form-control" name="value" id="value" value="'+attr_value+'"/>');
			break;
		case "textarea":
			input_box.html('<label for="value">Where value matches:</label><textarea class="form-control" name="value" id="value" >'+attr_value+'</textarea>');
			break;
		case "text":
			input_box.html('<label for="value">Where value matches:</label><input type="text" class="form-control" name="value" id="value" value="'+attr_value+'"/>');
			break;
		case "checkbox":
		default:			
			input_box.html('<div class="form-check form-check-inline"><label class="form-check-label" for="value">Where value matches:</label><input class="form-check-input" type="checkbox" name="value" id="value" '+(attr_value!=""&&attr_value!="false"&&attr_value!="0"?'checked':'')+'/></div>');
	}

	// keep track of the current input value
	input = $("#value");
	input.on("change", function(){
		if( input.attr("type") == "checkbox"){
			attr_value = $(this).prop("checked")?'true':'false';
		}else{
			attr_value = $(this).val();
		}
	});	
}
