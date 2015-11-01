/*jslint browser: true*/
/*global PNotify*/

(function($) {
    'use strict';

    $(document).ready(function() {

        PNotify.prototype.options.styling = 'fontawesome';

        $('.alertmsg').each( function() {
            var am = $('span.msg:first-child', this);
            var m = am.text();
            var t = am.next().text();

            $(function(){
                new PNotify({
                    type: t,
                    title: 'PyStart-GAE',
                    text: m,
                    icon: false
                });
            });

        });

    });
}(window.jQuery));
