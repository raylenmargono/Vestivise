/**
 * Created by raylenmargono on 1/27/17.
 */

class MainWalkThrough{

    static startWalkThrough(type, onComplete){
        let tour = new Shepherd.Tour({
            defaults: {
                classes: 'shepherd-theme-arrows'
            }
        });

        function displayOverlay(o){
            if($('.shep-overlay').length == 0){
                var shep_el = $('<div class="shep-overlay"></div>');
                $('body').append(shep_el);
            }
        }

        function onShow(id){
            prevZ = $(id).css("z-index");
            $(id).css("z-index", 51);
        }

        function onHide(id){
            $(id).css("z-index", prevZ);
        }

        Shepherd.on("show", displayOverlay);
        Shepherd.on("inactive", function(){
            $('.shep-overlay').hide()
            onComplete();
        });

        var prevZ = 0;

        const buttons = [
            {
                text : 'Back',
                action : tour.back,
                classes : "shep-button"
            },
            {
                text : 'Next',
                action : tour.next,
                classes : "shep-button"
            }
        ];

        if(type == "linkage"){
            tour.addStep('Return To Dashboard', {
                title: 'Return to Dashboard',
                text: 'Click here to return to dashboard after account syncs.',
                attachTo: '#returnButton left',
                when : {
                    show : onShow.bind(this, ".chart-container"),
                    hide: onHide.bind(this, ".chart-container")
                },
                tetherOptions:{
                    attachment:'top right',
                    targetAttachment:'bottom center',
                },
                buttons : [{
                    text: 'Next',
                    action: tour.next,
                    classes: "shep-button"
                }]
            });
        }
        else if(type=="dashboard"){
            tour.addStep('Rotate Modules', {
                title: 'Rotate Modules',
                text: 'Flip through the modules in each of the four sections using these buttons.',
                attachTo: '#sn-Asset right',
                when : {
                    show : onShow.bind(this, "#sn-Asset"),
                    hide: onHide.bind(this, "#sn-Asset")
                },
                buttons : [{
                    text: 'Next',
                    action: tour.next,
                    classes: "shep-button"
                }]
            });

            tour.addStep('More Info', {
                title: 'More Info',
                text: 'Hover over the modules for more information.',
                attachTo: '.vestiBlock bottom',
                when : {
                    show : onShow.bind(this, ".vestiBlock"),
                    hide: onHide.bind(this, ".vestiBlock")
                },
                buttons : buttons
            });

            tour.addStep('Understand Terms', {
                title: 'Understand Terms',
                text: 'Click on the highlighted words to view the annotations.',
                attachTo: '#holdingTypesidparent top',
                when : {
                    show : onShow.bind(this, "#holdingTypesid"),
                    hide: onHide.bind(this, "#holdingTypesid")
                },
                buttons : buttons
            });

            tour.addStep('Dashboard Categories', {
                title: 'Dashboard Categories',
                text: 'Scroll down or click here to jump to any of the four sections of the dashboard.',
                attachTo: '#moduleNav-container bottom',
                when : {
                    show : onShow.bind(this, "#moduleNav"),
                    hide: onHide.bind(this, "#moduleNav")
                },
                tetherOptions:{
                    attachment:'top right',
                    targetAttachment:'bottom center',
                },
                buttons : buttons
            });

            tour.addStep('Filter Accounts', {
                title: 'Filter Accounts',
                text: 'Click here to filter your dashboard by account(s) or to view all your accounts combined',
                attachTo: '#filterButton bottom',
                when : {
                    show : onShow.bind(this, '#filterButton'),
                    hide: onHide.bind(this, '#filterButton')
                },
                tetherOptions:{
                    attachment:'top right',
                    targetAttachment:'bottom center',
                },
                buttons :buttons
            });

            tour.addStep('Holding Breakdown', {
                title: 'Holding Breakdown',
                text: 'Click here to see the holdings that make up your portfolio.<br>The dashboard shown is based on the holdings that have been verified.',
                attachTo: '#holdingButton bottom',
                when : {
                    show : onShow.bind(this, "#holdingButton"),
                    hide: function() {
                        onHide("#holdingButton");
                        $('#holdingModal').modal('open');
                    }.bind(this)
                },
                tetherOptions:{
                    attachment:'top right',
                    targetAttachment:'bottom center',
                },
                buttons : [
                    {
                        text : 'Done',
                        action : tour.next,
                        classes : "shep-button"
                    }
                ]
            });
        }

        tour.start();
    }
}


export default MainWalkThrough;