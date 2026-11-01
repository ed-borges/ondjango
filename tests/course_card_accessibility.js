// Run with: node tests/course_card_accessibility.js
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('learning/static/learning/main.js', 'utf8').replace(/\nloadCatalog\(\);\s*$/, '\n');
let openButton = {dataset: {open: 'python'}};
const fixed = {'[data-ui-language]': {}, '.search-trigger': {}, '.mobile-menu': {}};
const context = {
  document: {
    addEventListener() {},
    querySelector(selector) {
      if (selector === '#session-form input[name=csrfmiddlewaretoken]') return {value: 'csrf'};
      if (selector === '#app') return {};
      return fixed[selector] || null;
    },
    querySelectorAll(selector) { return selector === '[data-open]' ? [openButton] : []; },
  },
  window: {scrollTo() {}}, currentLanguage: () => 'pt', console,
};
vm.createContext(context);
vm.runInContext(source, context);
vm.runInContext(`
  const course = {id:'python', title:'Python &amp; web', category:'PROGRAMAÇÃO', level:'Iniciante', description:'Curso', time:'', color:'orange', icon:'✳', chapters:[]};
  courses = [course];
  const markup = card(course);
  globalThis.cardMarkup = markup;
  render = () => {};
  bind();
`, context);
assert.match(context.cardMarkup, /<article class="course-card"><button type="button" class="course-card-open" data-open="python" aria-label="Abrir curso: Python &amp; web"><\/button>/);
openButton.onclick();
assert.equal(vm.runInContext('state.course.id', context), 'python');
context.currentLanguage = () => 'en';
assert.match(vm.runInContext('card(courses[0])', context), /aria-label="Open course: Python &amp; web"/);
console.log('Course cards: native button, accessible names PT/EN and activation OK');
