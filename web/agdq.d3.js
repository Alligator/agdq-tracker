'use strict';
var fg = '#444';
var bg = '#eee';
var colors = ['#fa6', '#f6a'];

function drawGraph(margin, width, height, parent, dt, gamelines) {
  var x = d3.time.scale().range([0, width]);
  var y0 = d3.scale.linear().range([height, 0]);
  var y1 = d3.scale.linear().range([height, 0]);

  var xAxis = d3.svg.axis().scale(x).orient("bottom").ticks(6);
  var yAxisLeft = d3.svg.axis().scale(y0).orient("left");

  var commasFormatter = d3.format(",.0f")

  var yAxisRight = d3.svg.axis()
      .scale(y1)
      .orient("right")
      .tickFormat(function(d) { return '$' + commasFormatter(d) });

  var vline = d3.svg.line()
      .interpolate("monotone")
      .x(function(d) { return x(d.date); })
      .y(function(d) { return y0(d.viewers); })
      .defined(function(d) { return d.viewers > 0 && d.viewers != null; });

  var tline = d3.svg.line()
      .interpolate("monotone")
      .x(function(d) { return x(d.date); })
      .y(function(d) { return y1(d.total); })
      .defined(function(d) { return d.total != null; });

  var svg = d3.select(parent).append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  x.domain(d3.extent(dt, function(d) { return d.date }));
  y0.domain(d3.extent(dt, function(d) { return d.viewers }));
  y1.domain(d3.extent(dt, function(d) { return d.total }));

  var focusLineG = svg.append('g')
    .attr('class', 'focusline');
  var focusLine = focusLineG.append('line')
    .style('display', 'none')
    .style('stroke', '#777');
  var lineg = svg.append('g').attr("pointer-events", "none").attr('opacity', 0);

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxisLeft)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .attr('class', 'axis-label')
      .style("text-anchor", "end")
      .text("Viewers");

  svg.append("g")
      .attr("class", "y axis")
      .attr("transform", "translate(" + width + " ,0)")
      .call(yAxisRight)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", -16)
      .attr("dy", ".71em")
      .attr('class', 'axis-label')
      .style("text-anchor", "end")
      .text("Donations");

  svg.append("path")
      .datum(dt)
      .attr("class", "line")
      .attr("d", vline)
      .style("stroke", colors[0]);

  svg.append("path")
      .datum(dt)
      .attr("class", "line")
      .attr("d", tline)
      .style("stroke", colors[1]);

  var tip = d3.select(parent).append('div')
    .attr('class', 'tooltip');

  var lines = [];
  var bisectDate = d3.bisector(function(d) { return d.date; }).left;
  var current_game = null;
  function tooltip() {
    var x0 = x.invert(d3.mouse(this)[0]),
        i = bisectDate(dt, x0, 1),
        d0 = dt[i - 1],
        d1 = dt[i],
        d = x0 - d0.date > d1.date - x0 ? d1 : d0;

    focusLine
      .attr('x1', x(d.date))
      .attr('x2', x(d.date))
      .attr('y1', 0)
      .attr('y2', height);

    var viewers = d.viewers;
    var total = null;

    if (d.total !== null)
      total = '$' + commasFormatter(d.total);

    var that = this;
    if (gamelines) {
      for (var i = 0; i < gamelines.length-1; i++) {
        if (d.date > gamelines[i][0] && d.date < gamelines[i+1][0]) {
          current_game = gamelines[i][1];
        } else if (d.date > gamelines[i+1][0]) {
          current_game = gamelines[i+1][1];
        }
        if (lines.length > 0) {
          var xpos = lines[i].attr('x1');
          var xmouse = d3.mouse(that)[0];
          // var diff = (width - Math.abs(xmouse - xpos)*3) / width;
          // lines[i].attr('opacity', diff);
        }
      }
    }

    var template = _.template(
      '<% if (current_game !== null) print("<div class=\\"tip-game\\">" + current_game + "</div>") %>' +
      '<div class="tip-text">' +
      '<div class="tip-viewers" style="color:' + colors[0] + '">' +
      '<div class="tip-label">Viewers</div>' +
      '<div><%= viewers %></div>' +
      '</div>' +
      '<div class="tip-total" style="color:' + colors[1] + '">' +
      '<div class="tip-label">Total</div>' +
      '<div><%= total %></div>' +
      '</div>' +
      '</div>'
    );
    tip.html(template({
      current_game: current_game,
      viewers: viewers,
      total: total
    }))
    // tip.html((current_game == null ? '' : ('<div class="tip-game">' +  current_game + '</div>')) +
    //          '<div class="tip-text">' + (viewers == null ? '' : '<div class="tip-viewers"><div>Viewers</div><div>' + viewers + '</div></div>') +
    //          (total == null ? '' : ('<div class="tip-total">' + total + '</div>')) + '</div>')
    .style("left", (d3.event.pageX + 20) + "px")
    .style("top", (d3.event.pageY - 20) + "px");
  }
  if (gamelines) {
    for (var i = 0; i < gamelines.length; i++) {
      lines.push(lineg
        .append('line')
        .attr('class', 'focusline')
        .attr('x1', x(gamelines[i][0]))
        .attr('x2', x(gamelines[i][0]))
        .attr('y1', 0)
        .attr('y2', height)
      );
    }
  }

  svg.append("rect")
      .attr("class", "overlay")
      .attr("width", width)
      .attr("height", height)
      .on("mouseover", function() {
        tip.style("display", null);
        focusLine.style("display", null);
        lineg.attr("opacity", 1);
      })
      .on("mouseout", function() {
        tip.style("display", "none");
        focusLine.style("display", "none");
        lineg.transition().attr("opacity", 0).duration(100);
      })
      .on("mousemove", tooltip)
      .on("click", function() {
        var elm = $('.game-link').filter(function() {
          return $(this).text() == current_game;
        });
        elm.click();
        elm.get(0).scrollIntoView();
        $('#per-game').get(0).scrollIntoView();
      });

  return svg;
}

d3.json("sgdq19.json", function(error, data) {
  var dt = [];
  var i = 0;
  var v = [];
  var t = [];
  var igd = {};

  if (data.viewers && data.viewers.length) {
    var prev = data.viewers[0][1];
    data.viewers.forEach(function (d) {
      // console.log(Math.abs(d[1] - prev), d[1], prev);
      var viewers;
      viewers = d[1] == null ? prev : d[1];
      prev = d[1] == null ? prev : d[1];
      v.push(viewers);
      t.push(d[2]);
      if (data.viewers.length < 460 || i % ((data.viewers.length/460)|0) == 0) {
        dt.push({
          date: new Date(d[0]*1000),
          viewers: Math.max.apply(null, v),
          total:   t.every(function(a){return a==null;}) ? null : Math.max.apply(null, t),
        });
        v = [];
        t = [];
      }
      i++;
    });

    var margin = {top: 20, right: 80, bottom: 30, left: 70},
        width = 900 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    var current_data = [];
    var games = data.games.slice();
    var gamelines = [];
    var next = games.shift();
    var current = undefined;
    for (var i = 0; i < data.viewers.length; i++) {
      var d = data.viewers[i];
      if (!next) {
        igd[current[1]] = current_data.slice();
      } else if(next[0] < d[0]) {
        if (current)
          igd[current[1]] = current_data.slice();
        current_data = [];
        current = next;
        next = games.shift();

        gamelines.push([new Date(d[0]*1000), current[1]]);
      }
      current_data.push({date: new Date(d[0]*1000), viewers: d[1] || 0, total:d[2]});
    }
    // add the current game to gamelines
    if (current)
      igd[current[1]] = current_data.slice();
    current = next;
    if (current)
      gamelines.push([new Date(d[0]*1000), current[1]]);
    gamelines.unshift([0, null]);
    var svg = drawGraph(margin, width, height, "#main-chart", dt, gamelines);
  } else {
    $('#main-chart').text('No data, yet.');
  }
  addGames(data.games, igd);
});

function addGames(list, igd) {
  var template = _.template(
    '<li class="game">' +
      '<div class="game-link"><%= title %></div>' +
      '<div class="game-runner"><%= runner %></div>' +
    '</li>'
  );
  var elm = $('<ul>');
  for (var i = 0; i < list.length; i++) {
    var data = { title: list[i][1], runner: list[i][2] };
    elm.append(template(data));
  }
  $('#games').append(elm);

  var prev = undefined;
  $('.game').click(function(e) {
    var $e = $(e.currentTarget);
    if (prev)
      prev.toggleClass('active');
    $e.toggleClass('active');
    prev = $e;
    var data = _.isEmpty(igd) ? null : igd[$e.find('.game-link').text()];
    if (!data) {
      $('#games-chart').html('No data.<br /><br />Either the game has not been played yet or something went wrong.');
    } else {
      $('#games-chart').html('');
      var margin = {top: 20, right: 80, bottom: 30, left: 70},
          width = 587 - margin.left - margin.right,
          height = 380 - margin.top - margin.bottom;
      var svg = drawGraph(margin, width, height, "#games-chart", data);
    }
  });
}
