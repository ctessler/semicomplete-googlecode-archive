base_patterns = {
  'USERNAME': r'''[a-zA-Z0-9_-]+''',
  'USER': r'''%USERNAME%''',
  'INT': r'''(?:[+-]?(?:[0-9]+))''',
  'NUMBER': r'''(?:[+-]?(?:(?:[0-9]+(?:\.[0-9]*)?)|(?:\.[0-9]+)))''',
  'POSITIVENUM': r'''\b[0-9]+\b''',
  'WORD': r'''\w+''',
  'NOTSPACE': r'''\S+''',
  'DATA': r'''.*?''',
  'GREEDYDATA': r'''.*''',
  'QUOTEDSTRING': r'''(?:(?<!\\)(?:"(?:\\.|[^\\"])*")|(?:'(?:\\.|[^\\'])*')|(?:`(?:\\.|[^\\`])*`))''',
  'MAC': r'''(?:%CISCOMAC%|%WINDOWSMAC%|%COMMONMAC%)''',
  'CISCOMAC': r'''(?:(?:[A-Fa-f0-9]{4}\.){2}[A-Fa-f0-9]{4})''',
  'WINDOWSMAC': r'''(?:(?:[A-Fa-f0-9]{2}-){5}[A-Fa-f0-9]{2})''',
  'COMMONMAC': r'''(?:(?:[A-Fa-f0-9]{2}:){5}[A-Fa-f0-9]{2})''',
  'IP': r'''(?<![0-9])(?:(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})[.](?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})[.](?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})[.](?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2}))(?![0-9])''',
  'HOSTNAME': r'''(?:[0-9A-z][0-9A-z-]{0,62})(?:\.(?:[0-9A-z][0-9A-z-]{0,62}))*\.?''',
  'HOST': r'''%HOSTNAME%''',
  'IPORHOST': r'''(?:%HOSTNAME%|%IP%)''',
  'HOSTPORT': r'''(?:%IPORHOST=~\.%:%POSITIVENUM%)''',
  'PATH': r'''(?:%UNIXPATH%|%WINPATH%)''',
  'UNIXPATH': r'''(?<![\w\\/])(?:/(?:[\w_@:.,-]+|\\.)*)+''',
  'LINUXTTY': r'''(?:/dev/pts/%POSITIVENUM%)''',
  'BSDTTY': r'''(?:/dev/tty[pq][a-z0-9])''',
  'TTY': r'''(?:%BSDTTY%|%LINUXTTY)''',
  'WINPATH': r'''(?:\\[^\\?*]*)+''',
  'URIPROTO': r'''[A-z]+(\+[A-z+]+)?''',
  'URIHOST': r'''%IPORHOST%(?:%PORT%)?''',
  'URIPATH': r'''(?:/[A-z0-9$.+!*'(),~#%-]*)+''',
  'URIPARAM': r'''\?(?:[A-z0-9]+(?:=(?:[^&]*))?(?:&(?:[A-z0-9]+(?:=(?:[^&]*))?)?)*)?''',
  'URIPATHPARAM': r'''%URIPATH%(?:%URIPARAM%)?''',
  'URI': r'''%URIPROTO%://(?:%USER%(?::[^@]*)?@)?(?:%URIHOST%)?(?:%URIPATH%)?(?:%URIPARAM%)?''',
  'MONTH': r'''\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b''',
  'MONTHNUM': r'''\b(?:0?[0-9]|1[0-2])\b''',
  'MONTHDAY': r'''(?:(?:3[01]|[0-2]?[0-9]))''',
  'DAY': r'''(?:Mon(?:day)?|Tue(?:sday)?|Wed(?:nesday)?|Thu(?:rsday)?|Fri(?:day)?|Sat(?:urday)?|Sun(?:day)?)''',
  'YEAR': r'''%INT%''',
  'TIME': r'''(?!<[0-9])(?:2[0123]|[01][0-9]):(?:[0-5][0-9])(?::(?:[0-5][0-9])(?:\.[0-9]+)?)?(?![0-9])''',
  'DATESTAMP': r'''%INT%/%INT%/%INT%-%INT%:%INT%:%INT%(\.%INT)?''',
  'SYSLOGDATE': r'''%MONTH% +%MONTHDAY% %TIME%''',
  'PROG': r'''(?:[A-z][\w-]+(?:\/[\w-]+)?)''',
  'PID': r'''%INT%''',
  'SYSLOGPROG': r'''%PROG%(?:\[%PID%\])?''',
  'HTTPDATE': r'''%MONTHDAY%/%MONTH%/%YEAR%:%TIME% %INT:ZONE%''',
  'QS': r'''%QUOTEDSTRING%''',
  'SYSLOGBASE': r'''%SYSLOGDATE% %HOSTNAME% %SYSLOGPROG%:''',
  'COMBINEDAPACHELOG': r'''%IPORHOST% %USER:IDENT% %USER:AUTH% \[%HTTPDATE%\] "%WORD% %URIPATHPARAM% HTTP/%NUMBER%" %NUMBER:RESPONSE% (?:%NUMBER:BYTES%|-) "(?:%URI:REFERRER%|-)" %QS:AGENT%''',
}
