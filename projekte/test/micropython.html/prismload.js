var goIncludesList = {
	prismCSS: { ready: false, type: 'text/css',        source: 'prism.css' },
	prismJS:  { ready: false, type: 'text/javascript', source: 'prism.js'  }
};
var goIncludesListSelfScriptName = 'prismload.js';
var goIncludesListLoadCompleteCallback = null;

function bsIncludesListLoad( loadCompleteCallback ) {
	var pathPrefix = '';
	try {
		var tempPrefix = document.getElementById(goIncludesListSelfScriptName).src.split('/');
		if( tempPrefix.length > 1 ) {
			tempPrefix.pop();
			pathPrefix = tempPrefix.join('/') + '/';
		};
	} catch(e) {
		pathPrefix = '';
	};
	for( var oIncludeEntry in goIncludesList ) {
		if( goIncludesList.hasOwnProperty(oIncludeEntry) ) {
			if( !goIncludesList[oIncludeEntry].ready ) {
				var elem = null;
				var xsrc = pathPrefix + goIncludesList[oIncludeEntry].source;
				if( goIncludesList[oIncludeEntry].type == 'text/javascript' ) {
					elem = document.createElement('script');
					elem.setAttribute('src', xsrc);
				} else
				if( goIncludesList[oIncludeEntry].type == 'text/css' ) {
					elem = document.createElement('link');
					elem.setAttribute('rel', 'stylesheet');
					elem.setAttribute('href', xsrc);
				} else
					console.log('[' + goIncludesListSelfScriptName + '] dynamic load not implemented, source: ' + goIncludesList[oIncludeEntry].source);
				elem.setAttribute('id', oIncludeEntry);
				elem.setAttribute('type', goIncludesList[oIncludeEntry].type);
				elem.setAttribute('onload', 'javascript:bsIncludesListOnLoad(this);');
				document.head.appendChild(elem);
			};
		};
	};
	goIncludesListLoadCompleteCallback = loadCompleteCallback;
};

function bsIncludesListOnLoad( self ) {
	goIncludesList[self.id].ready = true;
	console.log('[' + goIncludesListSelfScriptName + '] bsIncludesListOnLoad: ' + self.id + ' loaded');
	bsIncludesListOnComplete(self);
};

function bsIncludesListOnComplete( sender ) {
	// check if the whole goIncludesList is loaded
	for( var oIncludeEntry in goIncludesList ) {
		if( goIncludesList.hasOwnProperty(oIncludeEntry) ) {
			if( !goIncludesList[oIncludeEntry].ready ) {
				return console.log('[' + goIncludesListSelfScriptName + '] bsIncludesListOnComplete: loaded ' + sender.id + ' but not ready yet, waiting for: ' + oIncludeEntry);
			};
		};
	};
	console.log('[' + goIncludesListSelfScriptName + '] bsIncludesListOnComplete: all dependencies have been loaded');
	if( goIncludesListLoadCompleteCallback ) {
		goIncludesListLoadCompleteCallback();
	};
};

document.onreadystatechange = function() {
	if( document.readyState == "complete" ) {
		var coderegexp  = new RegExp('^</','i');
		var codeblocks = document.getElementsByTagName('code');
		for(var i = 0; i < codeblocks.length; i++) {
			var l = codeblocks[i].innerHTML.replaceAll('&','&amp;').replaceAll('<mark>','#@#m*a*r*k#@#').replaceAll('</mark>','#~#m*a*r*k#~#').split('\n');
			if( (l.length > 0) && coderegexp.test(l[l.length-1]) ) l.pop();
			codeblocks[i].innerHTML = l.join('\n').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('#@#m*a*r*k#@#','<mark>').replaceAll('#~#m*a*r*k#~#','</mark>');
		};
		bsIncludesListLoad(null);
	};
};