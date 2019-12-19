google.load("visualization", "1", {packages:["corechart", "annotatedtimeline"]});
google.setOnLoadCallback(function() {
  loadData();
});

var fg = '#F2F5E9';
var bg = '#364656';
var colors = ['#F4F4B8', '#55C19E'];
var txt = {
  color: fg,
  fontName: 'Source Sans Pro'
}

function time() {
  return new Date().toLocaleString();
}

function fillGames(games, igd) {
  var elm = $('<ul>');
  for (var i = 0; i < games.length; i++) {
    elm.append('<li class="game-link">' + games[i][1] + '</li>');
  }
  $('#games').append(elm);

  var prev = undefined;
  $('.game-link').click(function(e) {
    var $e = $(e.target);
    if (prev)
      prev.toggleClass('active');
    $e.toggleClass('active');
    prev = $e;
    $('#games-chart').html('');

    var gameData = igd[$e.text()];
    var gs = $('#game-stats').html('');

    if (!gameData || gameData.length == 0) {
    $('#games-chart').html('No data.<br /><br />Either the game has not been played yet or something went wrong.');
      return;
    }
    // remove nulls
    var gd = gameData.concat();
    for (var i = 0; i < gd.length; i++) {
      if (!gd[i][1]) {
        gd.splice(i, 1);
        i--; // wow
      }
    }
    var max = Math.max.apply(Math, gd.map(function(o) { return o[1]; }));
    var min = Math.min.apply(Math, gd.map(function(o) { return o[1]; }));
    var avg = 0;
    gd.forEach(function(e, i) { avg += e[1]; });
    avg = (avg/gd.length).toFixed(2);

    gs.append('<p>Max: ' + max + '</p>' +
              '<p>Min: ' + min + '</p>' +
              '<p>Avg: ' + avg + '</p>');

    var d = new google.visualization.DataTable();
    d.addColumn('date', 'time');
    d.addColumn('number', 'viewers');
    d.addColumn('number', 'donation total');
    for (var i = 0; i < gameData.length; i++) {
      var t = gameData[i][0];
      var v = gameData[i][1];
      var dn = gameData[i][2];
      d.addRow([t, v, dn]);
    }
    var options = {
      height: '400px',
      colors: colors,
      backgroundColor: bg,
      focusTarget: 'category',
      chartArea: {
        top: 5,
        left: 50,
        width: '88%',
        height: '88%'
      },
      // pointSize: 3,
      legend: {position: 'none'},
      hAxis: {
        slantedText: false,
        maxAlternation: 1,
        textStyle: txt,
        titleTextStyle: txt,
        baselineColor: fg,
        format: "HH:mm MMM d y"
      },
      vAxis: {
        gridlines: { count: -1 },
        textStyle: txt,
        titleTextStyle: txt,
        baselineColor: fg
      },
      vAxes: {
        0: { logScale: false },
        1: { logScale: false, minValue: 0, gridlines: { count: 0 } }
      },
      series: {
        0: { targetAxisIndex: 0 },
        1: { targetAxisIndex: 1 }
      },
      interpolateNulls: true
    }
    var monthYearFormatter = new google.visualization.DateFormat({ 
       pattern: "HH:mm MMM d y" 
    }); 
    monthYearFormatter.format(d, 0);
    var chart = new google.visualization.LineChart(document.getElementById('games-chart'));
    chart.draw(d, options);
  });
}

function loadData() {
  // var d = [['time', 'viewers']];
  var d = new google.visualization.DataTable();
  d.addColumn('datetime', 'time');
  d.addColumn('number', 'viewers');
  d.addColumn({type: 'string', role: 'annotation'});
  d.addColumn({type: 'string', role: 'annotationText'});
  d.addColumn('number', 'donation total');
  $.getJSON('agdq14.json', function(data) {
      var games = data.games;
      var game = data.games.shift();
      // remove games before we started tracking
      while (true) {
        if (game[0] - data.viewers[0][0] < 0)
          game = data.games.shift();
        else
          break;
      }

      var ig = [game].concat(games);
      var individualGameData = {};
      individualGameData[game[1]] = [];
      var prevGame = '';
      var viewers = [];
      var prev = data.viewers[0][0];
      var prevdn = data.viewers[0][2];

      for (var i = 0; i < data.viewers.length; i++) {
        // var t = new Date(data.viewers[i][0] * 1000).toLocaleString();
        var t = new Date(data.viewers[i][0] * 1000);
        var v = data.viewers[i][1];
        var dn = data.viewers[i][2];
        if (!dn)
          dn = prevdn;
        else
          prevdn = dn;

        var gameAnnotation = null;
        var gameAnnotationText = null;

        if (data.viewers[i][0] - prev > 310
            || i > 0 && Math.abs(v - data.viewers[i-1][1]) > v/4)
          v = null;

        if (i < data.viewers.length-1 && i > 1) {
          // are we between these two times
          var diffp = Math.abs(game[0] - data.viewers[i-1][0]);
          var diffc = Math.abs(game[0] - data.viewers[ i ][0]);
          var diffn = Math.abs(game[0] - data.viewers[i+1][0]);
          if (diffc < diffp && diffc < diffn || diffp < diffc) {
            prevGame = game[1];
            gameAnnotation = 'x';
            gameAnnotationText = game[1];
            var gt = game[0];
            // check for dupes
            game = data.games.shift();
            if (!game)
              break
            if (gt == game[0]) {
              gameAnnotationText += '\n' + game[1];
              game = data.games.shift();
            }
          }
        }

        if (individualGameData[prevGame])
          individualGameData[prevGame].push([t, v, dn]);
        else
          individualGameData[prevGame] = [[t, v, dn]];

        d.addRow([t, v, gameAnnotation, gameAnnotationText, dn]);

        if (v) viewers.push(v);

        prev = data.viewers[i][0];
      }
      fillGames(ig, individualGameData);

      var monthYearFormatter = new google.visualization.DateFormat({ 
           pattern: "HH:mm MMM d y" 
      }); 

      monthYearFormatter.format(d, 0);
      drawChart(d);

      var max = Math.max.apply(Math, viewers.map(function(o) { return o; }));
      var min = Math.min.apply(Math, viewers.map(function(o) { return o; }));
      var avg = 0;
      viewers.forEach(function(e, i) { avg += e; });
      avg = (avg/viewers.length).toFixed(2);
      $('#main-stats').append('<p>Max: ' + max + '</p>' +
                              '<p>Min: ' + min + '</p>' +
                              '<p>Avg: ' + avg + '</p>');
  });
}

function drawChart(data) {
  var options = {
    focusTarget: 'category',
    colors: colors,
    backgroundColor: bg,
     chartArea: {
      left: 60,
      top: 10,
      width: '100%',
      height: '85%'
     },
    legend: {position: 'none'},
    titleTextStyle: txt,
    hAxis: {
      gridlines: { count: 4, color: '#465666' },
      slantedText: false,
      maxAlternation: 1,
      textStyle: txt,
      titleTextStyle: txt,
      baselineColor: fg,
      format: 'HH:mm MMM d, y',
      title: 'Time'
    },
    vAxis: {
      gridlines: { count: -1 },
      textStyle: txt,
      titleTextStyle: txt,
      baselineColor: fg,
      title: 'Viewers'
    },
    vAxes: {
      0: { logScale: false },
      1: { logScale: false, minValue: 0, gridlines: { count: 0 } }
    },
    series: {
      0: { targetAxisIndex: 0 },
      1: { targetAxisIndex: 1 }
    },
    interpolateNulls: true,
    //,annotations: { style: 'line' }
  };

  var chart = new google.visualization.LineChart(document.getElementById('main-chart'));
  chart.draw(data, options);
}
