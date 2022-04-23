function getRandomInt(max) {
  return Math.floor(Math.random() * max);
}

function* range(start, end) {
    for (let i = start; i <= end; i++) {
        yield i;
    }
}

const colors = ['darkseagreen', 'green', 'brown']

let dndhexes = [
  {x: 0, y: 1, elevation: -10},
  {x: 0, y: 2, elevation: -1000, settlements: ['Ribossi']}
]

function elevToColor(e) {
	if (e < 0) {
  	return 'blue'
  } else {
		let band = Math.floor(e / 400)
    return colors[band]
  }
}

const draw = SVG().addTo('#map').size('1000', '1000')
const Hex = Honeycomb.extendHex({
  size: 15
})
// const h = Hex() // TODO do I even need this? 

const Grid = Honeycomb.defineGrid(Hex)
// all hexes created with the same Hex factory have same corners
const corners = Hex().corners()
// create SVG polygon to use over and over in SVG <use> element
const hexSymbol = draw.symbol()
  .polygon(corners.map(({
    x,
    y
  }) => `${x},${y}`))
  .stroke({
    width: 1,
    color: '#999'
  })

// make rectangular grid; onCreate's callback gives each hex a random elevation
const grid = Grid.rectangle({
  width: 15,
  height: 15,
  onCreate: (hex) => {hex.elevation = getRandomInt(1000)}
})

for (let d of dndhexes) {
  if (d.settlements === undefined) {
    d.settlements = []
  }
  grid.set([d.x, d.y], Hex(d.x, d.y, {settlements: d.settlements, elevation: d.elevation}))
}

grid.forEach(hex => {
  const {
    x,
    y
  } = hex.toPoint()
  // use hexSymbol and set its position for each hex
  draw.use(hexSymbol).attr({ fill: elevToColor(hex.elevation) }).translate(x, y)
  //attr('class', 'bingo').
})

function displayClicked({ offsetX, offsetY }) {
  const p = document.getElementById('location')
  // convert point to hex (coordinates)
  const hexCoordinates = Grid.pointToHex(offsetX, offsetY)
  // get the actual hex from the grid
  let g = grid.get(hexCoordinates)
  console.log(g)
  if (!(g === undefined)) {
    p.innerHTML = JSON.stringify(g)
  }
}

// TODO make this only apply on hexagons
document.addEventListener('click', displayClicked)




// python hexes
// https://github.com/redft/hexy
// python svg
// https://github.com/cduck/drawSvg
