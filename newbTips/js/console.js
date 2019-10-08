const foo = {name:'Tom', age: 30, nervous: false};
const bar = {name:'Dick', age: 40, nervous: true};
const baz = {name:'Harry', age: 50, nervous: false};


// Bad code
console.log(foo);
console.log(bar);
console.log(baz);

// Good code - Computed Property Names
console.log({foo, bar, baz});

// Good code - Making it stand out with CSS
console.log('%c My Friends', 'colour: orange; font-weight: bold;')
console.log({foo, bar, baz});

// Good code - Console Tables
console.table([foo, bar, baz]);



// Other tips

// Console time
console.time('looper')

    // Task
    let i = 0;
    while(i<1000000) { i++ }

console.timeEnd('looper')


// Stack Trace Logs to log where function is defined and where it was called (in which doc and which line)
const deleteMe = () => console.trace('bye bye database')
deleteMe()
deleteMe()