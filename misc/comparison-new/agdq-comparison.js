var colors = ['#e45649', '#e06c75','#50a14f', '#98c379','#c18401', '#e5c07b','#0184bc', '#61afef','#a626a4', '#c678dd','#0997b3', '#56b6c2'];
var i = 0;
function nextColor() {
  var color = colors[i];
  i = (i + 1) % colors.length;
  return color;
}

// notes
//
// - make rootDate the current marathon, so the timezones work
// - i hate utc
// - i hate not utc

const dateDiff = new Date().getTimezoneOffset() / 60;
const rootDate =  new Date(2021, 6, 4, 12, 0);

loadData({
  sgdq21: {
    url: '/sgdq21/sgdq21.json',
    start: new Date(2021, 6, 4, 12, 0),
    color: nextColor(),
    highlight: true,
  },
  agdq21: {
    url: '/agdq21/agdq21.json',
    start: new Date(2021, 0, 3, 12, 0),
    color: nextColor(),
  },
  sgdq20: {
    url: '/sgdq20/sgdq20.json',
    start: new Date(2020, 7, 16, 12, 0),
    color: nextColor(),
  },
  agdq20: {
    url: '/agdq20/agdq20.json',
    start: new Date(2020, 0, 5, 12, 0),
    color: nextColor(),
  },
  sgdq19: {
    url: '/sgdq19/sgdq19.json',
    start: new Date(2019, 5, 23, 12, 0),
    color: nextColor(),
  },
  agdq19: {
    url: '/agdq19/agdq19.json',
    start: new Date(2019, 0, 6, 12, 0),
    color: nextColor(),
  },
  sgdq18: {
    url: '/sgdq18/sgdq18.json',
    start: new Date(2018, 5, 24, 12, 0),
    color: nextColor(),
  },
  agdq18: {
    url: '/agdq18/agdq18.json',
    start: new Date(2018, 0, 7, 12),
    color: nextColor(),
  },
  sgdq17: {
    url: '/sgdq17/sgdq17.json',
    start: new Date(2017, 6, 2, 12),
    color: nextColor(),
  },
  agdq17: {
    url: '/agdq17/agdq17.json',
    start: new Date(2017, 0, 8, 12),
    color: nextColor(),
  },
  sgdq16: {
    url: '/sgdq16/sgdq16.json',
    start: new Date(2016, 6, 3, 12),
    color: nextColor(),
  },
  agdq16: {
    url: '/agdq16/agdq16.json',
    start: new Date(2016, 0, 3, 12),
    color: nextColor(),
  },
  sgdq15: {
    url: '/sgdq15/sgdq15.json',
    start: new Date(2015, 6, 26, 12),
    color: nextColor(),
  },
  agdq15: {
    url: '/agdq15/agdq15-scraped.json',
    start: new Date(2015, 0, 4, 12),
    color: nextColor(),
  },
  sgdq14: {
    url: '/sgdq14/sgdq14.json',
    start: new Date(2014, 5, 22, 12),
    color: nextColor(),
  },
  agdq14: {
    url: '/agdq14/agdq14.json',
    start: new Date(2014, 0, 5, 12),
    color: nextColor(),
  },
}).then(function(state) {
  drawCheckboxes(state);

  let resizeTimeout;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
      checkAndDraw(state);
    }, 500);
  });
});

function getQueryString() {
  var sp = window.location.href.split('?');
  if (sp.length === 1) {
    return;
  }
  var qs = sp[1];
  return qs.split(',');
}

function drawCheckboxes(state) {
  var el = document.querySelector('#main-checkboxes');
  var queryString = getQueryString();
  Object.keys(state).forEach(function(name) {
    var label = document.createElement('label');
    label.innerText = name;
    label.htmlFor = name;
    label.style = 'color: ' + state[name].color + (state[name].highlight ? '; font-weight: bold;' : ';')

    var checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = name;
    checkbox.style = 'margin-right: 1em;';
    checkbox.value = name
    if (queryString) {
      checkbox.checked = queryString.includes(name);
    } else {
      checkbox.checked = true;
    }
    checkbox.onchange = checkAndDraw.bind(this, state);

    var div = document.createElement('div');
    div.style.display = 'flex';
    div.appendChild(label);
    div.appendChild(checkbox);
    el.appendChild(div);
  });
  checkAndDraw(state);
}

function checkAndDraw(state) {
  var checkboxes = document.querySelectorAll('#main-checkboxes input');
  var dataToDraw = {};
  for (var i = 0; i < checkboxes.length; i++) {
    var cb = checkboxes[i];
    if (cb.checked) {
      dataToDraw[cb.value] = state[cb.value];
    }
  }
  drawGraph(dataToDraw);
}

function loadData(state) {
  var i = Object.keys(state).length
  return new Promise(function(resolve, reject) {
    Object.keys(state).forEach(function(name) {
      var url = state[name].url;
      d3.json(url, function(error, response) {
        state[name].data = response.viewers;
        if (!--i) {
          resolve(state);
        }
      });
    });
  });
}

function drawGraph(ogState) {
  var processData = function (startDate, point) {
    // if (i % ((length/460)|0) != 0) return;
    var diff = (point[0] * 1000) - startDate.getTime()
    var date = new Date(rootDate.getTime() + diff);
    date.setUTCHours(date.getUTCHours() - dateDiff);
    return { total: point[2], diff: diff, date };
  };

  var max = Object.keys(ogState).reduce(function(acc, name) {
    var l = ogState[name].data.length;
    return l > acc ? l : acc;
  }, -Infinity);
  var step = (max/2000)|0;

  const state = {};
  Object.keys(ogState).map(function(name) {
    state[name] = {
      data: ogState[name].data
        .filter(function(d, i) {
          return i % step === 0;
        })
        .map(processData.bind(this, ogState[name].start)),
      start: ogState[name].start,
      highlight: ogState[name].highlight,
      color: ogState[name].color,
    };
  });

  var minDiff  = Math.min.apply(Math, Object.keys(state).map(function(name) {
    const data = state[name].data[0];
    if (data) {
      return data.diff;
    }
    return null;
  }));
  var maxDiff  = Math.max.apply(Math, Object.keys(state).map(function(name) {
    const data = state[name].data[state[name].data.length-1];
    if (data) {
      return data.diff;
    }
    return null;
  }));
  var minTotal  = Math.min.apply(Math, Object.keys(state).map(function(name) {
    const data = state[name].data[0];
    if (data) {
      return data.total;
    }
    return null;
  }));
  var maxTotal  = Math.max.apply(Math, Object.keys(state).map(function(name) {
    const data = state[name].data[state[name].data.length-1];
    if (data) {
      return data.total;
    }
    return null;
  }));

  var el = document.getElementById('main-chart');
  var elWidth = el.getBoundingClientRect().width;
  var elHeight = window.innerHeight - 120;

  var margin = {top: 20, right: 10, bottom: 30, left: 100},
      width = elWidth - margin.left - margin.right,
      height = elHeight - margin.top - margin.bottom;

  var y = d3.scale.linear()
    .range([height, 0]);

  var commasFormatter = d3.format(",.0f")

  const endDate = new Date(rootDate);
  endDate.setDate(endDate.getDate() + 7);

  var x = d3.time.scale()
    .domain([rootDate, endDate])
    .range([0, width]);

  var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom")
    .ticks(12)
    .innerTickSize(-height)
    .tickFormat(d3.time.format.utc("%a %I%p"));

  var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left")
    .innerTickSize(-width)
    .outerTickSize(0)
    .tickFormat(function(d) { return '$' + commasFormatter(d) });

  var line = d3.svg.line()
    .interpolate("monotone")
    .x(function (d) { return x(d.date); })
    .y(function (d) { return y(d.total); })
    .defined(function(d) { return d.total > 0 && d.total != null; });

  y.domain([minTotal, maxTotal]);

  var svg = d3.select('#main-chart').html('').append('svg')
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var focusLineG = svg.append('g')
    .attr('class', 'focusline');
  var focusLine = focusLineG.append('line')
    .style('display', 'none')
    .style('stroke', '#FF4081');
  var lineg = svg.append('g').attr("pointer-events", "none").attr('opacity', 0);

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis);

  var keys = Object.keys(state);
  for (var i = keys.length - 1; i >= 0; i--) {
    svg.append("path")
        .datum(state[keys[i]].data)
        .attr("class", "line")
        .attr("d", line)
        .style("stroke", state[keys[i]].color)
        .style("stroke-width", state[keys[i]].highlight ? '3px' : '1.5px')
        .style("opacity", state[keys[i]].highlight ? '1' : '0.75');
  }

  var tip = d3.select('#main-chart').append('div')
    .attr('class', 'tooltip');

  var bisect = d3.bisector(function (d) { return d.date; }).left;
  var timeFmt = d3.time.format.utc("%a %I:%M%p");

  function tooltip () {
    var x0 = x.invert(d3.mouse(this)[0]);
      /*
      a = bisect(four, x0, 1),
      b = bisect(five, x0, 1),
      nFour = four[a - 1],
      nFive = five[b - 1];
      */

    // var aDiff = Math.abs(x(nFour.diff) - x(x0));
    // var bDiff = Math.abs(x(nFive.diff) - x(x0));
    // var xPos = aDiff < bDiff ? x(nFour.diff) : x(nFive.diff);

    focusLine
      .attr('x1', d3.mouse(this)[0])
      .attr('x2', d3.mouse(this)[0])
      .attr('y1', 0)
      .attr('y2', height);

    var totals = Object.keys(state).reduce(function(acc, name) {
      var bi = bisect(state[name].data, x0, 2);
      var point = state[name].data[bi - 1];
      // if (bi < state[name].data.length) {
        acc.push({ name: name, total: point.total });
        // acc[name] = '$' + commasFormatter(point.total);
      // }
      return acc;
    }, []);

    var html = totals
      .sort((a, b) => b.total - a.total)
      .map((total) => {
        var name = total.name;
        var fontWeight = (state[name].highlight ? '; font-weight: bold;' : ';')
        return '<div style="color: ' + state[name].color + '; display: flex; justify-content: space-between' + fontWeight + '">' +
          '<div class="tip-label">' + name + '</div>' +
          '<div>$' + (commasFormatter(total.total) || '0') + '</div>' +
        '</div>';
      })
      .join('');

    tip.html('<div class="tip-text" style="width: 100%; padding: 4px;"><span>' + timeFmt(x0) + '</span>' + html + '</div>')
      .style("left", (d3.event.pageX - 160) + "px")
      .style("top", (d3.event.pageY - 20) + "px");
  }

  svg.append("rect")
      .attr("class", "overlay")
      .attr("width", width)
      .attr("height", height)
      .on("mouseover", function() {
        tip.style("display", null);
        focusLine.style("display", null);
      })
      .on("mouseout", function() {
        tip.style("display", "none");
        focusLine.style("display", "none");
      })
      .on("mousemove", tooltip);
}
