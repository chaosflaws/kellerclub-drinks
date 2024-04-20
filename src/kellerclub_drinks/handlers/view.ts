interface Query<T extends Element | Element[]> {
    path(): string;
    value(): Element | Element[];
    childWithId(id: string): Query<Element>;
    oneName(name: string): Query<T>;
    withName(name: string): Query<Element>;
    childWithName(name: string): Query<Element>;
    oneClass(className: string): Query<T>;
    someClasses(className: string): Query<Element[]>;
    oneTag(tag: keyof HTMLElementTagNameMap): Query<T>;
    someTags(tag: keyof HTMLElementTagNameMap): Query<Element[]>;
    anyTags(tag: keyof HTMLElementTagNameMap): Query<Element[]>;
}

export function Query(): SingleQuery<HTMLElement>;
export function Query<T extends Element>(nodes: T): SingleQuery<T>;
export function Query<T extends Element>(nodes: T[]): MultiQuery<T>;
export function Query(nodes?: Element | Element[]) {
    if (!nodes) return new SingleQuery<HTMLElement>('[root]');
    if (nodes instanceof Element) return new SingleQuery(nodeToStr(nodes), nodes);
    else return new MultiQuery(nodes.map(node => nodeToStr(node)).join(','), nodes);
}

class SingleQuery<T extends Element> implements Query<Element> {
    readonly #node: T;
    readonly #path: string;

    constructor(path: string, node?: T) {
        this.#node = (node ?? document.documentElement) as T;
        this.#path = path;
    }

    path(): string {
        return this.#path;
    }

    value(): T {
        return this.#node;
    }

    childWithId(id: string) {
        const result = document.getElementById(id);
        if (result && this.#node.contains(result))
            return new SingleQuery<HTMLElement>(this.#path + `[childWithId=${id}]`, result);
        else throw err(this, `ID ${id} does not exist or is not a child of ${nodeToStr(this.#node)}!`);
    }

    oneName(name: string) {
        return this._oneName(name, this.#path + `[oneName=${name}]`);
    }

    private _oneName(name: string, path: string) {
        const result = this.#node.querySelector(`[name=${name}]`);
        if (result) return new SingleQuery(path, result);
        else throw err(this, `${name} does not appear as name attribute of a child of ${nodeToStr(this.#node)}!`);
    }

    withName(name: string) {
        if (this.#node.getAttribute('name') != name)
            throw err(this, `${nodeToStr(this.#node)} does not have name ${name}!`);
        return new SingleQuery(this.#path + `[withName=${name}]`, this.#node);
    }

    childWithName(name: string) {
        return this._oneName(name, this.#path + `[childWithName=${name}]`);
    }

    oneClass(className: string) {
        const result = this.#node.getElementsByClassName(className);
        if (result.length == 1)
            return new SingleQuery(this.#path + `[oneClass=${className}]`, result[0]);
        else throw err(this, `${className} is not a unique class name below ${nodeToStr(this.#node)}!`);
    }

    someClasses(className: string) {
        const result = this.#node.getElementsByClassName(className);
        if (result.length)
            return new MultiQuery(this.#path + `[someClasses=${className}]`, [...result]);
        else throw err(this, `${className} not present!`);
    }

    oneTag<T extends keyof HTMLElementTagNameMap>(tag: T): SingleQuery<HTMLElementTagNameMap[T]> {
        const result = this.#node.getElementsByTagName(tag);
        if (result.length == 1)
            return new SingleQuery(this.#path + `[oneTag=${tag}]`, result[0]);
        else throw err(this, `${tag} is not a unique element below ${nodeToStr(this.#node)}!`);
    }

    someTags<T extends keyof HTMLElementTagNameMap>(tag: T): MultiQuery<HTMLElementTagNameMap[T]> {
        const result = this.#node.getElementsByTagName(tag);
        if (result.length >= 1)
            return new MultiQuery(this.#path + `[someTags=${tag}]`, [...result]);
        else throw err(this, `${tag} not present below ${nodeToStr(this.#node)}!`);
    }

    anyTags<T extends keyof HTMLElementTagNameMap>(tag: T): MultiQuery<HTMLElementTagNameMap[T]> {
        const result = this.#node.getElementsByTagName(tag);
        return new MultiQuery(this.#path + `[someTags=${tag}]`, [...result]);
    }
}

class MultiQuery<T extends Element> implements Query<Element[]> {
    readonly #nodes: T[];
    readonly #path: string;

    constructor(path: string, nodes: T[]) {
        this.#nodes = nodes;
        this.#path = path;
    }

    path(): string {
        return this.#path;
    }

    value(): T[] {
        return this.#nodes;
    }

    childWithId(id: string): Query<Element> {
        const result = document.getElementById(id);
        if (result && this.#nodes.some(node => node.contains(result))) return new SingleQuery(this.#path + `[childWithId=${id}]`, result);
        else throw err(this, `ID ${id} not  found below some node in ${this.#nodes.map(node => nodeToStr(node)).join(',')}!`);
    }

    oneName(name: string) {
        const result = this.#nodes
            .map(node => node.querySelector(`[name=${name}]`))
            .filter(node => node == null) as Element[];

        if (this.#nodes.length == result.length) return new MultiQuery(this.#path + `[oneName=${name}]`, result);
        else throw err(this, `No name attribute ${name} below some node in ${this.#nodes.map(node => nodeToStr(node)).join(',')}!`);
    }

    withName(name: string) {
        const result = this.#nodes
            .filter(node => node.getAttribute('name') == name);

        if (result.length == 1) return new SingleQuery(this.#path + `[withName=${name}]`, result[0]);
        else throw err(this, `${result.length == 0 ? 'No node' : 'More than one node'} in ${this.#nodes.map(node => nodeToStr(node)).join(',')} has name ${name}!`);
    }

    childWithName(name: string) {
        const result = this.#nodes
            .map(node => node.querySelector(`[name=${name}]`))
            .filter(node => node == null) as Element[];

        if (result.length == 1) return new SingleQuery(this.#path + `[childWithName=${name}]`, result[0]);
        else throw err(this, `${name} is not unique in the children of ${this.#nodes.map(node => nodeToStr(node)).join(',')}!`);
    }

    oneClass(className: string) {
        const result = this.#nodes
            .map(node => node.getElementsByClassName(className))
            .filter(elements => elements.length == 1)
            .map(elements => elements[0]);

        if (this.#nodes.length == result.length) return new MultiQuery(this.#path + `[oneClass=${className}]`, result);
        else throw err(this, `${className} is not a unique class name below some node in ${this.#nodes.map(node => nodeToStr(node)).join(',')}!`);
    }

    someClasses(className: string) {
        const result = this.#nodes
            .map(node => node.getElementsByClassName(className))
            .filter(elements => elements.length >= 1)
            .map(elements => elements[0]);

        if (this.#nodes.length == result.length) return new MultiQuery(this.#path + `[someClasses=${className}]`, result);
        else throw err(this, `${className} not always present on ${this.#nodes.map(node => nodeToStr(node)).join(',')}!`);
    }

    oneTag<T extends keyof HTMLElementTagNameMap>(tag: T): MultiQuery<HTMLElementTagNameMap[T]> {
        const result = this.#nodes
            .map(node => node.getElementsByTagName(tag))
            .filter(elements => elements.length == 1)
            .map(elements => elements[0]);

        if (this.#nodes.length == result.length) return new MultiQuery(this.#path + `[oneTag=${tag}]`, result);
        else throw err(this, `${tag} is not a unique element below some node in ${this.#nodes.map(node => nodeToStr(node)).join(',')}!`);
    }

    someTags<T extends keyof HTMLElementTagNameMap>(tag: T): MultiQuery<HTMLElementTagNameMap[T]> {
        const result = this.#nodes
            .map(node => node.getElementsByTagName(tag))
            .filter(elements => elements.length >= 1)
            .map(elements => elements[0]);

        if (this.#nodes.length == result.length) return new MultiQuery(this.#path + `[someTags=${tag}]`, result);
        else throw err(this, `${tag} not always present below some node in ${this.#nodes.map(node => nodeToStr(node)).join(',')}!`);
    }

    anyTags<T extends keyof HTMLElementTagNameMap>(tag: T): MultiQuery<HTMLElementTagNameMap[T]> {
        const result = this.#nodes
            .map(node => node.getElementsByTagName(tag))
            .filter(elements => elements.length >= 1)
            .map(elements => elements[0]);

        return new MultiQuery(this.#path + `[someTags=${tag}]`, result);
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

function nodeToStr(node: Element) {
    return `${node.tagName}[#${node.id}]`
}
