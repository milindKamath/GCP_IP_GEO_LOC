$("button.gen").on("click",function(){
    $("#welcome").hide();
    $("#processing").show();
    
    function reverseAnimation() {
		$('#processing').removeClass('uncomplete').addClass('complete');
	}
})