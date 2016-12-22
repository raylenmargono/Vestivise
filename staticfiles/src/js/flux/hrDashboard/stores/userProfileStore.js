import {HRProfileSource} from 'js/flux/hrDashboard/sources/sources';
import {HRProfileActions} from 'js/flux/hrDashboard/actions/actions';
import { datasource, bind, createStore } from 'alt-utils/lib/decorators';
import alt from 'js/flux/alt';

@createStore(alt)
@datasource(HRProfileSource)
class HRProfileStore{

    constructor(){
        this.state = {
            companyName : "",
            isLoading : false,
            renewalDate : null
        };
    }

    @bind(HRProfileActions.loadingResults)
    profileSearchLoading(isLoading){
        this.setState({
            isLoading: isLoading
        });
    }

    @bind(HRProfileActions.receivedResults)
    profileSearchResults(payload){
        this.setState({
            isLoading: false,
            companyName : payload.company,
            renewalDate : payload.subscription_date
        });
    }

    @bind(HRProfileActions.fetchingResultsFailed)
    profileSearchFailed(e){
        //alt.rollback();
        this.setState({
            isLoading: false
        });
    }
}

export default HRProfileStore;