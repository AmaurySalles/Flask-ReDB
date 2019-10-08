const turtle = {
    name: 'Bob',
    legs: '4',
    shell: true,
    type: 'amphibious',
    meal: 10,
    diet: 'berries'
}


//Bad code
function feed(animal) {
    return `Feed ${animal.name} ${animal.meal} kilos of ${animal.diet}`;
}

//Good code
function feed({name, meal, diet}) {
    return `Feed ${name} ${meal} kilos of ${diet}`;
}

//Alternative good code
function feed(animal) {
    const {name, meal, diet} = animal;
    return `Feed ${name} ${meal} kilos of ${diet}`;
}