import {Query} from "../view.js";

export const drinkGrid = Query()
    .childWithId('drink-grid')
    .value();
export const gridButtons = Query(drinkGrid)
    .oneClass('selector-list')
    .anyTags('button')
    .value();

const settings = Query(drinkGrid)
    .someTags('form')
    .withClass('settings')
    .value();

const submit = Query(settings)
    .oneTag('button')
    .value();

export const data = {
    eventId: Number(Query(drinkGrid)
        .oneClass('main-form')
        .someTags('input')
        .withName('event')
        .value()
        .value),
    drinks: fetch('/api/drinks')
        .then(response => response.json())
        .then(json => new Map(Object.entries(json as {[s: string]: [string, number]})))
}

submit.classList.add('hidden');

for (const element of settings.elements) {
    element.addEventListener('click', () => {
        settings.requestSubmit();
    })
}
