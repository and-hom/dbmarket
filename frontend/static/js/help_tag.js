$(document).ready(function(){
    $('a.help-tag').popover({
        animation:false,
        html:false,
        placement:'right',
        trigger: 'click focus'
    });

    $('body').on('click', function (e) {
        $('a.help-tag').each(function () {
            //the 'is' for buttons that trigger popups
            //the 'has' for icons within a button that triggers a popup
            if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
                $(this).popover('hide');
            }
        });
    });
});
