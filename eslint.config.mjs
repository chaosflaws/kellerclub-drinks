import globals from "globals";
import tseslint from "typescript-eslint";

export default [
    {
        languageOptions: {
            globals: globals.browser,
            parserOptions: {
                project: true
            }
        }
    },
    ...tseslint.configs.strictTypeChecked,
];
