let ws3000 = require('ambientweather-ws3000');
let fs = require('fs');

async function main() {
  let sensors = await ws3000.query();

  const temps = [];
  for (let i = 1; i <= 8; ++i) {
    if (sensors[i].active) {
      temps.push(sensors[i].temperature);
    } else {
      temps.push('');
    }
  }
  fs.writeFileSync('temps.csv', temps.join(','));
}

main().then(() => {process.exit(0);});
