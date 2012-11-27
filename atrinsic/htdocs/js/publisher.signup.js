function initTermsFormManipulation(){
    $("#id_org_name").parent().prev().addClass("addLabelStyle");
    $("#id_org_name").attr("size", "40")
    $("#id_org_name").addClass("digSignature");
}
function initStep2FormManipulation(){
    $("<div class='clearfix'></div>").insertAfter($("#recaptcha_response_field").prev());
    $("legend").remove();
}
function initStep5FormManipulation(){
    $("legend").remove();
    $('#id_pub_country').change(function(){state_toggle_pub('#id_pub_country');});
    state_toggle_pub('#id_pub_country');
}


function initStep6FormManipulation(){
    $("legend").remove();
    $('#id_country').change(function(){state_toggle('#id_country');});
    state_toggle('#id_country');

    if ($('#id_payment_method').val() == '1') {
        $('#id_account_name').parent().parent().parent().hide();
        $('#id_payeename').parents(".contentCtn").show();
        $('#id_xs_firstname').parents(".contentCtn").hide();
        $('#id_paypal_email').parent().parent().hide();
    } else if ($('#id_payment_method').val() == '2') {
        $('#id_account_name').parent().parent().parent().show();
        $('#id_payeename').parents(".contentCtn").hide();
        $('#id_xs_firstname').parents(".contentCtn").show();
        $('#id_paypal_email').parent().parent().hide();
    } else if ($('#id_payment_method').val() == '3') {
        $('#id_account_name').parent().parent().parent().hide();
        $('#id_payeename').parents(".contentCtn").hide();
        $('#id_xs_firstname').parents(".contentCtn").show();
        $('#id_paypal_email').parent().parent().show();
    }
	
	$('#id_payment_method').change(function() {		
        if ($('#id_payment_method').val() == '1') {
            $('#id_account_name').parent().parent().parent().hide();
            $('#id_payeename').parents(".contentCtn").show();
            $('#id_xs_firstname').parents(".contentCtn").hide();
            $('#id_paypal_email').parent().parent().hide();
        } else if ($('#id_payment_method').val() == '2') {
            $('#id_account_name').parent().parent().parent().show();
            $('#id_payeename').parents(".contentCtn").hide();
            $('#id_xs_firstname').parents(".contentCtn").show();
            $('#id_paypal_email').parent().parent().hide();
        } else if ($('#id_payment_method').val() == '3') {
            $('#id_account_name').parent().parent().parent().hide();
            $('#id_payeename').parents(".contentCtn").hide();
            $('#id_xs_firstname').parents(".contentCtn").show();
            $('#id_paypal_email').parent().parent().show();
        }
	});
}

function state_toggle(dropdown){    
    $('#id_state').parent().parent().hide();
	$('#id_province').parent().parent().hide();
    if($(dropdown).val() == 'US'){
        $('#id_state').parent().parent().show();
        $('#id_province').parent().parent().hide();
    }else if($(dropdown).val() == 'CA'){
        $('#id_province').parent().parent().show();
        $('#id_state').parent().parent().hide();
    }else{
        $('#id_province').parent().parent().hide();
        $('#id_state').parent().parent().hide();
    }
}
function state_toggle_pub(dropdown){
    $('#id_pub_state').parent().parent().hide();
	$('#id_pub_province').parent().parent().hide();
    if($(dropdown).val() == 'US'){
        $('#id_pub_state').parent().parent().show();
        $('#id_pub_province').parent().parent().hide();
    }else if($(dropdown).val() == 'CA'){
        $('#id_pub_province').parent().parent().show();
        $('#id_pub_state').parent().parent().hide();
    }else{
        $('#id_pub_province').parent().parent().hide();
        $('#id_pub_state').parent().parent().hide();
    }
}