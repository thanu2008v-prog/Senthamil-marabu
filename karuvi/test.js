const K = require('./logic.js'); K.setBookWords(require('./bookwords.json'));
const M = require('../sources/moolam.json');
const by = {}; const ex = {};
let total = 0, words = 0;
for (const [id, t] of Object.entries(M)) {
  const a = id.split('.')[0];
  const r = K.checkGrammar(t); words += r.words;
  for (const f of r.findings) {
    const k = a + ' ' + f.rule + ' ' + f.nilai; by[k] = (by[k] || 0) + 1;
    (ex[k] = ex[k] || []).length < 4 && ex[k].push(id + ':' + f.word);
  }
}
console.log('words', words);
for (const k of Object.keys(by).sort()) console.log(k, by[k], ex[k].join(' '));
const kur = "யாயும் ஞாயும் யாரா கியரோ\nஎந்தையும் நுந்தையும் எம்முறைக் கேளிர்\nயானும் நீயும் எவ்வழி யறிதும்\nசெம்புலப் பெயல்நீர் போல\nஅன்புடை நெஞ்சம் தாங்கலந் தனவே";
const y = K.checkYappu(kur);
for (const l of y.lines) console.log(l.ezhuthu, l.vagai, l.seer.map(s => s.s + '=' + s.asai.map(a => a.peyar).join('-')).join(' | '), l.within);
console.log(y.pairs);
console.log(K.checkGrammar("ரவி டப்பா லட்டு ஜன்னல் பஸ் வந்தான் கவ் பார்ட்டி").findings.map(f=>f.word+' '+f.rule+' '+f.nilai));
