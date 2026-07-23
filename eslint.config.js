import js from "@eslint/js";
import globals from "globals";
import vue from "eslint-plugin-vue";

export default [
  {
    ignores: ["coverage/**", "dist/**", "node_modules/**"],
  },
  js.configs.recommended,
  ...vue.configs["flat/recommended"],
  {
    files: ["**/*.{js,vue}"],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    rules: {
      "no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
      "vue/attribute-hyphenation": "off",
      "vue/attributes-order": "off",
      "vue/html-closing-bracket-newline": "off",
      "vue/html-indent": "off",
      "vue/html-self-closing": "off",
      "vue/max-attributes-per-line": "off",
      "vue/multi-word-component-names": "off",
      "vue/singleline-html-element-content-newline": "off",
    },
  },
];
