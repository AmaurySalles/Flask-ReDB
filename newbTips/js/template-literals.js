const horse = {
    name: 'Topher',
    size: 'large',
    skills: ['jousting', 'racing'],
    age: 7,
}

// Bad string code
let bio = horse.name + 'is a ' + horse.size + ' ' + horse.age + 'year old horse, which killed human in a ' + horse.skills.join(' & ') + 'constest.';
console.log(bio);

// Good string code
const {name, age, size, skills} = horse;
let bio =  `${name} is a ${size} ${age} year old horse, which killed human in a ${skills.join(' & ')} constest.`;
console.log(bio);


// Advanced tag example
function horseAge(str, age) {
    const ageStr = age > 5 ? 'old' : 'young';
    return `${str[0]}${ageStr} at ${age} years`;
}
 const bio2 = horseAge`This horse is ${horse.age}`;
 console.log(bio2);