const badgeClasses = {
    'badge-dark': 0,
    'badge-light': 0,
    'badge-info': 0,
    'badge-warning': 0,
    'badge-danger': 0,
    'badge-success': 0,
    'badge-secondary': 0,
    'badge-primary': 0,
}

let tagBadgeMapping = {}

const getTagBadge = tag => {
    const tagLower = tag.toLowerCase()
    if (tagBadgeMapping[tagLower] === undefined) {
        const leastChosenClassName = Object.keys(badgeClasses).reduce(
            (className, current, index, item) =>
                badgeClasses[className] < badgeClasses[current] ? className : current
        )
        tagBadgeMapping[tagLower] = leastChosenClassName
        badgeClasses[leastChosenClassName]++
    }
    return tagBadgeMapping[tagLower]
}

function reportsTagFormatter(value, row, index) {
    const result = value?.map(item => {
        return `<span class="badge badge-pill ${getTagBadge(item)}">${item}</span>`
    })
    return result?.join(' ')
}