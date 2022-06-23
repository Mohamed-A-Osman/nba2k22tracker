function sort(tdata){
    var th = document.getElementsByTagName('th');
              for(let e of th){
                if(e.id == "0" || e.id == 2){
                    continue;
                  }
                
                e.addEventListener("click", ()=>{
                  Udata = tdata;
                  if(e.dataset.col == "desc"){
                    data = Udata.sort((a, b) => parseFloat(a[e.id]) - parseFloat(b[e.id]));
                    e.innerHTML = e.dataset.name + "&#9650";
                    e.dataset.col = "asc"
                    createTable(data, true)
                  }else{
                    for(let e of th){
                      e.style = "color:white";
                      e.innerHTML = e.dataset.name;
                      e.dataset.col = "neither"

                    }
                    e.style="color:red";
                    data = Udata.sort((a, b) => parseFloat(b[e.id]) - parseFloat(a[e.id]));
                    e.innerHTML = e.dataset.name + "&#9660";
                    e.dataset.col = "desc"
                    createTable(data, true)

                  }
                    
                })
              }
}
