/**
 * Created by raylenmargono on 12/6/16.
 */
import {hrAppAction} from 'js/flux/hrDashboard/actions/actions';
import {bind, createStore } from 'alt-utils/lib/decorators';
import alt from 'js/flux/alt';

@createStore(alt)
class HRAppStore{
    constructor() {
        this.state = {
            shouldHideNav : false
        };
    }

    @bind(hrAppAction.handleHideNav)
    handleHideNav(shouldHideNav){
        this.setState({
            shouldHideNav : shouldHideNav
        });
    }
}

export default HRAppStore;