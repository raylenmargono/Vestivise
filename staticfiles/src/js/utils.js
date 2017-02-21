function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function isJson(str) {
    try {
        JSON.parse(str);
    } catch (e) {
        return false;
    }
    return true;
}

function getRootUrl() {
    return window.location.origin?window.location.origin:window.location.protocol+'/'+window.location.host;
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function toUSDCurrency(enteredNumber){
    return Number(enteredNumber).toLocaleString('en-US', { style: 'currency', currency: 'USD' });
}
function localStoragePut(key, o){
    if(typeof o === "object"){
        o = JSON.stringify(o);
    }
    localStorage.setItem(key, o);
}
function localStorageGet(key){
    var o = localStorage.getItem(key);
    if(isJson(o)){
        o = JSON.parse(o);
    }
    return o;
}

const Storage = {
    put : localStoragePut,
    get : localStorageGet
};

export {getParameterByName, getRootUrl, getCookie, toUSDCurrency, Storage}