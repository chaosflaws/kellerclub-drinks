const {copyFile, readFile, writeFile, utimes} = require('node:fs/promises');
const {exec} = require('child_process');
const {src, dest, parallel, series, watch} = require('gulp');
const concat = require('gulp-concat');
const cleanCss = require('gulp-clean-css');
const ts = require('gulp-typescript');

function copyPython() {
    return src(['src/**/*.py', 'src/app.wsgi'])
        .pipe(dest('build/'));
}

function touchWsgi() {
    const now = new Date();
    return utimes('src/app.wsgi', now, now);
}

function copyTemplates() {
    return src('src/**/*.jinja2')
        .pipe(dest('build/'));
}

function copyBinStatic() {
    // gulp corrupts binary files
    return copyFile(
        'src/kellerclub_drinks/handlers/bootstrap_icons.woff2',
        'build/kellerclub_drinks/handlers/bootstrap_icons.woff2');
}

function modifyBaseTemplate() {
    const infile = 'src/kellerclub_drinks/handlers/base.jinja2';
    const outfile = 'build/kellerclub_drinks/handlers/base.jinja2';
    return readFile(infile)
        .then(content => content
            .toString()
            .replace('{% block css %}{% endblock %}', '')
            .replace('<link rel="stylesheet" href="/base.css">', '<link rel="stylesheet" href="/style.css">'))
        .then(result => writeFile(outfile, result));
}

function minCss() {
    return src('src/**/*.css')
        .pipe(cleanCss())
        .pipe(concat('kellerclub_drinks/handlers/style.css'))
        .pipe(dest('build/'));
}

const tsProject = ts.createProject('tsconfig.json');
function transpileTs() {
    return tsProject.src()
        .pipe(tsProject())
        .on('error', () => {})
        .pipe(dest('src'));
}

function copyJs() {
    return src('src/**/*.js')
        .pipe(dest('build/'))
}

function testPython() {
    const cmd = 'py -m unittest discover -s test';
    const env = {...process.env, 'PYTHONPATH': 'src'};
    return exec(cmd, {env});
}

function _watch() {
    watch('src/**/*.py', parallel(testPython, copyPython, touchWsgi));
    watch('src/app.wsgi', parallel(testPython, copyPython));
    watch('test/**/*.py', testPython);

    watch('src/**/*.jinja2', series(copyTemplates, modifyBaseTemplate));
    watch('src/**/*.woff2', copyBinStatic);
    watch('src/**/*.css', minCss);
    watch('src/**/*.ts', series(transpileTs, copyJs));
}

function serve() {
    return exec('py scripts/local_server.py');
}

const _default = series(
    testPython,
    parallel(
        copyPython,
        series(copyTemplates, copyBinStatic, modifyBaseTemplate),
        minCss,
        series(transpileTs, copyJs)));
exports.default = _default;

exports.watch = series(_default, _watch);
exports.serve = serve;
