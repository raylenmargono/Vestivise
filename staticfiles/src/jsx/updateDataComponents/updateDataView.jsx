import React from 'react';
import API from '../../js/api.js';
import { getRootUrl } from '../../js/utils.js';

class UpdateDataView extends React.Component {
    constructor(props) {
        super(props);
        this.displayName = 'UpdateDataView';
    }

    componentDidMount() {
        window.loading_screen = window.pleaseWait({
            logo: "",
            backgroundColor: '#F24258',
            loadingHtml: "<div class='sk-cube-grid'>"
                        +"<div class='sk-cube sk-cube1'></div>"
                        +"<div class='sk-cube sk-cube2'></div>"
                        +"<div class='sk-cube sk-cube3'></div>"
                        +"<div class='sk-cube sk-cube4'></div>"
                        +"<div class='sk-cube sk-cube5'></div>"
                        +"<div class='sk-cube sk-cube6'></div>"
                        +"<div class='sk-cube sk-cube7'></div>"
                        +"<div class='sk-cube sk-cube8'></div>"
                        +"<div class='sk-cube sk-cube9'></div>"
                        +"</div>"
                        + "<h1 id='loaderLabel'> Updating Data </h1>"
        });

        API.post(Urls.testNightlyProcess(), null)
        .done(function(res){
            console.log(res);
            window.location.href = Urls.dashboard();
        }.bind(this)) 
        .fail(function(e){
            console.log(e);
        }.bind(this));

    }

    render() {
        return <div></div>;
    }
}

export default UpdateDataView;
