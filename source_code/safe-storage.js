window.safeStorage={getItem:function(k){try{return window.localStorage.getItem(k)}catch(e){return null}},setItem:function(k,v){try{window.localStorage.setItem(k,v)}catch(e){}}};
