
implement appdata and gets / puts

i need to put back the js for notifications. and base.html. sigh.  its broken you know.

should i have any models?

fix notification. make a function that does the notification, and the top level function does a foreach
on the alerts. error, success, info.  warning?  so change the text in the flash and remove the crud!!!!
put in a loop with just this:


new PNotify({
    title: 'Font Awesome Success',
    text: 'Look at my beautiful styling! ^_^',
    type: 'success',
    styling: 'fontawesome'
                    });



