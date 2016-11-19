import AppActions from '../../actions/dashboard/dashboardActions';
import API from '../../../api';

export const DashboardSource = {
	performSearch : {
		
		remote(state){
			return API.get(Urls.profile())
		},

		loading : AppActions.dataLoading,

		success : AppActions.dataSuccess,

		error : AppActions.dataFail,

		shouldFetch(state){
			return true;
		}
	}
};