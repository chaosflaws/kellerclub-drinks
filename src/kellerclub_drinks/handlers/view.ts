interface Query<T extends Element | Element[] | DocumentFragment> {
    path(): string;
    format(): string;
    value(): Element | Element[] | DocumentFragment;

    childWithId(id: string): Query<Element>;

    oneName(name: string): Query<T>;
    childWithName(name: string): Query<Element>;

    oneClass(className: string): Query<T>;
    someClasses(className: string): Query<Element[]>;
    anyClasses(className: string): Query<Element[]>;

    oneTag(tag: keyof HTMLElementTagNameMap): Query<T>;
    someTags(tag: keyof HTMLElementTagNameMap): Query<Element[]>;
    anyTags(tag: keyof HTMLElementTagNameMap): Query<Element[]>;
}

interface ElementQuery<T extends Element | Element[]> extends Query<T> {
    parent(): Query<T>;

    withId(id: string): Query<Element>;

    withName(name: string): Query<Element>;

    withClass(className: string): Query<Element>;

    withTag(tag: keyof HTMLElementTagNameMap): Query<Element>;
}

export function Query(): SingleQuery<HTMLElement>;
export function Query(node: DocumentFragment): FragmentQuery;
export function Query<T extends Element>(node: T): SingleQuery<T>;
export function Query<T extends Element>(nodes: T[]): MultiQuery<T>;
export function Query(nodes?: Element | Element[] | DocumentFragment) {
    if (!nodes) return new SingleQuery<HTMLElement>('[root]');
    if (nodes instanceof DocumentFragment) return new FragmentQuery(nodeToStr(nodes), nodes);
    if (nodes instanceof Element) return new SingleQuery(nodeToStr(nodes), nodes);
    else return new MultiQuery(nodes.map(node => nodeToStr(node)).join(','), nodes);
}

class FragmentQuery implements Query<DocumentFragment> {
    readonly #node: DocumentFragment;
    readonly #path: string;

    constructor(path: string, node: DocumentFragment) {
        this.#node = node;
        this.#path = path;
    }

    path(): string {
        return this.#path;
    }

    format(): string {
        return nodeToStr(this.#node);
    }

    value(): DocumentFragment {
        return this.#node;
    }

    childWithId(id: string) {
        const result = this.#node.getElementById(id);
        if (result) return new SingleQuery(`[childWithId=${id}]`, result);
        else throw err(this, `ID ${id} does not exist or is not a child of ${this.format()}!`);
    }

    oneName(name: string) {
        return this._oneName(name, `[oneName=${name}]`);
    }

    private _oneName(name: string, path: string) {
        const result = this.#node.querySelector(`[name=${name}]`);
        if (result) return new SingleQuery(path, result);
        else throw err(this, `${name} does not appear as name attribute of a child of ${this.format()}!`);
    }

    childWithName(name: string) {
        return this._oneName(name, `[childWithName=${name}]`);
    }

    oneClass(className: string) {
        const result = this.#node.querySelector(`.${className}`);
        if (result) return new SingleQuery(this.#path + `[oneClass=${className}]`, result);
        else throw err(this, `${className} is not a unique class name below ${this.format()}!`);
    }

    someClasses(className: string) {
        const result = this.#node.querySelectorAll(`.${className}`);
        if (result.length)
            return new MultiQuery(this.#path + `[someClasses=${className}]`, [...result]);
        else throw err(this, `${className} not present below ${this.format()}!`);
    }

    anyClasses(className: string) {
        const result = this.#node.querySelectorAll(`.${className}`);
        return new MultiQuery(this.#path + `[anyClasses=${className}]`, [...result]);
    }

    oneTag<T extends keyof HTMLElementTagNameMap>(tag: T): SingleQuery<HTMLElementTagNameMap[T]> {
        const result = this.#node.querySelector(tag);
        if (result) return new SingleQuery(this.#path + `[oneTag=${tag}]`, result);
        else throw err(this, `${tag} is not a unique element below ${this.format()}!`);
    }

    someTags<T extends keyof HTMLElementTagNameMap>(tag: T): MultiQuery<HTMLElementTagNameMap[T]> {
        const result = this.#node.querySelectorAll(tag);
        if (result.length >= 1)
            return new MultiQuery(this.#path + `[someTags=${tag}]`, [...result]);
        else throw err(this, `${tag} not present below ${this.format()}!`);
    }

    anyTags<T extends keyof HTMLElementTagNameMap>(tag: T): MultiQuery<HTMLElementTagNameMap[T]> {
        const result = this.#node.querySelectorAll(tag);
        return new MultiQuery(this.#path + `[someTags=${tag}]`, [...result]);
    }
}

class SingleQuery<T extends Element> implements ElementQuery<Element> {
    readonly #node: T;
    readonly #path: string;

    constructor(path: string, node?: T) {
        this.#node = (node ?? document.documentElement) as T;
        this.#path = path;
    }

    path(): string {
        return this.#path;
    }

    format(): string {
        return nodeToStr(this.#node);
    }

    value(): T {
        return this.#node;
    }

    parent() {
        const result = this.#node.parentElement;
        if (result) return new SingleQuery('[parent]', result);
        else throw err(this, `${this.format()} does not have a parent element!`);
    }

    withId(id: string) {
        if (this.#node.id == id)
            return new SingleQuery(this.#path + `[withId=${id}]`, this.#node);
        throw err(this, `${this.format()} does not have ID ${id}!`);
    }

    childWithId(id: string) {
        const result = document.getElementById(id);
        if (result && this.#node.contains(result))
            return new SingleQuery<HTMLElement>(this.#path + `[childWithId=${id}]`, result);
        else throw err(this, `ID ${id} does not exist or is not a child of ${this.format()}!`);
    }

    oneName(name: string) {
        return this._oneName(name, this.#path + `[oneName=${name}]`);
    }

    private _oneName(name: string, path: string) {
        const result = this.#node.querySelector(`[name=${name}]`);
        if (result) return new SingleQuery(path, result);
        else throw err(this, `${name} does not appear as name attribute of a child of ${this.format()}!`);
    }

    withName(name: string) {
        if (this.#node.getAttribute('name') == name)
            return new SingleQuery(this.#path + `[withName=${name}]`, this.#node);
        throw err(this, `${this.format()} does not have name ${name}!`);
    }

    childWithName(name: string) {
        return this._oneName(name, this.#path + `[childWithName=${name}]`);
    }

    oneClass(className: string) {
        const result = this.#node.getElementsByClassName(className);
        if (result.length == 1)
            return new SingleQuery(this.#path + `[oneClass=${className}]`, result[0]);
        else throw err(this, `${className} is not a unique class name below ${this.format()}!`);
    }

    someClasses(className: string) {
        const result = this.#node.getElementsByClassName(className);
        if (result.length)
            return new MultiQuery(this.#path + `[someClasses=${className}]`, [...result]);
        else throw err(this, `${className} not present below ${this.format()}!`);
    }

    anyClasses(className: string) {
        const result = this.#node.getElementsByClassName(className);
        return new MultiQuery(this.#path + `[anyClasses=${className}]`, [...result]);
    }

    withClass(className: string) {
        if (this.#node.classList.contains(className))
            return new SingleQuery(this.#path + `[withClass=${className}]`, this.#node);
        else throw err(this, `${this.format()} does not have class ${className}!`);
    }

    oneTag<T extends keyof HTMLElementTagNameMap>(tag: T): SingleQuery<HTMLElementTagNameMap[T]> {
        const result = this.#node.getElementsByTagName(tag);
        if (result.length == 1)
            return new SingleQuery(this.#path + `[oneTag=${tag}]`, result[0]);
        else throw err(this, `${tag} is not a unique element below ${this.format()}!`);
    }

    someTags<T extends keyof HTMLElementTagNameMap>(tag: T): MultiQuery<HTMLElementTagNameMap[T]> {
        const result = this.#node.getElementsByTagName(tag);
        if (result.length >= 1)
            return new MultiQuery(this.#path + `[someTags=${tag}]`, [...result]);
        else throw err(this, `${tag} not present below ${this.format()}!`);
    }

    anyTags<T extends keyof HTMLElementTagNameMap>(tag: T): MultiQuery<HTMLElementTagNameMap[T]> {
        const result = this.#node.getElementsByTagName(tag);
        return new MultiQuery(this.#path + `[someTags=${tag}]`, [...result]);
    }

    withTag<T extends keyof HTMLElementTagNameMap>(tag: T): SingleQuery<HTMLElementTagNameMap[T]> {
        if (this.#node.tagName == tag) return new SingleQuery(this.#path + `[withTag=${tag}]`);
        else throw err(this, `${this.format()} does not have tag ${tag}!`);
    }
}

class MultiQuery<T extends Element> implements ElementQuery<Element[]> {
    readonly #nodes: T[];
    readonly #path: string;

    constructor(path: string, nodes: T[]) {
        this.#nodes = nodes;
        this.#path = path;
    }

    path(): string {
        return this.#path;
    }

    format(): string {
        return this.#nodes.map(node => nodeToStr(node)).join(',');
    }

    value(): T[] {
        return this.#nodes;
    }

    parent() {
        const result = this.#nodes
            .map(node => node.parentElement)
            .filter(node => node) as HTMLElement[];
        if (this.#nodes.length == result.length) return new MultiQuery('[parent]', result);
        else throw err(this, `Some node in ${this.format()} does not have a parent element!`);
    }

    withId(id: string) {
        const result = this.#nodes
            .filter(node => node.id == id);

        if (result.length == 1) return new SingleQuery(this.#path + `[withId=${id}]`, result[0]);
        else throw err(this, `${!result.length ? 'No node' : 'More than one node'} has ID ${id} in ${this.format()}!`);
    }

    childWithId(id: string): Query<Element> {
        const result = document.getElementById(id);
        if (result && this.#nodes.some(node => node.contains(result))) return new SingleQuery(this.#path + `[childWithId=${id}]`, result);
        else throw err(this, `ID ${id} not  found below some node in ${this.format()}!`);
    }

    oneName(name: string) {
        const result = this.#nodes
            .map(node => node.querySelector(`[name=${name}]`))
            .filter(node => node == null) as Element[];

        if (this.#nodes.length == result.length) return new MultiQuery(this.#path + `[oneName=${name}]`, result);
        else throw err(this, `No name attribute ${name} below some node in ${this.format()}!`);
    }

    withName(name: string) {
        const result = this.#nodes
            .filter(node => node.getAttribute('name') == name);

        if (result.length == 1) return new SingleQuery(this.#path + `[withName=${name}]`, result[0]);
        else throw err(this, `${!result.length ? 'No node' : 'More than one node'} has name ${name} in ${this.format()}!`);
    }

    childWithName(name: string) {
        const result = this.#nodes
            .map(node => node.querySelector(`[name=${name}]`))
            .filter(node => node) as Element[];

        if (result.length == 1) return new SingleQuery(this.#path + `[childWithName=${name}]`, result[0]);
        else throw err(this, `${name} is not unique in the children of ${this.format()}!`);
    }

    oneClass(className: string) {
        const result = this.#nodes
            .map(node => node.getElementsByClassName(className))
            .filter(elements => elements.length == 1)
            .map(elements => elements[0]);

        if (this.#nodes.length == result.length) return new MultiQuery(this.#path + `[oneClass=${className}]`, result);
        else throw err(this, `${className} is not a unique class name below some node in ${this.format()}!`);
    }

    someClasses(className: string) {
        const result = this.#nodes
            .map(node => node.getElementsByClassName(className))
            .filter(elements => elements.length >= 1);

        if (this.#nodes.length == result.length) return new MultiQuery(this.#path + `[someClasses=${className}]`, result.flatMap(coll => [...coll]));
        else throw err(this, `${className} not always present on ${this.format()}!`);
    }

    anyClasses(className: string) {
        const result = this.#nodes
            .map(node => node.getElementsByClassName(className));

        if (this.#nodes.length == result.length) return new MultiQuery(this.#path + `[anyClasses=${className}]`, result.flatMap(coll => [...coll]));
        else throw err(this, `${className} not always present on ${this.format()}!`);
    }

    withClass(className: string) {
        const result = this.#nodes
            .filter(node => node.classList.contains(className));

        if (result.length == 1) return new SingleQuery(this.#path + `[withClass=${className}]`, result[0]);
        else throw err(this, `${!result.length ? 'No node' : 'More than one node'} has class ${className} on ${this.format()}!`);
    }

    oneTag<T extends keyof HTMLElementTagNameMap>(tag: T): MultiQuery<HTMLElementTagNameMap[T]> {
        const result = this.#nodes
            .map(node => node.getElementsByTagName(tag))
            .filter(elements => elements.length == 1)
            .map(elements => elements[0]);

        if (this.#nodes.length == result.length) return new MultiQuery(this.#path + `[oneTag=${tag}]`, result);
        else throw err(this, `${tag} is not a unique element below some node in ${this.format()}!`);
    }

    someTags<T extends keyof HTMLElementTagNameMap>(tag: T): MultiQuery<HTMLElementTagNameMap[T]> {
        const result = this.#nodes
            .map(node => node.getElementsByTagName(tag))
            .filter(elements => elements.length >= 1);

        if (this.#nodes.length == result.length) return new MultiQuery(this.#path + `[someTags=${tag}]`, result.flatMap(coll => [...coll]));
        else throw err(this, `${tag} not always present below some node in ${this.format()}!`);
    }

    anyTags<T extends keyof HTMLElementTagNameMap>(tag: T): MultiQuery<HTMLElementTagNameMap[T]> {
        const result = this.#nodes
            .map(node => node.getElementsByTagName(tag));

        return new MultiQuery(this.#path + `[anyTags=${tag}]`, result.flatMap(coll => [...coll]));
    }

    withTag<T extends keyof HTMLElementTagNameMap>(tag: T): SingleQuery<HTMLElementTagNameMap[T]> {
        const result = this.#nodes
            .filter(node => node.tagName == tag) as unknown as HTMLElementTagNameMap[T][];

        if (result.length == 1) return new SingleQuery(this.#path + `[withTag=${tag}]`, result[0]);
        else throw err(this, `${!result.length ? 'No node' : 'More than one node'} has tag ${tag} on ${this.format()}!`);
    }
}

class ViewIntegrityError extends Error {
    constructor(query: Query<never>, message: string, ...params: never[]) {
        super(`Error on Query ${query.path()}: ${message}`, ...params);
    }
}

function err(query: Query<never>, message: string) {
    return new ViewIntegrityError(query, message);
}

function nodeToStr(node: Element | DocumentFragment) {
    if (node instanceof DocumentFragment) return '[Fragment]';
    if (node.id) return `${node.tagName}[#${node.id}]`;
    else return '<' + node.tagName + '>';
}
