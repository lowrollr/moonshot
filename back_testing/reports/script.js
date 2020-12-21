function sortRows(n) {
    let table = document.getElementById("ind_movements_data");
    let switching = true;
    let dir = "asc";
    var shouldSwitch;
    let switchcount = 0;

    let header = table.rows[0];
    let final_arr;

    let table_arr = []
    for (let i = 1; i < table.rows.length; i++) {
        let id = parseFloat(table.rows[i].getElementsByTagName("TD")[n].innerHTML.toLowerCase());
        table_arr.push([id, table.rows[i]]);
    }
    let rows = table_arr;
    while( switching ) {
        
        switching = false;
        for (i = 0; i < rows.length-2; i++) {
            shouldSwitch = false;
            let x = rows[i][0]
            let y = rows[i + 1][0]

            if ( dir === "asc" ) {
                if (x > y) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            } else if (dir == "desc") {
                if (x < y) {
                    // If so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            /* If a switch has been marked, make the switch
            and mark that a switch has been done: */
            rows = swap(rows, i+1, i);
            //rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            // Each time a switch is done, increase this count by 1:
            switchcount ++;
          } else {
            /* If no switching has been done AND the direction is "asc",
            set the direction to "desc" and run the while loop again. */
            if (switchcount == 0 && dir == "asc") {
              dir = "desc";
              switching = true;
            }
        }
        final_arr = rows;
    }
    table.innerHTML = "";
    table.appendChild(header);

    for( let i = 0; i < final_arr.length; i++) {
        table.appendChild(final_arr[i][1]);
    }
}

function quickSort(arr, left, right) {
	let index;

	//We want to check if we even need to do the sorting
	if (arr.length > 1)
	{
		//We first sort the function, and return the center which is used to divide the array
		index = sortingUsingPivot(arr, left, right);

		//If there are more elements on the left side of pivot that needs to be sorted
		if (left < index - 1)
		{
			//will put the entire left of the array into the quicksort again
			quickSort(arr, left, index - 1);
		}

		//If there are more elements on the right side of pivot that needs to be sorted
		if (index < right) 
		{
			//will put the entire right of the array into the quicksort again
			quickSort(arr, index, right);
		}
	}
} 

function sortingUsingPivot(arr, left, right) {
	//We are using the middle element of the array as our pivot
	let pivot = arr[Math.floor((right + left) / 2)];
	let l = left; //This is keeping track of left pointer
	let r = right; //this is keeping track of right pointer

	//Keep going until left pointer passes the right pointer
	while (l <= r) 
	{
		//Used Find the first element on the left side that is larger than the pivot element.
		//So that we know this is the element we want to move to the other side 
		while (arr[l] < pivot)
		{
			//Keep searching until we pass the pivot
			l++;
		}

		//Used Find the first element on the right side that is smaller than the pivot element.
		//So that we know this is the element we want to move to the other side 
		while (arr[r] > pivot) 
		{
			//Keep searching until we pass the pivot
			r--;
		} 

		//we want to swap the two elements as long as left pointer doesn't pass the right pointer
		if (l <= r) {
			swap(arr, l, r);
			l++;
			r--;
		}
	}

	//Return the left pointer as that is our new center to divide the array
	return l;
}

function swap(arr, leftIndex, rightIndex) {
	//We basically just swap the two items from the two different index
	let temp = arr[leftIndex];
	arr[leftIndex] = arr[rightIndex];
    arr[rightIndex] = temp;
    return arr;
}