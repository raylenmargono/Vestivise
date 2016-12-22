import csrftoken from './csrfToken';
import request from 'superagent';

class API{
	post(url, data){
		var q = request.post(url)
		return this.execute(q, data);
	}
	put(url, data){
		var q = request.put(url)
		return this.execute(q, data);
	}
	patch(url, data){
		var q = request.patch(url)
		return this.execute(q, data);
	}
	get(url, params){
		var q = request.get(url)
        if(params){
            q = q.query(params);
        }
		return this.execute(q);
	}
	delete(url){
		var q = request.delete(url)
		return this.execute(q);
	}

	execute(q, data){
		var result = q;
		if(data){
			result = result.send(data);
		}
		result = result.set('X-CSRFToken', csrftoken);
		return result;
	}
}

export default new API();