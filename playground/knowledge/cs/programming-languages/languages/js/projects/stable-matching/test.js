import propose from "./utlities/propose.js"
import men from "./data/men.json" with { type: "json" }
import women from "./data/women.json" with { type: "json" }

let available_men = ["m1", "m2", "m3"]
let non_engaged_women = ["w1", "w2", "w3"]
let engaged = []

function main() {
    while (available_men.length > 0) {
        let current_man = available_men.shift()
        let pref_list = men[current_man]

        for (const w of pref_list) {
            const success = propose(current_man, w, { women, engaged, available_men, non_engaged_women })

            if (success) {
                break
            }
        }
    }
}

main()