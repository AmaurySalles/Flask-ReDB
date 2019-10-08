const orders = [500, 30, 99, 15, 223];

// Bad Loop code
const total = 0;
const withTax = [];
const highValue = [];
for (i = 0; i < orders.length; i++){

    // Reduce
    total += orders[i];

    // Map
    withTax.push(orders[i] * 1.1);

    //Filter
    if (orders[i] > 100) {
        highValue.push(orders[i])
    }
}


// Good Loop code

// Reduce - acc is the accumulated value and curr is the current value
const total = orders.reduce((acc, cur) => acc + cur)

// Map
const withTax = orders.map(value => value * 1.1)

// Filter
const highValue = orders.filter(value => value > 100);
