
function colorhash(str) {
  var hash = 0;
  for (var i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  var colour = "#";
  for (var i = 0; i < 3; i++) {
    var value = (hash >> (i * 8)) & 0xff;
    colour += ("00" + value.toString(16)).substr(-2);
  }
  return colour;
}

function updatescores () {
  $.get(CTFd.config.urlRoot + '/api/v1/split_scores', function( response ) {
    var teams = $.parseJSON(JSON.stringify(response.data));
    drawscores('matched', teams);
    drawscores('unmatched', teams);
    drawscores('custom', teams);
  });
}

function drawscores(tab, teams){
  var table = $('#scoreboard-'+tab+' tbody');
  table.empty();
  for (var i = 0; i < teams['standings_'+tab].length; i++) {
      var row="<tr>\n" +
          "<th scope=\"row\" class=\"text-center\">{0}</th>".format(i + 1) +
          "<td><a href=\"{0}/team/{1}\">{2}</a></td>".format(CTFd.config.urlRoot, teams['standings_'+tab][i].id, htmlentities(teams['standings_'+tab][i].team)) +
          "<td>{0}</td>".format(teams['standings_'+tab][i].score) +
          "</tr>";

      table.append(row);
  }
}

function cumulativesum (arr) {
    var result = arr.concat();
    for (var i = 0; i < arr.length; i++){
        result[i] = arr.slice(0, i + 1).reduce(function(p, i){ return p + i; });
    }
    return result
}

function UTCtoDate(utc){
    var d = new Date(0);
    d.setUTCSeconds(utc);
    return d;
}

function scoregraph (tab, response) {
	console.log(response);
	var graph_id = 'score-graph-'+tab;
		var places = $.parseJSON(JSON.stringify(response.data));
		var places = places['places_'+tab];


        if (Object.keys(places).length === 0 ){
            // Replace spinner
            $('#'+graph_id).html(
                '<div class="text-center"><h3 class="spinner-error">No solves yet for '+tab+' teams</h3></div>'
            );
            return;
        }

        var teams = Object.keys(places);
        var traces = [];
        for(var i = 0; i < teams.length; i++){
            var team_score = [];
            var times = [];
            for(var j = 0; j < places[teams[i]]['solves'].length; j++){
                team_score.push(places[teams[i]]['solves'][j].value);
                var date = moment(places[teams[i]]['solves'][j].date);
                times.push(date.toDate());
            }
            team_score = cumulativesum(team_score);
            var trace = {
                x: times,
                y: team_score,
                mode: 'lines+markers',
                name: places[teams[i]]['name'],
                marker: {
                    color: colorhash(places[teams[i]]['name'] + places[teams[i]]['id']),
                },
                line: {
                    color: colorhash(places[teams[i]]['name'] + places[teams[i]]['id']),
                }
            };
            traces.push(trace);
        }

        traces.sort(function(a, b) {
            var scorediff = b['y'][b['y'].length - 1] - a['y'][a['y'].length - 1];
            if(!scorediff) {
                return a['x'][a['x'].length - 1] - b['x'][b['x'].length - 1];
            }
            return scorediff;
        });

        var layout = {
			
            title: 'Top 10 '+(tab == 'matched'?matched_name:tab == 'unmatched'?unmatched_name:'Custom')+' Teams',
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            hovermode: 'closest',
            xaxis: {
                showgrid: false,
                showspikes: true,
            },
            yaxis: {
                showgrid: false,
                showspikes: true,
            },
            legend: {
                "orientation": "h"
            }
        };

        $('#'+graph_id).empty(); // Remove spinners
        Plotly.newPlot(graph_id, traces, layout, {
            displaylogo: false
        });
}

function update(){
  updatescores();
  $.get(CTFd.config.urlRoot + '/api/v1/split_scores/top/10', function( response ) {
	scoregraph('matched', response);
	scoregraph('unmatched', response);
	scoregraph('custom', response);
  });
}

setInterval(update, 300000); // Update scores every 5 minutes
$.get(CTFd.config.urlRoot + '/api/v1/split_scores/top/10', function( response ) {
	scoregraph('matched', response);  // once for matching teams
	scoregraph('unmatched', response); // once for non-matching teams
	scoregraph('custom', response); // once for custom
});

$('a[id^=tab-]').mouseup(function () {
	// wait for tab to change
		resizeGraphs(100);
});

function resizeGraphs(timeout){
	timeout = timeout || 100;
	setTimeout(function(){
	    Plotly.Plots.resize(document.getElementById('score-graph-matched'));
	    Plotly.Plots.resize(document.getElementById('score-graph-unmatched'));
	    Plotly.Plots.resize(document.getElementById('score-graph-custom'));
	}, timeout);
}

window.onresize = function () {
    resizeGraphs(0);
};

$(function() {
	// Search drop down on custom tab
	$('.chosen-select-custom').chosen({ 
		allow_single_deselect: true,
		width: "60%",
		no_results_text: "No teams found for:",
		disable_search_threshold: 10		
	});
	// auto switch to tab if has is in url
	if(window.location.hash) {
		// hash found
		var hash = window.location.hash.substring(1); //Puts hash in variable, and removes the # character
		$('a[id=tab-'+hash+']').click();
		resizeGraphs();
	}
});

