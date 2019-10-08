// Ojects

const pikachu = { name: 'Pikachu'}
const stats = { hp: 40, attack: 60, defense: 50 }

// Bad Oject code
pikachu['hp'] = stats.hp
pikachu['attack'] = stats.attack
pikachu['defense'] = stats.defense

// OR

const lvl0 = Object.assign(pikachu, stats)
const lvl1 = Oject.assign(pikachu, { hp: 45 })


// Good Ojbect code (oject further to the right will have priority)
const lvl0 = { ...pikachu, ...stats }
const lvl1 = { ...pikachu, hp: 45}



// Arrays
let pokemon = ['Arbok', 'Raichu', 'Sandshrew'];

// Bad Array code
pokemon.push('Bulbasaur')
pokemon.push('Metapod')
pokemon.push('Weedle')


// Good Array code
// will push the array
pokemon = [ ...pokemon, 'Bulbasaur', 'Metapod', 'Weedle']

// will append to the end of the array
pokemon = [ 'Bulbasaur', 'Metapod', 'Weedle', ...pokemon]

// or anywhere in between
pokemon = [ 'Bulbasaur', 'Metapod', ...pokemon, 'Weedle']