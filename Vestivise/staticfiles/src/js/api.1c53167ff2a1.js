var csrfToken = require('./csrfToken.js');

function API(){
	this.url = "";
}

API.prototype.post = function(url, payload){
	var request = $.ajax({
		url: url,
		type: 'POST',
		data: payload,
		headers: {'X-CSRFToken': csrfToken},

	})
	return request;
}

API.prototype.get = function(url){
	var request = $.ajax({
		url: url,
		type: 'GET',
		headers: {'X-CSRFToken': csrfToken},

	})
	return request;
}

API.prototype.delete = function(url){
	var request = $.ajax({
		url: url,
		type: 'DELETE',
		headers: {'X-CSRFToken': csrfToken},

	})
	return request;
}

module.exports = new API();