export default {
    toUSDCurrency : function(enteredNumber){
        return Number(enteredNumber).toLocaleString('en-US', { style: 'currency', currency: 'USD' });
    }
};