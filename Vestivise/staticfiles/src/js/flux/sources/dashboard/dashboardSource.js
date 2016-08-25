import AppActions from '../../actions/dashboard/dashboardActions';
import API from '../../../api';

export const DashboardSource = {
	performSearch : {
		
		remote(state){
			return API.get(Urls.account())
		},

		loading : AppActions.dataLoading,

		success : AppActions.dataSuccess,

		error : AppActions.dataFail,

		shouldFetch(state){
			return true;
		}


	}
};