function getRandomInt(max) {
  return Math.floor(Math.random() * max);
}

function* range(start, end) {
    for (let i = start; i <= end; i++) {
        yield i;
    }
}

const colors = ['green', 'lightgreen', 'seagreen']

let dndhexes = [
  {x: 10, y: 8, elevation: 401, settlements: ['Ribossi']},
  {x: 11, y: 8, elevation: 1, settlements: ['Northshore']},
  {x: 12, y: 8, elevation: -1},
  {x: 10, y: 9, elevation: 401, settlements: ['Castle Baccia']},
  {x: 11, y: 9, elevation: 1, settlements: ['Shipmoot']},
  {x: 12, y: 9, elevation: -1},
  {x: 14, y: 10, elevation: 1, settlements: ['Pearl Island']},
  {x: 11, y: 10, elevation: 1, settlements: ['Sacra Mara']},
  {x: 11, y: 11, elevation: 1, settlements: ['Allrivers']}
]

function elevToColor(e) {
	if (e < 0) {
  	return 'blue'
  } else {
		let band = Math.floor(e / 400)
    return colors[band]
  }
}

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

const draw = SVG().addTo('#map').size('1000', '1000')
const Hex = Honeycomb.extendHex({
  size: 25
})

const Grid = Honeycomb.defineGrid(Hex)
// all hexes created with the same Hex factory have same corners
const corners = Hex().corners()
// create SVG polygon to use over and over in SVG <use> element
const plainHex = draw.symbol()
  .polygon(corners.map(({
    x,
    y
  }) => `${x},${y}`))
  .stroke({
    width: 1,
    color: '#999'
  })

const townSymbol = draw.symbol()
  .circle(10)
  .stroke({
    width: 1,
    color: '#999'
  })
  .fill({
    color: '#000'
  })

// make rectangular grid; onCreate's callback gives each hex a random elevation
const grid = Grid.rectangle({
  width: 20,
  height: 20,
  onCreate: (hex) => {hex.elevation = -1}
})

for (let d of dndhexes) {
  if (d.settlements === undefined) {
    grid.set([d.x, d.y], Hex(d.x, d.y, {elevation: d.elevation}))
  } else {
    grid.set([d.x, d.y], Hex(d.x, d.y, {settlements: d.settlements, elevation: d.elevation}))
  }
}

grid.forEach(hex => {
  const {
    x,
    y
  } = hex.toPoint()
  // use plainHex and set its position for each hex
  draw.use(plainHex).attr({ fill: elevToColor(hex.elevation) }).translate(x, y)
  if (hex.settlements) {
    draw.use(townSymbol).translate(x+20, y+20)
  }
})

// TODO make this only apply on hexagons
document.addEventListener('click', displayClicked)




// python hexes
// https://github.com/redft/hexy
// python svg
// https://github.com/cduck/drawSvg
