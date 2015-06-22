<!DOCTYPE html>
<html>
<meta http-equiv="refresh" content="{{refresh or -1}}">
<title>{{title or 'Virus'}}</title>

<xmp theme="united" style="display:none;">
% def torow(iterable):
%   return '| ' + ' | '.join(map(str, iterable)) + ' |'
% end
{{torow(d[0] for d in cursor.description)}}
{{torow('---' for _ in cursor.description)}}
% for row in cursor:
  {{torow(row)}}
% end
</xmp>

<script src="http://strapdownjs.com/v/0.2/strapdown.js"></script>
</html>
