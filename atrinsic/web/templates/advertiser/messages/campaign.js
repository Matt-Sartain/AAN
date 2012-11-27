{% load thumbnail_tag %}

banner_markup = '<div class="embed-banner-box"><h4>Embed Banners</h4><ul>' +
            {% for l in organization.link_set.all %}
            '<li><a class="html_add" value="link_{{ l.name|slugify }}">{{ l.name }}{% if l.banner.image %}: <img src="{{ l.banner.image|thumbnail }}"/>{% endif %}</a></li>' +
            {% endfor %}
            '</ul></div>';

markup = '<div class="embed-tag-box"><h4>Embed Labels</h4><ul>' +
        '<li><a class="html_add" value="first_name">First Name</a></li>' +
        '<li><a class="html_add" value="website_url">Website URL</a></li>' +
        '<li><a class="html_add" value="clicks_mtd">Clicks: MTD</a></li>' +
        '<li><a class="html_add" value="orders_mtd">Orders: MTD</a></li>' +
        '<li><a class="html_add" value="leads_mtd">Leads: MTD</a></li>' +
        '<li><a class="html_add" value="sales_mtd">Sales: MTD</a></li>' +
        '<li><a class="html_add" value="clicks_ytd">Clicks: YTD</a></li>' +
        '<li><a class="html_add" value="orders_ytd">Orders: YTD</a></li>' +
        '<li><a class="html_add" value="leads_ytd">Leads: YTD</a></li>' +
        '<li><a class="html_add" value="sales_ytd">Sales: YTD</a></li>' +
        '</ul></div>';
   
    
$("#id_body").css("float", "left");  
$('#id_body').parent().css("width","80%")      
$("#id_html_body").css("float", "left"); 
$('#id_html_body').parent().css("width","80%")     

$('#id_html_body').parent().append("<div class='embedBox'>"+markup + banner_markup+"</div>");
$('#id_body').parent().append("<div class='embedBox'>"+markup.replace(/html_/g, 'text_')+banner_markup.replace(/html_/g, 'text_')+"</div>");


$(".html_add").click(function() {
    $("#id_html_body").val($("#id_html_body").val() + '{'+$(this).attr('value')+'}'); 
});

$(".text_add").click(function() {
    $("#id_body").val($("#id_body").val() + '{'+$(this).attr('value')+'}'); 
});

