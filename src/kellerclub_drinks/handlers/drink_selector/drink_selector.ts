import {Query} from "../view.js";

export const drinkGrid = Query()
    .childWithId('drink-grid')
    .value();
export const gridButtons = Query(drinkGrid)
    .oneClass('grid')
    .someTags('button')
    .value();

export const data = {
    eventId: Number(Query(drinkGrid)
        .oneClass('grid-form')
        .someTags('input')
        .withName('event')
        .value()
        .value),
    drinks: fetch('/api/drinks')
        .then(response => response.json(), () => Error('Could not fetch drinks!'))
        .then(json => new Map(Object.entries(json as {[s: string]: string})))
}
