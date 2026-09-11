function find_partner_of_a_woman(woman, engaged) {
    let result = undefined

    for (const pair of engaged) {
        if (pair.includes(woman)) {
            result = pair[1]
            break
        }
    }

    return result
}

export default find_partner_of_a_woman;