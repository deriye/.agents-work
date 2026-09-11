import find_partner_of_a_woman from "./find_partner_of_a_woman.js"

function print(text, value) {
    console.log(`${text} ${JSON.stringify(value)}`)
}

function propose(new_man, woman, data) {
    const { women, engaged, available_men, non_engaged_women } = data;
    let pref_list = women[woman];
    let new_man_rank = pref_list.findIndex((m) => m == new_man)
    let new_man_availability_index = available_men.findIndex((m) => m == new_man)

    let success = false

    print("Available men (before)", available_men)

    // check if woman is engaged
    if (engaged.flat().includes(woman)) {
        let partner = find_partner_of_a_woman(woman, engaged)

        if (!partner) {
            success = true
        } else {
            let partner_index = pref_list.findIndex((m) => m == partner)
            success = new_man_rank < partner_index
        }

        if (success) {
            // remove new_man from available_men
            available_men.splice(new_man_availability_index, 1)
            
            // add partner to available_men
            available_men.push(partner)

            // updated engaged
            let pair_index = engaged.findIndex((p) => p[0] == woman && p[1] == partner);
            engaged.splice(pair_index, 1, [woman, new_man])
        }
    } else {
        success = true
        // remove new_man from available_men
        available_men.splice(new_man_availability_index, 1)

        // remove woman from non_engaged list
        let index = non_engaged_women.findIndex(w => w == woman);
        non_engaged_women.splice(index, 1);

        // add pair to engaged
        engaged.push([woman, new_man]);
    }

    print(`Result (${new_man}, ${woman}):`, success)
    print("Engaged:", engaged)
    print("Available men:", available_men)
    print("Non engaged women:", non_engaged_women)
    console.log("\n")

    return success
}

export default propose;