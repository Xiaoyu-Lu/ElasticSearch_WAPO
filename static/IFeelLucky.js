let $id = function(id) {
    return document.getElementById(id);
}

/**
 * Get a random number in the range [0, limit). limit is excluded.
 * @param limit Integer, upper limit of the random number (excluded)
 * @author Yunjing Lee
 */
let randomIdx = function(limit) {
    return Math.floor(Math.random() * limit);
}


let click_lucky = function() {
    let analyzers = document.getElementsByName('options_analyzer')
    analyzers[randomIdx(analyzers.length)].click()

    let optionsEmbeds = document.getElementsByName('options_embed')
    optionsEmbeds[randomIdx(optionsEmbeds.length)].click()

    $id('btn_search').click()
}

window.onload = function() {
    $id('btn_lucky').addEventListener('click', click_lucky);
};