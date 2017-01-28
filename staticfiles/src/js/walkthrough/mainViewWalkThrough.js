/**
 * Created by raylenmargono on 1/27/17.
 */

class MainWalkThrough{

    static startWalkThrough(type){
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
        });

        var prevZ = 0;

        if(type == "linkage"){
            tour.addStep('Return To Dashboard', {
                title: 'Example Shepherd',
                text: 'Creating a Shepherd is easy too! Just create ...',
                attachTo: '#returnButton left',
                when : {
                    show : onShow.bind(this, "#returnButton"),
                    hide: onHide.bind(this, "#returnButton")
                },
                tetherOptions:{
                    attachment:'top right',
                    targetAttachment:'bottom center',
                }
            });
        }

        tour.start();
    }

}


export default MainWalkThrough;