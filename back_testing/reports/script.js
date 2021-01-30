function sortRows(n, table_num=-1) {
    var table;
    if (table_num == -1) {
        table = document.getElementById("ind_movements_data");
    } else {
        table = document.getElementById("ind_movements_data" + String(table_num))
    }

    let header = table.rows[0];
    let final_arr;

    let table_arr = []
    for (let i = 1; i < table.rows.length; i++) {
        let id = parseFloat(table.rows[i].getElementsByTagName("TD")[n].innerHTML.toLowerCase());
        table_arr.push([id, table.rows[i]]);
    }
    let rows = table_arr;

    if ( this.direction === undefined ) {
        this.direction = true;
    }
    final_arr = quickSort(rows, 0, rows.length - 1);
    table.innerHTML = "";
    table.appendChild(header);

    if ( this.direction === false) {
        final_arr = final_arr.reverse();
    }

    for( let i = 0; i < final_arr.length; i++) {
        table.appendChild(final_arr[i][1]);
    }
    table.style.display = null;
    table.style['justify-content'] = 'center';
    this.direction = this.direction === true ? false : true;
    console.log(this.direction);
}

function swap(items, leftIndex, rightIndex){
    var temp = items[leftIndex];
    items[leftIndex] = items[rightIndex];
    items[rightIndex] = temp;
}

function partition(items, left, right) {
    var pivot   = items[Math.floor((right + left) / 2)][0], //middle element
        i       = left, //left pointer
        j       = right; //right pointer
    while (i <= j) {
        while (items[i][0] < pivot) {
            i++;
        }
        while (items[j][0] > pivot) {
            j--;
        }
        if (i <= j) {
            swap(items, i, j); //sawpping two elements
            i++;
            j--;
        }
    }
    return i;
}

function quickSort(items, left, right) {
    var index;
    if (items.length > 1) {
        index = partition(items, left, right); //index returned from partition
        if (left < index - 1) { //more elements on the left side of the pivot
            quickSort(items, left, index - 1);
        }
        if (index < right) { //more elements on the right side of the pivot
            quickSort(items, index, right);
        }
    }
    return items;
}

function revealTable(coin_num) {
    var table;
    if (coin_num == -1) {
        table = document.getElementById("ind_movements_data");
    } else {
        table = document.getElementById("ind_movements_data" + String(coin_num))
    }
    
    if (table.style.display == "none"){
        table.style.display = null;
        table.style['justify-content'] = 'center';
    }  else {
        table.style.display = 'none';
    }
}