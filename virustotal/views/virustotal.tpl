<!DOCTYPE html>
<html>
<head>
<script src="http://code.highcharts.com/adapters/standalone-framework.js"></script>
<script src="http://code.highcharts.com/highcharts.js"></script>
<script src="http://code.highcharts.com/modules/exporting.js"></script>
<title>{{title or 'Virus'}}</title>
</head>
<body>
<div id="container" style="min-width: 310px; height: 400px; max-width: 600px; margin: 0 auto"></div>
</body>
<script>
% import json
% data = {"chart": {"renderTo": "container"},
%         "title": {"text": "Virus Scores" + (": %s" % title if title else "")},
%         "series": [{"type": "pie", "name": "samples", "data": cursor.fetchall()}]}
var chart = new Highcharts.Chart({{!json.dumps(data)}});
</script>
</html>
