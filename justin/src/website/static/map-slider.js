jQuery(function() {
	var prefix = "#map-slider";
	var sliderMap = jQuery(prefix);
	var sliderValue = jQuery(prefix + "-val");
	var sliderImages = jQuery(prefix + "-images");

	sliderMap.slider({
		min: 0,
		max: 167,
		step: 1,
		orientation: "vertical",
		animate: 500,
		value: start_val,
		slide: function(e, ui) {
			sliderValue.val(ui.value);
			sliderImages.find("img").hide()
			jQuery(prefix + "-image-" + ui.value).show();
		}
	});

	// set initial val and image
	var initialValue = sliderMap.slider("value");
	jQuery(prefix + "-image-" + initialValue).show();
});