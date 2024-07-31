(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            var spinnerElement = $('#spinner');
            if (spinnerElement.length > 0) {
                spinnerElement.removeClass('show');
            }
        }, 1);
    };
    spinner();  // Call spinner function without parameter

    // Initiate the WOW.js library for animations
    if (typeof WOW !== 'undefined') {
        new WOW().init();
    } else {
        console.warn('WOW.js is not loaded.');
    }

    // Hero Header carousel
    if ($(".header-carousel").length) {
        $(".header-carousel").owlCarousel({
            animateOut: 'slideOutDown',
            items: 1,
            autoplay: true,
            smartSpeed: 500,
            dots: false,
            loop: true,
            nav: true,
            navText: [
                '<i class="bi bi-arrow-left"></i>',
                '<i class="bi bi-arrow-right"></i>'
            ]
        });
    }

    // Attractions carousel
    if ($(".attractions-carousel").length) {
        $(".attractions-carousel").owlCarousel({
            autoplay: true,
            smartSpeed: 2000,
            center: false,
            dots: false,
            loop: true,
            margin: 25,
            nav: true,
            navText: [
                '<i class="fa fa-angle-right"></i>',
                '<i class="fa fa-angle-left"></i>'
            ],
            responsiveClass: true,
            responsive: {
                0: { items: 1 },
                576: { items: 2 },
                768: { items: 2 },
                992: { items: 3 },
                1200: { items: 4 },
                1400: { items: 4 }
            }
        });
    }

    // Testimonial carousel
    if ($(".testimonial-carousel").length) {
        $(".testimonial-carousel").owlCarousel({
            autoplay: true,
            smartSpeed: 1500,
            center: false,
            dots: true,
            loop: true,
            margin: 25,
            nav: true,
            navText: [
                '<i class="fa fa-angle-right"></i>',
                '<i class="fa fa-angle-left"></i>'
            ],
            responsiveClass: true,
            responsive: {
                0: { items: 1 },
                576: { items: 1 },
                768: { items: 1 },
                992: { items: 1 },
                1200: { items: 1 }
            }
        });
    }

    // Facts counter
    if ($('[data-toggle="counter-up"]').length) {
        $('[data-toggle="counter-up"]').counterUp({
            delay: 5,
            time: 2000
        });
    }

    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });

    $('.back-to-top').click(function () {
        $('html, body').animate({ scrollTop: 0 }, 1500, 'easeInOutExpo');
        return false;
    });

})(jQuery);
