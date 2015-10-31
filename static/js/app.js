/*jslint browser: true*/
/*global PNotify*/

(function($) {
    'use strict';

    $(document).ready(function() {

        PNotify.prototype.options.styling = 'fontawesome';

        $('.alertmsg').each( function() {
            var m = $('span.msg:first-child',this).text();
            var t = $('span.msg:first-child',this).next().text();

            $(function(){
                new PNotify({
                    type: t,
                    title: 'Pystart-GAE',
                    text: m,
                    icon: false,
                    hide: true
                });
            });

        });

    });
}(window.jQuery));
