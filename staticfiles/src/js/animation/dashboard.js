function Animation(){}

Animation.animateAssets = function(moduleName, isFullScreen, topRowHeight, callback){
	if(!isFullScreen){
		$('.moduleContainer').css('height', 'calc(92vh - 64px)');
		
		$('#returnContainer').hide();
		$('#riskContainer').hide();
		$('#feeContainer').hide();

		$("body").css("background-color", "#BBDEFB");

		$('#assetContainer').animate({
			width: "100%",
			height: "100%",
		}, {
			duration: 1000,
			step: function(){
				$("#" + moduleName).highcharts().reflow();
			},
			done: function(){
				callback();
			}
		});
	}else{
		$('.moduleContainer').css('height', 'calc(100% - 64px)');
		
		$('#assetContainer').animate({
			width: "50%",
			height: "50%",
		}, {
			duration: 1000,
			step: function(){
				$("#" + moduleName).highcharts().reflow();
			},
			done:function(){
				$('#returnContainer').show();
				$('#riskContainer').show();
				$('#feeContainer').show();
				$('.modTitle').css('display', 'block');
				callback();
			}
		});
	}
}


Animation.animateReturn = function(moduleName, isFullScreen, topRowHeight, callback){	
	if(!isFullScreen){

		$('.moduleContainer').css('height', 'calc(92vh - 64px)');
		
		$('#assetContainer').hide();
		$('#riskContainer').hide();
		$('#feeContainer').hide();

		$('#returnContainer').css({
			"marginLeft": "50%",
		});

		$("body").css("background-color", "#BBDEFB");

		$('#returnContainer').animate({
			width: "100%",
			height: "100%",
			marginLeft : 0
		}, {
			duration: 1000,
			step: function(){
				$("#" + moduleName).highcharts().reflow();
			},
			done: function(){
				callback();
			}
		});
	}
	else{
		$('.moduleContainer').css('height', 'calc(100% - 64px)');

		$('#returnContainer').animate({
			width: "50%",
			height: "50%",
			marginLeft: "50%"
		}, {
			duration: 1000,
			step: function(){
				$("#" + moduleName).highcharts().reflow();
			},
			done:function(){
				$('#assetContainer').show();
				$('#riskContainer').show();
				$('#feeContainer').show();

				$('#returnContainer').css({
					marginLeft: 0,
				});

				callback();
			}
		});
	}
};

Animation.animateRisk = function(moduleName, isFullScreen, topRowHeight, callback){	

	if(!isFullScreen){
		$('.moduleContainer').css('height', 'calc(92vh - 64px)');

		$('#assetContainer').hide();
		$('#returnContainer').hide();
		$('#feeContainer').hide();

		$("#topRow").hide();

		$("body").css("background-color", "#BBDEFB");

		$("#riskContainer").css({
			marginTop: topRowHeight
		});

		$('#riskContainer').animate({
			width: "100%",
			height: "100%",
			marginTop : 0
		}, 
		{
			duration: 1000,
			step: function(){
				$("#" + moduleName).highcharts().reflow();
			},
			done: function(){
				$('#assetContainer').hide();
				$('#returnContainer').hide();
				$('#feeContainer').hide();
				callback();
			}
		});
		
	}
	else{
		$('.moduleContainer').css('height', 'calc(100% - 64px)');

		$('#riskContainer').animate({
			width: "50%",
			height: "50%",
			marginTop : topRowHeight
		}, {
			duration: 1000,
			step: function(){
				$("#" + moduleName).highcharts().reflow();
			},
			done:function(){
				$('#assetContainer').show();
				$('#returnContainer').show();
				$('#feeContainer').show();
				$("#topRow").show();

				$('#riskContainer').css({
					"marginTop": 0,
				});
				callback();	
			}
		});
	}
};

Animation.animateCost = function(moduleName, isFullScreen, topRowHeight, callback){	

	if(!isFullScreen){
		$('.moduleContainer').css('height', 'calc(92vh - 64px)');
		
		$('#riskContainer').hide();
		$('#returnContainer').hide();
		$('#assetContainer').hide();
		$("#topRow").hide();

		$("body").css("background-color", "#BBDEFB");

		$("#feeContainer").css({
			marginTop: topRowHeight,
			marginLeft : "50%"
		});

		$('#feeContainer').animate({
			width: "100%",
			height: "100%",
			marginTop : 0,
			marginLeft : 0
		}, {
			duration: 1000,
			step: function(){
				$("#" + moduleName).highcharts().reflow();
			},
			done: function(){
				callback();
			}
		});
	}
	else{
		$('.moduleContainer').css('height', 'calc(100% - 64px)');
		$("#bmenu-wrapper").css('display','none');

		$('#feeContainer').animate({
			width: "50%",
			height: "50%",
			marginLeft : "50%",
			marginTop: topRowHeight
		}, {
			duration: 1000,
			step: function(){
				$("#" + moduleName).highcharts().reflow();
			},
			done:function(){
				$('#riskContainer').show();
				$('#returnContainer').show();
				$('#assetContainer').show();
				$("#topRow").show();

				$('#feeContainer').css({
					"marginTop": 0,
					"marginLeft": 0
				});

				callback();
			}
		});
	}
}

export default Animation;

