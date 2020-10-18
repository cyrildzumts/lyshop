
/**
 * 
 * @param {*} options is a JSON defining the following data :
 * type - string
 * url - string
 * data - json
 * dataType - string
 * Example : 
 * type: 'POST',
   url : '/cart/add_to_cart/',
   data: {product_id: 102, quantity: 4},
   dataType: 'json'

   A future object is returned
 */
function ajax(options){
    return new Promise(function(resolve, reject){
        $.ajax(options).done(resolve).fail(reject);
    });
}

