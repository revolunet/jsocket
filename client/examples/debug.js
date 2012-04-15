
function debug() {
	var tgt = document.getElementById('log');
	for (var arg in arguments) {
		var val = arguments[arg];
		if (typeof val == 'string') {
			tgt.value += val + '\n';
		}
		else {
			tgt.value += JSON.stringify(val) + '\n';
		}
	}
	tgt.value += '\n';
	console.log(arguments);
}
