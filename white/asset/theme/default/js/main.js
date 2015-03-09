var White = {
	init: function() {
		White.slidey = $('.slidey');
		White.keys = [];

		//  Uh, bind to the resizing of the window?
		$(window).resize(White.bindResize).trigger('resize');

		// Re-/Set keys
		$(window).on('keyup', White.keyup);
		$(window).on('keydown', White.keydown);

		//  Set up the toggle link
		White.linky = $('.linky').on('click', White.toggleSlidey);

		//  Hide the thingymabob
		setTimeout(function() {
			//  Set up the slidey panel
			White.hideSlidey();

			$('body').addClass('js-enabled');
		}, 10);

		//  Listen for search link
		$('a[href="#search"]').click(function() {
			if(!White.linky.hasClass('active')) {
				return White.toggleSlidey.call(White.linky);
			}
		});
	},

	keyup: function(event) {
		White.keys[event.keyCode] = false;
	},

	keydown: function(event) {
		White.keys[event.keyCode] = true;

		// ctrl + shift + f => show Slidey and/or focus search bar
		if(White.keys[17] && White.keys[16] && White.keys[70]) {
			event.preventDefault();

			White.showSlidey.call(White.linky);
			$('input[type="search"]').focus();
		}

		// esc => hide Slidey
		if(White.keys[27]) {
			event.preventDefault();

			White.hideSlidey();
			$('input[type="search"]').blur();
		}
	},

	hideSlidey: function() {
		White.slidey.css('margin-top', this._slideyHeight);
		White.linky && White.linky.removeClass('active');

		return this;
	},

	showSlidey: function() {
		White.slidey.css('margin-top', 0);
		White.linky && White.linky.addClass('active');

		return this;
	},

	toggleSlidey: function() {
		var self = White;
		var me = $(this);

		me.toggleClass('active');
		self.slidey.css('margin-top', me.hasClass('active') ? 0 : self._slideyHeight);

		return false;
	},

	bindResize: function() {
		White._slideyHeight = -(White.slidey.height() + 1);
		White.hideSlidey();
	}
};

//  And bind loading
$(White.init);
