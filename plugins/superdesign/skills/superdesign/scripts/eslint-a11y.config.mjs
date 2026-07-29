// The five jsx-a11y rules that are NOT in `recommended` and that the superdesign gate assumes.
// Copy into the project under audit (this repo ships no package.json, so nothing here runs
// until a consumer installs the plugin):
//
//   npm i -D eslint eslint-plugin-jsx-a11y
//   // eslint.config.mjs
//   import a11y from 'eslint-plugin-jsx-a11y'
//   import superdesignA11y from './scripts/eslint-a11y.config.mjs'
//   export default [a11y.flatConfigs.recommended, superdesignA11y]

export default {
  files: ['**/*.{jsx,tsx}'],
  rules: {
    'jsx-a11y/no-aria-hidden-on-focusable': 'error',
    'jsx-a11y/control-has-associated-label': 'error',
    'jsx-a11y/anchor-ambiguous-text': 'error',
    'jsx-a11y/prefer-tag-over-role': 'error',
    'jsx-a11y/lang': 'error',
  },
}
